#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 隧道启动器
使用现有Token启动隧道
"""

import os
import subprocess
import time
import requests
import signal
import sys

# 您的Token
TUNNEL_TOKEN = "eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9"

class TunnelManager:
    def __init__(self):
        self.tunnel_process = None
        self.flask_process = None
        
    def start_flask(self):
        """启动Flask服务"""
        print("🚀 启动Flask服务...")
        try:
            self.flask_process = subprocess.Popen([
                'python', 'web_dashboard_simple.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务启动
            time.sleep(3)
            
            # 测试服务
            try:
                response = requests.get("http://127.0.0.1:8000", timeout=5)
                if response.status_code == 200:
                    print("✅ Flask服务启动成功")
                    return True
            except:
                pass
            
            print("❌ Flask服务启动失败")
            return False
            
        except Exception as e:
            print(f"❌ 启动Flask失败: {str(e)}")
            return False
    
    def start_tunnel(self):
        """启动Cloudflare隧道"""
        print("🌐 启动Cloudflare隧道...")
        try:
            self.tunnel_process = subprocess.Popen([
                'cloudflared', 'tunnel', 'run', '--token', TUNNEL_TOKEN
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待隧道启动
            time.sleep(5)
            
            # 检查进程是否还在运行
            if self.tunnel_process.poll() is None:
                print("✅ Cloudflare隧道启动成功")
                return True
            else:
                stdout, stderr = self.tunnel_process.communicate()
                print(f"❌ 隧道启动失败:")
                print(f"输出: {stdout.decode()}")
                print(f"错误: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ 启动隧道失败: {str(e)}")
            return False
    
    def test_connection(self):
        """测试连接"""
        print("🧪 测试连接...")
        
        # 测试本地
        try:
            response = requests.get("http://127.0.0.1:8000", timeout=5)
            if response.status_code == 200:
                print("✅ 本地服务正常")
            else:
                print("❌ 本地服务异常")
                return False
        except Exception as e:
            print(f"❌ 本地服务无法访问: {str(e)}")
            return False
        
        # 测试外部
        try:
            response = requests.get("https://ai.maraecowell.com", timeout=10)
            if response.status_code == 200:
                print("✅ 外部访问成功")
                print("🌐 访问地址: https://ai.maraecowell.com")
                return True
            else:
                print(f"⚠️ 外部访问返回: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 外部访问失败: {str(e)}")
            return False
    
    def stop_all(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process.wait()
            print("✅ 隧道已停止")
        
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process.wait()
            print("✅ Flask服务已停止")
    
    def run(self):
        """运行主程序"""
        print("🚀 TT-Live-AI 启动器")
        print("=" * 40)
        
        try:
            # 启动Flask
            if not self.start_flask():
                return False
            
            # 启动隧道
            if not self.start_tunnel():
                return False
            
            # 测试连接
            if not self.test_connection():
                print("⚠️ 连接测试失败，但服务可能仍在运行")
            
            print("\n✅ 服务启动完成!")
            print("📱 本地访问: http://127.0.0.1:8000")
            print("🌐 外部访问: https://ai.maraecowell.com")
            print("🛑 按 Ctrl+C 停止服务")
            
            # 保持运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号...")
            self.stop_all()
            print("✅ 所有服务已停止")
        except Exception as e:
            print(f"❌ 运行错误: {str(e)}")
            self.stop_all()

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n🛑 收到停止信号...")
    sys.exit(0)

if __name__ == "__main__":
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动管理器
    manager = TunnelManager()
    manager.run()
