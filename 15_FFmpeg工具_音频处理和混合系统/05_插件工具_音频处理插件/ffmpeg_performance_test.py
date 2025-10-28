#!/usr/bin/env python3
"""
FFmpeg 性能对比测试脚本
对比单进程 vs 多进程的处理性能
"""

import os
import sys
import time
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import subprocess

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "01_核心程序_FFmpeg音频处理器"))

from ffmpeg_audio_processor import FFmpegAudioProcessor
from ffmpeg_multi_instance_simple import FFmpegMultiInstanceProcessor, process_single_file_worker

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_process_performance(input_files: list, max_files: int = 10) -> dict:
    """测试单进程性能"""
    logger.info("=" * 60)
    logger.info("测试单进程性能")
    logger.info("=" * 60)
    
    # 限制测试文件数量
    test_files = input_files[:max_files]
    
    # 初始化单进程处理器
    processor = FFmpegAudioProcessor()
    
    start_time = time.time()
    successful = 0
    failed = 0
    total_size = 0
    
    for i, input_file in enumerate(test_files):
        logger.info(f"处理第 {i+1}/{len(test_files)} 个文件: {Path(input_file).name}")
        
        # 生成输出文件名
        input_path = Path(input_file)
        output_file = processor.output_dir / f"single_{input_path.stem}.m4a"
        
        # 处理音频
        success = processor.process_single_audio(
            input_file=input_file,
            output_file=str(output_file),
            background_combination=["white_noise", "room_tone"],
            main_volume=0.88
        )
        
        if success:
            successful += 1
            if os.path.exists(output_file):
                total_size += os.path.getsize(output_file)
            logger.info(f"✓ 处理成功: {Path(input_file).name}")
        else:
            failed += 1
            logger.error(f"✗ 处理失败: {Path(input_file).name}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return {
        'method': '单进程',
        'total_files': len(test_files),
        'successful': successful,
        'failed': failed,
        'success_rate': (successful / len(test_files)) * 100 if test_files else 0,
        'total_time': total_time,
        'average_time_per_file': total_time / len(test_files) if test_files else 0,
        'files_per_second': len(test_files) / total_time if total_time > 0 else 0,
        'total_size': total_size,
        'mb_per_second': (total_size / 1024 / 1024) / total_time if total_time > 0 else 0
    }

def test_multi_process_performance(input_files: list, max_files: int = 10, workers: int = 4) -> dict:
    """测试多进程性能"""
    logger.info("=" * 60)
    logger.info(f"测试多进程性能 ({workers}个进程)")
    logger.info("=" * 60)
    
    # 限制测试文件数量
    test_files = input_files[:max_files]
    
    # 初始化多进程处理器
    processor = FFmpegMultiInstanceProcessor(max_workers=workers)
    
    # 准备任务
    tasks = []
    for i, input_file in enumerate(test_files):
        input_path = Path(input_file)
        output_file = processor.processor.output_dir / f"multi_{input_path.stem}.m4a"
        
        task = {
            'input_file': input_file,
            'output_file': str(output_file),
            'background_combination': ["white_noise", "room_tone"],
            'main_volume': 0.88,
            'task_id': i
        }
        tasks.append(task)
    
    # 并行处理
    start_time = time.time()
    results = []
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_task = {
            executor.submit(process_single_file_worker, task): task 
            for task in tasks
        }
        
        for future in future_to_task:
            try:
                result = future.result()
                results.append(result)
                
                if result['success']:
                    logger.info(f"✓ 处理成功: {Path(result['input_file']).name}")
                else:
                    logger.error(f"✗ 处理失败: {Path(result['input_file']).name}")
                    
            except Exception as e:
                logger.error(f"任务执行异常: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计结果
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    total_size = sum(r.get('file_size', 0) for r in results if r['success'])
    
    return {
        'method': f'多进程({workers}个)',
        'total_files': len(test_files),
        'successful': successful,
        'failed': failed,
        'success_rate': (successful / len(test_files)) * 100 if test_files else 0,
        'total_time': total_time,
        'average_time_per_file': total_time / len(test_files) if test_files else 0,
        'files_per_second': len(test_files) / total_time if total_time > 0 else 0,
        'total_size': total_size,
        'mb_per_second': (total_size / 1024 / 1024) / total_time if total_time > 0 else 0
    }

def compare_performance(results: list):
    """对比性能结果"""
    logger.info("=" * 80)
    logger.info("性能对比结果")
    logger.info("=" * 80)
    
    # 打印表头
    print(f"{'方法':<15} {'文件数':<8} {'成功':<6} {'失败':<6} {'成功率':<8} {'总时间':<10} {'文件/秒':<10} {'MB/秒':<10}")
    print("-" * 80)
    
    # 打印结果
    for result in results:
        print(f"{result['method']:<15} "
              f"{result['total_files']:<8} "
              f"{result['successful']:<6} "
              f"{result['failed']:<6} "
              f"{result['success_rate']:<8.1f}% "
              f"{result['total_time']:<10.2f} "
              f"{result['files_per_second']:<10.2f} "
              f"{result['mb_per_second']:<10.2f}")
    
    # 计算性能提升
    if len(results) >= 2:
        single_result = results[0]
        multi_result = results[1]
        
        time_improvement = (single_result['total_time'] / multi_result['total_time']) if multi_result['total_time'] > 0 else 0
        speed_improvement = (multi_result['files_per_second'] / single_result['files_per_second']) if single_result['files_per_second'] > 0 else 0
        
        logger.info("=" * 80)
        logger.info("性能提升分析")
        logger.info("=" * 80)
        logger.info(f"时间提升: {time_improvement:.2f}x (多进程比单进程快 {time_improvement:.2f} 倍)")
        logger.info(f"速度提升: {speed_improvement:.2f}x (多进程比单进程快 {speed_improvement:.2f} 倍)")
        logger.info(f"效率提升: {((speed_improvement - 1) * 100):.1f}%")

def main():
    """主函数"""
    logger.info("FFmpeg性能对比测试")
    
    # 查找测试文件
    test_files = []
    edgetts_dir = Path("../../20_输出文件_处理完成的音频文件")
    if edgetts_dir.exists():
        for folder in edgetts_dir.iterdir():
            if folder.is_dir():
                for audio_file in folder.iterdir():
                    if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
                        test_files.append(str(audio_file))
                        if len(test_files) >= 20:  # 限制测试文件数量
                            break
                if len(test_files) >= 20:
                    break
    
    if not test_files:
        logger.error("未找到测试文件")
        return
    
    logger.info(f"找到 {len(test_files)} 个测试文件")
    
    # 测试不同配置
    test_configs = [
        {'max_files': 6, 'workers': 1, 'name': '单进程'},
        {'max_files': 6, 'workers': 2, 'name': '2进程'},
        {'max_files': 6, 'workers': 4, 'name': '4进程'},
        {'max_files': 6, 'workers': 8, 'name': '8进程'}
    ]
    
    results = []
    
    for config in test_configs:
        logger.info(f"\n开始测试: {config['name']}")
        
        if config['workers'] == 1:
            # 单进程测试
            result = test_single_process_performance(test_files, config['max_files'])
        else:
            # 多进程测试
            result = test_multi_process_performance(test_files, config['max_files'], config['workers'])
        
        results.append(result)
        
        # 等待一下，避免资源竞争
        time.sleep(2)
    
    # 对比结果
    compare_performance(results)
    
    logger.info("\n性能测试完成!")

if __name__ == "__main__":
    main()
