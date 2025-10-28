#!/usr/bin/env python3
"""
EdgeTTS真人直播语音测试案例
完整的测试流程和示例
"""

import random
import logging
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 导入规则加载器
import sys
sys.path.append('/Volumes/M2/TT_Live_AI_TTS/audio_pipeline')
from rules_loader import get_rules_loader

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveSpeechTestCase:
    """真人直播语音测试案例"""
    
    def __init__(self):
        self.rules = get_rules_loader()
        self.logger = logging.getLogger(__name__)
        
        # 测试案例配置
        self.test_cases = {
            "case_1": {
                "name": "游戏直播测试",
                "description": "模拟游戏直播场景，语速快、音调高、背景音丰富",
                "scenario": "gaming",
                "expected_tempo": (1.05, 1.15),
                "expected_pitch": (0.1, 0.3),
                "expected_background_prob": 0.9,
                "expected_event_prob": 0.4
            },
            "case_2": {
                "name": "聊天直播测试",
                "description": "模拟日常聊天直播，语速正常、音调稳定",
                "scenario": "chatting",
                "expected_tempo": (0.95, 1.05),
                "expected_pitch": (-0.1, 0.1),
                "expected_background_prob": 0.7,
                "expected_event_prob": 0.2
            },
            "case_3": {
                "name": "教学直播测试",
                "description": "模拟教学直播，语速稍慢、音调较低、环境音较少",
                "scenario": "teaching",
                "expected_tempo": (0.9, 1.0),
                "expected_pitch": (-0.2, 0.0),
                "expected_background_prob": 0.5,
                "expected_event_prob": 0.15
            },
            "case_4": {
                "name": "娱乐直播测试",
                "description": "模拟娱乐直播，语速适中、音调略高、环境音丰富",
                "scenario": "entertainment",
                "expected_tempo": (1.0, 1.1),
                "expected_pitch": (0.0, 0.2),
                "expected_background_prob": 0.8,
                "expected_event_prob": 0.3
            },
            "case_5": {
                "name": "新闻直播测试",
                "description": "模拟新闻直播，语速稳定、音调中性、环境音最少",
                "scenario": "news",
                "expected_tempo": (0.95, 1.05),
                "expected_pitch": (-0.1, 0.1),
                "expected_background_prob": 0.3,
                "expected_event_prob": 0.1
            }
        }
    
    def run_single_test_case(self, case_id: str, input_file: str) -> Dict[str, Any]:
        """运行单个测试案例"""
        if case_id not in self.test_cases:
            self.logger.error(f"❌ 未知测试案例: {case_id}")
            return None
        
        case_config = self.test_cases[case_id]
        self.logger.info(f"🧪 运行测试案例: {case_config['name']}")
        self.logger.info(f"📝 案例描述: {case_config['description']}")
        
        # 生成测试参数
        test_params = self._generate_test_params(case_config)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%H%M%S")
        base_name = Path(input_file).stem
        output_file = f"{base_name}_{case_id}_{timestamp}.m4a"
        
        # 构建FFmpeg命令
        cmd = self._build_test_command(input_file, output_file, test_params)
        
        # 执行命令
        start_time = datetime.now()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                self.logger.info(f"✅ 测试案例 {case_id} 成功: {output_file}")
                self.logger.info(f"⏱️ 处理时间: {processing_time:.2f}秒")
                
                return {
                    'case_id': case_id,
                    'case_name': case_config['name'],
                    'output_file': output_file,
                    'params': test_params,
                    'processing_time': processing_time,
                    'success': True,
                    'file_size': Path(output_file).stat().st_size if Path(output_file).exists() else 0
                }
            else:
                self.logger.error(f"❌ 测试案例 {case_id} 失败: {result.stderr}")
                return {
                    'case_id': case_id,
                    'case_name': case_config['name'],
                    'success': False,
                    'error': result.stderr
                }
        except Exception as e:
            self.logger.error(f"❌ 测试案例 {case_id} 异常: {e}")
            return {
                'case_id': case_id,
                'case_name': case_config['name'],
                'success': False,
                'error': str(e)
            }
    
    def _generate_test_params(self, case_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试参数"""
        params = {}
        
        # 语速和音高
        params['tempo'] = random.uniform(*case_config['expected_tempo'])
        params['pitch_semitones'] = random.uniform(*case_config['expected_pitch'])
        
        # 背景音效
        if random.random() < case_config['expected_background_prob']:
            environments = ['room_tone', 'living_room', 'office', 'cafe']
            env = random.choice(environments)
            params['background_sound'] = {
                'file': f"{env}.wav",
                'volume': random.uniform(0.06, 0.18),
                'start_offset': random.uniform(0, 30),
                'looped': True
            }
        else:
            params['background_sound'] = None
        
        # 事件音效
        params['events'] = []
        if random.random() < case_config['expected_event_prob']:
            event_types = ['keyboard', 'water_pour', 'chair_creak', 'paper_rustle']
            num_events = random.randint(1, 2)
            
            for _ in range(num_events):
                event_type = random.choice(event_types)
                params['events'].append({
                    'file': f"{event_type}.wav",
                    'volume': random.uniform(0.08, 0.20),
                    'trigger_time': random.uniform(3, 27),
                    'duration': random.uniform(1.0, 3.0)
                })
        
        # 音频增强参数
        params['compressor'] = {
            'threshold': -20,
            'ratio': 2.5,
            'attack': 15,
            'release': 150,
            'makeup': 2
        }
        
        params['equalizer'] = {
            'bands': [
                {'frequency': 250, 'gain_range': (1.1, 1.6), 'width': 100},
                {'frequency': 3000, 'gain_range': (1.3, 1.9), 'width': 600}
            ]
        }
        
        params['highpass_frequency'] = 60
        params['noise_amplitude'] = random.uniform(0.005, 0.012)
        
        return params
    
    def _build_test_command(self, input_file: str, output_file: str, params: Dict[str, Any]) -> List[str]:
        """构建测试FFmpeg命令"""
        cmd = ['ffmpeg', '-y', '-i', input_file]
        
        # 构建滤镜链
        filters = []
        
        # 1. 采样率转换
        filters.append('aresample=48000')
        
        # 2. 语速和音高调整
        if params['tempo'] != 1.0 or params['pitch_semitones'] != 0.0:
            pitch_ratio = 2 ** (params['pitch_semitones'] / 12)
            filters.append(f"rubberband=tempo={params['tempo']}:pitch={pitch_ratio}:formant=preserved")
        
        # 3. 音频增强
        compressor = params['compressor']
        filters.append(f"acompressor=threshold={compressor['threshold']}dB:ratio={compressor['ratio']}:attack={compressor['attack']}:release={compressor['release']}:makeup={compressor['makeup']}")
        
        # EQ调整
        for band in params['equalizer']['bands']:
            gain = random.uniform(*band['gain_range'])
            filters.append(f"equalizer=f={band['frequency']}:width_type=h:width={band['width']}:g={gain}")
        
        # 高通滤波器
        filters.append(f"highpass=f={params['highpass_frequency']}")
        
        # 4. 响度归一化
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        # 应用滤镜
        if filters:
            cmd.extend(['-af', ','.join(filters)])
        
        # 5. 输出编码
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '48000', '-ac', '2'])
        cmd.append(output_file)
        
        return cmd
    
    def run_all_test_cases(self, input_file: str) -> Dict[str, Any]:
        """运行所有测试案例"""
        self.logger.info("🧪 运行所有测试案例")
        self.logger.info("=" * 60)
        
        results = {}
        total_start_time = datetime.now()
        
        for case_id in self.test_cases.keys():
            self.logger.info(f"\n🎯 处理测试案例: {case_id}")
            result = self.run_single_test_case(case_id, input_file)
            results[case_id] = result
        
        total_end_time = datetime.now()
        total_time = (total_end_time - total_start_time).total_seconds()
        
        # 生成测试报告
        self._generate_test_report(results, total_time)
        
        return results
    
    def _generate_test_report(self, results: Dict[str, Any], total_time: float):
        """生成测试报告"""
        self.logger.info("\n📊 测试报告")
        self.logger.info("=" * 60)
        
        successful_cases = 0
        failed_cases = 0
        total_file_size = 0
        
        for case_id, result in results.items():
            if result and result.get('success'):
                successful_cases += 1
                file_size = result.get('file_size', 0)
                total_file_size += file_size
                self.logger.info(f"✅ {case_id}: {result['case_name']} - {result['output_file']} ({file_size/1024:.0f}KB)")
            else:
                failed_cases += 1
                self.logger.info(f"❌ {case_id}: {result['case_name'] if result else 'Unknown'} - 失败")
        
        self.logger.info(f"\n📈 测试统计:")
        self.logger.info(f"  总测试案例: {len(results)}")
        self.logger.info(f"  成功案例: {successful_cases}")
        self.logger.info(f"  失败案例: {failed_cases}")
        self.logger.info(f"  成功率: {successful_cases/len(results)*100:.1f}%")
        self.logger.info(f"  总处理时间: {total_time:.2f}秒")
        self.logger.info(f"  总文件大小: {total_file_size/1024:.0f}KB")
        
        # 保存测试报告到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_summary': {
                    'total_cases': len(results),
                    'successful_cases': successful_cases,
                    'failed_cases': failed_cases,
                    'success_rate': successful_cases/len(results)*100,
                    'total_time': total_time,
                    'total_file_size': total_file_size
                },
                'test_results': results
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 测试报告已保存: {report_file}")
    
    def create_comparison_audio(self, input_file: str) -> str:
        """创建对比音频"""
        self.logger.info("🔄 创建对比音频...")
        
        timestamp = datetime.now().strftime("%H%M%S")
        base_name = Path(input_file).stem
        comparison_file = f"{base_name}_comparison_{timestamp}.m4a"
        
        # 创建对比音频（原始 + 轻微处理）
        cmd = [
            'ffmpeg', '-y', '-i', input_file,
            '-af', 'aresample=48000,rubberband=tempo=1.02:pitch=1.05:formant=preserved,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=150:makeup=2,equalizer=f=250:width_type=h:width=100:g=1.3,equalizer=f=3000:width_type=h:width=600:g=1.5,highpass=f=60,loudnorm=I=-16:TP=-1.5:LRA=11',
            '-c:a', 'aac', '-b:a', '192k',
            '-ar', '48000', '-ac', '2',
            comparison_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"✅ 对比音频创建成功: {comparison_file}")
                return comparison_file
            else:
                self.logger.error(f"❌ 对比音频创建失败: {result.stderr}")
                return None
        except Exception as e:
            self.logger.error(f"❌ 对比音频创建失败: {e}")
            return None

def main():
    """主函数"""
    logger.info("🧪 EdgeTTS真人直播语音测试案例")
    logger.info("=" * 60)
    
    # 查找测试音频文件
    test_audio = '/Volumes/M2/TT_Live_AI_TTS/audio_pipeline/audio_pipeline/input_raw/test_1.wav'
    
    if not Path(test_audio).exists():
        logger.error(f"❌ 测试音频文件不存在: {test_audio}")
        return
    
    logger.info(f"🎵 使用测试音频: {test_audio}")
    
    # 创建测试案例
    test_case = LiveSpeechTestCase()
    
    # 显示测试案例信息
    logger.info("\n📋 测试案例列表:")
    for case_id, case_config in test_case.test_cases.items():
        logger.info(f"  {case_id}: {case_config['name']}")
        logger.info(f"    {case_config['description']}")
    
    # 运行所有测试案例
    results = test_case.run_all_test_cases(test_audio)
    
    # 创建对比音频
    comparison_file = test_case.create_comparison_audio(test_audio)
    
    # 显示最终结果
    logger.info("\n🎉 测试完成!")
    logger.info("=" * 60)
    logger.info("📁 生成的音频文件:")
    
    # 列出所有生成的音频文件
    current_dir = Path.cwd()
    audio_files = list(current_dir.glob("test_1_*.m4a"))
    audio_files.sort(key=lambda x: x.stat().st_mtime)
    
    for audio_file in audio_files:
        file_size = audio_file.stat().st_size / 1024
        logger.info(f"  {audio_file.name} ({file_size:.0f}KB)")
    
    logger.info("\n🎧 试听建议:")
    logger.info("  1. 先试听原始音频了解基础效果")
    logger.info("  2. 按场景顺序试听：news → teaching → chatting → entertainment → gaming")
    logger.info("  3. 对比不同场景的语速、音高、背景音差异")
    logger.info("  4. 根据试听效果调整规则参数")

if __name__ == '__main__':
    main()
