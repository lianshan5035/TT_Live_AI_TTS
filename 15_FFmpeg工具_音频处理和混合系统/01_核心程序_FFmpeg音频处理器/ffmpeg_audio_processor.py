"""
FFmpeg 音频处理器
为 TikTok 半无人直播添加背景音效和白噪音，避免被 AI 判定为录播
"""

import os
import subprocess
import logging
import random
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import tempfile
import shutil
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FFmpegAudioProcessor:
    """FFmpeg 音频处理器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化处理器
        
        Args:
            output_dir: 输出音频文件目录（如果为None，则使用TT_Live_AI_TTS目录下的20.1_ffpmeg输出文件_处理完成的音频文件）
        """
        # EdgeTTS输出目录
        self.edgetts_output_dir = Path("20_输出文件_处理完成的音频文件")
        
        # FFmpeg输出目录（专门的FFmpeg输出文件夹）
        if output_dir is None:
            # 确保在TT_Live_AI_TTS根目录下创建输出文件夹
            self.output_dir = Path("../../20.1_ffpmeg输出文件_处理完成的音频文件")
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True)
        
        # 背景音效目录
        self.background_sounds_dir = Path("background_sounds_背景音效文件存储目录")
        if not self.background_sounds_dir.exists():
            # 如果背景音效目录不存在，尝试创建并复制文件
            self.background_sounds_dir = Path("background_sounds")
            self.background_sounds_dir.mkdir(exist_ok=True)
        
        # 检查 FFmpeg 是否安装
        self._check_ffmpeg()
        
        # 批量处理记录
        self.batch_records = {}
        
        # 背景音效配置
        self.background_sounds = {
            "rain": {
                "file": "rain_light.wav",
                "volume": 0.3,
                "description": "细雨声"
            },
            "footsteps": {
                "file": "footsteps_carpet.wav", 
                "volume": 0.2,
                "description": "脚步声"
            },
            "drinking": {
                "file": "drinking_water.wav",
                "volume": 0.15,
                "description": "喝水声"
            },
            "keyboard": {
                "file": "keyboard_typing.wav",
                "volume": 0.25,
                "description": "键盘声"
            },
            "fireplace": {
                "file": "fireplace_crackling.wav",
                "volume": 0.2,
                "description": "篝火声"
            },
            "white_noise": {
                "file": "white_noise.wav",
                "volume": 0.70,  # 固定为70%，为前置滤镜预留空间
                "description": "白噪音"
            },
            "room_tone": {
                "file": "room_tone.wav",
                "volume": 0.15,
                "description": "房间音效"
            },
            "paper_rustle": {
                "file": "paper_rustle.wav",
                "volume": 0.2,
                "description": "纸张摩擦声"
            },
            "chair_creak": {
                "file": "chair_creak.wav",
                "volume": 0.15,
                "description": "椅子吱嘎声"
            },
            "clock_tick": {
                "file": "clock_tick.wav",
                "volume": 0.1,
                "description": "时钟滴答声"
            }
        }
        
        # 默认音效组合
        self.default_combinations = [
            ["rain", "white_noise"],
            ["fireplace", "room_tone"],
            ["keyboard", "drinking"],
            ["footsteps", "paper_rustle"],
            ["chair_creak", "clock_tick"]
        ]
        
        # 处理统计
        self.stats = {
            'processed_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'total_processing_time': 0
        }
    
    def _check_ffmpeg(self) -> bool:
        """检查 FFmpeg 是否安装"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("FFmpeg 已安装")
                return True
            else:
                logger.error("FFmpeg 未正确安装")
                return False
        except FileNotFoundError:
            logger.error("FFmpeg 未安装，请先安装 FFmpeg")
            return False
    
    def create_background_sounds(self) -> None:
        """创建背景音效文件"""
        logger.info("正在创建背景音效文件...")
        
        # 创建各种背景音效
        sound_configs = {
            "rain_light.wav": {
                "type": "noise",
                "frequency": "pink",
                "duration": 300,  # 5分钟
                "description": "细雨声"
            },
            "footsteps_carpet.wav": {
                "type": "impulse",
                "pattern": "random",
                "duration": 60,
                "description": "脚步声"
            },
            "drinking_water.wav": {
                "type": "impulse",
                "pattern": "periodic",
                "duration": 30,
                "description": "喝水声"
            },
            "keyboard_typing.wav": {
                "type": "impulse",
                "pattern": "random",
                "duration": 120,
                "description": "键盘声"
            },
            "fireplace_crackling.wav": {
                "type": "noise",
                "frequency": "brown",
                "duration": 300,
                "description": "篝火声"
            },
            "white_noise.wav": {
                "type": "noise",
                "frequency": "white",
                "duration": 300,
                "description": "白噪音"
            },
            "room_tone.wav": {
                "type": "noise",
                "frequency": "pink",
                "duration": 300,
                "description": "房间音效"
            },
            "paper_rustle.wav": {
                "type": "impulse",
                "pattern": "random",
                "duration": 45,
                "description": "纸张摩擦声"
            },
            "chair_creak.wav": {
                "type": "impulse",
                "pattern": "periodic",
                "duration": 30,
                "description": "椅子吱嘎声"
            },
            "clock_tick.wav": {
                "type": "impulse",
                "pattern": "periodic",
                "duration": 60,
                "description": "时钟滴答声"
            }
        }
        
        for filename, config in sound_configs.items():
            filepath = self.background_sounds_dir / filename
            if not filepath.exists():
                self._generate_sound_file(filepath, config)
                logger.info(f"创建音效文件: {filename}")
    
    def _generate_sound_file(self, filepath: Path, config: Dict) -> None:
        """生成音效文件"""
        try:
            # 检查是否有现有的白噪音模板
            white_noise_template = Path("/Volumes/M2/白噪声/2h白噪声.WAV")
            
            if config["type"] == "noise" and white_noise_template.exists():
                # 使用现有的白噪音模板
                logger.info(f"使用现有白噪音模板: {white_noise_template}")
                # 复制模板文件
                import shutil
                shutil.copy2(white_noise_template, filepath)
            elif config["type"] == "noise":
                # 生成噪音
                cmd = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-filter_complex', f'[0:a]volume=0.1[noise];[1:a]volume=0.05[bg];[noise][bg]amix=inputs=2:duration=first',
                    '-t', str(config["duration"]),
                    '-y', str(filepath)
                ]
                subprocess.run(cmd, capture_output=True, check=True)
            else:
                # 生成脉冲音效
                cmd = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-t', str(config["duration"]),
                    '-y', str(filepath)
                ]
                subprocess.run(cmd, capture_output=True, check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"生成音效文件失败 {filepath}: {e}")
            # 创建空的音效文件作为占位符
            with open(filepath, 'wb') as f:
                f.write(b'')
    
    def get_audio_duration(self, audio_file: str) -> float:
        """获取音频文件时长"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.error(f"获取音频时长失败: {result.stderr}")
                return 0.0
        except Exception as e:
            logger.error(f"获取音频时长异常: {e}")
            return 0.0
    
    def process_single_audio(self, input_file: str, output_file: str = None,
                           background_combination: List[str] = None,
                           main_volume: float = 1.0) -> bool:
        """
        处理单个音频文件
        
        Args:
            input_file: 输入音频文件路径
            output_file: 输出音频文件路径
            background_combination: 背景音效组合
            main_volume: 主音频音量
            
        Returns:
            bool: 是否处理成功
        """
        if not os.path.exists(input_file):
            logger.error(f"输入文件不存在: {input_file}")
            return False
        
        if output_file is None:
            input_path = Path(input_file)
            output_file = self.output_dir / f"processed_{input_path.name}"
        
        if background_combination is None:
            background_combination = random.choice(self.default_combinations)
        
        try:
            # 构建 FFmpeg 命令
            cmd = self._build_ffmpeg_command(
                input_file, str(output_file), 
                background_combination, main_volume
            )
            
            # 执行处理
            start_time = datetime.now()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            self.stats['total_processing_time'] += processing_time
            
            if result.returncode == 0:
                self.stats['success_count'] += 1
                logger.info(f"音频处理成功: {output_file}")
                logger.info(f"处理耗时: {processing_time:.2f} 秒")
                return True
            else:
                self.stats['failed_count'] += 1
                logger.error(f"音频处理失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.stats['failed_count'] += 1
            logger.error(f"音频处理异常: {e}")
            return False
    
    def _build_ffmpeg_command(self, input_file: str, output_file: str,
                            background_combination: List[str],
                            main_volume: float) -> List[str]:
        """构建 FFmpeg 命令"""
        
        # 获取主音频时长
        main_duration = self.get_audio_duration(input_file)
        logger.info(f"主音频时长: {main_duration:.2f} 秒")
        
        # 基础命令
        cmd = ['ffmpeg', '-y']
        
        # 添加输入文件
        cmd.extend(['-i', input_file])
        
        # 添加背景音效输入
        background_inputs = []
        background_filters = []
        
        for i, sound_name in enumerate(background_combination):
            if sound_name in self.background_sounds:
                sound_file = self.background_sounds_dir / self.background_sounds[sound_name]['file']
                if sound_file.exists():
                    cmd.extend(['-i', str(sound_file)])
                    background_inputs.append(f'[{i+1}:a]')
                    volume = self.background_sounds[sound_name]['volume']
                    
                    # 对于白噪音，使用截取模式，其他音效使用循环模式
                    if sound_name == "white_noise":
                        # 白噪音：截取与主音频相同长度的片段
                        background_filters.append(f'[{i+1}:a]volume={volume},atrim=duration={main_duration}[bg{i}]')
                    else:
                        # 其他音效：循环播放到主音频长度
                        background_filters.append(f'[{i+1}:a]volume={volume},aloop=loop=-1:size=2e+09,atrim=duration={main_duration}[bg{i}]')
        
        # 构建滤镜链
        filter_parts = []
        
        # 主音频音量调整和格式转换
        filter_parts.append(f'[0:a]volume={main_volume},aresample=44100[main]')
        
        # 背景音效处理
        if background_filters:
            filter_parts.extend(background_filters)
            
            # 混合背景音效
            if len(background_inputs) > 1:
                bg_mix = ''.join([f'[bg{i}]' for i in range(len(background_inputs))])
                filter_parts.append(f'{bg_mix}amix=inputs={len(background_inputs)}:duration=first[bgmix]')
            else:
                filter_parts.append('[bg0]volume=0.5[bgmix]')
            
            # 最终混合
            filter_parts.append('[main][bgmix]amix=inputs=2:duration=first:weights=1 0.3[final]')
        else:
            filter_parts.append('[main]volume=0.9[final]')
        
        # 添加滤镜
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # 输出设置
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])  # 使用 MP4 容器格式
        cmd.append(output_file)
        
        return cmd
    
    def process_batch(self, input_files: List[str], 
                     background_combinations: List[List[str]] = None,
                     main_volume: float = 1.0) -> List[Dict]:
        """
        批量处理音频文件
        
        Args:
            input_files: 输入文件列表
            background_combinations: 背景音效组合列表
            main_volume: 主音频音量
            
        Returns:
            List[Dict]: 处理结果列表
        """
        logger.info(f"开始批量处理 {len(input_files)} 个音频文件")
        
        if background_combinations is None:
            background_combinations = [random.choice(self.default_combinations) 
                                     for _ in range(len(input_files))]
        
        results = []
        
        for i, input_file in enumerate(input_files):
            logger.info(f"正在处理第 {i+1}/{len(input_files)} 个文件: {input_file}")
            
            # 生成输出文件名
            input_path = Path(input_file)
            output_file = self.output_dir / f"processed_{input_path.name}"
            
            # 选择背景音效组合
            bg_combo = background_combinations[i] if i < len(background_combinations) else random.choice(self.default_combinations)
            
            # 处理音频
            success = self.process_single_audio(
                input_file=input_file,
                output_file=str(output_file),
                background_combination=bg_combo,
                main_volume=main_volume
            )
            
            result = {
                'input_file': input_file,
                'output_file': str(output_file),
                'background_sounds': bg_combo,
                'success': success,
                'file_size': os.path.getsize(output_file) if success and os.path.exists(output_file) else 0
            }
            
            results.append(result)
            self.stats['processed_count'] += 1
            
            if success:
                logger.info(f"✓ 第 {i+1} 个文件处理成功")
            else:
                logger.error(f"✗ 第 {i+1} 个文件处理失败")
        
        # 显示统计信息
        self._show_batch_statistics()
        
        return results
    
    def _show_batch_statistics(self) -> None:
        """显示批量处理统计信息"""
        logger.info("=" * 50)
        logger.info("批量处理完成!")
        logger.info(f"总处理文件数: {self.stats['processed_count']}")
        logger.info(f"成功: {self.stats['success_count']}")
        logger.info(f"失败: {self.stats['failed_count']}")
        logger.info(f"成功率: {self.stats['success_count']/self.stats['processed_count']*100:.1f}%")
        logger.info(f"总处理时间: {self.stats['total_processing_time']:.2f} 秒")
        logger.info(f"平均处理时间: {self.stats['total_processing_time']/self.stats['processed_count']:.2f} 秒/文件")
        logger.info("=" * 50)
    
    def get_available_background_sounds(self) -> Dict[str, Dict]:
        """获取可用的背景音效"""
        return self.background_sounds.copy()
    
    def get_default_combinations(self) -> List[List[str]]:
        """获取默认音效组合"""
        return self.default_combinations.copy()
    
    def scan_edgetts_output_folder(self) -> Dict[str, List[str]]:
        """
        扫描EdgeTTS输出文件夹，识别音频文件
        
        Returns:
            Dict[str, List[str]]: 文件夹名 -> 音频文件列表的映射
        """
        logger.info(f"扫描EdgeTTS输出文件夹: {self.edgetts_output_dir}")
        
        if not self.edgetts_output_dir.exists():
            logger.warning(f"EdgeTTS输出文件夹不存在: {self.edgetts_output_dir}")
            return {}
        
        folder_audio_map = {}
        
        # 扫描所有子文件夹
        for folder_path in self.edgetts_output_dir.iterdir():
            if folder_path.is_dir():
                folder_name = folder_path.name
                audio_files = []
                
                # 扫描文件夹中的音频文件
                for audio_file in folder_path.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        audio_files.append(str(audio_file))
                
                if audio_files:
                    folder_audio_map[folder_name] = audio_files
                    logger.info(f"发现文件夹 '{folder_name}' 中有 {len(audio_files)} 个音频文件")
        
        return folder_audio_map
    
    def create_ffmpeg_output_folder(self, edgetts_folder_name: str) -> Path:
        """
        为EdgeTTS文件夹创建对应的FFmpeg输出文件夹
        
        Args:
            edgetts_folder_name: EdgeTTS文件夹名称
            
        Returns:
            Path: FFmpeg输出文件夹路径
        """
        # 创建FFmpeg输出文件夹名称：ffmpeg_原文件夹名
        ffmpeg_folder_name = f"ffmpeg_{edgetts_folder_name}"
        ffmpeg_output_path = self.output_dir / ffmpeg_folder_name
        ffmpeg_output_path.mkdir(exist_ok=True)
        
        logger.info(f"创建FFmpeg输出文件夹: {ffmpeg_output_path}")
        return ffmpeg_output_path
    
    def process_folder_batch(self, edgetts_folder_name: str, 
                           background_combination: List[str] = None,
                           main_volume: float = 0.85) -> Dict:
        """
        批量处理EdgeTTS文件夹中的所有音频
        
        Args:
            edgetts_folder_name: EdgeTTS文件夹名称
            background_combination: 背景音效组合
            main_volume: 主音频音量
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"开始批量处理文件夹: {edgetts_folder_name}")
        
        # 扫描EdgeTTS文件夹
        folder_audio_map = self.scan_edgetts_output_folder()
        
        if edgetts_folder_name not in folder_audio_map:
            logger.error(f"未找到EdgeTTS文件夹: {edgetts_folder_name}")
            return {"success": False, "error": "文件夹不存在"}
        
        audio_files = folder_audio_map[edgetts_folder_name]
        logger.info(f"找到 {len(audio_files)} 个音频文件需要处理")
        
        # 创建FFmpeg输出文件夹
        ffmpeg_output_path = self.create_ffmpeg_output_folder(edgetts_folder_name)
        
        # 设置背景音效组合
        if background_combination is None:
            background_combination = random.choice(self.default_combinations)
        
        # 批量处理结果
        batch_results = {
            "edgetts_folder": edgetts_folder_name,
            "ffmpeg_folder": ffmpeg_output_path.name,
            "total_files": len(audio_files),
            "processed_files": [],
            "success_count": 0,
            "failed_count": 0,
            "background_sounds": background_combination,
            "main_volume": main_volume,
            "start_time": datetime.now().isoformat()
        }
        
        # 处理每个音频文件
        for i, audio_file in enumerate(audio_files):
            logger.info(f"处理第 {i+1}/{len(audio_files)} 个文件: {Path(audio_file).name}")
            
            # 生成输出文件名
            input_path = Path(audio_file)
            output_filename = f"ffmpeg_{input_path.stem}.m4a"
            output_file = ffmpeg_output_path / output_filename
            
            # 处理音频
            success = self.process_single_audio(
                input_file=audio_file,
                output_file=str(output_file),
                background_combination=background_combination,
                main_volume=main_volume
            )
            
            # 记录结果
            file_result = {
                "input_file": audio_file,
                "output_file": str(output_file),
                "success": success,
                "file_size": output_file.stat().st_size if success and output_file.exists() else 0
            }
            
            batch_results["processed_files"].append(file_result)
            
            if success:
                batch_results["success_count"] += 1
                logger.info(f"✓ 处理成功: {output_filename}")
            else:
                batch_results["failed_count"] += 1
                logger.error(f"✗ 处理失败: {output_filename}")
        
        # 完成统计
        batch_results["end_time"] = datetime.now().isoformat()
        batch_results["success_rate"] = batch_results["success_count"] / batch_results["total_files"] * 100
        
        # 保存批量处理记录
        self.batch_records[edgetts_folder_name] = batch_results
        
        # 显示结果
        self._show_batch_results(batch_results)
        
        return batch_results
    
    def _show_batch_results(self, batch_results: Dict) -> None:
        """显示批量处理结果"""
        logger.info("=" * 60)
        logger.info("批量处理完成!")
        logger.info(f"EdgeTTS文件夹: {batch_results['edgetts_folder']}")
        logger.info(f"FFmpeg文件夹: {batch_results['ffmpeg_folder']}")
        logger.info(f"总文件数: {batch_results['total_files']}")
        logger.info(f"成功: {batch_results['success_count']}")
        logger.info(f"失败: {batch_results['failed_count']}")
        logger.info(f"成功率: {batch_results['success_rate']:.1f}%")
        logger.info(f"背景音效: {batch_results['background_sounds']}")
        logger.info("=" * 60)
    
    def get_batch_records(self) -> Dict:
        """获取批量处理记录"""
        return self.batch_records.copy()
    
    def save_batch_records(self, records_file: str = None) -> None:
        """保存批量处理记录"""
        if records_file is None:
            records_file = self.output_dir / f"batch_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(self.batch_records, f, ensure_ascii=False, indent=2)
            logger.info(f"批量处理记录已保存到: {records_file}")
        except Exception as e:
            logger.error(f"保存批量处理记录失败: {e}")
    
    def create_custom_combination(self, sound_names: List[str]) -> bool:
        """创建自定义音效组合"""
        for sound_name in sound_names:
            if sound_name not in self.background_sounds:
                logger.error(f"不支持的音效: {sound_name}")
                return False
        
        self.default_combinations.append(sound_names)
        logger.info(f"添加自定义音效组合: {sound_names}")
        return True
    
    def save_processing_log(self, results: List[Dict], log_file: str = None) -> None:
        """保存处理日志"""
        if log_file is None:
            log_file = self.output_dir / f"processing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': results,
            'background_sounds': self.background_sounds,
            'default_combinations': self.default_combinations
        }
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            logger.info(f"处理日志已保存到: {log_file}")
        except Exception as e:
            logger.error(f"保存处理日志失败: {e}")

def main():
    """测试函数"""
    processor = FFmpegAudioProcessor()
    
    # 创建背景音效文件
    processor.create_background_sounds()
    
    # 测试单个文件处理
    test_input = "test_input.mp3"
    if os.path.exists(test_input):
        success = processor.process_single_audio(test_input)
        if success:
            print("单个音频处理测试成功!")
        else:
            print("单个音频处理测试失败!")
    else:
        print("测试输入文件不存在，跳过测试")

if __name__ == "__main__":
    main()
