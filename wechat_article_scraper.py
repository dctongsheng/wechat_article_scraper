#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章抓取器
功能：
1. 抓取文章标题
2. 提取正文纯文本内容
3. 提取正文中所有图片链接
4. 下载图片并用OCR识别中文文字
5. 输出所有信息到控制台
"""

import requests
import re
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from PIL import Image
import pytesseract
from io import BytesIO
import logging
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeChatArticleScraper:
    """微信公众号文章抓取器"""
    
    def __init__(self, output_dir="downloaded_images"):
        """
        初始化抓取器
        
        Args:
            output_dir (str): 图片下载目录
        """
        self.session = requests.Session()
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建图片下载目录: {output_dir}")
    
    def get_article_content(self, url):
        """
        获取文章内容
        
        Args:
            url (str): 微信公众号文章链接
            
        Returns:
            dict: 包含文章信息的字典
        """
        try:
            logger.info(f"开始抓取文章: {url}")
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章信息
            article_info = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'images': self._extract_images(soup),
                'ocr_results': []
            }
            
            logger.info(f"成功提取文章标题: {article_info['title']}")
            logger.info(f"成功提取正文内容，长度: {len(article_info['content'])} 字符")
            logger.info(f"发现 {len(article_info['images'])} 张图片")
            
            return article_info
            
        except Exception as e:
            logger.error(f"抓取文章失败: {str(e)}")
            return None
    
    def _extract_title(self, soup):
        """提取文章标题"""
        # 尝试多种方式提取标题
        title_selectors = [
            'h1.rich_media_title',
            'h1[id*="activity-name"]',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    return title
        
        return "未找到标题"
    
    def _extract_content(self, soup):
        """提取文章正文内容"""
        # 尝试多种方式提取正文
        content_selectors = [
            'div.rich_media_content',
            'div[id*="js_content"]',
            'div.article-content',
            'div.content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式标签
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # 获取纯文本内容
                content = content_elem.get_text(separator='\n', strip=True)
                # 清理多余的空白字符
                content = re.sub(r'\n\s*\n', '\n\n', content)
                return content
        
        return "未找到正文内容"
    
    def _extract_images(self, soup):
        """提取文章中的图片链接"""
        images = []
        
        # 查找所有图片标签
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if src:
                # 处理相对URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://mp.weixin.qq.com' + src
                
                # 过滤掉一些不需要的图片
                if not any(skip in src.lower() for skip in ['avatar', 'icon', 'logo', 'qrcode']):
                    images.append({
                        'src': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
        
        return images
    
    def download_image(self, image_url, filename):
        """
        下载图片
        
        Args:
            image_url (str): 图片URL
            filename (str): 保存的文件名
            
        Returns:
            str: 下载的文件路径，失败返回None
        """
        try:
            response = self.session.get(image_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"成功下载图片: {filename}")
            return file_path
            
        except Exception as e:
            logger.error(f"下载图片失败 {image_url}: {str(e)}")
            return None
    
    def ocr_image(self, image_path):
        """
        对图片进行OCR识别
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: OCR识别结果
        """
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 使用pytesseract进行OCR识别
            # 设置语言为中文简体
            text = pytesseract.image_to_string(image, lang='chi_sim')
            
            # 清理识别结果
            text = text.strip()
            
            if text:
                logger.info(f"OCR识别成功: {image_path}")
                return text
            else:
                logger.warning(f"OCR识别结果为空: {image_path}")
                return "OCR识别结果为空"
                
        except Exception as e:
            logger.error(f"OCR识别失败 {image_path}: {str(e)}")
            return f"OCR识别失败: {str(e)}"
    
    def process_article(self, url):
        """
        处理完整的文章抓取流程
        
        Args:
            url (str): 微信公众号文章链接
            
        Returns:
            dict: 完整的文章信息
        """
        # 1. 获取文章内容
        article_info = self.get_article_content(url)
        if not article_info:
            return None
        
        # 2. 下载图片并进行OCR识别
        for i, img_info in enumerate(article_info['images']):
            logger.info(f"处理第 {i+1} 张图片: {img_info['src']}")
            
            # 生成文件名
            file_extension = self._get_file_extension(img_info['src'])
            filename = f"image_{i+1}{file_extension}"
            
            # 下载图片
            image_path = self.download_image(img_info['src'], filename)
            
            if image_path:
                # OCR识别
                ocr_text = self.ocr_image(image_path)
                
                # 保存OCR结果
                article_info['ocr_results'].append({
                    'image_url': img_info['src'],
                    'local_path': image_path,
                    'ocr_text': ocr_text,
                    'alt': img_info['alt'],
                    'title': img_info['title']
                })
                
                # 添加延迟，避免请求过于频繁
                time.sleep(1)
        
        return article_info
    
    def _get_file_extension(self, url):
        """从URL中提取文件扩展名"""
        parsed = urlparse(url)
        path = parsed.path
        if '.' in path:
            return '.' + path.split('.')[-1]
        return '.jpg'  # 默认扩展名
    
    def print_results(self, article_info):
        """
        将结果输出到控制台
        
        Args:
            article_info (dict): 文章信息
        """
        if not article_info:
            print("没有可用的文章信息")
            return
        
        print("\n" + "="*80)
        print("微信公众号文章抓取结果")
        print("="*80)
        
        # 1. 文章标题
        print(f"\n📰 文章标题:")
        print(f"   {article_info['title']}")
        
        # 2. 文章链接
        print(f"\n🔗 文章链接:")
        print(f"   {article_info['url']}")
        
        # 3. 正文内容
        print(f"\n📝 正文内容:")
        content = article_info['content']
        if len(content) > 500:
            print(f"   {content[:500]}...")
            print(f"   (内容过长，已截取前500字符，完整内容请查看日志)")
        else:
            print(f"   {content}")
        
        # 4. 图片信息
        print(f"\n🖼️  图片信息 (共{len(article_info['images'])}张):")
        for i, img in enumerate(article_info['images']):
            print(f"   图片 {i+1}:")
            print(f"     URL: {img['src']}")
            if img['alt']:
                print(f"     描述: {img['alt']}")
            if img['title']:
                print(f"     标题: {img['title']}")
        
        # 5. OCR识别结果
        print(f"\n🔍 OCR识别结果:")
        for i, ocr_result in enumerate(article_info['ocr_results']):
            print(f"   图片 {i+1} OCR结果:")
            print(f"     本地路径: {ocr_result['local_path']}")
            print(f"     识别文字: {ocr_result['ocr_text']}")
            print()
        
        print("="*80)
        print("抓取完成！")

    def extract_account_name(self, soup):
        """尝试提取公众号名称"""
        selectors = [
            '#js_name',
            'a#js_name',
            '.rich_media_meta_list .rich_media_meta_nickname',
            'span.rich_media_meta_text',
        ]
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem:
                name = elem.get_text(strip=True)
                if name:
                    return name
        return ""

    def extract_publish_date(self, soup):
        """尝试提取发布日期（返回字符串）"""
        # 微信常见发布时间在script里或span#publish_time
        candidates = []
        span = soup.select_one('#publish_time')
        if span:
            candidates.append(span.get_text(strip=True))
        time_span = soup.select_one('span.rich_media_meta_text')
        if time_span:
            candidates.append(time_span.get_text(strip=True))
        for text in candidates:
            if text:
                return text
        return ""

# ================== 飞书写入功能 ==================
class FeishuBitableClient:
    def __init__(self, app_id: str, app_secret: str, app_token: str, table_id: str, auth_mode: str = 'tenant', bearer_token: str | None = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id
        self.auth_mode = auth_mode
        self.bearer_token = bearer_token
        self.base = "https://open.feishu.cn/open-apis"
        self._app_access_token = None

    def _get_tenant_access_token(self) -> str:
        if self._app_access_token:
            return self._app_access_token
        url = f"{self.base}/auth/v3/tenant_access_token/internal/"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }, timeout=30)
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"获取tenant_access_token失败: {data}")
        self._app_access_token = data["tenant_access_token"]
        return self._app_access_token

    def _get_authorization_header(self) -> dict:
        """根据配置返回 Authorization 头。"""
        if self.auth_mode == 'user' and self.bearer_token:
            return {"Authorization": f"Bearer {self.bearer_token}"}
        # 默认使用租户 token
        return {"Authorization": f"Bearer {self._get_tenant_access_token()}"}

    def add_record(self, fields: dict) -> dict:
        url = f"{self.base}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        headers = {**self._get_authorization_header(), "Content-Type": "application/json"}
        payload = {"fields": fields}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        if resp.status_code != 200 or data.get("code", 0) != 0:
            raise RuntimeError(f"写入飞书失败: status={resp.status_code}, body={resp.text}")
        return data

    def list_tables(self) -> list:
        """列出 base 下所有表（用于诊断 app_token 是否正确）"""
        url = f"{self.base}/bitable/v1/apps/{self.app_token}/tables"
        headers = self._get_authorization_header()
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        if resp.status_code != 200 or data.get("code", 0) != 0:
            raise RuntimeError(f"获取表列表失败: status={resp.status_code}, body={resp.text}")
        return data.get("data", {}).get("items", [])

    def ensure_table_exists(self):
        """校验 table_id 是否存在；不存在则抛错并打印可用表信息"""
        tables = self.list_tables()
        table_ids = [t.get('table_id') or t.get('id') for t in tables]
        if self.table_id not in table_ids:
            names = [f"{t.get('name')}({t.get('table_id') or t.get('id')})" for t in tables]
            raise RuntimeError(
                "表ID不存在或不在该多维表格下。请确认 FEISHU_APP_TOKEN 与 FEISHU_TABLE_ID 是否对应同一个多维表格。" \
                + (" 可用表: " + ", ".join(names) if names else " 未获取到任何表，请检查 App Token 是否正确、应用是否有访问权限")
            )


def main():
    """主函数"""
    # 从配置读取文章链接
    article_url = getattr(config, 'ARTICLE_URL', "https://mp.weixin.qq.com/s/w0h03IsxfSrour3NpE_FqA")
    
    print("微信公众号文章抓取器")
    print("="*50)
    
    # 创建抓取器实例
    scraper = WeChatArticleScraper()
    
    # 处理文章
    article_info = scraper.process_article(article_url)
    
    # 输出结果
    if article_info:
        scraper.print_results(article_info)
        
        # 写入飞书
        if getattr(config, 'FEISHU_ENABLED', False):
            try:
                # 解析公众号名与发布日期
                # 重新获取soup以抽取账号/日期（也可在get_article_content中保留soup，这里为简洁重复请求一次）
                html = scraper.session.get(article_url, headers=scraper.headers, timeout=30)
                html.raise_for_status()
                soup = BeautifulSoup(html.text, 'html.parser')
                account_name = scraper.extract_account_name(soup)
                publish_date = scraper.extract_publish_date(soup)

                fields_map = getattr(config, 'FEISHU_FIELDS', {})
                client = FeishuBitableClient(
                    app_id=getattr(config, 'FEISHU_APP_ID', ''),
                    app_secret=getattr(config, 'FEISHU_APP_SECRET', ''),
                    app_token=getattr(config, 'FEISHU_APP_TOKEN', ''),
                    table_id=getattr(config, 'FEISHU_TABLE_ID', ''),
                    auth_mode=getattr(config, 'FEISHU_AUTH_MODE', 'tenant'),
                    bearer_token=getattr(config, 'FEISHU_BEARER_TOKEN', None),
                )
                # 先校验 token 与表是否存在
                client.ensure_table_exists()
                # 组装正文 + OCR摘要
                ocr_combined = []
                for i, item in enumerate(article_info.get('ocr_results', [])):
                    ocr_combined.append(f"[图片{i+1}] {item.get('image_url','')}\n{item.get('ocr_text','')}")
                ocr_text = "\n\n".join(ocr_combined) if ocr_combined else ""
                full_content = article_info['content'] + ("\n\n📸 图片 OCR 识别内容：\n" + ocr_text if ocr_text else "")

                fields = {
                    fields_map.get('account_name', '公众号名称'): account_name or '',
                    fields_map.get('title', '标题'): article_info['title'],
                    fields_map.get('content', '正文'): full_content,
                    fields_map.get('read_count', '阅读量'): '',
                    fields_map.get('publish_date', '发布日期'): publish_date or '',
                }
                client.add_record(fields)
                print("✅ 已写入飞书多维表格")
            except Exception as e:
                print(f"⚠️ 写入飞书失败: {e}")
    else:
        print("抓取失败，请检查网络连接和文章链接")


if __name__ == "__main__":
    main()
