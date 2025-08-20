#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章抓取器 FastAPI 服务
提供两个API接口：
1. GET /article/info - 获取文章信息
2. POST /article/save-to-feishu - 保存文章到飞书
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import uvicorn
from bs4 import BeautifulSoup
import logging

# 导入现有的类和配置
from wechat_article_scraper import WeChatArticleScraper, FeishuBitableClient
import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="微信公众号文章抓取器API",
    description="提供微信公众号文章抓取和飞书保存功能",
    version="1.0.0"
)

# 请求模型
class ArticleRequest(BaseModel):
    url: HttpUrl
    include_ocr: Optional[bool] = True
    download_images: Optional[bool] = True

class FeishuSaveRequest(BaseModel):
    url: HttpUrl
    include_ocr: Optional[bool] = True
    download_images: Optional[bool] = True

# 响应模型
class ImageInfo(BaseModel):
    src: str
    alt: str
    title: str

class OCRResult(BaseModel):
    image_url: str
    local_path: str
    ocr_text: str
    alt: str
    title: str

class ArticleInfo(BaseModel):
    url: str
    title: str
    content: str
    account_name: Optional[str] = ""
    publish_date: Optional[str] = ""
    images: List[ImageInfo]
    ocr_results: List[OCRResult]
    image_count: int
    content_length: int

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# 全局抓取器实例
scraper = WeChatArticleScraper(output_dir=config.OUTPUT_DIR)

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "微信公众号文章抓取器API",
        "version": "1.0.0",
        "endpoints": {
            "/article/info": "GET - 获取文章信息",
            "/article/save-to-feishu": "POST - 保存文章到飞书",
            "/docs": "API文档"
        }
    }

@app.get("/article/info", response_model=ApiResponse)
async def get_article_info(url: str, include_ocr: bool = True, download_images: bool = True):
    """
    功能1：获取文章信息
    
    Args:
        url: 微信公众号文章链接
        include_ocr: 是否进行OCR识别
        download_images: 是否下载图片
    
    Returns:
        包含文章标题、正文、图片等信息的响应
    """
    try:
        logger.info(f"开始处理文章信息请求: {url}")
        
        # 获取基本文章内容
        article_info = scraper.get_article_content(url)
        if not article_info:
            raise HTTPException(status_code=400, detail="无法获取文章内容，请检查URL是否正确")
        
        # 获取公众号名称和发布日期
        try:
            response = scraper.session.get(url, headers=scraper.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            account_name = scraper.extract_account_name(soup)
            publish_date = scraper.extract_publish_date(soup)
        except Exception as e:
            logger.warning(f"获取公众号信息失败: {e}")
            account_name = ""
            publish_date = ""
        
        # 处理图片和OCR（如果需要）
        if download_images and include_ocr:
            for i, img_info in enumerate(article_info['images']):
                try:
                    # 生成文件名
                    file_extension = scraper._get_file_extension(img_info['src'])
                    filename = f"{config.IMAGE_FILENAME_PREFIX}{i+1}{file_extension}"
                    
                    # 下载图片
                    image_path = scraper.download_image(img_info['src'], filename)
                    
                    if image_path:
                        # OCR识别
                        ocr_text = scraper.ocr_image(image_path)
                        
                        # 保存OCR结果
                        article_info['ocr_results'].append({
                            'image_url': img_info['src'],
                            'local_path': image_path,
                            'ocr_text': ocr_text,
                            'alt': img_info['alt'],
                            'title': img_info['title']
                        })
                except Exception as e:
                    logger.error(f"处理图片 {i+1} 失败: {e}")
                    if not config.CONTINUE_ON_ERROR:
                        raise HTTPException(status_code=500, detail=f"处理图片失败: {e}")
        
        # 构建响应数据
        response_data = ArticleInfo(
            url=article_info['url'],
            title=article_info['title'],
            content=article_info['content'],
            account_name=account_name,
            publish_date=publish_date,
            images=[ImageInfo(**img) for img in article_info['images']],
            ocr_results=[OCRResult(**ocr) for ocr in article_info['ocr_results']],
            image_count=len(article_info['images']),
            content_length=len(article_info['content'])
        )
        
        logger.info(f"成功处理文章: {article_info['title']}")
        return ApiResponse(
            success=True,
            message="文章信息获取成功",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文章信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.post("/article/save-to-feishu", response_model=ApiResponse)
async def save_article_to_feishu(request: FeishuSaveRequest, background_tasks: BackgroundTasks):
    """
    功能2：保存文章到飞书
    
    Args:
        request: 包含文章URL和处理选项的请求
        background_tasks: 后台任务（用于异步处理图片下载和OCR）
    
    Returns:
        保存结果响应
    """
    try:
        logger.info(f"开始处理飞书保存请求: {request.url}")
        
        # 检查飞书配置
        if not config.FEISHU_ENABLED:
            raise HTTPException(status_code=400, detail="飞书功能未启用")
        
        # 获取文章内容
        article_info = scraper.get_article_content(str(request.url))
        if not article_info:
            raise HTTPException(status_code=400, detail="无法获取文章内容，请检查URL是否正确")
        
        # 获取公众号名称和发布日期
        try:
            response = scraper.session.get(str(request.url), headers=scraper.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            account_name = scraper.extract_account_name(soup)
            publish_date = scraper.extract_publish_date(soup)
        except Exception as e:
            logger.warning(f"获取公众号信息失败: {e}")
            account_name = ""
            publish_date = ""
        
        # 如果需要OCR，在后台处理图片
        ocr_text = ""
        if request.download_images and request.include_ocr:
            # 同步处理OCR（为了确保数据完整性）
            for i, img_info in enumerate(article_info['images']):
                try:
                    file_extension = scraper._get_file_extension(img_info['src'])
                    filename = f"{config.IMAGE_FILENAME_PREFIX}{i+1}{file_extension}"
                    image_path = scraper.download_image(img_info['src'], filename)
                    
                    if image_path:
                        ocr_result = scraper.ocr_image(image_path)
                        article_info['ocr_results'].append({
                            'image_url': img_info['src'],
                            'local_path': image_path,
                            'ocr_text': ocr_result,
                            'alt': img_info['alt'],
                            'title': img_info['title']
                        })
                except Exception as e:
                    logger.error(f"处理图片 {i+1} 失败: {e}")
                    if not config.CONTINUE_ON_ERROR:
                        raise HTTPException(status_code=500, detail=f"处理图片失败: {e}")
            
            # 组装OCR文本
            ocr_combined = []
            for i, item in enumerate(article_info.get('ocr_results', [])):
                ocr_combined.append(f"[图片{i+1}] {item.get('image_url','')}\n{item.get('ocr_text','')}")
            ocr_text = "\n\n".join(ocr_combined) if ocr_combined else ""
        
        # 组装完整内容
        full_content = article_info['content']
        if ocr_text:
            full_content += "\n\n📸 图片 OCR 识别内容：\n" + ocr_text
        
        # 创建飞书客户端
        client = FeishuBitableClient(
            app_id=config.FEISHU_APP_ID,
            app_secret=config.FEISHU_APP_SECRET,
            app_token=config.FEISHU_APP_TOKEN,
            table_id=config.FEISHU_TABLE_ID,
            auth_mode=config.FEISHU_AUTH_MODE,
            bearer_token=config.FEISHU_BEARER_TOKEN,
        )
        
        # 验证表是否存在
        client.ensure_table_exists()
        
        # 准备字段数据
        fields_map = config.FEISHU_FIELDS
        fields = {
            fields_map.get('account_name', '公众号名称'): account_name or '',
            fields_map.get('title', '标题'): article_info['title'],
            fields_map.get('content', '正文'): full_content,
            fields_map.get('read_count', '阅读量'): '',
            fields_map.get('publish_date', '发布日期'): publish_date or '',
        }
        
        # 写入飞书
        result = client.add_record(fields)
        
        logger.info(f"成功保存文章到飞书: {article_info['title']}")
        return ApiResponse(
            success=True,
            message="文章已成功保存到飞书",
            data={
                "title": article_info['title'],
                "account_name": account_name,
                "publish_date": publish_date,
                "content_length": len(full_content),
                "image_count": len(article_info['images']),
                "ocr_count": len(article_info['ocr_results']),
                "feishu_record_id": result.get('data', {}).get('record', {}).get('record_id', '')
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存到飞书失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存到飞书失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务运行正常"}

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )