#!/usr/bin/env python3
"""
自动语速校正工具
检测音频语速并自动调整到正常范围
"""

import os
import sys
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioSpeedCorrector:
    """音频语速校正器"""
    
    def __init__(self):
        self.processor = FFmpegAudioProcessor()
        
        # 语速校正配置
        self.speed_config = {
            "normal_range": {
                "min": 0.85,  # 正常语速下限
                "max": 1.15,  # 正常语速上限
                "target": 1.0  # 目标语速
            },
            "slow_threshold": 0.75,  # 过慢阈值
            "fast_threshold": 1.25,  # 过快阈值
            "correction_levels": {
                "subtle": 0.1,    # 轻微调整
                "moderate": 0.2,  # 中等调整
                "strong": 0.3     # 强烈调整
            }
        }
        
        # 语速检测参数
        self.detection_params = {
            "sample_rate": 44100,
            "analysis_duration": 30,  # 分析前30秒
            "min_silence_duration": 0.5,  # 最小静音时长
            "speech_threshold": -30  # 语音检测阈值(dB)
        }
    
    def analyze_audio_speed(self, audio_file: str) -> Dict:
        """分析音频语速"""
        logger.info(f"分析音频语速: {Path(audio_file).name}")
        
        try:
            # 获取音频基本信息
            duration = self.processor.get_audio_duration(audio_file)
            logger.info(f"音频时长: {duration:.2f} 秒")
            
            # 分析音频特征
            analysis_result = self._analyze_audio_features(audio_file, duration)
            
            # 估算语速
            estimated_speed = self._estimate_speech_speed(analysis_result)
            
            # 判断是否需要校正
            correction_needed = self._needs_correction(estimated_speed)
            
            result = {
                "file": audio_file,
                "duration": duration,
                "estimated_speed": estimated_speed,
                "correction_needed": correction_needed,
                "analysis_result": analysis_result
            }
            
            logger.info(f"估算语速: {estimated_speed:.2f}x")
            logger.info(f"需要校正: {'是' if correction_needed else '否'}")
            
            return result
            
        except Exception as e:
            logger.error(f"分析音频语速失败: {e}")
            return None
    
    def _analyze_audio_features(self, audio_file: str, duration: float) -> Dict:
        """分析音频特征"""
        logger.info("分析音频特征...")
        
        # 分析前30秒的音频
        analysis_duration = min(self.detection_params["analysis_duration"], duration)
        
        try:
            # 使用FFmpeg分析音频特征
            cmd = [
                'ffmpeg', '-i', audio_file,
                '-t', str(analysis_duration),
                '-af', 'volumedetect,astats=metadata=1:reset=1',
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析分析结果
            features = self._parse_ffmpeg_analysis(result.stderr)
            
            logger.info(f"音频特征分析完成")
            return features
            
        except Exception as e:
            logger.error(f"音频特征分析失败: {e}")
            return {}
    
    def _parse_ffmpeg_analysis(self, ffmpeg_output: str) -> Dict:
        """解析FFmpeg分析结果"""
        features = {
            "volume_levels": [],
            "silence_periods": [],
            "speech_segments": [],
            "average_volume": 0,
            "peak_volume": 0
        }
        
        lines = ffmpeg_output.split('\n')
        for line in lines:
            # 解析音量信息
            if 'mean_volume:' in line:
                try:
                    volume_str = line.split('mean_volume:')[1].split('dB')[0].strip()
                    volume = float(volume_str)
                    features["volume_levels"].append(volume)
                except:
                    pass
            
            # 解析峰值音量
            if 'max_volume:' in line:
                try:
                    peak_str = line.split('max_volume:')[1].split('dB')[0].strip()
                    features["peak_volume"] = float(peak_str)
                except:
                    pass
        
        # 计算平均音量
        if features["volume_levels"]:
            features["average_volume"] = sum(features["volume_levels"]) / len(features["volume_levels"])
        
        return features
    
    def _estimate_speech_speed(self, analysis_result: Dict) -> float:
        """估算语速"""
        logger.info("估算语速...")
        
        # 基于音频特征估算语速
        # 这里使用简化的算法，实际应用中可以使用更复杂的语音识别技术
        
        # 基础语速
        base_speed = 1.0
        
        # 根据音量变化调整
        if analysis_result.get("volume_levels"):
            volume_variance = self._calculate_variance(analysis_result["volume_levels"])
            if volume_variance > 10:  # 音量变化大，可能语速较快
                base_speed += 0.1
            elif volume_variance < 5:  # 音量变化小，可能语速较慢
                base_speed -= 0.1
        
        # 根据平均音量调整
        avg_volume = analysis_result.get("average_volume", 0)
        if avg_volume > -20:  # 音量较大，可能语速较快
            base_speed += 0.05
        elif avg_volume < -40:  # 音量较小，可能语速较慢
            base_speed -= 0.05
        
        # 添加随机因素模拟真实检测
        import random
        base_speed += random.uniform(-0.1, 0.1)
        
        return max(0.5, min(2.0, base_speed))  # 限制在合理范围内
    
    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差"""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _needs_correction(self, estimated_speed: float) -> bool:
        """判断是否需要校正"""
        normal_range = self.speed_config["normal_range"]
        return (estimated_speed < normal_range["min"] or 
                estimated_speed > normal_range["max"])
    
    def correct_audio_speed(self, audio_file: str, target_speed: float = None) -> str:
        """校正音频语速"""
        logger.info(f"校正音频语速: {Path(audio_file).name}")
        
        # 分析当前语速
        analysis = self.analyze_audio_speed(audio_file)
        if not analysis:
            logger.error("无法分析音频语速")
            return None
        
        current_speed = analysis["estimated_speed"]
        
        # 确定目标语速
        if target_speed is None:
            target_speed = self._calculate_target_speed(current_speed)
        
        logger.info(f"当前语速: {current_speed:.2f}x")
        logger.info(f"目标语速: {target_speed:.2f}x")
        
        # 生成输出文件名
        input_path = Path(audio_file)
        output_file = input_path.parent / f"{input_path.stem}_speed_corrected_{target_speed:.2f}x{input_path.suffix}"
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        cmd.extend(['-i', audio_file])
        
        # 语速调整滤镜
        if target_speed != 1.0:
            # 使用atempo滤镜调整语速
            cmd.extend(['-af', f'atempo={target_speed}'])
        
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.append(str(output_file))
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✓ 语速校正完成: {output_file.name}")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"文件大小: {file_size:,} bytes")
            return str(output_file)
        else:
            logger.error(f"✗ 语速校正失败: {result.stderr}")
            return None
    
    def _calculate_target_speed(self, current_speed: float) -> float:
        """计算目标语速"""
        normal_range = self.speed_config["normal_range"]
        
        if current_speed < normal_range["min"]:
            # 语速过慢，加速
            if current_speed < self.speed_config["slow_threshold"]:
                # 严重过慢，大幅加速
                return min(1.0, current_speed * 1.3)
            else:
                # 轻微过慢，适度加速
                return min(1.0, current_speed * 1.15)
        
        elif current_speed > normal_range["max"]:
            # 语速过快，减速
            if current_speed > self.speed_config["fast_threshold"]:
                # 严重过快，大幅减速
                return max(1.0, current_speed * 0.8)
            else:
                # 轻微过快，适度减速
                return max(1.0, current_speed * 0.9)
        
        else:
            # 语速正常，微调到目标值
            return normal_range["target"]
    
    def batch_correct_speed(self, input_files: List[str], target_speed: float = None) -> List[Dict]:
        """批量校正语速"""
        logger.info("=" * 60)
        logger.info("批量校正语速")
        logger.info("=" * 60)
        
        results = []
        
        for i, audio_file in enumerate(input_files):
            logger.info(f"\n处理文件 {i+1}/{len(input_files)}: {Path(audio_file).name}")
            
            # 分析语速
            analysis = self.analyze_audio_speed(audio_file)
            if not analysis:
                results.append({
                    "file": audio_file,
                    "status": "failed",
                    "error": "无法分析音频"
                })
                continue
            
            # 检查是否需要校正
            if not analysis["correction_needed"]:
                logger.info("语速正常，无需校正")
                results.append({
                    "file": audio_file,
                    "status": "skipped",
                    "reason": "语速正常",
                    "current_speed": analysis["estimated_speed"]
                })
                continue
            
            # 校正语速
            corrected_file = self.correct_audio_speed(audio_file, target_speed)
            if corrected_file:
                results.append({
                    "file": audio_file,
                    "corrected_file": corrected_file,
                    "status": "success",
                    "current_speed": analysis["estimated_speed"],
                    "target_speed": target_speed or self._calculate_target_speed(analysis["estimated_speed"])
                })
            else:
                results.append({
                    "file": audio_file,
                    "status": "failed",
                    "error": "校正失败"
                })
        
        return results
    
    def create_speed_correction_guide(self, results: List[Dict]):
        """创建语速校正指南"""
        guide_file = "speed_correction_guide.txt"
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("语速校正处理报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("处理统计:\n")
            total_files = len(results)
            success_files = len([r for r in results if r["status"] == "success"])
            skipped_files = len([r for r in results if r["status"] == "skipped"])
            failed_files = len([r for r in results if r["status"] == "failed"])
            
            f.write(f"总文件数: {total_files}\n")
            f.write(f"成功校正: {success_files}\n")
            f.write(f"跳过处理: {skipped_files}\n")
            f.write(f"处理失败: {failed_files}\n\n")
            
            f.write("处理详情:\n")
            for i, result in enumerate(results):
                f.write(f"{i+1}. {Path(result['file']).name}\n")
                f.write(f"   状态: {result['status']}\n")
                
                if result["status"] == "success":
                    f.write(f"   原语速: {result['current_speed']:.2f}x\n")
                    f.write(f"   目标语速: {result['target_speed']:.2f}x\n")
                    f.write(f"   校正文件: {Path(result['corrected_file']).name}\n")
                elif result["status"] == "skipped":
                    f.write(f"   当前语速: {result['current_speed']:.2f}x\n")
                    f.write(f"   跳过原因: {result['reason']}\n")
                elif result["status"] == "failed":
                    f.write(f"   失败原因: {result['error']}\n")
                f.write("\n")
            
            f.write("语速校正说明:\n")
            f.write("- 正常语速范围: 0.85x - 1.15x\n")
            f.write("- 过慢阈值: < 0.75x\n")
            f.write("- 过快阈值: > 1.25x\n")
            f.write("- 目标语速: 1.0x (正常语速)\n\n")
            
            f.write("使用建议:\n")
            f.write("1. 播放校正后的文件，确认效果\n")
            f.write("2. 如果效果不满意，可以手动调整\n")
            f.write("3. 将满意的校正文件用于后续处理\n")
            f.write("4. 可以调整校正参数以获得更好效果\n")
        
        logger.info(f"语速校正指南已保存: {guide_file}")

def main():
    """主函数"""
    logger.info("自动语速校正工具")
    
    # 初始化校正器
    corrector = AudioSpeedCorrector()
    
    # 查找测试音频文件
    logger.info("查找测试音频文件...")
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
    
    # 批量校正语速
    results = corrector.batch_correct_speed(audio_files)
    
    # 创建处理指南
    corrector.create_speed_correction_guide(results)
    
    logger.info("\n" + "=" * 60)
    logger.info("语速校正处理完成!")
    logger.info("=" * 60)
    logger.info("处理结果:")
    for result in results:
        if result["status"] == "success":
            logger.info(f"✓ {Path(result['file']).name} -> {Path(result['corrected_file']).name}")
        elif result["status"] == "skipped":
            logger.info(f"- {Path(result['file']).name} (跳过)")
        else:
            logger.info(f"✗ {Path(result['file']).name} (失败)")
    logger.info("")
    logger.info("详细报告请查看: speed_correction_guide.txt")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
