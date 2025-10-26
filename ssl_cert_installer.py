#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare SSL 证书安装脚本
安装源证书到本地服务器
"""

import os
import subprocess
import time
import requests

# SSL证书内容
CERTIFICATE = """-----BEGIN CERTIFICATE-----
MIIEqjCCA5KgAwIBAgIUZA/3L9UAH6KS4JKm6O1bUEUu2/swDQYJKoZIhvcNAQEL
BQAwgYsxCzAJBgNVBAYTAlVTMRkwFwYDVQQKExBDbG91ZEZsYXJlLCBJbmMuMTQw
MgYDVQQLEytDbG91ZEZsYXJlIE9yaWdpbiBTU0wgQ2VydGlmaWNhdGUgQXV0aG9y
aXR5MRYwFAYDVQQHEw1TYW4gRnJhbmNpc2NvMRMwEQYDVQQIEwpDYWxpZm9ybmlh
MB4XDTI1MTAyNjE4NDUwMFoXDTQwMTAyMjE4NDUwMFowYjEZMBcGA1UEChMQQ2xv
dWRGbGFyZSwgSW5jLjEdMBsGA1UECxMUQ2xvdWRGbGFyZSBPcmlnaW4gQ0ExJjAk
BgNVBAMTHUNsb3VkRmxhcmUgT3JpZ2luIENlcnRpZmljYXRlMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAg3CpnnajvHIGqqkK6e5/kv2wnjyl8kBRo8B2
Civ4V/QYvwgzuny5GRagKj5GGrjWVTg7WpQHbxWd3f1ovrkMNmiRBFFzGKAbkZec
YwAoSMCGjpNXgyZ3iGutMJMVjkEtDoaOk4xPVlUtYzNa1XO9D+dljIMaMgCLatQi
7Wf92xLc/ADxjq7Q/NpaiCe+SRvYEUGsWltF/CrNGY9LaAPvwnRed66CiyrQAi1d
SBYYmuqu/O3wSvhOZX6f5/EMCKNBmkEgaQncPuxju7MhxNSF7g+ylryWIndRErEH
FvSwhL16afpmb1KE/f5wxzPJZ9ljP51L/J7TufZIcruozVRTqQIDAQABo4IBLDCC
ASgwDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMCBggrBgEFBQcD
ATAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBR3M73mXQnjt8EpMlnF01iMXba+BzAf
BgNVHSMEGDAWgBQk6FNXXXw0QIep65TbuuEWePwppDBABggrBgEFBQcBAQQ0MDIw
MAYIKwYBBQUHMAGGJGh0dHA6Ly9vY3NwLmNsb3VkZmxhcmUuY29tL29yaWdpbl9j
YTAtBgNVHREEJjAkghEqLm1hcmFlY293ZWxsLmNvbYIPbWFyYWVjb3dlbGwuY29t
MDgGA1UdHwQxMC8wLaAroCmGJ2h0dHA6Ly9jcmwuY2xvdWRmbGFyZS5jb20vb3Jp
Z2luX2NhLmNybDANBgkqhkiG9w0BAQsFAAOCAQEAkMNBa7Pxz8J1HjoSRlSKe9sK
L60RCvqjZubzA9wUJm1gsjJN63hmBcSRAmx6QlrKBBzfzt/wMecF5UGVP6pRG2xu
axPcw6Y8E3K3EdgHFeXucj5wqEIYdeFk8fpAfsnb1ZrcjpajJK/KJmTEZCRYAMs9
7Jxxmn/ALPSCP9elnSAkW8DDu80c2rPQO3ZgpjQfJ30NJn4kkNTjziapd0PeznBH
H+akScIRVWnuxUR0VPaWH/3qJydKcBaqwP/XkkOVipB/9WU/Vk3g4atdQl471JQF
GsMWPk5NYVuhLAHy9az/r2hkIQQ8QMOIjzcv8ZwDG0KGWb/08HiiAKA/6V6n3Q==
-----END CERTIFICATE-----"""

PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCDcKmedqO8cgaq
qQrp7n+S/bCePKXyQFGjwHYKK/hX9Bi/CDO6fLkZFqAqPkYauNZVODtalAdvFZ3d
/Wi+uQw2aJEEUXMYoBuRl5xjAChIwIaOk1eDJneIa60wkxWOQS0Oho6TjE9WVS1j
M1rVc70P52WMgxoyAItq1CLtZ/3bEtz8APGOrtD82lqIJ75JG9gRQaxaW0X8Ks0Z
j0toA+/CdF53roKLKtACLV1IFhia6q787fBK+E5lfp/n8QwIo0GaQSBpCdw+7GO7
syHE1IXuD7KWvJYid1ESsQcW9LCEvXpp+mZvUoT9/nDHM8ln2WM/nUv8ntO59khy
u6jNVFOpAgMBAAECggEAAVNVnpJnOHtfkQEx6eXcwFR8dL1mALFV3BnQ3ELmbFVQ
ROhAr0uFNAPRUIO+whO68506JKxz/mfgfEXgicsvce1a3bPdk4dqfRd4krCvIfwG
ZLHciCckkvS1CIBJ5MdIUfUY7dN/Kal5EvRIYPkxFFPlfLCGHIV6t8nVDVcHDW/E
UBVLDAiemPt/BkwnE6sGR5nrOU22yBekfgDdjGqNT7AXkmCLtSofjzkQjXCb+4IS
C6WNFovXFOXlmepGAvXmq/GwGuM2NP6AH15FdKWl8flBUnP7SxBXUEKneY5KCFBn
53IFBz7geS1YWgWYh55pmpzJng4xLF65P+LNICKeQQKBgQC4YfEmWZcWeNPQJpcm
JkTG74J0wJv4XKxfOPT7QHen1mZy4nXV0juys/Dn/+vSaC940sW4OkhvNseZMxQc
WG/CZE2ChZnSWTXWdPzDeIIhQTKUSiLKSHrmm49VZep8aZjFyXVSiJrkNpUcssLn
/autRUwF3TQKVhm+FRd2TR3CiQKBgQC2fmPs6JfKa/leRZuNlgChJECXm3MoYlsN
NinVxlne7KP6km6kw9hWA4c0f1Svku7FjtxOXTbwjYZiB8Us7TV6r+vqW+g08Qbp
g6FsXvBDciLi9JbLvLCTrYiBrUICzybQ5V3vKZpER8nUZ95hkt8n4OyStzMM0/CS
Q4pvRfxAIQKBgGiDO8ndJoMaYhWuiiaZsoqA4JWFR+NzxFEFW/e/BxQft1qPevOE
g0o8LOWUbvuJCr+V2XUftEc16dWw2klm55JsgHLnf9V3s8in705tVHW9GwprK2U1
yFRHAOwLJOr4gBw8oT/zJrkNJ2BpA4m0hEdm7Dy2sfTZ8SWJlw77j07hAoGAf3Nh
wjDm4Z3q+GXQr19VbTTuT3NnR4r5YA61xPDUDxZhpzvhPfzw95FbOdS7histypdt
UOVU20db1NbsY+X+dYKrVm99iovScf9WG2NqlQ//QVXkgsFy6JBHR5mDAoc96qJl
qgP6Ezm3wToRWz/Bzg4N6qE7a/gQiXXWFsRf2UECgYBgyozQTVr8BCNV0S2ixu0F
uPUxOCKwmMuZs2txzBTsgK4IVSQxYhrGdsrAcGOYGW+defW1QXbN1JqJ7ElzEEBR
VxSpFeEwtyaRvffRTJb/QiiD+o4l0IskEiN4UA2Z4RUBA7alpiKbC1ln9mAo7K3u
KXa+ejj9gDAQ07FsSzj2sQ==
-----END PRIVATE KEY-----"""

def install_ssl_certificates():
    """安装SSL证书"""
    print("🔐 安装SSL证书...")
    
    # 创建证书目录
    cert_dir = "/etc/ssl/cloudflare"
    os.makedirs(cert_dir, exist_ok=True)
    
    try:
        # 写入证书文件
        with open(f"{cert_dir}/origin.pem", "w") as f:
            f.write(CERTIFICATE)
        print("✅ 证书文件已安装")
        
        # 写入私钥文件
        with open(f"{cert_dir}/origin.key", "w") as f:
            f.write(PRIVATE_KEY)
        print("✅ 私钥文件已安装")
        
        # 设置权限
        os.chmod(f"{cert_dir}/origin.pem", 0o644)
        os.chmod(f"{cert_dir}/origin.key", 0o600)
        print("✅ 文件权限已设置")
        
        return True
        
    except Exception as e:
        print(f"❌ 安装证书失败: {str(e)}")
        return False

def create_nginx_config():
    """创建Nginx配置"""
    print("🌐 创建Nginx配置...")
    
    nginx_config = f"""server {{
    listen 8000 ssl;
    server_name ai.maraecowell.com;
    
    ssl_certificate /etc/ssl/cloudflare/origin.pem;
    ssl_certificate_key /etc/ssl/cloudflare/origin.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {{
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}"""
    
    try:
        with open("/etc/nginx/sites-available/cloudflare-tunnel", "w") as f:
            f.write(nginx_config)
        print("✅ Nginx配置已创建")
        return True
    except Exception as e:
        print(f"❌ 创建Nginx配置失败: {str(e)}")
        return False

def start_services():
    """启动服务"""
    print("🚀 启动服务...")
    
    # 启动Flask服务在8001端口
    print("📱 启动Flask服务...")
    flask_process = subprocess.Popen([
        'python', 'web_dashboard_simple.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待Flask启动
    time.sleep(5)
    
    # 测试Flask服务
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
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
        'cloudflared', 'tunnel', 'run', '--token', 'eyJhIjoiMTgwOGMwMzFjYmU4NmE4YTAyMTJmNDlkZTFiMzI0NzAiLCJ0IjoiYzg2M2QwODktMTZmMC00ODdhLTgxY2YtNTA3NTAwYzE2MzY3IiwicyI6Ik1XRXdPR0poTnpjdE5tSXdaQzAwT0RGbUxXRmpOMkV0WmpZNFpESmpZelExWVRRMCJ9'
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

def main():
    """主函数"""
    print("🚀 Cloudflare SSL 证书安装")
    print("=" * 50)
    
    try:
        # 安装SSL证书
        if install_ssl_certificates():
            print("✅ SSL证书安装完成")
        else:
            print("❌ SSL证书安装失败")
            return False
        
        # 启动服务
        if start_services():
            print("\n✅ 服务启动完成!")
            print("📱 本地访问: http://127.0.0.1:8000")
            print("🌐 外部访问: https://ai.maraecowell.com")
            return True
        else:
            print("❌ 服务启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 运行错误: {str(e)}")
        return False

if __name__ == "__main__":
    main()
