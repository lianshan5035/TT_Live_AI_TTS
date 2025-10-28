#!/usr/bin/env python3
"""
高级随机化音频处理脚本
实现同人不同场次的直播效果
"""

import os
import sys
import logging
import subprocess
import random
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedRandomAudioProcessor:
    """高级随机化音频处理器"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # 随机化参数配置
        self.random_config = {
            "tempo_range": (0.88, 1.12),  # ±12% 语速调整
            "pitch_range": (-0.4, 0.4),   # ±0.4 半音调整
            "formant_preserved": True,     # 保持formant
            "event_sound_probability": 0.15,  # 15% 概率添加事件音效
            "room_sound_probability": 0.8,    # 80% 概率添加房间音效
        }
        
        # 环境底噪库
        self.background_sounds = {
            "room_ambient": [
                {"file": "room_tone.wav", "volume_range": (0.08, 0.15), "description": "房间环境音"},
                {"file": "office_ambient.wav", "volume_range": (0.06, 0.12), "description": "办公室环境音"},
                {"file": "living_room.wav", "volume_range": (0.07, 0.14), "description": "客厅环境音"},
            ],
            "weather_sounds": [
                {"file": "rain_light.wav", "volume_range": (0.05, 0.10), "description": "小雨声"},
                {"file": "rain_heavy.wav", "volume_range": (0.08, 0.15), "description": "大雨声"},
                {"file": "wind.wav", "volume_range": (0.04, 0.08), "description": "风声"},
            ],
            "mechanical_sounds": [
                {"file": "fan.wav", "volume_range": (0.06, 0.12), "description": "风扇声"},
                {"file": "air_conditioner.wav", "volume_range": (0.05, 0.10), "description": "空调声"},
                {"file": "computer_hum.wav", "volume_range": (0.03, 0.07), "description": "电脑运行声"},
            ]
        }
        
        # 事件音效库
        self.event_sounds = [
            {"file": "keyboard_typing.wav", "volume_range": (0.15, 0.25), "description": "键盘打字声"},
            {"file": "water_pour.wav", "volume_range": (0.12, 0.20), "description": "倒水声"},
            {"file": "footsteps.wav", "volume_range": (0.10, 0.18), "description": "脚步声"},
            {"file": "chair_creak.wav", "volume_range": (0.08, 0.15), "description": "椅子吱嘎声"},
            {"file": "paper_rustle.wav", "volume_range": (0.06, 0.12), "description": "纸张摩擦声"},
            {"file": "mouse_click.wav", "volume_range": (0.05, 0.10), "description": "鼠标点击声"},
        ]
        
        # 声线模板
        self.voice_templates = {
            "calm": {
                "name": "平静声线",
                "tempo_modifier": (0.95, 1.05),
                "pitch_modifier": (-0.2, 0.1),
                "eq_250hz": (0.8, 1.2),
                "eq_3khz": (0.9, 1.1),
                "compressor_threshold": 0.1,
                "description": "适合平静内容的声线"
            },
            "excited": {
                "name": "兴奋声线",
                "tempo_modifier": (1.05, 1.15),
                "pitch_modifier": (0.1, 0.3),
                "eq_250hz": (0.7, 1.0),
                "eq_3khz": (1.1, 1.3),
                "compressor_threshold": 0.08,
                "description": "适合兴奋内容的声线"
            },
            "serious": {
                "name": "低沉声线",
                "tempo_modifier": (0.90, 1.00),
                "pitch_modifier": (-0.3, -0.1),
                "eq_250hz": (1.1, 1.4),
                "eq_3khz": (0.8, 1.0),
                "compressor_threshold": 0.12,
                "description": "适合严肃内容的声线"
            },
            "friendly": {
                "name": "友好声线",
                "tempo_modifier": (1.00, 1.10),
                "pitch_modifier": (0.0, 0.2),
                "eq_250hz": (0.9, 1.1),
                "eq_3khz": (1.0, 1.2),
                "compressor_threshold": 0.09,
                "description": "适合友好内容的声线"
            }
        }
        
        # 输出配置
        self.output_config = {
            "format": "m4a",
            "codec": "aac",
            "bitrate": "192k",
            "sample_rate": "44100",
            "channels": "2"
        }
    
    def generate_random_parameters(self, voice_template: str = None) -> Dict:
        """生成随机参数"""
        logger.info("生成随机参数...")
        
        # 选择声线模板
        if voice_template and voice_template in self.voice_templates:
            template = self.voice_templates[voice_template]
            logger.info(f"使用声线模板: {template['name']}")
        else:
            # 随机选择声线模板
            template_name = random.choice(list(self.voice_templates.keys()))
            template = self.voice_templates[template_name]
            logger.info(f"随机选择声线模板: {template['name']}")
        
        # 基础随机参数
        base_tempo = random.uniform(*self.random_config["tempo_range"])
        base_pitch = random.uniform(*self.random_config["pitch_range"])
        
        # 应用声线模板修饰
        tempo_modifier = random.uniform(*template["tempo_modifier"])
        pitch_modifier = random.uniform(*template["pitch_modifier"])
        
        final_tempo = base_tempo * tempo_modifier
        final_pitch = base_pitch + pitch_modifier
        
        # 限制在合理范围内
        final_tempo = max(0.7, min(1.3, final_tempo))
        final_pitch = max(-0.5, min(0.5, final_pitch))
        
        # 生成EQ参数
        eq_250hz = random.uniform(*template["eq_250hz"])
        eq_3khz = random.uniform(*template["eq_3khz"])
        
        # 生成压缩器参数
        compressor_threshold = template["compressor_threshold"]
        compressor_ratio = random.uniform(8, 12)
        
        # 选择背景音效
        background_sound = self._select_background_sound()
        
        # 选择事件音效
        event_sound = self._select_event_sound()
        
        params = {
            "tempo": final_tempo,
            "pitch": final_pitch,
            "formant_preserved": self.random_config["formant_preserved"],
            "eq_250hz": eq_250hz,
            "eq_3khz": eq_3khz,
            "compressor_threshold": compressor_threshold,
            "compressor_ratio": compressor_ratio,
            "background_sound": background_sound,
            "event_sound": event_sound,
            "voice_template": template["name"],
            "template_description": template["description"]
        }
        
        logger.info(f"生成参数: 语速={final_tempo:.3f}x, 音高={final_pitch:.3f}半音")
        logger.info(f"EQ: 250Hz={eq_250hz:.2f}, 3kHz={eq_3khz:.2f}")
        logger.info(f"背景音效: {background_sound['description'] if background_sound else '无'}")
        logger.info(f"事件音效: {event_sound['description'] if event_sound else '无'}")
        
        return params
    
    def _select_background_sound(self) -> Optional[Dict]:
        """选择背景音效"""
        if random.random() > self.random_config["room_sound_probability"]:
            return None
        
        # 随机选择音效类别
        sound_category = random.choice(list(self.background_sounds.keys()))
        sound_options = self.background_sounds[sound_category]
        
        # 随机选择具体音效
        selected_sound = random.choice(sound_options).copy()
        
        # 随机设置音量
        volume_range = selected_sound["volume_range"]
        selected_sound["volume"] = random.uniform(*volume_range)
        
        # 随机设置起点（0-30秒）
        selected_sound["start_time"] = random.uniform(0, 30)
        
        # 随机设置淡入淡出时间
        selected_sound["fade_in"] = random.uniform(0.5, 2.0)
        selected_sound["fade_out"] = random.uniform(0.5, 2.0)
        
        return selected_sound
    
    def _select_event_sound(self) -> Optional[Dict]:
        """选择事件音效"""
        if random.random() > self.random_config["event_sound_probability"]:
            return None
        
        # 随机选择事件音效
        selected_sound = random.choice(self.event_sounds).copy()
        
        # 随机设置音量
        volume_range = selected_sound["volume_range"]
        selected_sound["volume"] = random.uniform(*volume_range)
        
        # 随机设置触发时间点（音频长度的20%-80%之间）
        selected_sound["trigger_time"] = random.uniform(0.2, 0.8)
        
        # 随机设置持续时间
        selected_sound["duration"] = random.uniform(1.0, 4.0)
        
        return selected_sound
    
    def process_audio_with_random_params(self, input_file: str, params: Dict) -> Optional[str]:
        """使用随机参数处理音频"""
        logger.info(f"处理音频: {Path(input_file).name}")
        
        # 获取音频时长
        duration = self.processor.get_audio_duration(input_file)
        logger.info(f"音频时长: {duration:.2f} 秒")
        
        # 生成输出文件名
        input_path = Path(input_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"random_{params['voice_template']}_{timestamp}.m4a"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', input_file])
        
        # 添加背景音效输入
        input_count = 1
        if params['background_sound']:
            bg_sound_file = self.processor.background_sounds_dir / params['background_sound']['file']
            if bg_sound_file.exists():
                cmd.extend(['-i', str(bg_sound_file)])
                input_count += 1
        
        # 添加事件音效输入
        if params['event_sound']:
            event_sound_file = self.processor.background_sounds_dir / params['event_sound']['file']
            if event_sound_file.exists():
                cmd.extend(['-i', str(event_sound_file)])
                input_count += 1
        
        # 构建复杂的滤镜链
        filter_complex = self._build_advanced_filter_complex(input_file, params, input_count)
        cmd.extend(['-filter_complex', filter_complex])
        
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', self.output_config['codec']])
        cmd.extend(['-b:a', self.output_config['bitrate']])
        cmd.extend(['-ar', self.output_config['sample_rate']])
        cmd.extend(['-ac', self.output_config['channels']])
        cmd.extend(['-f', self.output_config['format']])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 随机化处理完成: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return output_file
        else:
            logger.error(f"✗ 随机化处理失败: {result.stderr}")
            return None
    
    def _build_advanced_filter_complex(self, input_file: str, params: Dict, input_count: int) -> str:
        """构建高级滤镜复合命令"""
        filter_parts = []
        
        # 1. 主音频预处理
        main_filters = []
        
        # EQ调整
        main_filters.append(f"equalizer=f=250:width_type=h:width=100:g={params['eq_250hz']}")
        main_filters.append(f"equalizer=f=3000:width_type=h:width=500:g={params['eq_3khz']}")
        
        # 压缩器
        main_filters.append(f"acompressor=threshold={params['compressor_threshold']}:ratio={params['compressor_ratio']}:attack=200:release=1000")
        
        # 响度归一化
        main_filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        
        # 应用预处理滤镜
        filter_parts.append(f'[0:a]{",".join(main_filters)}[main_pre]')
        
        # 2. Rubberband时间拉伸和音高变换
        if params['tempo'] != 1.0 or params['pitch'] != 0.0:
            rubberband_params = f"tempo={params['tempo']}:pitch={params['pitch']}"
            if params['formant_preserved']:
                rubberband_params += ":formant=preserved"
            filter_parts.append(f'[main_pre]rubberband={rubberband_params}[main_processed]')
        else:
            filter_parts.append(f'[main_pre]volume=1.0[main_processed]')
        
        # 3. 背景音效处理
        if params['background_sound']:
            bg_sound = params['background_sound']
            bg_filters = [
                f"volume={bg_sound['volume']}",
                f"atrim=start={bg_sound['start_time']}",
                f"afade=t=in:ss=0:d={bg_sound['fade_in']}",
                f"afade=t=out:st={self.processor.get_audio_duration(input_file) - bg_sound['fade_out']}:d={bg_sound['fade_out']}"
            ]
            filter_parts.append(f'[1:a]{",".join(bg_filters)}[bg_processed]')
        
        # 4. 事件音效处理
        if params['event_sound']:
            event_sound = params['event_sound']
            trigger_time = event_sound['trigger_time'] * self.processor.get_audio_duration(input_file)
            event_filters = [
                f"volume={event_sound['volume']}",
                f"atrim=duration={event_sound['duration']}",
                f"adelay={trigger_time * 1000}|{trigger_time * 1000}"
            ]
            input_idx = 2 if params['background_sound'] else 1
            filter_parts.append(f'[{input_idx}:a]{",".join(event_filters)}[event_processed]')
        
        # 5. 混合所有音效
        mix_inputs = ['[main_processed]']
        mix_weights = ['1']
        
        if params['background_sound']:
            mix_inputs.append('[bg_processed]')
            mix_weights.append('0.3')
        
        if params['event_sound']:
            mix_inputs.append('[event_processed]')
            mix_weights.append('0.2')
        
        mix_filter = f"amix=inputs={len(mix_inputs)}:duration=first:weights={' '.join(mix_weights)}[final]"
        filter_parts.append(mix_filter)
        
        return ';'.join(filter_parts)
    
    def batch_process_with_randomization(self, input_files: List[str], voice_template: str = None) -> List[Dict]:
        """批量随机化处理"""
        logger.info("=" * 60)
        logger.info("开始批量随机化处理")
        logger.info("=" * 60)
        
        results = []
        
        for i, audio_file in enumerate(input_files):
            logger.info(f"\n处理文件 {i+1}/{len(input_files)}: {Path(audio_file).name}")
            
            # 为每个文件生成不同的随机参数
            params = self.generate_random_parameters(voice_template)
            
            # 处理音频
            output_file = self.process_audio_with_random_params(audio_file, params)
            
            if output_file:
                results.append({
                    "input_file": audio_file,
                    "output_file": output_file,
                    "parameters": params,
                    "status": "success"
                })
            else:
                results.append({
                    "input_file": audio_file,
                    "output_file": None,
                    "parameters": params,
                    "status": "failed"
                })
        
        return results
    
    def create_processing_report(self, results: List[Dict]):
        """创建处理报告"""
        report_file = f"random_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"处理报告已保存: {report_file}")
        
        # 创建统计报告
        success_count = len([r for r in results if r["status"] == "success"])
        failed_count = len([r for r in results if r["status"] == "failed"])
        
        logger.info("=" * 60)
        logger.info("批量随机化处理完成!")
        logger.info("=" * 60)
        logger.info(f"总文件数: {len(results)}")
        logger.info(f"成功处理: {success_count}")
        logger.info(f"处理失败: {failed_count}")
        logger.info("")
        logger.info("处理特点:")
        logger.info("- 每条音频都有不同的语速和音高")
        logger.info("- 随机添加背景环境音效")
        logger.info("- 随机添加事件音效")
        logger.info("- 应用不同的声线模板")
        logger.info("- 响度归一化和动态调整")
        logger.info("- EQ优化口型自然度")
        logger.info("")
        logger.info("效果说明:")
        logger.info("- 听感上像同个人不同场次的对话")
        logger.info("- 重复率极低，真实感强")
        logger.info("- 适合TikTok直播场景")
        logger.info("=" * 60)

def main():
    """主函数"""
    logger.info("高级随机化音频处理脚本")
    
    # 初始化处理器
    processor = AdvancedRandomAudioProcessor()
    
    # 查找测试音频文件
    logger.info("查找EdgeTTS生成的测试音频文件...")
    edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
    
    if not edgetts_dir.exists():
        logger.error("EdgeTTS输出目录不存在")
        return
    
    # 收集音频文件
    audio_files = []
    for folder in edgetts_dir.iterdir():
        if folder.is_dir():
            for audio_file in folder.iterdir():
                if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                    audio_files.append(str(audio_file))
    
    if not audio_files:
        logger.error("未找到音频文件")
        return
    
    logger.info(f"找到 {len(audio_files)} 个音频文件")
    
    # 批量随机化处理
    results = processor.batch_process_with_randomization(audio_files)
    
    # 创建处理报告
    processor.create_processing_report(results)

if __name__ == "__main__":
    main()
