@echo off
chcp 65001 >nul
echo 🚀 开始安装微信公众号文章抓取器...
echo ==================================

REM 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python环境检查通过

REM 检查pip
echo 🔍 检查pip包管理器...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到pip，请先安装pip
    pause
    exit /b 1
)

echo ✅ pip检查通过

REM 检查Tesseract
echo 🔍 检查Tesseract OCR...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Tesseract，请先安装Tesseract for Windows
    echo 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo 安装步骤:
    echo 1. 下载并安装Tesseract for Windows
    echo 2. 下载中文语言包 chi_sim.traineddata
    echo 3. 将语言包放入Tesseract安装目录的tessdata文件夹
    echo 4. 将Tesseract添加到系统PATH环境变量
    echo.
    pause
    exit /b 1
)

tesseract --version
echo ✅ Tesseract检查通过

REM 检查中文语言包
echo 🔍 检查中文语言包...
tesseract --list-langs | findstr "chi_sim" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  中文简体语言包未安装，OCR功能可能无法正常工作
    echo 请确保已安装chi_sim.traineddata语言包
) else (
    echo ✅ 中文简体语言包已安装
)

REM 安装Python依赖包
echo 📦 安装Python依赖包...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ 依赖包安装失败，尝试手动安装...
    python -m pip install requests beautifulsoup4 lxml Pillow pytesseract
)

REM 测试安装
echo 🧪 测试安装...
python -c "import requests, bs4, PIL, pytesseract; print('✅ 所有依赖包导入成功')"

if %errorlevel% neq 0 (
    echo ❌ 安装测试失败，请检查错误信息
    pause
    exit /b 1
)

echo ✅ 安装测试通过

echo.
echo 🎉 安装完成！
echo ==================================
echo 使用方法：
echo 1. 修改 wechat_article_scraper.py 中的文章链接
echo 2. 运行: python wechat_article_scraper.py
echo.
echo 注意事项：
echo - 确保网络连接正常
echo - 某些文章可能需要登录才能访问
echo - OCR识别效果取决于图片质量
echo.
echo 如有问题，请查看 README.md 文件
pause 