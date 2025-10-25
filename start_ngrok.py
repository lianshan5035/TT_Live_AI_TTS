#!/usr/bin/env python3
"""
TT-Live-AI A3-TK 口播生成系统 - ngrok 自动映射脚本
自动暴露公网接口供 GPTs 调用
"""
import os
import time
import subprocess
import json
import requests
from pyngrok import ngrok, conf
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ngrok.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_ngrok_config():
    """加载 ngrok 配置"""
    load_dotenv()
    ngrok_token = os.getenv('NGROK_TOKEN')
    
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
        logger.info("✅ ngrok token 已加载")
        return True
    else:
        logger.warning("⚠️ 未找到 NGROK_TOKEN，将使用免费版本")
        return False

def start_ngrok_tunnel(port=5000):
    """启动 ngrok 隧道"""
    try:
        # 配置 ngrok
        conf.get_default().config_path = os.path.join(os.getcwd(), "ngrok.yml")
        
        # 启动隧道
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url
        
        logger.info(f"🚀 ngrok 隧道已启动")
        logger.info(f"📡 公网地址: {public_url}")
        logger.info(f"🔗 本地地址: http://localhost:{port}")
        
        return public_url, tunnel
        
    except Exception as e:
        logger.error(f"启动 ngrok 隧道失败: {str(e)}")
        return None, None

def get_tunnel_info(tunnel):
    """获取隧道信息"""
    try:
        # 获取隧道详细信息
        tunnels = ngrok.get_tunnels()
        for t in tunnels:
            if t.public_url:
                return {
                    "public_url": t.public_url,
                    "local_url": f"http://localhost:{t.config['addr'].split(':')[-1]}",
                    "protocol": t.proto,
                    "name": t.name
                }
    except Exception as e:
        logger.error(f"获取隧道信息失败: {str(e)}")
    
    return None

def test_endpoint(public_url):
    """测试端点是否可用"""
    try:
        # 测试健康检查端点
        health_url = f"{public_url}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ 端点测试成功")
            return True
        else:
            logger.error(f"❌ 端点测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 端点测试失败: {str(e)}")
        return False

def save_tunnel_info(public_url, tunnel_info):
    """保存隧道信息到文件"""
    info = {
        "public_url": public_url,
        "tunnel_info": tunnel_info,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    
    with open("logs/ngrok_info.json", "w") as f:
        json.dump(info, f, indent=2)
    
    logger.info("📄 隧道信息已保存到 logs/ngrok_info.json")

def monitor_tunnel(tunnel):
    """监控隧道状态"""
    logger.info("🔍 开始监控隧道状态...")
    
    try:
        while True:
            # 检查隧道是否仍然活跃
            tunnels = ngrok.get_tunnels()
            active_tunnels = [t for t in tunnels if t.public_url]
            
            if not active_tunnels:
                logger.warning("⚠️ 隧道已断开")
                break
            
            # 等待 30 秒后再次检查
            time.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号，正在关闭隧道...")
        ngrok.disconnect()
        logger.info("✅ 隧道已关闭")
    except Exception as e:
        logger.error(f"❌ 监控隧道时出错: {str(e)}")

def main():
    """主函数"""
    logger.info("🚀 启动 TT-Live-AI ngrok 映射服务...")
    
    # 创建必要目录
    os.makedirs('logs', exist_ok=True)
    
    # 加载配置
    load_ngrok_config()
    
    # 启动隧道
    public_url, tunnel = start_ngrok_tunnel()
    
    if not public_url:
        logger.error("❌ 无法启动 ngrok 隧道")
        return
    
    # 获取隧道信息
    tunnel_info = get_tunnel_info(tunnel)
    
    # 保存隧道信息
    save_tunnel_info(public_url, tunnel_info)
    
    # 测试端点
    if test_endpoint(public_url):
        logger.info("🎉 ngrok 映射成功！")
        logger.info(f"📡 GPTs 可访问地址: {public_url}")
        logger.info("🔗 生成接口: POST {public_url}/generate")
        logger.info("❤️ 健康检查: GET {public_url}/health")
        logger.info("📊 系统状态: GET {public_url}/status")
        
        # 监控隧道
        monitor_tunnel(tunnel)
    else:
        logger.error("❌ 端点测试失败，请检查 Flask 服务是否正在运行")

if __name__ == '__main__':
    main()
