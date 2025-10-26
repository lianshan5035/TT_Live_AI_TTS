#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 自动配置脚本
直接连接Cloudflare API进行隧道配置
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudflareAutoConfig:
    """Cloudflare自动配置器"""
    
    def __init__(self):
        self.api_token = None
        self.account_id = None
        self.zone_id = None
        self.domain = "maraecowell.com"
        self.subdomain = "ai"
        self.full_domain = f"{self.subdomain}.{self.domain}"
        
    def get_cloudflare_token(self):
        """获取Cloudflare API Token"""
        print("🔑 配置Cloudflare API Token")
        print("请按照以下步骤获取API Token:")
        print("1. 访问 https://dash.cloudflare.com/profile/api-tokens")
        print("2. 点击 'Create Token'")
        print("3. 选择 'Custom token'")
        print("4. 设置权限:")
        print("   - Zone:Zone:Read")
        print("   - Zone:DNS:Edit") 
        print("   - Account:Cloudflare Tunnel:Edit")
        print("5. 复制生成的Token")
        print()
        
        token = input("请输入您的Cloudflare API Token: ").strip()
        if not token:
            print("❌ Token不能为空")
            return False
            
        self.api_token = token
        return True
    
    def get_account_info(self):
        """获取Cloudflare账户信息"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # 获取账户列表
            response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
            if response.status_code != 200:
                print(f"❌ 获取账户信息失败: {response.text}")
                return False
            
            accounts = response.json()['result']
            if not accounts:
                print("❌ 未找到Cloudflare账户")
                return False
            
            # 选择第一个账户
            self.account_id = accounts[0]['id']
            print(f"✅ 使用账户: {accounts[0]['name']} (ID: {self.account_id})")
            return True
            
        except Exception as e:
            print(f"❌ 获取账户信息失败: {str(e)}")
            return False
    
    def get_zone_info(self):
        """获取域名Zone信息"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # 搜索域名
            response = requests.get(f'https://api.cloudflare.com/client/v4/zones?name={self.domain}', headers=headers)
            if response.status_code != 200:
                print(f"❌ 获取域名信息失败: {response.text}")
                return False
            
            zones = response.json()['result']
            if not zones:
                print(f"❌ 未找到域名 {self.domain}")
                return False
            
            self.zone_id = zones[0]['id']
            print(f"✅ 找到域名: {self.domain} (Zone ID: {self.zone_id})")
            return True
            
        except Exception as e:
            print(f"❌ 获取域名信息失败: {str(e)}")
            return False
    
    def create_tunnel(self):
        """创建Cloudflare隧道"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        tunnel_name = "a3-tt-live-ai"
        
        try:
            # 检查隧道是否已存在
            response = requests.get(f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/cfd_tunnel', headers=headers)
            if response.status_code == 200:
                tunnels = response.json()['result']
                for tunnel in tunnels:
                    if tunnel['name'] == tunnel_name:
                        print(f"✅ 隧道已存在: {tunnel_name} (ID: {tunnel['id']})")
                        return tunnel['id']
            
            # 创建新隧道
            data = {
                'name': tunnel_name,
                'config_src': 'cloudflared'
            }
            
            response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/cfd_tunnel', 
                                   headers=headers, json=data)
            
            if response.status_code != 200:
                print(f"❌ 创建隧道失败: {response.text}")
                return None
            
            tunnel = response.json()['result']
            tunnel_id = tunnel['id']
            print(f"✅ 隧道创建成功: {tunnel_name} (ID: {tunnel_id})")
            return tunnel_id
            
        except Exception as e:
            print(f"❌ 创建隧道失败: {str(e)}")
            return None
    
    def create_tunnel_config(self, tunnel_id):
        """创建隧道配置"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        config = {
            'config': {
                'ingress': [
                    {
                        'hostname': self.full_domain,
                        'service': 'http://127.0.0.1:8000'
                    },
                    {
                        'service': 'http_status:404'
                    }
                ]
            }
        }
        
        try:
            response = requests.put(f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/cfd_tunnel/{tunnel_id}/configurations', 
                                  headers=headers, json=config)
            
            if response.status_code != 200:
                print(f"❌ 配置隧道失败: {response.text}")
                return False
            
            print(f"✅ 隧道配置成功: {self.full_domain} -> http://127.0.0.1:8000")
            return True
            
        except Exception as e:
            print(f"❌ 配置隧道失败: {str(e)}")
            return False
    
    def create_dns_record(self, tunnel_id):
        """创建DNS记录"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # 获取隧道CNAME
        try:
            response = requests.get(f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/cfd_tunnel/{tunnel_id}', headers=headers)
            if response.status_code != 200:
                print(f"❌ 获取隧道信息失败: {response.text}")
                return False
            
            tunnel = response.json()['result']
            cname_target = f"{tunnel_id}.cfargotunnel.com"
            
            # 检查DNS记录是否已存在
            response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records?name={self.full_domain}', headers=headers)
            if response.status_code == 200:
                records = response.json()['result']
                for record in records:
                    if record['name'] == self.full_domain and record['type'] == 'CNAME':
                        print(f"✅ DNS记录已存在: {self.full_domain} -> {record['content']}")
                        return True
            
            # 创建DNS记录
            data = {
                'type': 'CNAME',
                'name': self.full_domain,
                'content': cname_target,
                'comment': 'A3-TT-Live-AI Tunnel'
            }
            
            response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records', 
                                   headers=headers, json=data)
            
            if response.status_code != 200:
                print(f"❌ 创建DNS记录失败: {response.text}")
                return False
            
            print(f"✅ DNS记录创建成功: {self.full_domain} -> {cname_target}")
            return True
            
        except Exception as e:
            print(f"❌ 创建DNS记录失败: {str(e)}")
            return False
    
    def generate_tunnel_token(self, tunnel_id):
        """生成隧道Token"""
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/cfd_tunnel/{tunnel_id}/token', 
                                   headers=headers)
            
            if response.status_code != 200:
                print(f"❌ 生成Token失败: {response.text}")
                return None
            
            token = response.json()['result']['token']
            print(f"✅ 隧道Token生成成功")
            return token
            
        except Exception as e:
            print(f"❌ 生成Token失败: {str(e)}")
            return None
    
    def save_config(self, tunnel_id, token):
        """保存配置到文件"""
        config = {
            'tunnel_id': tunnel_id,
            'tunnel_token': token,
            'domain': self.full_domain,
            'account_id': self.account_id,
            'zone_id': self.zone_id,
            'created_at': datetime.now().isoformat()
        }
        
        # 保存到.env文件
        env_content = f"""# Cloudflare Tunnel 配置
CLOUDFLARE_TUNNEL_TOKEN={token}
CLOUDFLARE_TUNNEL_NAME=a3-tt-live-ai
TUNNEL_FULL_DOMAIN={self.full_domain}
CLOUDFLARE_ACCOUNT_ID={self.account_id}
CLOUDFLARE_ZONE_ID={self.zone_id}
CLOUDFLARE_TUNNEL_ID={tunnel_id}

# 部署模式
DEPLOYMENT_MODE=cloudflare_tunnel
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # 保存详细配置
        with open('cloudflare_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 配置已保存到 .env 和 cloudflare_config.json")
        return True
    
    def test_tunnel(self, token):
        """测试隧道连接"""
        print("🧪 测试隧道连接...")
        
        try:
            # 启动cloudflared
            cmd = ['cloudflared', 'tunnel', 'run', '--token', token]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # 等待隧道启动
            for i in range(30):
                try:
                    response = requests.get(f"https://{self.full_domain}/api/tasks", timeout=3)
                    if response.status_code == 200:
                        print(f"✅ 隧道测试成功: https://{self.full_domain}")
                        process.terminate()
                        return True
                except:
                    pass
                time.sleep(1)
            
            print("⚠️ 隧道测试超时，请检查本地服务是否运行")
            process.terminate()
            return False
            
        except Exception as e:
            print(f"❌ 隧道测试失败: {str(e)}")
            return False
    
    def run_auto_config(self):
        """运行自动配置"""
        print("🚀 Cloudflare 自动配置开始")
        print("=" * 50)
        
        # 步骤1: 获取API Token
        if not self.get_cloudflare_token():
            return False
        
        # 步骤2: 获取账户信息
        if not self.get_account_info():
            return False
        
        # 步骤3: 获取域名信息
        if not self.get_zone_info():
            return False
        
        # 步骤4: 创建隧道
        tunnel_id = self.create_tunnel()
        if not tunnel_id:
            return False
        
        # 步骤5: 配置隧道
        if not self.create_tunnel_config(tunnel_id):
            return False
        
        # 步骤6: 创建DNS记录
        if not self.create_dns_record(tunnel_id):
            return False
        
        # 步骤7: 生成Token
        token = self.generate_tunnel_token(tunnel_id)
        if not token:
            return False
        
        # 步骤8: 保存配置
        if not self.save_config(tunnel_id, token):
            return False
        
        # 步骤9: 测试隧道
        self.test_tunnel(token)
        
        print("\n🎉 Cloudflare配置完成!")
        print(f"🌐 您的应用可以通过 https://{self.full_domain} 访问")
        print("📝 配置已保存到 .env 文件")
        
        return True

def main():
    """主函数"""
    configurator = CloudflareAutoConfig()
    
    try:
        success = configurator.run_auto_config()
        if success:
            print("\n✅ 配置成功完成!")
        else:
            print("\n❌ 配置失败，请检查错误信息")
    except KeyboardInterrupt:
        print("\n🛑 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()
