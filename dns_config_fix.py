#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare DNS 配置解决方案
使用API令牌配置DNS记录
"""

import os
import json
import requests
import subprocess
import time
from datetime import datetime

# API令牌
API_TOKEN = "2vyptbH_jzcQwSYYuMIIyQNPYs79jZIlfr4mtKSS"
DOMAIN = "ai.maraecowell.com"
TUNNEL_ID = "c863d089-16f0-487a-81cf-507500c16367"

def get_zone_id():
    """获取Zone ID"""
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

def create_cname_record(zone_id):
    """创建CNAME记录"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    cname_target = f"{TUNNEL_ID}.cfargotunnel.com"
    
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
            record = response.json()['result']
            print(f"✅ DNS记录创建成功: {DOMAIN} -> {cname_target}")
            print(f"记录ID: {record['id']}")
            return True
        else:
            print(f"❌ 创建DNS记录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建DNS记录失败: {str(e)}")
        return False

def update_existing_record(zone_id):
    """更新现有DNS记录"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 获取现有记录
    try:
        response = requests.get(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={DOMAIN}', headers=headers)
        if response.status_code == 200:
            records = response.json()['result']
            if records:
                record_id = records[0]['id']
                print(f"✅ 找到现有记录: {record_id}")
                
                # 更新记录
                cname_target = f"{TUNNEL_ID}.cfargotunnel.com"
                data = {
                    'type': 'CNAME',
                    'name': DOMAIN,
                    'content': cname_target,
                    'comment': 'A3-TT-Live-AI Tunnel'
                }
                
                response = requests.put(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}', 
                                      headers=headers, json=data)
                
                if response.status_code == 200:
                    print(f"✅ DNS记录更新成功: {DOMAIN} -> {cname_target}")
                    return True
                else:
                    print(f"❌ 更新DNS记录失败: {response.text}")
                    return False
            else:
                print("❌ 未找到现有记录")
                return False
        else:
            print(f"❌ 获取DNS记录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 更新DNS记录失败: {str(e)}")
        return False

def test_dns_propagation():
    """测试DNS传播"""
    print("🧪 测试DNS传播...")
    
    for i in range(5):
        try:
            response = requests.get(f"https://{DOMAIN}", timeout=10)
            if response.status_code == 200:
                print("✅ DNS传播成功，外部访问正常")
                return True
            else:
                print(f"⚠️ DNS传播中，返回: {response.status_code}")
        except Exception as e:
            print(f"⚠️ DNS传播中，错误: {str(e)}")
        
        time.sleep(10)
    
    print("❌ DNS传播超时")
    return False

def main():
    """主函数"""
    print("🚀 Cloudflare DNS 配置解决方案")
    print("=" * 50)
    
    # 获取Zone ID
    zone_id = get_zone_id()
    if not zone_id:
        return False
    
    # 更新DNS记录
    if update_existing_record(zone_id):
        print("✅ DNS记录更新成功")
    elif create_cname_record(zone_id):
        print("✅ DNS记录创建成功")
    else:
        print("❌ DNS记录配置失败")
        return False
    
    # 测试DNS传播
    if test_dns_propagation():
        print("\n🎉 配置完成!")
        print(f"🌐 访问地址: https://{DOMAIN}")
        return True
    else:
        print("⚠️ DNS传播可能需要更长时间")
        return False

if __name__ == "__main__":
    main()
