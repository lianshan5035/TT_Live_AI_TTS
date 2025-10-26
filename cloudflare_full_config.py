#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare 完整配置解决方案
直接通过API配置隧道和DNS
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

# 您的Cloudflare Token
CF_TOKEN = "eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9"

def get_account_info():
    """获取账户信息"""
    headers = {
        'Authorization': f'Bearer {CF_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://api.cloudflare.com/client/v4/accounts', headers=headers)
        if response.status_code == 200:
            accounts = response.json()['result']
            if accounts:
                account_id = accounts[0]['id']
                print(f"✅ 账户ID: {account_id}")
                return account_id
        print(f"❌ 获取账户失败: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 获取账户失败: {str(e)}")
        return None

def get_zone_info(domain="maraecowell.com"):
    """获取Zone信息"""
    headers = {
        'Authorization': f'Bearer {CF_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'https://api.cloudflare.com/client/v4/zones?name={domain}', headers=headers)
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
        'Authorization': f'Bearer {CF_TOKEN}',
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

def configure_tunnel(account_id, tunnel_id, domain="ai.maraecowell.com"):
    """配置隧道"""
    headers = {
        'Authorization': f'Bearer {CF_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    config = {
        'config': {
            'ingress': [
                {
                    'hostname': domain,
                    'service': 'http://127.0.0.1:8000'
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
            print(f"✅ 隧道配置成功: {domain} -> http://127.0.0.1:8000")
            return True
        else:
            print(f"❌ 配置隧道失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 配置隧道失败: {str(e)}")
        return False

def create_dns_record(zone_id, tunnel_id, domain="ai.maraecowell.com"):
    """创建DNS记录"""
    headers = {
        'Authorization': f'Bearer {CF_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    cname_target = f"{tunnel_id}.cfargotunnel.com"
    
    data = {
        'type': 'CNAME',
        'name': domain,
        'content': cname_target,
        'comment': 'A3-TT-Live-AI Tunnel'
    }
    
    try:
        response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', 
                               headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ DNS记录创建成功: {domain} -> {cname_target}")
            return True
        else:
            print(f"❌ 创建DNS记录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建DNS记录失败: {str(e)}")
        return False

def generate_tunnel_token(account_id, tunnel_id):
    """生成隧道Token"""
    headers = {
        'Authorization': f'Bearer {CF_TOKEN}',
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

def test_tunnel_connection():
    """测试隧道连接"""
    print("🧪 测试隧道连接...")
    
    # 检查本地服务
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✅ 本地服务运行正常")
        else:
            print("❌ 本地服务响应异常")
            return False
    except:
        print("❌ 本地服务无法访问")
        return False
    
    # 测试外部访问
    try:
        response = requests.get("https://ai.maraecowell.com", timeout=10)
        if response.status_code == 200:
            print("✅ 外部访问成功")
            return True
        else:
            print(f"⚠️ 外部访问返回: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 外部访问失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 Cloudflare 完整配置")
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
        'domain': 'ai.maraecowell.com',
        'created_at': datetime.now().isoformat()
    }
    
    with open('cloudflare_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ 配置已保存到 cloudflare_config.json")
    
    # 步骤8: 测试连接
    print("\n⏳ 等待DNS传播...")
    time.sleep(10)
    test_tunnel_connection()
    
    print("\n🎉 配置完成!")
    print("🌐 访问地址: https://ai.maraecowell.com")
    
    return True

if __name__ == "__main__":
    main()
