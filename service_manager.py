#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 最终解决方案
使用正确的配置启动服务
"""

import os
import subprocess
import time
import requests
import signal
import sys
import threading

# 配置
TUNNEL_TOKEN = "eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9"
DOMAIN = "ai.maraecowell.com"
LOCAL_PORT = 8000

class ServiceManager:
    def __init__(self):
        self.flask_process = None
        self.tunnel_process = None
        self.running = True
        
    def start_flask(self):
        """启动Flask服务"""
        print("🚀 启动Flask服务...")
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['DEPLOYMENT_MODE'] = 'cloudflare_tunnel'
            env['CLOUDFLARE_TUNNEL_TOKEN'] = TUNNEL_TOKEN
            env['TUNNEL_FULL_DOMAIN'] = DOMAIN
            
            self.flask_process = subprocess.Popen([
                'python', 'web_dashboard_simple.py'
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务启动
            for i in range(10):
                time.sleep(1)
                try:
                    response = requests.get(f"http://127.0.0.1:{LOCAL_PORT}", timeout=2)
                    if response.status_code == 200:
                        print("✅ Flask服务启动成功")
                        return True
                except:
                    continue
            
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
                if stdout:
                    print(f"输出: {stdout.decode()}")
                if stderr:
                    print(f"错误: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ 启动隧道失败: {str(e)}")
            return False
    
    def monitor_services(self):
        """监控服务状态"""
        while self.running:
            try:
                # 检查Flask服务
                if self.flask_process and self.flask_process.poll() is not None:
                    print("⚠️ Flask服务已停止")
                    break
                
                # 检查隧道服务
                if self.tunnel_process and self.tunnel_process.poll() is not None:
                    print("⚠️ Cloudflare隧道已停止")
                    break
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ 监控错误: {str(e)}")
                time.sleep(5)
    
    def test_connection(self):
        """测试连接"""
        print("🧪 测试连接...")
        
        # 测试本地
        try:
            response = requests.get(f"http://127.0.0.1:{LOCAL_PORT}", timeout=5)
            if response.status_code == 200:
                print("✅ 本地服务正常")
            else:
                print(f"⚠️ 本地服务返回: {response.status_code}")
        except Exception as e:
            print(f"❌ 本地服务无法访问: {str(e)}")
            return False
        
        # 测试外部
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
    
    def stop_all(self):
        """停止所有服务"""
        print("🛑 停止所有服务...")
        self.running = False
        
        if self.tunnel_process:
            self.tunnel_process.terminate()
            try:
                self.tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
            print("✅ 隧道已停止")
        
        if self.flask_process:
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
            print("✅ Flask服务已停止")
    
    def run(self):
        """运行主程序"""
        print("🚀 TT-Live-AI 服务管理器")
        print("=" * 50)
        
        try:
            # 启动Flask
            if not self.start_flask():
                return False
            
            # 启动隧道
            if not self.start_tunnel():
                return False
            
            # 测试连接
            self.test_connection()
            
            print("\n✅ 服务启动完成!")
            print(f"📱 本地访问: http://127.0.0.1:{LOCAL_PORT}")
            print(f"🌐 外部访问: https://{DOMAIN}")
            print("🛑 按 Ctrl+C 停止服务")
            
            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 保持运行
            while self.running:
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
    manager = ServiceManager()
    manager.run()
