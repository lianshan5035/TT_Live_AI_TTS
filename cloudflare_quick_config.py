#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 快速配置脚本
使用现有Token快速配置
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

# 使用您现有的Token
EXISTING_TOKEN = "eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9"

def create_env_config():
    """创建环境变量配置"""
    env_content = f"""# Cloudflare Tunnel 配置
CLOUDFLARE_TUNNEL_TOKEN={EXISTING_TOKEN}
CLOUDFLARE_TUNNEL_NAME=a3-tt-live-ai
TUNNEL_FULL_DOMAIN=ai.maraecowell.com

# 部署模式
DEPLOYMENT_MODE=cloudflare_tunnel

# Flask配置
FLASK_PORT=8000
SECRET_KEY=tt_live_ai_secret_key_2024
FLASK_ENV=production
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 环境变量配置已创建")

def create_cloudflare_config():
    """创建Cloudflare配置文件"""
    config_content = """# Cloudflare Tunnel 配置文件
tunnel: a3-tt-live-ai

ingress:
  # 规则 1: 将 ai.maraecowell.com 指向本地 Flask 服务
  - hostname: ai.maraecowell.com
    service: http://127.0.0.1:8000
  
  # 规则 2: catch-all 规则 - 处理其他所有请求，返回 404
  # 重要：此规则必须放在最后
  - service: http_status:404
"""
    
    with open('cloudflare_config.yml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Cloudflare配置文件已创建")

def test_tunnel():
    """测试隧道连接"""
    print("🧪 测试Cloudflare隧道...")
    
    try:
        # 使用Token启动隧道
        cmd = ['cloudflared', 'tunnel', 'run', '--token', EXISTING_TOKEN]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ 等待隧道启动...")
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ Cloudflare隧道已启动")
            print("🌐 访问地址: https://ai.maraecowell.com")
            print("📝 按 Ctrl+C 停止隧道")
            
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 停止隧道...")
                process.terminate()
                process.wait()
                print("✅ 隧道已停止")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 隧道启动失败:")
            print(f"输出: {stdout}")
            print(f"错误: {stderr}")
            
    except Exception as e:
        print(f"❌ 测试隧道失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 Cloudflare 快速配置")
    print("=" * 40)
    
    # 创建配置文件
    create_env_config()
    create_cloudflare_config()
    
    print("\n📋 配置完成!")
    print("🔧 已创建以下文件:")
    print("   - .env (环境变量)")
    print("   - cloudflare_config.yml (Cloudflare配置)")
    
    print("\n🧪 是否要测试隧道连接? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            test_tunnel()
        else:
            print("✅ 配置完成，您可以稍后手动测试")
    except:
        print("\n✅ 配置完成")

if __name__ == "__main__":
    main()
