#!/usr/bin/env python3
"""
EdgeTTS 批量语音后处理管线
零手工，自动防护所有常见异常
"""

import os
import sys
import json
import logging
import subprocess
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

import click
from tqdm import tqdm

# 设置日志
def setup_logging(log_dir: Path) -> logging.Logger:
    """设置日志系统"""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger('audio_pipeline')
    logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_dir / 'pipeline.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def detect_ffmpeg_features() -> Dict[str, bool]:
    """检测FFmpeg功能支持"""
    features = {
        'ffmpeg': False,
        'ffprobe': False,
        'rubberband': False,
        'mp3lame': False,
        'fdk_aac': False,
        'opus': False,
        'soxr': False,
        'speex': False,
        'ladspa': False,
        'lv2': False,
        'vorbis': False
    }
    
    # 检测ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            features['ffmpeg'] = True
            logger.info("✓ FFmpeg 已安装")
        else:
            logger.error("✗ FFmpeg 未正确安装")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.error("✗ FFmpeg 未找到")
    
    # 检测ffprobe
    try:
        result = subprocess.run(['ffprobe', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            features['ffprobe'] = True
            logger.info("✓ FFprobe 已安装")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.error("✗ FFprobe 未找到")
    
    # 检测rubberband支持
    if features['ffmpeg']:
        try:
            result = subprocess.run(['ffmpeg', '-filters'], 
                                  capture_output=True, text=True, timeout=10)
            if 'rubberband' in result.stdout:
                features['rubberband'] = True
                logger.info("✓ Rubberband 支持已启用")
            else:
                logger.warning("⚠ Rubberband 支持未启用，将使用atempo回退")
        except subprocess.TimeoutExpired:
            logger.warning("⚠ 无法检测Rubberband支持")
    
    # 检测编码器支持
    if features['ffmpeg']:
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], 
                                  capture_output=True, text=True, timeout=10)
            encoder_output = result.stdout
            
            # MP3编码器
            if 'libmp3lame' in encoder_output:
                features['mp3lame'] = True
                logger.info("✓ MP3编码支持已启用")
            
            # FDK-AAC编码器（高质量AAC）
            if 'libfdk_aac' in encoder_output:
                features['fdk_aac'] = True
                logger.info("✓ FDK-AAC编码支持已启用")
            
            # Opus编码器
            if 'libopus' in encoder_output:
                features['opus'] = True
                logger.info("✓ Opus编码支持已启用")
            
            # Speex编码器
            if 'libspeex' in encoder_output:
                features['speex'] = True
                logger.info("✓ Speex编码支持已启用")
            
            # Vorbis编码器
            if 'libvorbis' in encoder_output:
                features['vorbis'] = True
                logger.info("✓ Vorbis编码支持已启用")
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠ 无法检测编码器支持")
    
    # 检测重采样器支持
    if features['ffmpeg']:
        try:
            result = subprocess.run(['ffmpeg', '-filters'], 
                                  capture_output=True, text=True, timeout=10)
            filter_output = result.stdout
            
            # SoX重采样器
            if 'aresample' in filter_output:
                # 检查是否支持soxr
                result2 = subprocess.run(['ffmpeg', '-h', 'filter=aresample'], 
                                       capture_output=True, text=True, timeout=10)
                if 'soxr' in result2.stdout:
                    features['soxr'] = True
                    logger.info("✓ SoX重采样器支持已启用")
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠ 无法检测重采样器支持")
    
    # 检测LADSPA/LV2支持
    if features['ffmpeg']:
        try:
            result = subprocess.run(['ffmpeg', '-filters'], 
                                  capture_output=True, text=True, timeout=10)
            filter_output = result.stdout
            
            if 'ladspa' in filter_output:
                features['ladspa'] = True
                logger.info("✓ LADSPA插件支持已启用")
            
            if 'lv2' in filter_output:
                features['lv2'] = True
                logger.info("✓ LV2插件支持已启用")
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠ 无法检测插件支持")
    
    return features

def get_audio_info(file_path: Path) -> Dict[str, Any]:
    """获取音频文件信息"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"获取音频信息失败: {file_path}")
            return {}
        
        data = json.loads(result.stdout)
        
        # 查找音频流
        audio_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        if not audio_stream:
            logger.error(f"未找到音频流: {file_path}")
            return {}
        
        duration = float(data.get('format', {}).get('duration', 0))
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        
        return {
            'duration': duration,
            'sample_rate': sample_rate,
            'channels': channels,
            'codec': audio_stream.get('codec_name', 'unknown')
        }
    except Exception as e:
        logger.error(f"解析音频信息失败 {file_path}: {e}")
        return {}

def collect_inputs(input_dir: Path, preview: Optional[int] = None) -> List[Path]:
    """收集输入文件"""
    audio_extensions = {'.wav', '.mp3', '.aac', '.m4a', '.flac'}
    input_files = []
    
    for file_path in input_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            input_files.append(file_path)
    
    # 按文件名排序
    input_files.sort()
    
    # 预览模式限制数量
    if preview:
        input_files = input_files[:preview]
        logger.info(f"预览模式：只处理前 {preview} 个文件")
    
    logger.info(f"找到 {len(input_files)} 个音频文件")
    return input_files

def pick_background(ambience_dir: Path, duration: float) -> Optional[Dict[str, Any]]:
    """选择背景音效"""
    if not ambience_dir.exists() or not any(ambience_dir.iterdir()):
        logger.info("无背景素材，仅使用白噪音")
        return None
    
    # 收集背景文件
    bg_files = []
    for file_path in ambience_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {'.wav', '.mp3', '.aac'}:
            bg_files.append(file_path)
    
    if not bg_files:
        logger.info("背景目录为空，仅使用白噪音")
        return None
    
    # 随机选择背景文件
    bg_file = random.choice(bg_files)
    
    # 获取背景文件信息
    bg_info = get_audio_info(bg_file)
    if not bg_info:
        logger.warning(f"无法获取背景文件信息: {bg_file}")
        return None
    
    bg_duration = bg_info['duration']
    
    # 随机选择起点
    if bg_duration > duration:
        start_offset = random.uniform(0, bg_duration - duration)
        looped = False
    else:
        start_offset = random.uniform(0, bg_duration)
        looped = True
    
    return {
        'file': bg_file,
        'start_offset': start_offset,
        'volume': random.uniform(0.15, 0.35),
        'looped': looped,
        'duration': bg_duration
    }

def pick_events(events_dir: Path, duration: float, probability: float) -> List[Dict[str, Any]]:
    """选择事件音效"""
    events = []
    
    if not events_dir.exists() or not any(events_dir.iterdir()):
        logger.info("无事件音效素材")
        return events
    
    # 收集事件文件
    event_files = []
    for file_path in events_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {'.wav', '.mp3', '.aac'}:
            event_files.append(file_path)
    
    if not event_files:
        logger.info("事件目录为空")
        return events
    
    # 随机选择0-2个事件
    num_events = random.choices([0, 1, 2], weights=[1-probability, probability*0.7, probability*0.3])[0]
    
    for _ in range(num_events):
        if not event_files:
            break
        
        event_file = random.choice(event_files)
        event_files.remove(event_file)  # 避免重复选择
        
        # 获取事件文件信息
        event_info = get_audio_info(event_file)
        if not event_info:
            continue
        
        event_duration = event_info['duration']
        
        # 随机延迟时间（在音频的20%-80%之间）
        delay_start = duration * 0.2
        delay_end = duration * 0.8
        delay_ms = random.uniform(delay_start, delay_end) * 1000
        
        # 检查事件长度是否足够
        if event_duration < 1.0:  # 事件太短
            continue
        
        events.append({
            'file': event_file,
            'delay_ms': delay_ms,
            'volume': random.uniform(0.1, 0.3),
            'duration': event_duration
        })
    
    logger.info(f"选择了 {len(events)} 个事件音效")
    return events

def build_filter_chain(params: Dict[str, Any], features: Dict[str, bool]) -> str:
    """构建FFmpeg滤镜链"""
    filters = []
    
    # 1. 采样率转换（如果需要）
    if params['sample_rate'] not in [44100, 48000]:
        if features.get('soxr', False):
            filters.append('aresample=resampler=soxr:osr=48000')
            logger.info(f"使用SoX重采样器转换: {params['sample_rate']} -> 48000")
        else:
            filters.append('aresample=48000')
            logger.info(f"使用默认重采样器转换: {params['sample_rate']} -> 48000")
    
    # 2. 语速和音高调整
    if features['rubberband']:
        # 使用Rubberband
        tempo = params['tempo']
        pitch_semitones = params['pitch_semitones']
        pitch_ratio = 2 ** (pitch_semitones / 12)  # 转换为比例
        
        rubberband_params = f"tempo={tempo}:pitch={pitch_ratio}:formant=preserved"
        filters.append(f"rubberband={rubberband_params}")
        params['use_rubberband'] = True
    else:
        # 使用atempo回退
        tempo = params['tempo']
        params['use_rubberband'] = False
        
        if tempo < 0.5:
            # 多次串联atempo
            atempo_count = int(1 / tempo) + 1
            atempo_value = tempo ** (1 / atempo_count)
            for _ in range(atempo_count):
                filters.append(f"atempo={atempo_value}")
        elif tempo > 2.0:
            # 多次串联atempo
            atempo_count = int(tempo) + 1
            atempo_value = tempo ** (1 / atempo_count)
            for _ in range(atempo_count):
                filters.append(f"atempo={atempo_value}")
        else:
            filters.append(f"atempo={tempo}")
        
        logger.info(f"使用atempo回退: tempo={tempo}")
    
    # 3. 语音处理链
    voice_filters = [
        "acompressor=threshold=-18dB:ratio=3:attack=15:release=180:makeup=3",
        "equalizer=f=250:t=h:width=120:g=2",
        "equalizer=f=3500:t=h:width=800:g=2",
        "highpass=f=80"
    ]
    filters.extend(voice_filters)
    
    return ",".join(filters)

def build_ffmpeg_command(input_file: Path, output_file: Path, params: Dict[str, Any], 
                        features: Dict[str, bool]) -> List[str]:
    """构建FFmpeg命令"""
    cmd = ['ffmpeg', '-y']
    
    # 输入文件
    cmd.extend(['-i', str(input_file)])
    
    # 背景音效输入
    if params['background']:
        cmd.extend(['-i', str(params['background']['file'])])
    
    # 事件音效输入
    for event in params['events']:
        cmd.extend(['-i', str(event['file'])])
    
    # 构建滤镜复合命令
    filter_parts = []
    
    # 主音频处理
    main_filter = build_filter_chain(params, features)
    filter_parts.append(f"[0:a]{main_filter}[voice]")
    
    # 背景音效处理
    if params['background']:
        bg = params['background']
        bg_filters = [
            f"volume={bg['volume']}",
            f"atrim=start={bg['start_offset']}"
        ]
        
        if bg['looped']:
            bg_filters.append("aloop=loop=-1:size=2e+09")
        
        bg_filters.extend([
            "afade=t=in:ss=0:d=2",
            "afade=t=out:st=0:d=2"
        ])
        
        filter_parts.append(f"[1:a]{','.join(bg_filters)}[bg]")
    
    # 白噪音生成
    noise_amplitude = params['noise_amplitude']
    filter_parts.append(f"anoisesrc=color=pink:amplitude={noise_amplitude}[noise_raw]")
    filter_parts.append(f"[noise_raw]highpass=f=200,lowpass=f=9000[noise]")
    
    # 事件音效处理
    event_labels = []
    input_idx = 2 if params['background'] else 1
    
    for i, event in enumerate(params['events']):
        event_filters = [
            f"volume={event['volume']}",
            f"adelay={event['delay_ms']}|{event['delay_ms']}",
            "afade=t=in:ss=0:d=0.5",
            "afade=t=out:st=0:d=0.5"
        ]
        event_label = f"event{i}"
        event_labels.append(f"[{event_label}]")
        filter_parts.append(f"[{input_idx}:a]{','.join(event_filters)}[{event_label}]")
        input_idx += 1
    
    # 混合所有音效
    mix_inputs = ["[voice]"]
    mix_weights = ["1"]
    
    if params['background']:
        mix_inputs.append("[bg]")
        mix_weights.append("0.3")
    
    mix_inputs.append("[noise]")
    mix_weights.append("0.1")
    
    mix_inputs.extend(event_labels)
    mix_weights.extend(["0.2"] * len(event_labels))
    
    mix_filter = f"amix=inputs={len(mix_inputs)}:duration=first:weights={' '.join(mix_weights)}:dropout_transition=2[final]"
    filter_parts.append(mix_filter)
    
    # 最终处理
    filter_parts.append("[final]loudnorm=I=-19:TP=-2:LRA=9[out]")
    
    cmd.extend(['-filter_complex', ';'.join(filter_parts)])
    cmd.extend(['-map', '[out]'])
    
    # 输出编码（优先使用高质量编码器）
    if features.get('fdk_aac', False):
        cmd.extend(['-c:a', 'libfdk_aac', '-b:a', '192k', '-profile:a', 'aac_low'])
        logger.info("使用FDK-AAC高质量编码")
    elif features.get('mp3lame', False):
        cmd.extend(['-c:a', 'libmp3lame', '-b:a', '192k'])
        logger.info("使用MP3编码")
    else:
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        logger.info("使用默认AAC编码")
    
    cmd.extend(['-ar', '48000', '-ac', '2'])
    cmd.append(str(output_file))
    
    return cmd

def run_ffmpeg(cmd: List[str], timeout: int = 600) -> Tuple[bool, str, float]:
    """运行FFmpeg命令"""
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                               timeout=timeout, check=False)
        
        processing_time = time.time() - start_time
        
        if result.returncode == 0:
            return True, "", processing_time
        else:
            return False, result.stderr, processing_time
            
    except subprocess.TimeoutExpired:
        processing_time = time.time() - start_time
        return False, f"处理超时 ({timeout}s)", processing_time
    except Exception as e:
        processing_time = time.time() - start_time
        return False, str(e), processing_time

def process_file(input_file: Path, output_dir: Path, params: Dict[str, Any], 
                features: Dict[str, bool], skip_existing: bool = False) -> Dict[str, Any]:
    """处理单个文件"""
    logger.info(f"处理文件: {input_file.name}")
    
    # 生成输出文件路径
    output_file = output_dir / f"{input_file.stem}.mp3"
    
    # 检查是否跳过
    if skip_existing and output_file.exists():
        logger.info(f"跳过已存在文件: {output_file.name}")
        return {
            'input_file': str(input_file),
            'output_file': str(output_file),
            'status': 'skipped',
            'reason': 'file_exists'
        }
    
    # 获取音频信息
    audio_info = get_audio_info(input_file)
    if not audio_info:
        return {
            'input_file': str(input_file),
            'output_file': str(output_file),
            'status': 'failed',
            'reason': 'invalid_audio'
        }
    
    # 更新参数
    params.update({
        'duration': audio_info['duration'],
        'sample_rate': audio_info['sample_rate'],
        'channels': audio_info['channels']
    })
    
    # 检查音频长度
    if audio_info['duration'] < 3.0:
        logger.warning(f"音频过短 ({audio_info['duration']:.1f}s)，跳过环境音效")
        params['background'] = None
        params['events'] = []
    
    if audio_info['duration'] > 600:  # 10分钟
        logger.warning(f"音频过长 ({audio_info['duration']:.1f}s)，可能影响处理速度")
        params['warning'] = 'long_audio'
    
    # 构建FFmpeg命令
    cmd = build_ffmpeg_command(input_file, output_file, params, features)
    
    # 运行FFmpeg
    success, error_msg, processing_time = run_ffmpeg(cmd)
    
    # 准备结果（确保所有Path对象转换为字符串）
    def convert_paths(obj):
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: convert_paths(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_paths(item) for item in obj]
        else:
            return obj
    
    result = {
        'input_file': str(input_file),
        'output_file': str(output_file),
        'duration': audio_info['duration'],
        'tempo': params['tempo'],
        'pitch_semitones': params['pitch_semitones'],
        'use_rubberband': params.get('use_rubberband', False),
        'background': convert_paths(params['background']),
        'events': convert_paths(params['events']),
        'noise_amplitude': params['noise_amplitude'],
        'fallback_atempo': not params.get('use_rubberband', True),
        'ffmpeg_command': ' '.join(cmd),
        'processing_time_sec': processing_time,
        'status': 'success' if success else 'failed'
    }
    
    if not success:
        result['error'] = error_msg
        logger.error(f"处理失败: {input_file.name} - {error_msg}")
        
        # 保存错误日志
        error_log_file = Path('logs/failed') / f"{input_file.stem}.log"
        error_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(error_log_file, 'w', encoding='utf-8') as f:
            f.write(f"File: {input_file}\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Error: {error_msg}\n")
    else:
        logger.info(f"✓ 处理完成: {output_file.name}")
    
    return result

# 全局logger变量
logger = None

@click.command()
@click.option('--input-dir', default='audio_pipeline/input_raw', 
              help='输入目录')
@click.option('--output-dir', default='audio_pipeline/output_processed', 
              help='输出目录')
@click.option('--ambience-dir', default='audio_pipeline/assets/ambience', 
              help='背景音效目录')
@click.option('--events-dir', default='audio_pipeline/assets/events', 
              help='事件音效目录')
@click.option('--threads', default=None, type=int, 
              help='处理线程数')
@click.option('--preview', default=None, type=int, 
              help='只处理前N个文件')
@click.option('--tempo-range', nargs=2, default=[0.97, 1.03], type=float, 
              help='语速范围')
@click.option('--pitch-range', nargs=2, default=[-0.4, 0.4], type=float, 
              help='音高范围（半音）')
@click.option('--noise-range', nargs=2, default=[0.008, 0.015], type=float, 
              help='白噪音幅度范围')
@click.option('--ambience-volume', nargs=2, default=[0.15, 0.35], type=float, 
              help='背景音效音量范围')
@click.option('--event-prob', default=0.15, type=float, 
              help='事件音效概率')
@click.option('--seed', default=None, type=int, 
              help='随机种子')
@click.option('--dry-run', is_flag=True, 
              help='仅打印命令，不执行')
@click.option('--skip-existing', is_flag=True, 
              help='跳过已存在的输出文件')
def main(input_dir, output_dir, ambience_dir, events_dir, threads, preview,
         tempo_range, pitch_range, noise_range, ambience_volume, event_prob,
         seed, dry_run, skip_existing):
    """EdgeTTS 批量语音后处理管线"""
    global logger
    
    # 设置日志
    logger = setup_logging(Path('audio_pipeline/logs'))
    
    # 设置随机种子
    if seed is not None:
        random.seed(seed)
        logger.info(f"使用随机种子: {seed}")
    
    logger.info("=" * 60)
    logger.info("EdgeTTS 批量语音后处理管线启动")
    logger.info("=" * 60)
    
    # 检测FFmpeg功能
    logger.info("检测FFmpeg功能...")
    features = detect_ffmpeg_features()
    
    if not features['ffmpeg']:
        logger.error("FFmpeg未安装或不可用，请参考README安装")
        sys.exit(1)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 收集输入文件
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"输入目录不存在: {input_path}")
        sys.exit(1)
    
    input_files = collect_inputs(input_path, preview)
    if not input_files:
        logger.error("未找到输入文件")
        sys.exit(1)
    
    # 处理文件
    results = []
    start_time = time.time()
    
    if dry_run:
        logger.info("干运行模式：仅显示命令")
        for input_file in input_files[:3]:  # 只显示前3个
            params = {
                'tempo': random.uniform(*tempo_range),
                'pitch_semitones': random.uniform(*pitch_range),
                'noise_amplitude': random.uniform(*noise_range),
                'background': pick_background(Path(ambience_dir), 60),
                'events': pick_events(Path(events_dir), 60, event_prob)
            }
            cmd = build_ffmpeg_command(input_file, output_path / f"{input_file.stem}.mp3", 
                                     params, features)
            logger.info(f"命令: {' '.join(cmd)}")
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            for input_file in input_files:
                # 生成随机参数
                params = {
                    'tempo': random.uniform(*tempo_range),
                    'pitch_semitones': random.uniform(*pitch_range),
                    'noise_amplitude': random.uniform(*noise_range),
                    'background': pick_background(Path(ambience_dir), 60),  # 假设60秒
                    'events': pick_events(Path(events_dir), 60, event_prob)
                }
                
                future = executor.submit(process_file, input_file, output_path, 
                                        params, features, skip_existing)
                futures.append(future)
            
            # 收集结果
            with tqdm(total=len(futures), desc="处理进度") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)
    
    # 统计结果
    total_time = time.time() - start_time
    success_count = len([r for r in results if r['status'] == 'success'])
    failed_count = len([r for r in results if r['status'] == 'failed'])
    skipped_count = len([r for r in results if r['status'] == 'skipped'])
    
    logger.info("=" * 60)
    logger.info("处理完成!")
    logger.info("=" * 60)
    logger.info(f"总文件数: {len(results)}")
    logger.info(f"成功处理: {success_count}")
    logger.info(f"处理失败: {failed_count}")
    logger.info(f"跳过文件: {skipped_count}")
    logger.info(f"总耗时: {total_time:.1f} 秒")
    
    # 保存结果JSON
    results_file = Path('audio_pipeline/logs') / f"results_{int(time.time())}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结果已保存: {results_file}")
    
    if failed_count > 0:
        logger.warning(f"有 {failed_count} 个文件处理失败，请检查日志")
        sys.exit(1)

if __name__ == '__main__':
    main()
