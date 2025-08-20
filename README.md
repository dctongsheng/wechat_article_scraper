# 微信公众号文章抓取器

这是一个功能完整的微信公众号文章抓取工具，可以自动抓取文章内容、下载图片并进行OCR文字识别。

## 功能特性

✅ **文章内容抓取**
- 自动提取文章标题
- 提取正文纯文本内容
- 智能过滤无关内容

✅ **图片处理**
- 自动发现文章中的所有图片
- 批量下载图片到本地
- 支持多种图片格式

✅ **OCR文字识别**
- 使用Tesseract进行中文OCR识别
- 自动识别图片中的中文文字
- 输出结构化的识别结果

✅ **结果展示**
- 控制台友好输出
- 详细的日志记录
- 结构化的数据格式

## 安装要求

### 1. Python环境
- Python 3.7+
- pip包管理器

### 2. 系统依赖

#### macOS (推荐使用Homebrew)
```bash
# 安装Tesseract和中文语言包
brew install tesseract
brew install tesseract-lang

# 验证安装
tesseract --version
tesseract --list-langs
```

#### Ubuntu/Debian
```bash
# 安装Tesseract和中文语言包
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-chi-sim

# 验证安装
tesseract --version
tesseract --list-langs
```

#### Windows
1. 下载并安装 [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
2. 下载中文语言包 `chi_sim.traineddata`
3. 将语言包放入Tesseract安装目录的`tessdata`文件夹
4. 将Tesseract添加到系统PATH环境变量

### 3. Python依赖包
```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者手动安装
pip install requests beautifulsoup4 lxml Pillow pytesseract
```

## 使用方法

### 1. 基本使用
```python
from wechat_article_scraper import WeChatArticleScraper

# 创建抓取器实例
scraper = WeChatArticleScraper()

# 抓取文章
article_url = "https://mp.weixin.qq.com/s/w0h03IsxfSrour3NpE_FqA"
article_info = scraper.process_article(article_url)

# 输出结果
scraper.print_results(article_info)
```

### 2. 命令行运行
```bash
# 直接运行脚本
python wechat_article_scraper.py

# 或者指定Python版本
python3 wechat_article_scraper.py
```

### 3. 自定义配置
```python
# 自定义图片下载目录
scraper = WeChatArticleScraper(output_dir="my_images")

# 自定义请求头
scraper.headers.update({
    'User-Agent': '你的自定义User-Agent'
})
```

## 输出结果

脚本运行后会输出以下信息：

1. **文章标题** - 文章的完整标题
2. **文章链接** - 原始文章URL
3. **正文内容** - 提取的纯文本内容（前500字符预览）
4. **图片信息** - 所有图片的URL、描述和标题
5. **OCR结果** - 每张图片的文字识别结果

## 文件结构

```
wparticle/
├── wechat_article_scraper.py  # 主脚本文件
├── requirements.txt            # 依赖包列表
├── README.md                  # 使用说明
└── downloaded_images/         # 图片下载目录（自动创建）
```

## 注意事项

⚠️ **重要提醒**
- 请遵守网站的robots.txt和使用条款
- 不要过于频繁地请求，建议添加适当的延迟
- 某些文章可能需要登录才能访问
- OCR识别效果取决于图片质量和文字清晰度

🔧 **故障排除**

1. **OCR识别失败**
   - 检查Tesseract是否正确安装
   - 确认中文语言包是否安装
   - 验证图片文件是否损坏

2. **网络请求失败**
   - 检查网络连接
   - 确认文章链接是否有效
   - 可能需要更新User-Agent

3. **内容提取失败**
   - 微信公众号可能更新了页面结构
   - 尝试更新CSS选择器
   - 检查页面是否加载完整

## 技术架构

- **网络请求**: requests + Session
- **HTML解析**: BeautifulSoup4 + lxml
- **图像处理**: Pillow (PIL)
- **OCR识别**: pytesseract + Tesseract
- **日志记录**: Python logging模块

## 更新日志

- v1.0.0: 初始版本，支持基本抓取和OCR功能
- 支持多种图片格式
- 智能内容提取
- 完整的错误处理

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

如有问题，请查看日志输出或提交Issue。 