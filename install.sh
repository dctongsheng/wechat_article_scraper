#!/bin/bash

# 微信公众号文章抓取器 - 自动安装脚本
# 适用于 macOS 和 Linux 系统

echo "🚀 开始安装微信公众号文章抓取器..."
echo "=================================="

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "✅ 检测到 macOS 系统"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✅ 检测到 Linux 系统"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python 版本: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "✅ Python 版本: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ 未找到 Python，请先安装 Python 3.7+"
    exit 1
fi

# 检查 pip
echo "🔍 检查 pip 包管理器..."
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ 未找到 pip，请先安装 pip"
    exit 1
fi

# 安装 Tesseract
echo "🔍 检查 Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    echo "📦 安装 Tesseract OCR..."
    
    if [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            echo "使用 Homebrew 安装..."
            brew install tesseract
            brew install tesseract-lang
        else
            echo "❌ 未找到 Homebrew，请先安装 Homebrew"
            echo "安装命令: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        echo "使用 apt 安装..."
        sudo apt update
        sudo apt install -y tesseract-ocr
        sudo apt install -y tesseract-ocr-chi-sim
    fi
else
    echo "✅ Tesseract 已安装"
fi

# 验证 Tesseract 安装
echo "🔍 验证 Tesseract 安装..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n 1)
    echo "✅ $TESSERACT_VERSION"
    
    # 检查中文语言包
    if tesseract --list-langs | grep -q "chi_sim"; then
        echo "✅ 中文简体语言包已安装"
    else
        echo "⚠️  中文简体语言包未安装，OCR功能可能无法正常工作"
        if [[ "$OS" == "macos" ]]; then
            echo "请运行: brew install tesseract-lang"
        elif [[ "$OS" == "linux" ]]; then
            echo "请运行: sudo apt install tesseract-ocr-chi-sim"
        fi
    fi
else
    echo "❌ Tesseract 安装失败"
    exit 1
fi

# 安装 Python 依赖包
echo "📦 安装 Python 依赖包..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
fi

echo "使用 $PIP_CMD 安装依赖..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python 依赖包安装成功"
else
    echo "❌ Python 依赖包安装失败，尝试手动安装..."
    $PIP_CMD install requests beautifulsoup4 lxml Pillow pytesseract
fi

# 测试安装
echo "🧪 测试安装..."
$PYTHON_CMD -c "
import requests
import bs4
from PIL import Image
import pytesseract
print('✅ 所有依赖包导入成功')
"

if [ $? -eq 0 ]; then
    echo "✅ 安装测试通过"
else
    echo "❌ 安装测试失败，请检查错误信息"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo "=================================="
echo "使用方法："
echo "1. 修改 wechat_article_scraper.py 中的文章链接"
echo "2. 运行: $PYTHON_CMD wechat_article_scraper.py"
echo ""
echo "注意事项："
echo "- 确保网络连接正常"
echo "- 某些文章可能需要登录才能访问"
echo "- OCR识别效果取决于图片质量"
echo ""
echo "如有问题，请查看 README.md 文件" 