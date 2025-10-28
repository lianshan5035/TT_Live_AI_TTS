# EdgeTTS 到 FFmpeg 音频处理流程详解

## 🔄 完整处理流程

### 1. EdgeTTS 生成音频 → FFmpeg 处理流程

```
EdgeTTS生成音频 → 音频位置识别 → FFmpeg开始工作 → 输出处理结果
      ↓              ↓              ↓              ↓
   文本转语音     文件路径检测    背景音效混合    最终音频文件
```

## 🎯 关键步骤详解

### 步骤1: EdgeTTS 音频生成

#### 🎵 EdgeTTS 生成过程
```python
async def synthesize_single(self, text: str, output_file: str, 
                          voice_name: str = None, 
                          rate: str = "+0%", 
                          pitch: str = "+0Hz") -> bool:
    """
    生成单个音频文件
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径
        voice_name: 语音名称
        rate: 语速
        pitch: 音调
    """
    try:
        # 1. 构建SSML
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">'
        ssml += f'<voice name="{voice}">'
        ssml += f'<prosody rate="{rate}" pitch="{pitch}">'
        ssml += text
        ssml += '</prosody></voice></speak>'
        
        # 2. 生成音频
        communicate = edge_tts.Communicate(ssml, voice)
        await communicate.save(output_file)
        
        logger.info(f"TTS音频生成成功: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"TTS音频生成失败: {e}")
        return False
```

#### 📁 音频文件位置
```python
# EdgeTTS生成的音频文件位置
temp_tts_file = self.temp_dir / f"tts_{random.randint(1000, 9999)}.mp3"
# 例如: temp_audio/tts_1234.mp3
```

### 步骤2: FFmpeg 音频位置识别

#### 🔍 文件路径检测
```python
def process_single_audio(self, input_file: str, output_file: str = None,
                       background_combination: List[str] = None,
                       main_volume: float = 1.0) -> bool:
    """
    处理单个音频文件
    
    Args:
        input_file: EdgeTTS生成的音频文件路径
        output_file: FFmpeg处理后的输出文件路径
        background_combination: 背景音效组合
        main_volume: 主音频音量
    """
    # 1. 验证EdgeTTS生成的音频文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"EdgeTTS音频文件不存在: {input_file}")
        return False
    
    logger.info(f"检测到EdgeTTS音频文件: {input_file}")
    
    # 2. 获取音频文件信息
    file_size = os.path.getsize(input_file)
    logger.info(f"音频文件大小: {file_size} bytes")
    
    # 3. 获取音频时长
    duration = self.get_audio_duration(input_file)
    logger.info(f"音频时长: {duration:.2f} 秒")
```

#### ⏱️ 音频时长检测
```python
def get_audio_duration(self, audio_file: str) -> float:
    """获取EdgeTTS生成的音频文件时长"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"EdgeTTS音频时长检测成功: {duration:.2f} 秒")
            return duration
        else:
            logger.error(f"音频时长检测失败: {result.stderr}")
            return 0.0
    except Exception as e:
        logger.error(f"音频时长检测异常: {e}")
        return 0.0
```

### 步骤3: FFmpeg 开始工作

#### 🎛️ FFmpeg 命令构建
```python
def _build_ffmpeg_command(self, input_file: str, output_file: str,
                        background_combination: List[str],
                        main_volume: float) -> List[str]:
    """构建FFmpeg处理命令"""
    
    # 1. 获取EdgeTTS音频时长
    main_duration = self.get_audio_duration(input_file)
    logger.info(f"EdgeTTS音频时长: {main_duration:.2f} 秒")
    
    # 2. 基础FFmpeg命令
    cmd = ['ffmpeg', '-y']
    
    # 3. 添加EdgeTTS生成的音频作为主输入
    cmd.extend(['-i', input_file])  # EdgeTTS音频文件
    
    # 4. 添加背景音效输入
    background_inputs = []
    background_filters = []
    
    for i, sound_name in enumerate(background_combination):
        if sound_name in self.background_sounds:
            sound_file = self.background_sounds_dir / self.background_sounds[sound_name]['file']
            if sound_file.exists():
                cmd.extend(['-i', str(sound_file)])  # 背景音效文件
                background_inputs.append(f'[{i+1}:a]')
                volume = self.background_sounds[sound_name]['volume']
                
                # 白噪音：根据EdgeTTS音频时长截取
                if sound_name == "white_noise":
                    background_filters.append(f'[{i+1}:a]volume={volume},atrim=duration={main_duration}[bg{i}]')
                else:
                    # 其他音效：循环到EdgeTTS音频长度
                    background_filters.append(f'[{i+1}:a]volume={volume},aloop=loop=-1:size=2e+09,atrim=duration={main_duration}[bg{i}]')
    
    # 5. 构建滤镜链
    filter_parts = []
    
    # EdgeTTS音频处理
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
        
        # 最终混合：EdgeTTS音频 + 背景音效
        filter_parts.append('[main][bgmix]amix=inputs=2:duration=first:weights=1 0.3[final]')
    else:
        filter_parts.append('[main]volume=0.9[final]')
    
    # 6. 添加滤镜
    cmd.extend(['-filter_complex', ';'.join(filter_parts)])
    
    # 7. 输出设置
    cmd.extend(['-map', '[final]'])
    cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
    cmd.extend(['-ar', '44100', '-ac', '2'])
    cmd.extend(['-f', 'mp4'])
    cmd.append(output_file)
    
    return cmd
```

#### 🚀 FFmpeg 执行过程
```python
def process_single_audio(self, input_file: str, output_file: str = None,
                       background_combination: List[str] = None,
                       main_volume: float = 1.0) -> bool:
    """执行FFmpeg处理"""
    
    try:
        # 1. 构建FFmpeg命令
        cmd = self._build_ffmpeg_command(
            input_file, str(output_file), 
            background_combination, main_volume
        )
        
        logger.info("开始执行FFmpeg处理...")
        logger.info(f"FFmpeg命令: {' '.join(cmd)}")
        
        # 2. 执行FFmpeg处理
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        self.stats['total_processing_time'] += processing_time
        
        # 3. 检查处理结果
        if result.returncode == 0:
            self.stats['success_count'] += 1
            logger.info(f"FFmpeg处理成功: {output_file}")
            logger.info(f"处理耗时: {processing_time:.2f} 秒")
            return True
        else:
            self.stats['failed_count'] += 1
            logger.error(f"FFmpeg处理失败: {result.stderr}")
            return False
            
    except Exception as e:
        self.stats['failed_count'] += 1
        logger.error(f"FFmpeg处理异常: {e}")
        return False
```

## 🔄 完整集成流程

### AudioMixer 中的完整流程
```python
async def process_text_to_mixed_audio(self, text: str, output_file: str,
                                    mix_config: str = "natural",
                                    voice_name: str = "xiaoxiao") -> bool:
    """完整的文本到混合音频处理流程"""
    
    try:
        start_time = datetime.now()
        
        # 步骤1: EdgeTTS生成音频
        temp_tts_file = self.temp_dir / f"tts_{random.randint(1000, 9999)}.mp3"
        logger.info(f"正在生成TTS音频: {text[:30]}...")
        
        tts_success = await self.tts_processor.synthesize_single(
            text=text,
            output_file=str(temp_tts_file),
            voice_name=voice_name
        )
        
        if not tts_success:
            logger.error("EdgeTTS音频生成失败")
            return False
        
        logger.info(f"EdgeTTS音频生成成功: {temp_tts_file}")
        
        # 步骤2: FFmpeg识别音频位置并开始处理
        logger.info("FFmpeg开始识别音频位置...")
        
        config = self.mix_configs[mix_config]
        mix_success = self.ffmpeg_processor.process_single_audio(
            input_file=str(temp_tts_file),  # EdgeTTS生成的音频文件
            output_file=output_file,        # FFmpeg处理后的输出文件
            background_combination=config["background_sounds"],
            main_volume=config["main_volume"]
        )
        
        # 清理临时文件
        if temp_tts_file.exists():
            temp_tts_file.unlink()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        self.stats['processing_time'] += processing_time
        
        if mix_success:
            self.stats['success_count'] += 1
            logger.info(f"音频混合成功: {output_file}")
            logger.info(f"总处理时间: {processing_time:.2f} 秒")
            return True
        else:
            self.stats['failed_count'] += 1
            logger.error("音频混合失败")
            return False
            
    except Exception as e:
        self.stats['failed_count'] += 1
        logger.error(f"处理异常: {e}")
        return False
```

## 🎯 关键识别机制

### 1. 文件存在性检查
```python
# 检查EdgeTTS生成的音频文件是否存在
if not os.path.exists(input_file):
    logger.error(f"EdgeTTS音频文件不存在: {input_file}")
    return False

logger.info(f"检测到EdgeTTS音频文件: {input_file}")
```

### 2. 音频信息获取
```python
# 获取文件大小
file_size = os.path.getsize(input_file)
logger.info(f"音频文件大小: {file_size} bytes")

# 获取音频时长
duration = self.get_audio_duration(input_file)
logger.info(f"音频时长: {duration:.2f} 秒")
```

### 3. FFmpeg命令构建
```python
# 将EdgeTTS音频作为主输入
cmd.extend(['-i', input_file])  # EdgeTTS音频文件

# 根据EdgeTTS音频时长调整背景音效
if sound_name == "white_noise":
    background_filters.append(f'[{i+1}:a]volume={volume},atrim=duration={main_duration}[bg{i}]')
```

## 🚀 使用示例

### 1. 直接调用
```python
from audio_mixer import AudioMixer

# 创建音频混合器
mixer = AudioMixer("mixed_audio")

# 处理文本到混合音频
success = await mixer.process_text_to_mixed_audio(
    text="这是一个测试文本",
    output_file="output.m4a",
    mix_config="natural_live",
    voice_name="xiaoxiao"
)
```

### 2. 分步调用
```python
from edgetts_processor import EdgeTTSProcessor
from ffmpeg_audio_processor import FFmpegAudioProcessor

# 步骤1: EdgeTTS生成音频
tts_processor = EdgeTTSProcessor("temp_tts")
tts_success = await tts_processor.synthesize_single(
    text="测试文本",
    output_file="temp_audio.mp3",
    voice_name="xiaoxiao"
)

# 步骤2: FFmpeg处理音频
if tts_success:
    ffmpeg_processor = FFmpegAudioProcessor("processed_audio")
    ffmpeg_success = ffmpeg_processor.process_single_audio(
        input_file="temp_audio.mp3",  # EdgeTTS生成的音频
        output_file="final_output.m4a",
        background_combination=["white_noise", "room_tone"],
        main_volume=0.85
    )
```

## 📊 处理流程总结

```
EdgeTTS生成音频 → 文件路径检测 → 音频信息获取 → FFmpeg命令构建 → 执行处理 → 输出结果
      ↓              ↓              ↓              ↓              ↓          ↓
   文本转语音     文件存在检查    时长大小检测    命令参数构建    子进程执行   混合音频
```

这个流程确保了EdgeTTS生成的音频能够被FFmpeg正确识别和处理，实现从文本到最终混合音频的完整转换。
