#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI A3标准测试脚本
测试A3标准系统的各项功能
"""

import requests
import json
import time
import os
from pathlib import Path

class A3Tester:
    """A3标准测试器"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.tts_url = "http://localhost:5001"
        
    def test_system_status(self):
        """测试系统状态"""
        print("🔍 测试系统状态...")
        
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 系统状态: {data.get('status', 'unknown')}")
                print(f"✅ TTS服务: {data.get('tts_service', {}).get('status', 'unknown')}")
                return True
            else:
                print(f"❌ 系统状态检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 系统状态检查异常: {str(e)}")
            return False
    
    def test_a3_config(self):
        """测试A3配置"""
        print("🔍 测试A3配置...")
        
        try:
            response = requests.get(f"{self.base_url}/api/a3-config", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    config = data.get('data', {})
                    print(f"✅ 情绪配置: {len(config.get('emotion_config', {}))} 种")
                    print(f"✅ 语音库: {len(config.get('voice_library', {}).get('Female', [])) + len(config.get('voice_library', {}).get('Male', []))} 个")
                    print(f"✅ 修辞库: {len(config.get('rhetoric_library', {}))} 类")
                    print(f"✅ 开场库: {len(config.get('opening_library', {}))} 种")
                    return True
                else:
                    print(f"❌ A3配置获取失败: {data.get('message', 'unknown')}")
                    return False
            else:
                print(f"❌ A3配置检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ A3配置检查异常: {str(e)}")
            return False
    
    def test_tts_service(self):
        """测试TTS服务"""
        print("🔍 测试TTS服务...")
        
        try:
            response = requests.get(f"{self.tts_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ TTS服务健康检查通过")
                return True
            else:
                print(f"❌ TTS服务健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ TTS服务检查异常: {str(e)}")
            return False
    
    def test_a3_batch_generation(self):
        """测试A3批次生成"""
        print("🔍 测试A3批次生成...")
        
        try:
            data = {
                "product_name": "Test Product",
                "batch_id": 1,
                "batch_size": 5  # 小批次测试
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate-a3-batch",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    scripts = result.get('scripts', [])
                    print(f"✅ A3批次生成成功: {len(scripts)} 条脚本")
                    
                    # 检查脚本结构
                    if scripts:
                        script = scripts[0]
                        required_fields = ['script_id', 'english_script', 'chinese_translation', 'emotion', 'voice', 'a3_params']
                        missing_fields = [field for field in required_fields if field not in script]
                        if not missing_fields:
                            print("✅ 脚本结构完整")
                            return True
                        else:
                            print(f"❌ 脚本缺少字段: {missing_fields}")
                            return False
                    else:
                        print("❌ 没有生成脚本")
                        return False
                else:
                    print(f"❌ A3批次生成失败: {result.get('error', 'unknown')}")
                    return False
            else:
                print(f"❌ A3批次生成请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ A3批次生成异常: {str(e)}")
            return False
    
    def test_file_upload(self):
        """测试文件上传"""
        print("🔍 测试文件上传...")
        
        try:
            # 创建测试Excel文件
            test_file_path = self.create_test_excel()
            
            with open(test_file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    parsed_data = result.get('parsed_data', {})
                    if parsed_data.get('success'):
                        print(f"✅ 文件上传成功: {result.get('filename')}")
                        print(f"✅ 解析成功: {parsed_data.get('total_scripts')} 条脚本")
                        return True
                    else:
                        print(f"❌ 文件解析失败: {parsed_data.get('error', 'unknown')}")
                        return False
                else:
                    print(f"❌ 文件上传失败: {result.get('error', 'unknown')}")
                    return False
            else:
                print(f"❌ 文件上传请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 文件上传异常: {str(e)}")
            return False
        finally:
            # 清理测试文件
            if 'test_file_path' in locals() and os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    def create_test_excel(self):
        """创建测试Excel文件"""
        import pandas as pd
        
        test_data = {
            '产品名称': ['Test Product', 'Test Product', 'Test Product'],
            '文案内容': [
                'This is a test script for A3 standard validation.',
                'Another test script to verify the system functionality.',
                'Third test script to ensure proper processing.'
            ],
            '中文翻译': [
                '这是用于A3标准验证的测试脚本。',
                '另一个用于验证系统功能的测试脚本。',
                '第三个用于确保正确处理过程的测试脚本。'
            ],
            '情感': ['Friendly', 'Confident', 'Calm'],
            '语音模型': ['en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-DavisNeural'],
            '产品类型': ['美妆个护', '美妆个护', '美妆个护']
        }
        
        df = pd.DataFrame(test_data)
        test_file_path = 'test_a3_input.xlsx'
        df.to_excel(test_file_path, index=False)
        
        return test_file_path
    
    def test_logs(self):
        """测试日志功能"""
        print("🔍 测试日志功能...")
        
        try:
            response = requests.get(f"{self.base_url}/api/logs", timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    logs = result.get('data', {}).get('logs', [])
                    print(f"✅ 日志获取成功: {len(logs)} 条记录")
                    return True
                else:
                    print(f"❌ 日志获取失败: {result.get('message', 'unknown')}")
                    return False
            else:
                print(f"❌ 日志请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 日志检查异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始A3标准系统测试")
        print("=" * 50)
        
        tests = [
            ("系统状态", self.test_system_status),
            ("A3配置", self.test_a3_config),
            ("TTS服务", self.test_tts_service),
            ("A3批次生成", self.test_a3_batch_generation),
            ("文件上传", self.test_file_upload),
            ("日志功能", self.test_logs)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 测试: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 测试通过")
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🎯 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！A3标准系统运行正常")
            return True
        else:
            print("⚠️ 部分测试失败，请检查系统配置")
            return False

def main():
    """主函数"""
    tester = A3Tester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ A3标准系统测试完成，系统运行正常")
        print("🌐 访问 http://localhost:8000 使用A3标准控制中心")
    else:
        print("\n❌ A3标准系统测试失败，请检查系统状态")
    
    return success

if __name__ == "__main__":
    main()
