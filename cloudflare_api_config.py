#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare API 配置脚本
使用新的API令牌配置隧道
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

# 新的API令牌
API_TOKEN = "2vyptbH_jzcQwSYYuMIIyQNPYs79jZIlfr4mtKSS"
DOMAIN = "ai.maraecowell.com"
LOCAL_PORT = 8000

def get_account_info():
    """获取账户信息"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 尝试获取用户信息
        response = requests.get('https://api.cloudflare.com/client/v4/user', headers=headers)
        if response.status_code == 200:
            user_info = response.json()['result']
            print(f"✅ 用户信息: {user_info.get('email', 'Unknown')}")
            
            # 尝试获取账户信息
            response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
            if response.status_code == 200:
                accounts = response.json()['result']
                if accounts:
                    account_id = accounts[0]['id']
                    print(f"✅ 账户ID: {account_id}")
                    return account_id
                else:
                    # 如果没有账户，尝试使用用户ID
                    user_id = user_info.get('id')
                    if user_id:
                        print(f"✅ 使用用户ID: {user_id}")
                        return user_id
            else:
                print(f"⚠️ 无法获取账户信息: {response.text}")
                return None
        print(f"❌ 获取用户信息失败: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 获取账户失败: {str(e)}")
        return None

def get_zone_info():
    """获取Zone信息"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'https://api.cloudflare.com/client/v4/zones?name=maraecowell.com', headers=headers)
        if response.status_code == 200:
            zones = response.json()['result']
            if zones:
                zone_id = zones[0]['id']
                print(f"✅ Zone ID: {zone_id}")
                return zone_id
        print(f"❌ 获取Zone失败: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 获取Zone失败: {str(e)}")
        return None

def create_tunnel(account_id, tunnel_name="a3-tt-live-ai"):
    """创建隧道"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'name': tunnel_name,
        'config_src': 'cloudflared'
    }
    
    try:
        response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            tunnel = response.json()['result']
            tunnel_id = tunnel['id']
            print(f"✅ 隧道创建成功: {tunnel_id}")
            return tunnel_id
        else:
            print(f"❌ 创建隧道失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建隧道失败: {str(e)}")
        return None

def configure_tunnel(account_id, tunnel_id):
    """配置隧道"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    config = {
        'config': {
            'ingress': [
                {
                    'hostname': DOMAIN,
                    'service': f'http://127.0.0.1:{LOCAL_PORT}'
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
    }
    
    try:
        response = requests.put(f'https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations', 
                              headers=headers, json=config)
        
        if response.status_code == 200:
            print(f"✅ 隧道配置成功: {DOMAIN} -> http://127.0.0.1:{LOCAL_PORT}")
            return True
        else:
            print(f"❌ 配置隧道失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 配置隧道失败: {str(e)}")
        return False

def create_dns_record(zone_id, tunnel_id):
    """创建DNS记录"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    cname_target = f"{tunnel_id}.cfargotunnel.com"
    
    data = {
        'type': 'CNAME',
        'name': DOMAIN,
        'content': cname_target,
        'comment': 'A3-TT-Live-AI Tunnel'
    }
    
    try:
        response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ DNS记录创建成功: {DOMAIN} -> {cname_target}")
            return True
        else:
            print(f"❌ 创建DNS记录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建DNS记录失败: {str(e)}")
        return None

def generate_tunnel_token(account_id, tunnel_id):
    """生成隧道Token"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/token', 
                               headers=headers)
        
        if response.status_code == 200:
            token = response.json()['result']['token']
            print(f"✅ 隧道Token生成成功")
            return token
        else:
            print(f"❌ 生成Token失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 生成Token失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("🚀 Cloudflare API 配置")
    print("=" * 50)
    
    # 步骤1: 获取账户信息
    account_id = get_account_info()
    if not account_id:
        return False
    
    # 步骤2: 获取Zone信息
    zone_id = get_zone_info()
    if not zone_id:
        return False
    
    # 步骤3: 创建隧道
    tunnel_id = create_tunnel(account_id)
    if not tunnel_id:
        return False
    
    # 步骤4: 配置隧道
    if not configure_tunnel(account_id, tunnel_id):
        return False
    
    # 步骤5: 创建DNS记录
    if not create_dns_record(zone_id, tunnel_id):
        return False
    
    # 步骤6: 生成Token
    token = generate_tunnel_token(account_id, tunnel_id)
    if not token:
        return False
    
    # 步骤7: 保存配置
    config = {
        'account_id': account_id,
        'zone_id': zone_id,
        'tunnel_id': tunnel_id,
        'token': token,
        'domain': DOMAIN,
        'api_token': API_TOKEN,
        'created_at': datetime.now().isoformat()
    }
    
    with open('cloudflare_api_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ 配置已保存到 cloudflare_api_config.json")
    print(f"🔑 新Token: {token}")
    
    return True

if __name__ == "__main__":
    main()
