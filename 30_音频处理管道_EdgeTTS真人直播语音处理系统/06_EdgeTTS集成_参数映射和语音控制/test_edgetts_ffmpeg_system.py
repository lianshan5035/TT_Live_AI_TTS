#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeTTS到FFmpeg处理系统测试脚本
验证完整的EdgeTTS生成音频后使用FFmpeg进行真人直播语音处理的流程
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from edgetts_ffmpeg_processor import EdgeTTSFFmpegProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EdgeTTSFFmpegTester:
    """EdgeTTS到FFmpeg处理系统测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.processor = EdgeTTSFFmpegProcessor()
        self.test_results = []
        
    async def test_single_emotion(self, text: str, voice: str, emotion: str) -> dict:
        """测试单个情绪处理"""
        logger.info(f"🧪 测试情绪: {emotion}")
        
        try:
            # 生成输出文件名
            timestamp = int(asyncio.get_event_loop().time())
            output_file = f"test_{emotion}_{timestamp}.m4a"
            
            # 处理音频
            start_time = asyncio.get_event_loop().time()
            success = await self.processor.process_audio(text, voice, emotion, output_file)
            end_time = asyncio.get_event_loop().time()
            
            # 检查输出文件
            file_exists = os.path.exists(output_file)
            file_size = os.path.getsize(output_file) if file_exists else 0
            
            result = {
                "emotion": emotion,
                "voice": voice,
                "success": success,
                "output_file": output_file,
                "file_exists": file_exists,
                "file_size": file_size,
                "processing_time": end_time - start_time,
                "error": None
            }
            
            if success and file_exists:
                logger.info(f"✅ {emotion} 测试成功: {output_file} ({file_size} bytes)")
            else:
                logger.error(f"❌ {emotion} 测试失败")
                result["error"] = "处理失败或文件不存在"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {emotion} 测试异常: {e}")
            return {
                "emotion": emotion,
                "voice": voice,
                "success": False,
                "output_file": None,
                "file_exists": False,
                "file_size": 0,
                "processing_time": 0,
                "error": str(e)
            }
    
    async def test_all_emotions(self) -> list:
        """测试所有情绪类型"""
        logger.info("🎭 开始测试所有情绪类型")
        
        # 测试数据
        test_cases = [
            {
                "text": "Hello, this is urgent content! Limited time offer available now!",
                "voice": "en-US-JennyNeural",
                "emotion": "Urgent"
            },
            {
                "text": "This is calm and soothing content. Take a deep breath and relax.",
                "voice": "en-US-AvaNeural",
                "emotion": "Calm"
            },
            {
                "text": "Welcome to our warm and friendly community. We're here to help you.",
                "voice": "en-US-NancyNeural",
                "emotion": "Warm"
            },
            {
                "text": "Exciting news! Our new product is launching today! Don't miss out!",
                "voice": "en-US-AriaNeural",
                "emotion": "Excited"
            },
            {
                "text": "This is professional content. Let me explain the technical details.",
                "voice": "en-US-BrandonNeural",
                "emotion": "Professional"
            }
        ]
        
        results = []
        for test_case in test_cases:
            result = await self.test_single_emotion(
                test_case["text"],
                test_case["voice"],
                test_case["emotion"]
            )
            results.append(result)
            
            # 添加延迟避免API限制
            await asyncio.sleep(3)
        
        return results
    
    async def test_batch_processing(self) -> dict:
        """测试批量处理"""
        logger.info("📦 开始测试批量处理")
        
        # 批量测试数据
        texts = [
            "This is the first batch test audio.",
            "This is the second batch test audio.",
            "This is the third batch test audio."
        ]
        voices = [
            "en-US-JennyNeural",
            "en-US-AvaNeural", 
            "en-US-NancyNeural"
        ]
        emotions = [
            "Urgent",
            "Calm",
            "Warm"
        ]
        
        try:
            start_time = asyncio.get_event_loop().time()
            batch_files = await self.processor.batch_process(
                texts, voices, emotions, "batch_test_output"
            )
            end_time = asyncio.get_event_loop().time()
            
            result = {
                "success": True,
                "total_files": len(texts),
                "successful_files": len(batch_files),
                "success_rate": len(batch_files) / len(texts) * 100,
                "processing_time": end_time - start_time,
                "output_files": batch_files,
                "error": None
            }
            
            logger.info(f"✅ 批量处理完成: {len(batch_files)}/{len(texts)} 成功")
            return result
            
        except Exception as e:
            logger.error(f"❌ 批量处理测试异常: {e}")
            return {
                "success": False,
                "total_files": len(texts),
                "successful_files": 0,
                "success_rate": 0,
                "processing_time": 0,
                "output_files": [],
                "error": str(e)
            }
    
    def test_parameter_conversion(self) -> dict:
        """测试参数转换功能"""
        logger.info("🔄 测试参数转换功能")
        
        test_cases = [
            {"python_rate": 0.8, "expected_edge_tts": "-20%"},
            {"python_rate": 1.0, "expected_edge_tts": "+0%"},
            {"python_rate": 1.2, "expected_edge_tts": "+20%"},
            {"python_pitch": 0.8, "expected_edge_tts": "-10Hz"},
            {"python_pitch": 1.0, "expected_edge_tts": "+0Hz"},
            {"python_pitch": 1.2, "expected_edge_tts": "+10Hz"},
            {"python_volume": 0.8, "expected_edge_tts": "-10%"},
            {"python_volume": 1.0, "expected_edge_tts": "+0%"},
            {"python_volume": 1.2, "expected_edge_tts": "+10%"}
        ]
        
        results = []
        for case in test_cases:
            if "python_rate" in case:
                result = self.processor.python_to_edge_tts_rate(case["python_rate"])
                param_type = "rate"
            elif "python_pitch" in case:
                result = self.processor.python_to_edge_tts_pitch(case["python_pitch"])
                param_type = "pitch"
            elif "python_volume" in case:
                result = self.processor.python_to_edge_tts_volume(case["python_volume"])
                param_type = "volume"
            
            expected = case[f"expected_edge_tts"]
            success = result == expected
            
            test_result = {
                "parameter_type": param_type,
                "input": case[f"python_{param_type}"],
                "expected": expected,
                "actual": result,
                "success": success
            }
            
            results.append(test_result)
            
            if success:
                logger.info(f"✅ {param_type} 转换正确: {case[f'python_{param_type}']} → {result}")
            else:
                logger.error(f"❌ {param_type} 转换错误: {case[f'python_{param_type}']} → {result} (期望: {expected})")
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "total_tests": len(results),
            "successful_tests": success_count,
            "success_rate": success_count / len(results) * 100,
            "results": results
        }
    
    def test_emotion_parameter_generation(self) -> dict:
        """测试情绪参数生成"""
        logger.info("🎭 测试情绪参数生成")
        
        emotions = ["Urgent", "Calm", "Warm", "Excited", "Professional"]
        results = []
        
        for emotion in emotions:
            try:
                params = self.processor.generate_emotion_parameters(emotion)
                
                # 验证参数范围
                edge_tts_params = params["edge_tts"]
                ffmpeg_params = params["ffmpeg"]
                
                # 检查EdgeTTS参数
                rate_valid = 0.5 <= edge_tts_params["rate"] <= 2.0
                pitch_valid = 0.0 <= edge_tts_params["pitch"] <= 2.0
                volume_valid = 0.5 <= edge_tts_params["volume"] <= 1.5
                
                # 检查FFmpeg参数
                tempo_valid = 0.5 <= ffmpeg_params["tempo"] <= 2.0
                pitch_adj_valid = 0.5 <= ffmpeg_params["pitch"] <= 2.0
                
                all_valid = all([rate_valid, pitch_valid, volume_valid, tempo_valid, pitch_adj_valid])
                
                result = {
                    "emotion": emotion,
                    "success": all_valid,
                    "edge_tts_params": edge_tts_params,
                    "ffmpeg_params": ffmpeg_params,
                    "validation": {
                        "rate_valid": rate_valid,
                        "pitch_valid": pitch_valid,
                        "volume_valid": volume_valid,
                        "tempo_valid": tempo_valid,
                        "pitch_adj_valid": pitch_adj_valid
                    }
                }
                
                results.append(result)
                
                if all_valid:
                    logger.info(f"✅ {emotion} 参数生成正确")
                else:
                    logger.error(f"❌ {emotion} 参数生成错误")
                    
            except Exception as e:
                logger.error(f"❌ {emotion} 参数生成异常: {e}")
                results.append({
                    "emotion": emotion,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        return {
            "total_emotions": len(emotions),
            "successful_emotions": success_count,
            "success_rate": success_count / len(emotions) * 100,
            "results": results
        }
    
    def generate_test_report(self, emotion_results: list, batch_result: dict, 
                           conversion_result: dict, param_result: dict) -> dict:
        """生成测试报告"""
        logger.info("📊 生成测试报告")
        
        # 统计情绪测试结果
        emotion_success_count = sum(1 for r in emotion_results if r["success"])
        emotion_total_size = sum(r["file_size"] for r in emotion_results if r["success"])
        emotion_avg_time = sum(r["processing_time"] for r in emotion_results) / len(emotion_results)
        
        # 生成报告
        report = {
            "test_info": {
                "timestamp": int(asyncio.get_event_loop().time()),
                "test_version": "1.0.0",
                "description": "EdgeTTS到FFmpeg处理系统完整测试"
            },
            "emotion_tests": {
                "total_tests": len(emotion_results),
                "successful_tests": emotion_success_count,
                "success_rate": emotion_success_count / len(emotion_results) * 100,
                "total_output_size": emotion_total_size,
                "average_processing_time": emotion_avg_time,
                "results": emotion_results
            },
            "batch_processing": batch_result,
            "parameter_conversion": conversion_result,
            "emotion_parameters": param_result,
            "summary": {
                "overall_success": emotion_success_count > 0 and batch_result["success"],
                "total_tests": len(emotion_results) + 1,
                "successful_tests": emotion_success_count + (1 if batch_result["success"] else 0),
                "overall_success_rate": (emotion_success_count + (1 if batch_result["success"] else 0)) / (len(emotion_results) + 1) * 100
            }
        }
        
        return report
    
    async def run_complete_test(self) -> dict:
        """运行完整测试"""
        logger.info("🚀 开始运行EdgeTTS到FFmpeg处理系统完整测试")
        
        try:
            # 1. 测试参数转换
            logger.info("=" * 60)
            logger.info("1️⃣ 测试参数转换功能")
            conversion_result = self.test_parameter_conversion()
            
            # 2. 测试情绪参数生成
            logger.info("=" * 60)
            logger.info("2️⃣ 测试情绪参数生成")
            param_result = self.test_emotion_parameter_generation()
            
            # 3. 测试所有情绪处理
            logger.info("=" * 60)
            logger.info("3️⃣ 测试所有情绪处理")
            emotion_results = await self.test_all_emotions()
            
            # 4. 测试批量处理
            logger.info("=" * 60)
            logger.info("4️⃣ 测试批量处理")
            batch_result = await self.test_batch_processing()
            
            # 5. 生成测试报告
            logger.info("=" * 60)
            logger.info("5️⃣ 生成测试报告")
            report = self.generate_test_report(emotion_results, batch_result, 
                                             conversion_result, param_result)
            
            # 保存测试报告
            report_file = f"edgetts_ffmpeg_test_report_{int(asyncio.get_event_loop().time())}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📄 测试报告已保存: {report_file}")
            
            # 输出测试总结
            logger.info("=" * 60)
            logger.info("🎉 测试完成总结")
            logger.info(f"总体成功率: {report['summary']['overall_success_rate']:.1f}%")
            logger.info(f"情绪测试: {emotion_results.count(True)}/{len(emotion_results)} 成功")
            logger.info(f"批量处理: {'成功' if batch_result['success'] else '失败'}")
            logger.info(f"参数转换: {conversion_result['success_rate']:.1f}% 成功")
            logger.info(f"参数生成: {param_result['success_rate']:.1f}% 成功")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 完整测试异常: {e}")
            return {"error": str(e)}

async def main():
    """主函数"""
    logger.info("🎯 EdgeTTS到FFmpeg处理系统测试启动")
    
    # 创建测试器
    tester = EdgeTTSFFmpegTester()
    
    # 运行完整测试
    report = await tester.run_complete_test()
    
    if "error" in report:
        logger.error(f"❌ 测试失败: {report['error']}")
        return False
    else:
        logger.info("✅ 所有测试完成")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
