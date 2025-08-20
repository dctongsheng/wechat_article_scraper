# 🚀 快速开始指南

## 5分钟快速上手

### 1. 一键安装（推荐）

#### macOS/Linux 用户
```bash
# 进入项目目录
cd content/wparticle

# 运行自动安装脚本
./install.sh
```

#### Windows 用户
```cmd
# 进入项目目录
cd content\wparticle

# 运行自动安装脚本
install.bat
```

### 2. 手动安装

如果自动安装失败，请按以下步骤手动安装：

#### 步骤1: 安装系统依赖
- **macOS**: `brew install tesseract tesseract-lang`
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr tesseract-ocr-chi-sim`
- **Windows**: 下载安装 [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)

#### 步骤2: 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 步骤3: 验证安装
```bash
python test_installation.py
```

### 3. 开始使用

#### 修改文章链接
编辑 `config.py` 文件，修改 `ARTICLE_URL` 为你要抓取的文章链接：

```python
ARTICLE_URL = "https://mp.weixin.qq.com/s/你的文章ID"
```

#### 运行抓取器
```bash
python wechat_article_scraper.py
```

### 4. 查看结果

脚本运行完成后，你将看到：
- 📰 文章标题
- 🔗 文章链接  
- 📝 正文内容预览
- 🖼️ 图片信息列表
- 🔍 OCR识别结果

所有图片将下载到 `downloaded_images/` 目录中。

## 常见问题

### Q: 安装失败怎么办？
A: 运行 `python test_installation.py` 查看具体错误，然后参考 README.md 中的故障排除部分。

### Q: OCR识别不准确？
A: 确保安装了中文语言包，图片质量越高识别效果越好。

### Q: 抓取失败？
A: 检查网络连接，某些文章可能需要登录才能访问。

## 下一步

- 📖 阅读 [README.md](README.md) 了解详细功能
- ⚙️ 查看 [config.py](config.py) 自定义配置
- 🐛 遇到问题？运行测试脚本诊断

---

**提示**: 首次使用建议先运行测试脚本确保环境正确配置！ 