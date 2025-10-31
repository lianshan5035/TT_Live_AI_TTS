#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI-TTS 环境设置工具
自动配置虚拟环境和系统设置
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def create_directories(install_dir):
    """创建必要的目录结构"""
    print("📁 创建目录结构...")
    
    directories = [
        "logs",
        "input", 
        "outputs",
        "templates",
        "static/css",
        "static/js",
        "static/images",
        "venv"
    ]
    
    for directory in directories:
        dir_path = Path(install_dir) / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ 目录结构创建完成")

def setup_virtual_environment(install_dir):
    """设置虚拟环境"""
    print("🐍 设置 Python 虚拟环境...")
    
    venv_path = Path(install_dir) / "venv"
    
    if venv_path.exists():
        print("  ⚠️  虚拟环境已存在，跳过创建")
        return True
    
    try:
        # 创建虚拟环境
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True)
        
        print("  ✅ 虚拟环境创建成功")
        
        # 升级 pip
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        subprocess.run([
            str(python_path), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        print("  ✅ pip 升级完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 虚拟环境设置失败: {e}")
        return False

def install_packages(install_dir, requirements_file):
    """安装 Python 包"""
    print("📦 安装 Python 包...")
    
    venv_path = Path(install_dir) / "venv"
    
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    try:
        subprocess.run([
            str(python_path), "-m", "pip", "install", "-r", requirements_file
        ], check=True)
        
        print("  ✅ 包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 包安装失败: {e}")
        return False

def create_config_files(install_dir, config_template):
    """创建配置文件"""
    print("⚙️  创建配置文件...")
    
    # 复制配置文件
    config_path = Path(install_dir) / "config.json"
    if config_template.exists():
        shutil.copy2(config_template, config_path)
        print("  ✅ config.json 创建完成")
    
    # 创建 .env 文件
    env_path = Path(install_dir) / ".env"
    env_template = config_template.parent / ".env_template"
    
    if env_template.exists():
        shutil.copy2(env_template, env_path)
        print("  ✅ .env 文件创建完成")
    
    return True

def set_file_permissions(install_dir):
    """设置文件权限（Unix 系统）"""
    if os.name == 'nt':  # Windows
        print("  ⚠️  Windows 系统，跳过权限设置")
        return True
    
    print("🔐 设置文件权限...")
    
    try:
        # 设置脚本执行权限
        for script in Path(install_dir).rglob("*.sh"):
            os.chmod(script, 0o755)
            print(f"  ✅ {script.name}")
        
        # 设置 Python 文件执行权限
        for py_file in Path(install_dir).rglob("*.py"):
            os.chmod(py_file, 0o755)
        
        print("  ✅ 权限设置完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 权限设置失败: {e}")
        return False

def create_startup_scripts(install_dir):
    """创建启动脚本"""
    print("🚀 创建启动脚本...")
    
    # macOS/Linux 启动脚本
    startup_script = Path(install_dir) / "start_tts_system.sh"
    with open(startup_script, 'w', encoding='utf-8') as f:
        f.write('''#!/bin/bash
# TT-Live-AI-TTS 系统启动脚本

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$INSTALL_DIR"

echo "🚀 启动 TT-Live-AI-TTS 系统..."
echo "安装目录: $INSTALL_DIR"

# 激活虚拟环境
source venv/bin/activate

# 启动服务
./12_启动脚本_服务启动和管理/start_services_一键启动所有服务.sh
''')
    
    os.chmod(startup_script, 0o755)
    print("  ✅ start_tts_system.sh 创建完成")
    
    # Windows 启动脚本
    startup_bat = Path(install_dir) / "start_tts_system.bat"
    with open(startup_bat, 'w', encoding='utf-8') as f:
        f.write('''@echo off
REM TT-Live-AI-TTS 系统启动脚本

setlocal enabledelayedexpansion
chcp 65001 >nul

set INSTALL_DIR=%~dp0
cd /d "%INSTALL_DIR%"

echo 🚀 启动 TT-Live-AI-TTS 系统...
echo 安装目录: %INSTALL_DIR%

REM 激活虚拟环境
call venv\\Scripts\\activate.bat

REM 启动服务
call "12_启动脚本_服务启动和管理\\start_services_一键启动所有服务.bat"
''')
    
    print("  ✅ start_tts_system.bat 创建完成")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python setup_environment.py <安装目录> [requirements文件]")
        sys.exit(1)
    
    install_dir = sys.argv[1]
    requirements_file = sys.argv[2] if len(sys.argv) > 2 else "requirements.txt"
    
    print("=" * 60)
    print("TT-Live-AI-TTS 环境设置工具")
    print("=" * 60)
    print(f"安装目录: {install_dir}")
    print(f"依赖文件: {requirements_file}")
    print()
    
    # 检查安装目录
    install_path = Path(install_dir)
    if not install_path.exists():
        print(f"❌ 安装目录不存在: {install_dir}")
        sys.exit(1)
    
    # 检查依赖文件
    req_path = Path(requirements_file)
    if not req_path.exists():
        print(f"❌ 依赖文件不存在: {requirements_file}")
        sys.exit(1)
    
    # 执行设置步骤
    steps = [
        ("创建目录", lambda: create_directories(install_dir)),
        ("设置虚拟环境", lambda: setup_virtual_environment(install_dir)),
        ("安装包", lambda: install_packages(install_dir, requirements_file)),
        ("创建配置文件", lambda: create_config_files(install_dir, Path("config/config.json"))),
        ("设置权限", lambda: set_file_permissions(install_dir)),
        ("创建启动脚本", lambda: create_startup_scripts(install_dir))
    ]
    
    success = True
    for step_name, step_func in steps:
        try:
            print(f"\n[{step_name}]")
            if not step_func():
                success = False
        except Exception as e:
            print(f"❌ {step_name} 失败: {e}")
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 环境设置完成！")
        print(f"安装目录: {install_dir}")
        print("启动命令:")
        if os.name == 'nt':
            print(f"  cd {install_dir}")
            print("  start_tts_system.bat")
        else:
            print(f"  cd {install_dir}")
            print("  ./start_tts_system.sh")
    else:
        print("❌ 环境设置失败，请检查错误信息")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
