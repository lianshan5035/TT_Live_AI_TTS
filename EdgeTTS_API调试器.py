#!/usr/bin/env python3
"""
EdgeTTS API调试脚本
测试4个API服务的独立调用，确保不相互影响
"""
import requests
import json
import time
import threading
from datetime import datetime

class APIDebugger:
    def __init__(self):
        self.apis = [
            {"name": "API-5001", "url": "http://127.0.0.1:5001/generate"},
            {"name": "API-5002", "url": "http://127.0.0.1:5002/generate"},
            {"name": "API-5003", "url": "http://127.0.0.1:5003/generate"},
            {"name": "API-5004", "url": "http://127.0.0.1:5004/generate"}
        ]
        self.results = {}
        self.lock = threading.Lock()
    
    def test_single_api(self, api_info, test_text, thread_id):
        """测试单个API"""
        api_name = api_info["name"]
        api_url = api_info["url"]
        
        print(f"🧵 线程{thread_id}: 开始测试 {api_name}")
        
        try:
            # 准备测试数据
            data = {
                "product_name": f"调试测试_{api_name}",
                "scripts": [{
                    "text": test_text,
                    "voice": "en-US-JennyNeural",
                    "rate": "+0%",
                    "pitch": "+0Hz",
                    "volume": "+0%",
                    "emotion": "Friendly"
                }]
            }
            
            # 发送请求
            start_time = time.time()
            response = requests.post(api_url, json=data, timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 分析响应
            result = {
                "api_name": api_name,
                "status_code": response.status_code,
                "response_time": response_time,
                "content_length": len(response.content),
                "success": False,
                "error": None
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if 'sample_audios' in json_response and json_response['sample_audios']:
                        audio_path = json_response['sample_audios'][0]
                        result["audio_path"] = audio_path
                        result["success"] = True
                        print(f"✅ 线程{thread_id}: {api_name} 成功 - 响应时间: {response_time:.2f}s")
                    else:
                        result["error"] = "No sample_audios in response"
                        print(f"❌ 线程{thread_id}: {api_name} 失败 - 无音频文件")
                except json.JSONDecodeError:
                    result["error"] = "Invalid JSON response"
                    print(f"❌ 线程{thread_id}: {api_name} 失败 - JSON解析错误")
            else:
                result["error"] = f"HTTP {response.status_code}"
                print(f"❌ 线程{thread_id}: {api_name} 失败 - HTTP {response.status_code}")
            
            # 保存结果
            with self.lock:
                self.results[api_name] = result
                
        except Exception as e:
            with self.lock:
                self.results[api_name] = {
                    "api_name": api_name,
                    "success": False,
                    "error": str(e)
                }
            print(f"❌ 线程{thread_id}: {api_name} 异常 - {e}")
    
    def test_concurrent_apis(self):
        """并发测试所有API"""
        print("🔧 开始并发测试4个API服务")
        print("=" * 60)
        
        test_text = "Hello, this is a test for API debugging. We are testing concurrent calls."
        
        # 创建线程
        threads = []
        for i, api_info in enumerate(self.apis):
            thread = threading.Thread(
                target=self.test_single_api, 
                args=(api_info, test_text, i+1)
            )
            threads.append(thread)
        
        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("=" * 60)
        print(f"🎉 并发测试完成 - 总耗时: {total_time:.2f}s")
        
        # 显示结果统计
        self.show_results()
    
    def test_sequential_apis(self):
        """顺序测试所有API"""
        print("🔧 开始顺序测试4个API服务")
        print("=" * 60)
        
        test_text = "Hello, this is a sequential test for API debugging."
        
        start_time = time.time()
        
        for i, api_info in enumerate(self.apis):
            print(f"📡 测试 {i+1}/4: {api_info['name']}")
            self.test_single_api(api_info, test_text, i+1)
            time.sleep(1)  # 间隔1秒
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("=" * 60)
        print(f"🎉 顺序测试完成 - 总耗时: {total_time:.2f}s")
        
        # 显示结果统计
        self.show_results()
    
    def show_results(self):
        """显示测试结果"""
        print("\n📊 测试结果统计:")
        print("-" * 60)
        
        success_count = 0
        total_count = len(self.results)
        
        for api_name, result in self.results.items():
            status = "✅ 成功" if result.get("success", False) else "❌ 失败"
            response_time = result.get("response_time", 0)
            error = result.get("error", "")
            
            print(f"{api_name}: {status}")
            if result.get("success"):
                print(f"  └─ 响应时间: {response_time:.2f}s")
                print(f"  └─ 音频路径: {result.get('audio_path', 'N/A')}")
                success_count += 1
            else:
                print(f"  └─ 错误: {error}")
            print()
        
        print(f"📈 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        # 检查是否有相互影响
        if success_count == total_count:
            print("🎯 所有API服务独立运行正常，无相互影响")
        elif success_count > 0:
            print("⚠️ 部分API服务有问题，可能存在相互影响")
        else:
            print("❌ 所有API服务都失败，需要检查配置")
    
    def test_api_isolation(self):
        """测试API隔离性"""
        print("🔬 测试API服务隔离性")
        print("=" * 60)
        
        # 测试1: 并发调用
        print("测试1: 并发调用测试")
        self.test_concurrent_apis()
        
        print("\n" + "="*60 + "\n")
        
        # 测试2: 顺序调用
        print("测试2: 顺序调用测试")
        self.results = {}  # 重置结果
        self.test_sequential_apis()
        
        print("\n" + "="*60 + "\n")
        
        # 测试3: 压力测试
        print("测试3: 压力测试")
        self.stress_test()
    
    def stress_test(self):
        """压力测试"""
        print("💪 开始压力测试 - 每个API连续调用5次")
        
        test_text = "This is a stress test for API isolation."
        stress_results = {}
        
        for api_info in self.apis:
            api_name = api_info["name"]
            print(f"\n🔥 压力测试 {api_name}")
            
            success_count = 0
            total_time = 0
            
            for i in range(5):
                try:
                    data = {
                        "product_name": f"压力测试_{api_name}_{i+1}",
                        "scripts": [{
                            "text": f"{test_text} Call {i+1}",
                            "voice": "en-US-JennyNeural",
                            "rate": "+0%",
                            "pitch": "+0Hz",
                            "volume": "+0%",
                            "emotion": "Friendly"
                        }]
                    }
                    
                    start_time = time.time()
                    response = requests.post(api_info["url"], json=data, timeout=30)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        success_count += 1
                        total_time += (end_time - start_time)
                        print(f"  ✅ 调用 {i+1}/5 成功")
                    else:
                        print(f"  ❌ 调用 {i+1}/5 失败 - HTTP {response.status_code}")
                    
                    time.sleep(0.5)  # 短暂间隔
                    
                except Exception as e:
                    print(f"  ❌ 调用 {i+1}/5 异常 - {e}")
            
            stress_results[api_name] = {
                "success_rate": success_count / 5 * 100,
                "avg_response_time": total_time / success_count if success_count > 0 else 0
            }
            
            print(f"  📊 成功率: {success_count}/5 ({success_count/5*100:.1f}%)")
            if success_count > 0:
                print(f"  📊 平均响应时间: {total_time/success_count:.2f}s")
        
        print("\n🎯 压力测试完成")
        print("-" * 40)
        for api_name, result in stress_results.items():
            print(f"{api_name}: 成功率 {result['success_rate']:.1f}%, 平均响应 {result['avg_response_time']:.2f}s")

def main():
    """主函数"""
    print("🔧 EdgeTTS API调试器")
    print("=" * 60)
    print("🎯 目标: 确保4个API服务独立运行，不相互影响")
    print("=" * 60)
    
    debugger = APIDebugger()
    debugger.test_api_isolation()
    
    print("\n🎉 API调试完成!")
    print("💡 如果所有测试都通过，说明API服务配置正确，可以安全使用多线程处理")

if __name__ == "__main__":
    main()
