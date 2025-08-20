#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装测试脚本
用于验证微信公众号文章抓取器的所有依赖是否正确安装
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """
    测试模块导入
    
    Args:
        module_name (str): 模块名
        package_name (str): 包名（可选）
    
    Returns:
        bool: 导入是否成功
    """
    try:
        if package_name:
            module = importlib.import_module(module_name, package_name)
        else:
            module = importlib.import_module(module_name)
        print(f"✅ {module_name} 导入成功")
        return True
    except ImportError as e:
        print(f"❌ {module_name} 导入失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} 导入异常: {e}")
        return False

def test_tesseract():
    """测试Tesseract OCR功能"""
    try:
        import pytesseract
        
        # 检查Tesseract是否可用
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract 版本: {version}")
        except Exception as e:
            print(f"❌ Tesseract 不可用: {e}")
            return False
        
        # 检查可用语言
        try:
            langs = pytesseract.get_languages()
            if 'chi_sim' in langs:
                print("✅ 中文简体语言包已安装")
            else:
                print("⚠️  中文简体语言包未安装")
                print("   可用语言:", langs)
        except Exception as e:
            print(f"⚠️  无法获取语言列表: {e}")
        
        return True
        
    except ImportError:
        print("❌ pytesseract 模块未安装")
        return False

def test_pil():
    """测试PIL图像处理功能"""
    try:
        from PIL import Image
        print(f"✅ PIL 版本: {Image.__version__}")
        return True
    except ImportError:
        print("❌ PIL 模块未安装")
        return False

def test_requests():
    """测试requests网络请求功能"""
    try:
        import requests
        print(f"✅ requests 版本: {requests.__version__}")
        return True
    except ImportError:
        print("❌ requests 模块未安装")
        return False

def test_beautifulsoup():
    """测试BeautifulSoup HTML解析功能"""
    try:
        import bs4
        print(f"✅ beautifulsoup4 版本: {bs4.__version__}")
        return True
    except ImportError:
        print("❌ beautifulsoup4 模块未安装")
        return False

def test_lxml():
    """测试lxml XML/HTML解析功能"""
    try:
        import lxml
        print(f"✅ lxml 版本: {lxml.__version__}")
        return True
    except ImportError:
        print("❌ lxml 模块未安装")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试微信公众号文章抓取器依赖...")
    print("=" * 60)
    
    # 测试Python版本
    print(f"🐍 Python 版本: {sys.version}")
    if sys.version_info >= (3, 7):
        print("✅ Python版本符合要求 (>= 3.7)")
    else:
        print("❌ Python版本过低，需要3.7+")
        return False
    
    print()
    
    # 测试各个依赖模块
    tests = [
        ("requests", test_requests),
        ("beautifulsoup4", test_beautifulsoup),
        ("lxml", test_lxml),
        ("PIL", test_pil),
        ("Tesseract", test_tesseract),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"🔍 测试 {name}...")
        if test_func():
            passed += 1
        print()
    
    # 输出测试结果
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有依赖测试通过！可以开始使用抓取器了。")
        print("\n使用方法:")
        print("1. 修改 config.py 中的文章链接")
        print("2. 运行: python wechat_article_scraper.py")
        return True
    else:
        print("❌ 部分依赖测试失败，请检查安装。")
        print("\n安装建议:")
        print("1. 运行自动安装脚本: ./install.sh (macOS/Linux) 或 install.bat (Windows)")
        print("2. 手动安装: pip install -r requirements.txt")
        print("3. 安装Tesseract OCR工具")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 