#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI-TTS 依赖检查工具
检查系统环境和 Python 依赖包
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}")
        print("   需要 Python 3.8 或更高版本")
        return False
    else:
        print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True

def check_system_info():
    """检查系统信息"""
    print("🔍 检查系统信息...")
    system = platform.system()
    version = platform.version()
    print(f"✅ 操作系统: {system} {version}")
    
    # 检查架构
    arch = platform.machine()
    print(f"✅ 系统架构: {arch}")
    
    return True

def check_pip():
    """检查 pip 是否可用"""
    print("🔍 检查 pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip 可用: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip 不可用")
            return False
    except Exception as e:
        print(f"❌ pip 检查失败: {e}")
        return False

def check_required_packages():
    """检查必需的 Python 包"""
    print("🔍 检查必需的 Python 包...")
    
    required_packages = [
        "flask",
        "edge-tts", 
        "pandas",
        "openpyxl",
        "requests",
        "tqdm",
        "numpy",
        "psutil",
        "colorama"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺失的包: {', '.join(missing_packages)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有必需的包都已安装")
        return True

def check_disk_space():
    """检查磁盘空间"""
    print("🔍 检查磁盘空间...")
    
    try:
        if platform.system() == "Windows":
            import shutil
            total, used, free = shutil.disk_usage("C:")
        else:
            statvfs = os.statvfs("/")
            free = statvfs.f_frsize * statvfs.f_bavail
        
        free_gb = free / (1024**3)
        
        if free_gb < 2:
            print(f"⚠️  可用磁盘空间不足: {free_gb:.1f}GB")
            print("   建议至少 2GB 可用空间")
            return False
        else:
            print(f"✅ 可用磁盘空间: {free_gb:.1f}GB")
            return True
    except Exception as e:
        print(f"⚠️  无法检查磁盘空间: {e}")
        return True

def check_network():
    """检查网络连接"""
    print("🔍 检查网络连接...")
    
    try:
        import requests
        response = requests.get("https://pypi.org", timeout=5)
        if response.status_code == 200:
            print("✅ 网络连接正常")
            return True
        else:
            print("⚠️  网络连接异常")
            return False
    except Exception as e:
        print(f"⚠️  网络检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("TT-Live-AI-TTS 依赖检查工具")
    print("=" * 60)
    print()
    
    checks = [
        ("Python 版本", check_python_version),
        ("系统信息", check_system_info),
        ("pip 工具", check_pip),
        ("必需包", check_required_packages),
        ("磁盘空间", check_disk_space),
        ("网络连接", check_network)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查失败: {e}")
            results.append((name, False))
        print()
    
    # 总结
    print("=" * 60)
    print("检查结果总结:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有检查都通过！系统已准备好安装 TT-Live-AI-TTS")
    else:
        print("⚠️  部分检查未通过，请解决上述问题后重新运行")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
