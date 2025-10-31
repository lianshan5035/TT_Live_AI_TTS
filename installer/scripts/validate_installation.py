#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI-TTS 安装验证工具
验证安装是否成功完成
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_installation_structure(install_dir):
    """检查安装目录结构"""
    print("📁 检查安装目录结构...")
    
    required_dirs = [
        "logs",
        "input",
        "outputs", 
        "templates",
        "static",
        "venv"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        dir_path = Path(install_dir) / directory
        if dir_path.exists():
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} - 缺失")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def check_core_files(install_dir):
    """检查核心文件"""
    print("📄 检查核心文件...")
    
    required_files = [
        "02_TTS服务_语音合成系统/run_tts_TTS语音合成服务.py",
        "03_Web界面_控制台系统/web_dashboard_simple_Web控制台界面.py",
        "12_启动脚本_服务启动和管理/start_services_一键启动所有服务.sh",
        "config.json",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(install_dir) / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 缺失")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_virtual_environment(install_dir):
    """检查虚拟环境"""
    print("🐍 检查虚拟环境...")
    
    venv_path = Path(install_dir) / "venv"
    
    if not venv_path.exists():
        print("  ❌ 虚拟环境目录不存在")
        return False
    
    # 检查 Python 可执行文件
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    if python_path.exists():
        print("  ✅ Python 可执行文件")
    else:
        print("  ❌ Python 可执行文件缺失")
        return False
    
    if pip_path.exists():
        print("  ✅ pip 可执行文件")
    else:
        print("  ❌ pip 可执行文件缺失")
        return False
    
    return True

def check_python_packages(install_dir):
    """检查 Python 包"""
    print("📦 检查 Python 包...")
    
    venv_path = Path(install_dir) / "venv"
    
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    required_packages = [
        "flask",
        "edge_tts",
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
            result = subprocess.run([
                str(python_path), "-c", f"import {package.replace('-', '_')}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package} - 未安装")
                missing_packages.append(package)
        except Exception as e:
            print(f"  ❌ {package} - 检查失败: {e}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_configuration_files(install_dir):
    """检查配置文件"""
    print("⚙️  检查配置文件...")
    
    # 检查 config.json
    config_path = Path(install_dir) / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("  ✅ config.json 格式正确")
        except Exception as e:
            print(f"  ❌ config.json 格式错误: {e}")
            return False
    else:
        print("  ❌ config.json 不存在")
        return False
    
    # 检查 .env
    env_path = Path(install_dir) / ".env"
    if env_path.exists():
        print("  ✅ .env 文件存在")
    else:
        print("  ❌ .env 文件不存在")
        return False
    
    return True

def check_startup_scripts(install_dir):
    """检查启动脚本"""
    print("🚀 检查启动脚本...")
    
    # macOS/Linux 启动脚本
    startup_sh = Path(install_dir) / "start_tts_system.sh"
    if startup_sh.exists():
        print("  ✅ start_tts_system.sh")
    else:
        print("  ❌ start_tts_system.sh - 缺失")
        return False
    
    # Windows 启动脚本
    startup_bat = Path(install_dir) / "start_tts_system.bat"
    if startup_bat.exists():
        print("  ✅ start_tts_system.bat")
    else:
        print("  ❌ start_tts_system.bat - 缺失")
        return False
    
    return True

def test_service_startup(install_dir):
    """测试服务启动"""
    print("🧪 测试服务启动...")
    
    venv_path = Path(install_dir) / "venv"
    
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    # 测试 TTS 服务导入
    try:
        result = subprocess.run([
            str(python_path), "-c", 
            "import sys; sys.path.append('.'); from '02_TTS服务_语音合成系统.run_tts_TTS语音合成服务' import *"
        ], capture_output=True, text=True, cwd=install_dir)
        
        if result.returncode == 0:
            print("  ✅ TTS 服务模块导入成功")
        else:
            print(f"  ❌ TTS 服务模块导入失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ TTS 服务测试失败: {e}")
        return False
    
    # 测试 Web 控制台导入
    try:
        result = subprocess.run([
            str(python_path), "-c",
            "import sys; sys.path.append('.'); from '03_Web界面_控制台系统.web_dashboard_simple_Web控制台界面' import *"
        ], capture_output=True, text=True, cwd=install_dir)
        
        if result.returncode == 0:
            print("  ✅ Web 控制台模块导入成功")
        else:
            print(f"  ❌ Web 控制台模块导入失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Web 控制台测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_installation.py <安装目录>")
        sys.exit(1)
    
    install_dir = sys.argv[1]
    
    print("=" * 60)
    print("TT-Live-AI-TTS 安装验证工具")
    print("=" * 60)
    print(f"安装目录: {install_dir}")
    print()
    
    # 检查安装目录
    install_path = Path(install_dir)
    if not install_path.exists():
        print(f"❌ 安装目录不存在: {install_dir}")
        sys.exit(1)
    
    # 执行验证步骤
    checks = [
        ("安装目录结构", lambda: check_installation_structure(install_dir)),
        ("核心文件", lambda: check_core_files(install_dir)),
        ("虚拟环境", lambda: check_virtual_environment(install_dir)),
        ("Python 包", lambda: check_python_packages(install_dir)),
        ("配置文件", lambda: check_configuration_files(install_dir)),
        ("启动脚本", lambda: check_startup_scripts(install_dir)),
        ("服务启动测试", lambda: test_service_startup(install_dir))
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            print(f"\n[{check_name}]")
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} 检查失败: {e}")
            results.append((check_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结:")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 安装验证通过！TT-Live-AI-TTS 已正确安装")
        print("\n🚀 启动系统:")
        if os.name == 'nt':
            print(f"  cd {install_dir}")
            print("  start_tts_system.bat")
        else:
            print(f"  cd {install_dir}")
            print("  ./start_tts_system.sh")
        
        print("\n🌐 访问地址:")
        print("  Web 控制台: http://127.0.0.1:8000")
        print("  TTS 服务: http://127.0.0.1:5001")
    else:
        print("❌ 安装验证失败，请检查上述问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
