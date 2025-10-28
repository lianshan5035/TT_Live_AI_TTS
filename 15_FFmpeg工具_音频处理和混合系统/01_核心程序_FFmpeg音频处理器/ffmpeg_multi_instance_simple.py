#!/usr/bin/env python3
"""
FFmpeg 多实例并发处理器 - 简化版
针对TikTok半无人直播场景的高效音频处理方案
不依赖外部库，使用标准库实现多进程优化
"""

import os
import sys
import time
import logging
import multiprocessing
import subprocess
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Optional
import random

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from ffmpeg_audio_processor import FFmpegAudioProcessor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_single_file_worker(task: Dict) -> Dict:
    """单个文件处理工作函数 - 独立进程"""
    try:
        input_file = task['input_file']
        output_file = task['output_file']
        background_combination = task['background_combination']
        main_volume = task['main_volume']
        
        # 创建FFmpeg处理器实例
        processor = FFmpegAudioProcessor()
        
        # 获取主音频时长
        main_duration = processor.get_audio_duration(input_file)
        
        # 构建FFmpeg命令
        cmd = ['ffmpeg', '-y']
        
        # 添加输入文件
        cmd.extend(['-i', input_file])
        
        # 添加背景音效输入
        background_inputs = []
        background_filters = []
        
        for i, sound_name in enumerate(background_combination):
            if sound_name in processor.background_sounds:
                sound_file = processor.background_sounds_dir / processor.background_sounds[sound_name]['file']
                if sound_file.exists():
                    cmd.extend(['-i', str(sound_file)])
                    background_inputs.append(f'[{i+1}:a]')
                    volume = processor.background_sounds[sound_name]['volume']
                    
                    # 对于白噪音，使用截取模式，其他音效使用循环模式
                    if sound_name == "white_noise":
                        background_filters.append(f'[{i+1}:a]volume={volume},atrim=duration={main_duration}[bg{i}]')
                    else:
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
            filter_parts.append('[main][bgmix]amix=inputs=2:duration=first:weights=1 0.25[final]')
        else:
            filter_parts.append('[main]volume=0.9[final]')
        
        # 添加滤镜
        cmd.extend(['-filter_complex', ';'.join(filter_parts)])
        
        # 输出设置
        cmd.extend(['-map', '[final]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-ac', '2'])
        cmd.extend(['-f', 'mp4'])
        
        # 性能优化参数
        cmd.extend(['-threads', '2'])  # 限制每个FFmpeg进程的线程数
        cmd.extend(['-preset', 'fast'])  # 快速编码预设
        
        cmd.append(output_file)
        
        # 执行处理
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            return {
                'success': True,
                'processing_time': processing_time,
                'file_size': file_size,
                'output_file': output_file,
                'task_id': task['task_id']
            }
        else:
            return {
                'success': False,
                'error': result.stderr,
                'processing_time': processing_time,
                'task_id': task['task_id']
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'processing_time': 0,
            'task_id': task.get('task_id', -1)
        }

class FFmpegMultiInstanceProcessor:
    """FFmpeg多实例处理器 - 简化版"""
    
    def __init__(self, max_workers: int = None):
        """
        初始化多实例处理器
        
        Args:
            max_workers: 最大工作进程数
        """
        # 系统资源检测
        self.cpu_count = multiprocessing.cpu_count()
        
        # 配置参数
        self.max_workers = max_workers or min(self.cpu_count, 8)  # 默认不超过8个进程
        
        # 处理器实例
        self.processor = FFmpegAudioProcessor()
        
        logger.info(f"FFmpeg多实例处理器初始化完成")
        logger.info(f"CPU核心数: {self.cpu_count}")
        logger.info(f"最大工作进程: {self.max_workers}")
    
    def process_files_parallel(self, 
                              input_files: List[str],
                              background_combinations: List[List[str]] = None,
                              main_volume: float = 0.88,
                              output_dir: str = None) -> Dict:
        """
        并行处理多个音频文件
        
        Args:
            input_files: 输入文件列表
            background_combinations: 背景音效组合列表
            main_volume: 主音频音量
            output_dir: 输出目录
            
        Returns:
            Dict: 处理结果统计
        """
        logger.info(f"开始并行处理 {len(input_files)} 个音频文件")
        logger.info(f"使用 {self.max_workers} 个工作进程")
        
        # 准备任务
        tasks = []
        for i, input_file in enumerate(input_files):
            # 生成输出文件名
            input_path = Path(input_file)
            if output_dir:
                output_file = Path(output_dir) / f"processed_{input_path.stem}.m4a"
            else:
                output_file = self.processor.output_dir / f"processed_{input_path.stem}.m4a"
            
            # 选择背景音效组合
            if background_combinations and i < len(background_combinations):
                bg_combo = background_combinations[i]
            else:
                bg_combo = random.choice(self.processor.default_combinations)
            
            task = {
                'input_file': input_file,
                'output_file': str(output_file),
                'background_combination': bg_combo,
                'main_volume': main_volume,
                'task_id': i
            }
            tasks.append(task)
        
        # 并行处理
        results = []
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(process_single_file_worker, task): task 
                for task in tasks
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    result['input_file'] = task['input_file']
                    result['output_file'] = task['output_file']
                    results.append(result)
                    
                    if result['success']:
                        logger.info(f"✓ 处理成功: {Path(task['input_file']).name}")
                    else:
                        logger.error(f"✗ 处理失败: {Path(task['input_file']).name} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"任务执行异常: {task['input_file']} - {e}")
                    results.append({
                        'task_id': task['task_id'],
                        'input_file': task['input_file'],
                        'output_file': task['output_file'],
                        'success': False,
                        'error': str(e),
                        'processing_time': 0
                    })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计结果
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        total_size = sum(r.get('file_size', 0) for r in results if r['success'])
        
        result_summary = {
            'total_files': len(input_files),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(input_files)) * 100 if input_files else 0,
            'total_processing_time': total_time,
            'average_time_per_file': total_time / len(input_files) if input_files else 0,
            'total_output_size': total_size,
            'files_per_second': len(input_files) / total_time if total_time > 0 else 0,
            'mb_per_second': (total_size / 1024 / 1024) / total_time if total_time > 0 else 0,
            'detailed_results': results
        }
        
        logger.info("=" * 60)
        logger.info("并行处理完成!")
        logger.info(f"总文件数: {result_summary['total_files']}")
        logger.info(f"成功: {result_summary['successful']}")
        logger.info(f"失败: {result_summary['failed']}")
        logger.info(f"成功率: {result_summary['success_rate']:.1f}%")
        logger.info(f"总处理时间: {result_summary['total_processing_time']:.2f} 秒")
        logger.info(f"平均每文件: {result_summary['average_time_per_file']:.2f} 秒")
        logger.info(f"处理速度: {result_summary['files_per_second']:.2f} 文件/秒")
        logger.info(f"数据吞吐: {result_summary['mb_per_second']:.2f} MB/秒")
        logger.info("=" * 60)
        
        return result_summary
    
    def process_folder_batch_parallel(self, 
                                    edgetts_folder_name: str,
                                    background_combination: List[str] = None,
                                    main_volume: float = 0.88) -> Dict:
        """
        并行处理EdgeTTS文件夹批量
        
        Args:
            edgetts_folder_name: EdgeTTS文件夹名称
            background_combination: 背景音效组合
            main_volume: 主音频音量
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"开始并行处理EdgeTTS文件夹: {edgetts_folder_name}")
        
        # 扫描EdgeTTS文件夹
        folder_audio_map = self.processor.scan_edgetts_output_folder()
        
        if edgetts_folder_name not in folder_audio_map:
            logger.error(f"未找到EdgeTTS文件夹: {edgetts_folder_name}")
            return {"success": False, "error": "文件夹不存在"}
        
        audio_files = folder_audio_map[edgetts_folder_name]
        logger.info(f"找到 {len(audio_files)} 个音频文件需要处理")
        
        # 创建FFmpeg输出文件夹
        ffmpeg_output_path = self.processor.create_ffmpeg_output_folder(edgetts_folder_name)
        
        # 设置背景音效组合
        if background_combination is None:
            background_combination = random.choice(self.processor.default_combinations)
        
        # 并行处理
        result = self.process_files_parallel(
            input_files=audio_files,
            background_combinations=[background_combination] * len(audio_files),
            main_volume=main_volume,
            output_dir=str(ffmpeg_output_path)
        )
        
        # 添加文件夹信息
        result['edgetts_folder'] = edgetts_folder_name
        result['ffmpeg_folder'] = ffmpeg_output_path.name
        result['background_sounds'] = background_combination
        
        return result
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        return {
            'cpu_count': self.cpu_count,
            'max_workers': self.max_workers,
            'ffmpeg_version': self._get_ffmpeg_version()
        }
    
    def _get_ffmpeg_version(self) -> str:
        """获取FFmpeg版本"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                return lines[0] if lines else "Unknown"
            return "Unknown"
        except:
            return "Not installed"

def main():
    """主函数 - 演示多实例处理"""
    logger.info("FFmpeg多实例处理器演示")
    
    # 初始化处理器
    processor = FFmpegMultiInstanceProcessor(max_workers=4)
    
    # 显示系统信息
    system_info = processor.get_system_info()
    logger.info("系统信息:")
    for key, value in system_info.items():
        logger.info(f"  {key}: {value}")
    
    # 演示并行处理
    logger.info("\n开始演示并行处理...")
    
    # 查找测试文件
    test_files = []
    edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
    if edgetts_dir.exists():
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        test_files.append(str(audio_file))
                        if len(test_files) >= 6:  # 限制测试文件数量
                            break
                if len(test_files) >= 6:
                    break
    
    if test_files:
        logger.info(f"找到 {len(test_files)} 个测试文件")
        
        # 并行处理
        result = processor.process_files_parallel(
            input_files=test_files,
            main_volume=0.88
        )
        
        logger.info("处理完成!")
    else:
        logger.warning("未找到测试文件")

if __name__ == "__main__":
    main()
