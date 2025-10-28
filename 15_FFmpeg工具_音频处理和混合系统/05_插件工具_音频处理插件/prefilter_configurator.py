#!/usr/bin/env python3
"""
前置滤镜配置工具
为音频处理添加前置滤镜功能
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PreFilterConfigurator:
    """前置滤镜配置器"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # 前置滤镜预设
        self.pre_filters = {
            "none": {
                "name": "无前置滤镜",
                "description": "不添加任何前置滤镜",
                "filters": [],
                "use_case": "保持原始音频"
            },
            "basic_enhancement": {
                "name": "基础增强",
                "description": "基础音频增强滤镜",
                "filters": [
                    "volume=1.1",  # 轻微音量提升
                    "aresample=44100"  # 重采样到44.1kHz
                ],
                "use_case": "轻微提升音频质量"
            },
            "voice_enhancement": {
                "name": "语音增强",
                "description": "专门针对语音的增强滤镜",
                "filters": [
                    "highpass=f=80",  # 高通滤波，去除低频噪音
                    "lowpass=f=8000",  # 低通滤波，去除高频噪音
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
            "warm_sound": {
                "name": "温暖音色",
                "description": "增加音频的温暖感",
                "filters": [
                    "highpass=f=60",  # 轻微高通
                    "lowpass=f=12000",  # 轻微低通
                    "volume=1.03"
                ],
                "use_case": "增加音频温暖感"
            },
            "crisp_clear": {
                "name": "清脆清晰",
                "description": "增强音频的清晰度和清脆感",
                "filters": [
                    "highpass=f=120",  # 较强高通
                    "lowpass=f=6000",  # 较强低通
                    "volume=1.06"
                ],
                "use_case": "增强清晰度"
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
            "pre_filter": "none",  # 默认无前置滤镜
            "output_enabled": False  # 暂时不输出
        }
    
    def list_pre_filters(self):
        """列出所有前置滤镜选项"""
        logger.info("=" * 60)
        logger.info("前置滤镜选项列表")
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
    
    def preview_filter_chain(self, input_file: str) -> str:
        """预览滤镜链效果（不输出文件）"""
        logger.info("=" * 60)
        logger.info("预览滤镜链效果")
        logger.info("=" * 60)
        
        logger.info(f"输入文件: {Path(input_file).name}")
        
        # 获取当前配置
        pre_filter_key = self.current_config["pre_filter"]
        white_noise_volume = self.current_config["white_noise_volume"]
        
        pre_filter_config = self.pre_filters[pre_filter_key]
        logger.info(f"前置滤镜: {pre_filter_config['name']}")
        logger.info(f"白噪音音量: {white_noise_volume*100:.0f}%")
        
        # 构建滤镜链
        filter_chain = self._build_filter_chain(input_file, pre_filter_config, white_noise_volume)
        
        logger.info("完整滤镜链:")
        for i, step in enumerate(filter_chain, 1):
            logger.info(f"  {i}. {step}")
        
        logger.info("")
        logger.info("注意: 当前设置为预览模式，不会生成输出文件")
        logger.info("如需生成文件，请先启用输出功能")
        
        return " -> ".join(filter_chain)
    
    def _build_filter_chain(self, input_file: str, pre_filter_config: Dict, white_noise_volume: float) -> List[str]:
        """构建完整滤镜链"""
        filter_chain = []
        
        # 1. 前置滤镜
        if pre_filter_config['filters']:
            filter_chain.extend(pre_filter_config['filters'])
        else:
            filter_chain.append("passthrough")  # 无滤镜时使用直通
        
        # 2. 白噪音混合
        if white_noise_volume > 0:
            filter_chain.append(f"white_noise_mix={white_noise_volume}")
        
        # 3. 最终处理
        filter_chain.extend([
            "aresample=44100",  # 重采样
            "volume=0.8"  # 最终音量调整
        ])
        
        return filter_chain
    
    def create_filter_test_file(self, input_file: str) -> Optional[str]:
        """创建滤镜测试文件（仅在启用输出时）"""
        if not self.current_config["output_enabled"]:
            logger.info("输出已禁用，跳过文件生成")
            return None
        
        logger.info("=" * 60)
        logger.info("创建滤镜测试文件")
        logger.info("=" * 60)
        
        # 获取音频时长
        duration = self.processor.get_audio_duration(input_file)
        logger.info(f"音频时长: {duration:.2f} 秒")
        
        # 生成输出文件名
        pre_filter_key = self.current_config["pre_filter"]
        white_noise_volume = self.current_config["white_noise_volume"]
        
        input_path = Path(input_file)
        output_file = f"prefilter_{pre_filter_key}_{white_noise_volume:.2f}noise.m4a"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', input_file])
        
        # 添加白噪音输入
        if white_noise_volume > 0:
            white_noise_file = self.processor.background_sounds_dir / "white_noise.wav"
            if white_noise_file.exists():
                cmd.extend(['-i', str(white_noise_file)])
        
        # 构建滤镜链
        filter_complex = self._build_ffmpeg_filter_complex(input_file, white_noise_volume)
        cmd.extend(['-filter_complex', filter_complex])
        
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        cmd.append(output_file)
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 滤镜测试文件生成成功: {output_file}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return output_file
        else:
            logger.error(f"✗ 滤镜测试文件生成失败: {result.stderr}")
            return None
    
    def _build_ffmpeg_filter_complex(self, input_file: str, white_noise_volume: float) -> str:
        """构建FFmpeg滤镜复合命令"""
        pre_filter_key = self.current_config["pre_filter"]
        pre_filter_config = self.pre_filters[pre_filter_key]
        
        filter_parts = []
        
        # 前置滤镜
        if pre_filter_config['filters']:
            pre_filters_str = ','.join(pre_filter_config['filters'])
            filter_parts.append(f'[0:a]{pre_filters_str}[main]')
        else:
            filter_parts.append(f'[0:a]volume=1.0[main]')
        
        # 白噪音混合
        if white_noise_volume > 0:
            filter_parts.extend([
                f'[1:a]volume={white_noise_volume},atrim=duration={self.processor.get_audio_duration(input_file)}[bg0]',
                f'[main][bg0]amix=inputs=2:duration=first:weights=1 0.7[final]'
            ])
        else:
            filter_parts.append(f'[main]volume=0.8[final]')
        
        return ';'.join(filter_parts)
    
    def create_configuration_guide(self):
        """创建配置指南"""
        guide_file = "prefilter_configuration_guide.txt"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("前置滤镜配置指南\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("当前配置:\n")
            f.write(f"白噪音音量: {self.current_config['white_noise_volume']*100:.0f}%\n")
            f.write(f"前置滤镜: {self.pre_filters[self.current_config['pre_filter']]['name']}\n")
            f.write(f"输出状态: {'启用' if self.current_config['output_enabled'] else '禁用'}\n\n")
            
            f.write("前置滤镜选项:\n")
            for filter_key, filter_config in self.pre_filters.items():
                f.write(f"- {filter_key}: {filter_config['name']}\n")
                f.write(f"  描述: {filter_config['description']}\n")
                f.write(f"  适用场景: {filter_config['use_case']}\n")
                if filter_config['filters']:
                    f.write(f"  滤镜链: {' -> '.join(filter_config['filters'])}\n")
                f.write("\n")
            
            f.write("使用说明:\n")
            f.write("1. 选择合适的前置滤镜\n")
            f.write("2. 调整白噪音音量\n")
            f.write("3. 预览滤镜链效果\n")
            f.write("4. 启用输出生成测试文件\n")
            f.write("5. 确认效果后应用到批量处理\n\n")
            
            f.write("配置方法:\n")
            f.write("- 使用 set_pre_filter() 设置前置滤镜\n")
            f.write("- 使用 set_white_noise_volume() 设置白噪音音量\n")
            f.write("- 使用 set_output_enabled() 启用/禁用输出\n")
            f.write("- 使用 preview_filter_chain() 预览效果\n")
        
        logger.info(f"配置指南已保存: {guide_file}")

def main():
    """主函数"""
    logger.info("前置滤镜配置工具")
    
    # 初始化配置器
    configurator = PreFilterConfigurator()
    
    # 显示当前配置
    current_config = configurator.get_current_config()
    logger.info("当前配置:")
    logger.info(f"  白噪音音量: {current_config['white_noise_volume']*100:.0f}%")
    logger.info(f"  前置滤镜: {configurator.pre_filters[current_config['pre_filter']]['name']}")
    logger.info(f"  输出状态: {'启用' if current_config['output_enabled'] else '禁用'}")
    
    # 列出所有前置滤镜选项
    configurator.list_pre_filters()
    
    # 创建配置指南
    configurator.create_configuration_guide()
    
    logger.info("\n" + "=" * 60)
    logger.info("前置滤镜配置工具已就绪!")
    logger.info("=" * 60)
    logger.info("当前状态:")
    logger.info("  - 白噪音音量: 70%")
    logger.info("  - 前置滤镜: 无前置滤镜")
    logger.info("  - 输出状态: 禁用")
    logger.info("")
    logger.info("下一步操作:")
    logger.info("1. 选择合适的前置滤镜")
    logger.info("2. 预览滤镜链效果")
    logger.info("3. 启用输出生成测试文件")
    logger.info("4. 确认效果后应用到批量处理")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
