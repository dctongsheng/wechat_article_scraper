#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章抓取器配置文件
用户可以在这里修改各种设置参数
"""

# 文章链接配置
ARTICLE_URL = "https://mp.weixin.qq.com/s/brQ_pc6w_FNomWJdi3iXDA"

# 输出目录配置
OUTPUT_DIR = "downloaded_images"

# 网络请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
REQUEST_DELAY = 1     # 请求间隔延迟（秒）
MAX_RETRIES = 3       # 最大重试次数

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# OCR配置
OCR_LANGUAGE = 'chi_sim'  # OCR识别语言：chi_sim(中文简体), eng(英文)
OCR_CONFIG = '--psm 6'    # OCR页面分割模式

# 内容提取配置
MAX_CONTENT_PREVIEW = 500  # 控制台输出的内容预览最大长度
CONTENT_SELECTORS = [
    'div.rich_media_content',
    'div[id*="js_content"]',
    'div.article-content',
    'div.content'
]

TITLE_SELECTORS = [
    'h1.rich_media_title',
    'h1[id*="activity-name"]',
    'h1',
    'title'
]

# 图片过滤配置
IMAGE_FILTERS = ['avatar', 'icon', 'logo', 'qrcode']  # 过滤的图片关键词

# 日志配置
LOG_LEVEL = 'INFO'  # 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 文件命名配置
IMAGE_FILENAME_PREFIX = "image_"  # 图片文件名前缀
IMAGE_FILENAME_SUFFIX = ""        # 图片文件名后缀

# 错误处理配置
CONTINUE_ON_ERROR = True  # 遇到错误时是否继续处理
SKIP_FAILED_IMAGES = True # 是否跳过下载失败的图片 

# ================== 飞书多维表格（Bitable）配置 ==================
# 是否启用飞书写入
FEISHU_ENABLED = True

# 内部应用凭据（若使用 tenant_access_token 需要）
FEISHU_APP_ID = "cli_a82e9b4a24ff1013"
FEISHU_APP_SECRET = "cYOe9sYbtkeRPvdAWG4xYgLsZg4GtSAg"

# Bitable 应用与表配置（按你的 curl）
FEISHU_APP_TOKEN = "Bgw9bRUMcan9wgsI6d2c47Pyn4d"  # App Token（base）
FEISHU_TABLE_ID = "tblgfkEasd6grJrZ"               # 表ID

# 鉴权模式与直传 Bearer Token（与你 curl 保持一致）
# 模式可选：'user'（优先使用下方 FEISHU_BEARER_TOKEN）、'tenant'（使用租户 token）
FEISHU_AUTH_MODE = 'user'
FEISHU_BEARER_TOKEN = "u-cMV5u8vBldmWgDJ_RyP.fOkhnvP0ghwppMG044Cw2dpn"

# 写入字段名（与表中的列名称一一对应）
FEISHU_FIELDS = {
    'account_name': '公众号名称',
    'title': '标题',
    'content': '正文',
    'read_count': '阅读量',
    'publish_date': '发布日期',
} 