#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI A3标准启动脚本
完全符合GPTs-A3文档规范的启动器
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class A3Launcher:
    """A3标准启动器"""
    
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def check_dependencies(self):
        """检查依赖项"""
        logger.info("🔍 检查A3标准依赖项...")
        
        required_packages = [
            'flask', 'edge-tts', 'pandas', 'numpy', 
            'requests', 'asyncio', 'openpyxl'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"❌ {package} 未安装")
        
        if missing_packages:
            logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.info("请运行: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("✅ 所有依赖项检查通过")
        return True
    
    def create_directories(self):
        """创建必要的目录"""
        logger.info("📁 创建A3标准目录结构...")
        
        directories = [
            'templates', 'static/css', 'static/js', 'static/images',
            'input', 'outputs', 'logs', 'temp'
        ]
        
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"✅ 目录已创建: {dir_name}")
    
    def start_tts_service(self):
        """启动TTS服务"""
        logger.info("🚀 启动A3标准TTS服务...")
        
        try:
            # 检查端口5001是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5001))
            sock.close()
            
            if result == 0:
                logger.warning("⚠️ 端口5001已被占用，尝试使用端口5002")
                # 修改run_tts.py中的端口
                self.update_tts_port(5002)
                tts_port = 5002
            else:
                tts_port = 5001
            
            # 启动TTS服务
            tts_script = self.base_dir / 'run_tts.py'
            if tts_script.exists():
                process = subprocess.Popen([
                    sys.executable, str(tts_script)
                ], cwd=str(self.base_dir))
                
                self.processes.append(process)
                logger.info(f"✅ TTS服务已启动 (PID: {process.pid}, 端口: {tts_port})")
                
                # 等待服务启动
                time.sleep(3)
                return True
            else:
                logger.error("❌ 找不到run_tts.py文件")
                return False
                
        except Exception as e:
            logger.error(f"❌ TTS服务启动失败: {str(e)}")
            return False
    
    def update_tts_port(self, port):
        """更新TTS服务端口"""
        try:
            tts_file = self.base_dir / 'run_tts.py'
            if tts_file.exists():
                content = tts_file.read_text(encoding='utf-8')
                content = content.replace('port=5001', f'port={port}')
                tts_file.write_text(content, encoding='utf-8')
                logger.info(f"✅ TTS服务端口已更新为: {port}")
        except Exception as e:
            logger.error(f"❌ 更新TTS端口失败: {str(e)}")
    
    def start_web_dashboard(self):
        """启动Web控制中心"""
        logger.info("🌐 启动A3标准Web控制中心...")
        
        try:
            # 检查端口8000是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                logger.warning("⚠️ 端口8000已被占用，尝试使用端口8001")
                web_port = 8001
            else:
                web_port = 8000
            
            # 启动Web服务
            web_script = self.base_dir / 'a3_web_dashboard.py'
            if web_script.exists():
                process = subprocess.Popen([
                    sys.executable, str(web_script)
                ], cwd=str(self.base_dir))
                
                self.processes.append(process)
                logger.info(f"✅ Web控制中心已启动 (PID: {process.pid}, 端口: {web_port})")
                
                # 等待服务启动
                time.sleep(3)
                return True
            else:
                logger.error("❌ 找不到a3_web_dashboard.py文件")
                return False
                
        except Exception as e:
            logger.error(f"❌ Web控制中心启动失败: {str(e)}")
            return False
    
    def check_services(self):
        """检查服务状态"""
        logger.info("🔍 检查A3标准服务状态...")
        
        services = [
            {'name': 'TTS服务', 'port': 5001, 'path': '/health'},
            {'name': 'Web控制中心', 'port': 8000, 'path': '/api/status'}
        ]
        
        all_healthy = True
        
        for service in services:
            try:
                import requests
                response = requests.get(
                    f"http://localhost:{service['port']}{service['path']}", 
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info(f"✅ {service['name']} 运行正常")
                else:
                    logger.warning(f"⚠️ {service['name']} 响应异常: {response.status_code}")
                    all_healthy = False
            except Exception as e:
                logger.error(f"❌ {service['name']} 检查失败: {str(e)}")
                all_healthy = False
        
        return all_healthy
    
    def show_startup_info(self):
        """显示启动信息"""
        logger.info("🎉 A3标准系统启动完成!")
        logger.info("=" * 60)
        logger.info("📡 服务地址:")
        logger.info("   🌐 Web控制中心: http://localhost:8000")
        logger.info("   🎤 TTS服务: http://localhost:5001")
        logger.info("=" * 60)
        logger.info("🎯 A3标准特性:")
        logger.info("   ✅ 完全符合GPTs-A3文档规范")
        logger.info("   ✅ 12种情绪参数配置")
        logger.info("   ✅ 数学动态参数库")
        logger.info("   ✅ 防检测机制")
        logger.info("   ✅ TikTok合规规则")
        logger.info("   ✅ 800条脚本批次生成")
        logger.info("=" * 60)
        logger.info("💡 使用说明:")
        logger.info("   1. 访问 http://localhost:8000 打开A3标准控制中心")
        logger.info("   2. 上传Excel文件或直接生成A3标准脚本")
        logger.info("   3. 支持10批次×80条=800条脚本生成")
        logger.info("   4. 按Ctrl+C停止服务")
        logger.info("=" * 60)
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info("🛑 收到停止信号，正在关闭A3标准服务...")
        self.stop_all_services()
        sys.exit(0)
    
    def stop_all_services(self):
        """停止所有服务"""
        logger.info("🛑 停止A3标准服务...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ 进程 {process.pid} 已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️ 强制终止进程 {process.pid}")
            except Exception as e:
                logger.error(f"❌ 停止进程失败: {str(e)}")
        
        self.processes.clear()
        logger.info("✅ 所有服务已停止")
    
    def run(self):
        """运行A3标准启动器"""
        try:
            logger.info("🚀 TT-Live-AI A3标准启动器")
            logger.info("📋 完全符合GPTs-A3文档规范")
            
            # 设置信号处理器
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # 检查依赖项
            if not self.check_dependencies():
                return False
            
            # 创建目录
            self.create_directories()
            
            # 启动TTS服务
            if not self.start_tts_service():
                return False
            
            # 启动Web控制中心
            if not self.start_web_dashboard():
                return False
            
            # 检查服务状态
            if not self.check_services():
                logger.warning("⚠️ 部分服务可能未正常启动")
            
            # 显示启动信息
            self.show_startup_info()
            
            # 保持运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 用户中断，正在停止服务...")
                self.stop_all_services()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ A3标准启动器运行失败: {str(e)}")
            self.stop_all_services()
            return False

def main():
    """主函数"""
    launcher = A3Launcher()
    success = launcher.run()
    
    if success:
        logger.info("✅ A3标准启动器正常退出")
        sys.exit(0)
    else:
        logger.error("❌ A3标准启动器异常退出")
        sys.exit(1)

if __name__ == "__main__":
    main()
