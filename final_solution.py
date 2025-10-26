#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 最终解决方案
创建正确的配置文件并启动服务
"""

import os
import subprocess
import time
import requests
import signal
import sys

# 配置
TUNNEL_TOKEN = "eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9"
DOMAIN = "ai.maraecowell.com"
LOCAL_PORT = 8000

def create_cloudflare_config():
    """创建Cloudflare配置文件"""
    config_content = f"""# Cloudflare Tunnel 配置文件
tunnel: a3-tt-live-ai

ingress:
  # 规则 1: 将 {DOMAIN} 指向本地 Flask 服务
  - hostname: {DOMAIN}
    service: http://127.0.0.1:{LOCAL_PORT}
  
  # 规则 2: catch-all 规则 - 处理其他所有请求，返回 404
  # 重要：此规则必须放在最后
  - service: http_status:404
"""
    
    with open('cloudflare_config.yml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Cloudflare配置文件已创建")

def start_services():
    """启动服务"""
    print("🚀 启动服务...")
    
    # 创建配置文件
    create_cloudflare_config()
    
    # 启动Flask服务
    print("📱 启动Flask服务...")
    flask_process = subprocess.Popen([
        'python', 'web_dashboard_simple.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待Flask启动
    time.sleep(5)
    
    # 测试Flask服务
    try:
        response = requests.get(f"http://127.0.0.1:{LOCAL_PORT}", timeout=5)
        if response.status_code == 200:
            print("✅ Flask服务启动成功")
        else:
            print(f"❌ Flask服务启动失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flask服务启动失败: {str(e)}")
        return False
    
    # 启动Cloudflare隧道
    print("🌐 启动Cloudflare隧道...")
    tunnel_process = subprocess.Popen([
        'cloudflared', 'tunnel', '--config', 'cloudflare_config.yml', 'run', 'a3-tt-live-ai'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待隧道启动
    time.sleep(5)
    
    # 检查隧道进程
    if tunnel_process.poll() is None:
        print("✅ Cloudflare隧道启动成功")
    else:
        stdout, stderr = tunnel_process.communicate()
        print(f"❌ 隧道启动失败:")
        if stdout:
            print(f"输出: {stdout.decode()}")
        if stderr:
            print(f"错误: {stderr.decode()}")
        return False
    
    # 测试连接
    print("🧪 测试连接...")
    time.sleep(5)
    
    try:
        response = requests.get(f"https://{DOMAIN}", timeout=10)
        if response.status_code == 200:
            print("✅ 外部访问成功")
            print(f"🌐 访问地址: https://{DOMAIN}")
            return True
        else:
            print(f"⚠️ 外部访问返回: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 外部访问失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 Cloudflare 最终解决方案")
    print("=" * 50)
    
    try:
        if start_services():
            print("\n✅ 服务启动完成!")
            print(f"📱 本地访问: http://127.0.0.1:{LOCAL_PORT}")
            print(f"🌐 外部访问: https://{DOMAIN}")
            print("🛑 按 Ctrl+C 停止服务")
            
            # 保持运行
            while True:
                time.sleep(1)
        else:
            print("❌ 服务启动失败")
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
