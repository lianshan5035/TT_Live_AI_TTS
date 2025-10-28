#!/usr/bin/env python3
"""
高级音频处理工具 - 集成Rubberband
使用Rubberband进行高质量的时间拉伸和音高变换
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedAudioProcessor:
    """高级音频处理器 - 集成Rubberband"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # Rubberband配置
        self.rubberband_config = {
            "enabled": True,
            "quality": "high",  # high, standard, draft
            "formant": "preserved",  # preserved, shifted
            "pitch_mode": "consistent",  # consistent, high-quality, fast
            "channels": "independent"  # independent, coupled
        }
        
        # 语速校正预设（使用Rubberband）
        self.speed_presets = {
            "normal": {
                "speed": 1.0,
                "pitch": 1.0,
                "description": "正常语速",
                "use_case": "保持原始语速和音高"
            },
            "slightly_faster": {
                "speed": 1.15,
                "pitch": 1.0,
                "description": "轻微加速 (15%)",
                "use_case": "语速略慢，保持音高"
            },
            "moderately_faster": {
                "speed": 1.25,
                "pitch": 1.0,
                "description": "适度加速 (25%)",
                "use_case": "语速明显过慢，保持音高"
            },
            "significantly_faster": {
                "speed": 1.35,
                "pitch": 1.0,
                "description": "显著加速 (35%)",
                "use_case": "语速严重过慢，保持音高"
            },
            "much_faster": {
                "speed": 1.5,
                "pitch": 1.0,
                "description": "大幅加速 (50%)",
                "use_case": "语速极其过慢，保持音高"
            },
            "faster_higher": {
                "speed": 1.2,
                "pitch": 1.1,
                "description": "加速+升调",
                "use_case": "语速慢且音调低"
            },
            "faster_lower": {
                "speed": 1.2,
                "pitch": 0.9,
                "description": "加速+降调",
                "use_case": "语速慢且音调高"
            }
        }
        
        # 前置滤镜预设（增强版）
        self.pre_filters = {
            "none": {
                "name": "无前置滤镜",
                "description": "不添加任何前置滤镜",
                "filters": [],
                "use_case": "保持原始音频"
            },
            "voice_enhancement": {
                "name": "语音增强",
                "description": "专门针对语音的增强滤镜",
                "filters": [
                    "highpass=f=80",  # 高通滤波
                    "lowpass=f=8000",  # 低通滤波
                    "volume=1.05"  # 轻微音量提升
                ],
                "use_case": "优化语音清晰度"
            },
            "noise_reduction": {
                "name": "降噪处理",
                "description": "减少背景噪音的滤镜",
                "filters": [
                    "highpass=f=100",  # 高通滤波
                    "lowpass=f=7000",  # 低通滤波
                    "volume=1.08"  # 音量补偿
                ],
                "use_case": "减少背景噪音"
            },
            "dynamic_range": {
                "name": "动态范围压缩",
                "description": "压缩动态范围，使音量更均匀",
                "filters": [
                    "acompressor=threshold=0.089:ratio=9:attack=200:release=1000",
                    "volume=1.02"
                ],
                "use_case": "平衡音量动态"
            },
            "broadcast_quality": {
                "name": "广播级质量",
                "description": "达到广播级音频质量的滤镜",
                "filters": [
                    "highpass=f=80",
                    "lowpass=f=8000",
                    "acompressor=threshold=0.089:ratio=9:attack=200:release=1000",
                    "volume=1.04"
                ],
                "use_case": "专业广播级质量"
            }
        }
        
        # 当前配置
        self.current_config = {
            "white_noise_volume": 0.70,  # 70%白噪音
            "pre_filter": "voice_enhancement",  # 默认语音增强
            "speed_preset": "normal",  # 默认正常语速
            "output_enabled": False  # 暂时不输出
        }
    
    def check_rubberband_support(self) -> bool:
        """检查Rubberband支持"""
        logger.info("检查Rubberband支持...")
        
        try:
            # 检查FFmpeg是否支持rubberband滤镜
            result = subprocess.run(['ffmpeg', '-filters'], capture_output=True, text=True)
            if 'rubberband' in result.stdout:
                logger.info("✓ FFmpeg支持Rubberband滤镜")
                return True
            else:
                logger.warning("✗ FFmpeg不支持Rubberband滤镜")
                return False
        except Exception as e:
            logger.error(f"检查Rubberband支持失败: {e}")
            return False
    
    def list_speed_presets(self):
        """列出语速预设选项"""
        logger.info("=" * 60)
        logger.info("Rubberband语速预设选项")
        logger.info("=" * 60)
        
        for preset_key, preset_config in self.speed_presets.items():
            logger.info(f"{preset_key}:")
            logger.info(f"  名称: {preset_config['description']}")
            logger.info(f"  语速: {preset_config['speed']:.2f}x")
            logger.info(f"  音高: {preset_config['pitch']:.2f}x")
            logger.info(f"  适用场景: {preset_config['use_case']}")
            logger.info("")
    
    def list_pre_filters(self):
        """列出前置滤镜选项"""
        logger.info("=" * 60)
        logger.info("前置滤镜选项")
        logger.info("=" * 60)
        
        for filter_key, filter_config in self.pre_filters.items():
            logger.info(f"{filter_key}:")
            logger.info(f"  名称: {filter_config['name']}")
            logger.info(f"  描述: {filter_config['description']}")
            logger.info(f"  适用场景: {filter_config['use_case']}")
            if filter_config['filters']:
                logger.info(f"  滤镜链: {' -> '.join(filter_config['filters'])}")
            else:
                logger.info(f"  滤镜链: 无")
            logger.info("")
    
    def set_speed_preset(self, preset_key: str) -> bool:
        """设置语速预设"""
        if preset_key not in self.speed_presets:
            logger.error(f"未知的语速预设: {preset_key}")
            return False
        
        self.current_config["speed_preset"] = preset_key
        preset_config = self.speed_presets[preset_key]
        
        logger.info(f"语速预设已设置为: {preset_config['description']}")
        logger.info(f"语速: {preset_config['speed']:.2f}x")
        logger.info(f"音高: {preset_config['pitch']:.2f}x")
        logger.info(f"适用场景: {preset_config['use_case']}")
        
        return True
    
    def set_pre_filter(self, filter_key: str) -> bool:
        """设置前置滤镜"""
        if filter_key not in self.pre_filters:
            logger.error(f"未知的前置滤镜: {filter_key}")
            return False
        
        self.current_config["pre_filter"] = filter_key
        filter_config = self.pre_filters[filter_key]
        
        logger.info(f"前置滤镜已设置为: {filter_config['name']}")
        logger.info(f"描述: {filter_config['description']}")
        logger.info(f"适用场景: {filter_config['use_case']}")
        
        if filter_config['filters']:
            logger.info(f"滤镜链: {' -> '.join(filter_config['filters'])}")
        else:
            logger.info("滤镜链: 无")
        
        return True
    
    def set_white_noise_volume(self, volume: float) -> bool:
        """设置白噪音音量"""
        if not 0.0 <= volume <= 1.0:
            logger.error(f"白噪音音量必须在0.0-1.0之间: {volume}")
            return False
        
        self.current_config["white_noise_volume"] = volume
        logger.info(f"白噪音音量已设置为: {volume*100:.0f}%")
        return True
    
    def set_output_enabled(self, enabled: bool):
        """设置是否启用输出"""
        self.current_config["output_enabled"] = enabled
        status = "启用" if enabled else "禁用"
        logger.info(f"输出已{status}")
    
    def get_current_config(self) -> Dict:
        """获取当前配置"""
        return self.current_config.copy()
    
    def find_test_audio(self) -> str:
        """查找测试音频文件"""
        logger.info("查找EdgeTTS生成的测试音频文件...")
        
        # 查找EdgeTTS输出目录
        edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
        if not edgetts_dir.exists():
            logger.error("EdgeTTS输出目录不存在")
            return None
        
        # 查找音频文件
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        logger.info(f"找到测试音频: {audio_file.name}")
                        return str(audio_file)
        
        logger.error("未找到EdgeTTS音频文件")
        return None
    
    def preview_processing_chain(self, input_file: str) -> str:
        """预览处理链效果（不输出文件）"""
        logger.info("=" * 60)
        logger.info("预览高级音频处理链")
        logger.info("=" * 60)
        
        logger.info(f"输入文件: {Path(input_file).name}")
        
        # 获取当前配置
        pre_filter_key = self.current_config["pre_filter"]
        speed_preset_key = self.current_config["speed_preset"]
        white_noise_volume = self.current_config["white_noise_volume"]
        
        pre_filter_config = self.pre_filters[pre_filter_key]
        speed_preset_config = self.speed_presets[speed_preset_key]
        
        logger.info(f"前置滤镜: {pre_filter_config['name']}")
        logger.info(f"语速预设: {speed_preset_config['description']}")
        logger.info(f"白噪音音量: {white_noise_volume*100:.0f}%")
        
        # 构建处理链
        processing_chain = self._build_processing_chain(
            input_file, pre_filter_config, speed_preset_config, white_noise_volume
        )
        
        logger.info("完整处理链:")
        for i, step in enumerate(processing_chain, 1):
            logger.info(f"  {i}. {step}")
        
        logger.info("")
        logger.info("注意: 当前设置为预览模式，不会生成输出文件")
        logger.info("如需生成文件，请先启用输出功能")
        
        return " -> ".join(processing_chain)
    
    def _build_processing_chain(self, input_file: str, pre_filter_config: Dict, 
                              speed_preset_config: Dict, white_noise_volume: float) -> List[str]:
        """构建完整处理链"""
        processing_chain = []
        
        # 1. 前置滤镜
        if pre_filter_config['filters']:
            processing_chain.extend(pre_filter_config['filters'])
        else:
            processing_chain.append("passthrough")
        
        # 2. Rubberband时间拉伸和音高变换
        speed = speed_preset_config['speed']
        pitch = speed_preset_config['pitch']
        
        if speed != 1.0 or pitch != 1.0:
            rubberband_params = f"tempo={speed}:pitch={pitch}"
            processing_chain.append(f"rubberband({rubberband_params})")
        
        # 3. 白噪音混合
        if white_noise_volume > 0:
            processing_chain.append(f"white_noise_mix={white_noise_volume}")
        
        # 4. 最终处理
        processing_chain.extend([
            "aresample=44100",  # 重采样
            "volume=0.8"  # 最终音量调整
        ])
        
        return processing_chain
    
    def process_audio_advanced(self, input_file: str) -> Optional[str]:
        """高级音频处理（仅在启用输出时）"""
        if not self.current_config["output_enabled"]:
            logger.info("输出已禁用，跳过文件生成")
            return None
        
        logger.info("=" * 60)
        logger.info("高级音频处理")
        logger.info("=" * 60)
        
        # 获取音频时长
        duration = self.processor.get_audio_duration(input_file)
        logger.info(f"音频时长: {duration:.2f} 秒")
        
        # 获取当前配置
        pre_filter_key = self.current_config["pre_filter"]
        speed_preset_key = self.current_config["speed_preset"]
        white_noise_volume = self.current_config["white_noise_volume"]
        
        pre_filter_config = self.pre_filters[pre_filter_key]
        speed_preset_config = self.speed_presets[speed_preset_key]
        
        logger.info(f"前置滤镜: {pre_filter_config['name']}")
        logger.info(f"语速预设: {speed_preset_config['description']}")
        logger.info(f"白噪音音量: {white_noise_volume*100:.0f}%")
        
        # 生成输出文件名
        input_path = Path(input_file)
        output_file = f"advanced_{pre_filter_key}_{speed_preset_key}_{white_noise_volume:.2f}noise.m4a"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', input_file])
        
        # 添加白噪音输入
        if white_noise_volume > 0:
            white_noise_file = self.processor.background_sounds_dir / "white_noise.wav"
            if white_noise_file.exists():
                cmd.extend(['-i', str(white_noise_file)])
        
        # 构建滤镜链
        filter_complex = self._build_ffmpeg_filter_complex(
            input_file, pre_filter_config, speed_preset_config, white_noise_volume
        )
        cmd.extend(['-filter_complex', filter_complex])
        
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 高级音频处理完成: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return output_file
        else:
            logger.error(f"✗ 高级音频处理失败: {result.stderr}")
            return None
    
    def _build_ffmpeg_filter_complex(self, input_file: str, pre_filter_config: Dict,
                                   speed_preset_config: Dict, white_noise_volume: float) -> str:
        """构建FFmpeg滤镜复合命令"""
        filter_parts = []
        
        # 前置滤镜
        if pre_filter_config['filters']:
            pre_filters_str = ','.join(pre_filter_config['filters'])
            filter_parts.append(f'[0:a]{pre_filters_str}[pre]')
        else:
            filter_parts.append(f'[0:a]volume=1.0[pre]')
        
        # Rubberband时间拉伸和音高变换
        speed = speed_preset_config['speed']
        pitch = speed_preset_config['pitch']
        
        if speed != 1.0 or pitch != 1.0:
            rubberband_params = f"tempo={speed}:pitch={pitch}"
            filter_parts.append(f'[pre]rubberband={rubberband_params}[main]')
        else:
            filter_parts.append(f'[pre]volume=1.0[main]')
        
        # 白噪音混合
        if white_noise_volume > 0:
            filter_parts.extend([
                f'[1:a]volume={white_noise_volume},atrim=duration={self.processor.get_audio_duration(input_file)}[bg0]',
                f'[main][bg0]amix=inputs=2:duration=first:weights=1 0.7[final]'
            ])
        else:
            filter_parts.append(f'[main]volume=0.8[final]')
        
        return ';'.join(filter_parts)
    
    def create_advanced_guide(self):
        """创建高级处理指南"""
        guide_file = "advanced_audio_processing_guide.txt"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("高级音频处理指南 - 集成Rubberband\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("当前配置:\n")
            f.write(f"白噪音音量: {self.current_config['white_noise_volume']*100:.0f}%\n")
            f.write(f"前置滤镜: {self.pre_filters[self.current_config['pre_filter']]['name']}\n")
            f.write(f"语速预设: {self.speed_presets[self.current_config['speed_preset']]['description']}\n")
            f.write(f"输出状态: {'启用' if self.current_config['output_enabled'] else '禁用'}\n\n")
            
            f.write("Rubberband优势:\n")
            f.write("- 高质量的时间拉伸，保持音质\n")
            f.write("- 独立的音高变换，不影响语速\n")
            f.write("- 保持音频的自然度和清晰度\n")
            f.write("- 适合语音处理的专业级工具\n\n")
            
            f.write("语速预设选项:\n")
            for preset_key, preset_config in self.speed_presets.items():
                f.write(f"- {preset_key}: {preset_config['description']}\n")
                f.write(f"  语速: {preset_config['speed']:.2f}x\n")
                f.write(f"  音高: {preset_config['pitch']:.2f}x\n")
                f.write(f"  适用场景: {preset_config['use_case']}\n\n")
            
            f.write("前置滤镜选项:\n")
            for filter_key, filter_config in self.pre_filters.items():
                f.write(f"- {filter_key}: {filter_config['name']}\n")
                f.write(f"  描述: {filter_config['description']}\n")
                f.write(f"  适用场景: {filter_config['use_case']}\n\n")
            
            f.write("处理流程:\n")
            f.write("1. 前置滤镜处理 (可选)\n")
            f.write("2. Rubberband时间拉伸和音高变换\n")
            f.write("3. 白噪音混合\n")
            f.write("4. 最终音频优化\n\n")
            
            f.write("使用建议:\n")
            f.write("- 优先使用Rubberband进行语速调整\n")
            f.write("- 根据音频特点选择合适的前置滤镜\n")
            f.write("- 平衡语速、音高和白噪音效果\n")
            f.write("- 适合TikTok直播场景的专业处理\n")
        
        logger.info(f"高级处理指南已保存: {guide_file}")

def main():
    """主函数"""
    logger.info("高级音频处理工具 - 集成Rubberband")
    
    # 初始化处理器
    processor = AdvancedAudioProcessor()
    
    # 检查Rubberband支持
    if not processor.check_rubberband_support():
        logger.warning("Rubberband支持检查失败，但继续运行")
    
    # 显示当前配置
    current_config = processor.get_current_config()
    logger.info("当前配置:")
    logger.info(f"  白噪音音量: {current_config['white_noise_volume']*100:.0f}%")
    logger.info(f"  前置滤镜: {processor.pre_filters[current_config['pre_filter']]['name']}")
    logger.info(f"  语速预设: {processor.speed_presets[current_config['speed_preset']]['description']}")
    logger.info(f"  输出状态: {'启用' if current_config['output_enabled'] else '禁用'}")
    
    # 列出语速预设选项
    processor.list_speed_presets()
    
    # 列出前置滤镜选项
    processor.list_pre_filters()
    
    # 创建高级处理指南
    processor.create_advanced_guide()
    
    logger.info("\n" + "=" * 60)
    logger.info("高级音频处理工具已就绪!")
    logger.info("=" * 60)
    logger.info("当前状态:")
    logger.info("  - 白噪音音量: 70%")
    logger.info("  - 前置滤镜: 语音增强")
    logger.info("  - 语速预设: 正常语速")
    logger.info("  - 输出状态: 禁用")
    logger.info("")
    logger.info("Rubberband优势:")
    logger.info("  - 高质量时间拉伸，保持音质")
    logger.info("  - 独立音高变换，不影响语速")
    logger.info("  - 保持音频自然度和清晰度")
    logger.info("  - 专业级语音处理工具")
    logger.info("")
    logger.info("下一步操作:")
    logger.info("1. 选择合适的前置滤镜")
    logger.info("2. 选择语速预设")
    logger.info("3. 预览处理链效果")
    logger.info("4. 启用输出生成测试文件")
    logger.info("5. 确认效果后应用到批量处理")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
