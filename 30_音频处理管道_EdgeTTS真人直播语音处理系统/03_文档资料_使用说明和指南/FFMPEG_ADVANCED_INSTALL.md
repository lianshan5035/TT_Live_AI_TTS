# FFmpeg 高级音频处理扩展安装指南

本指南将帮助您安装支持高级音频处理功能的FFmpeg，包括高品质时间伸缩、变调、重采样和编码功能。

## 🎯 核心扩展库

### 1. librubberband - 高品质时间伸缩/变调
**功能**: 支持共振峰保持的时间伸缩和变调，是语音处理的核心
```bash
# macOS
brew install rubberband

# Ubuntu/Debian
sudo apt install rubberband-cli

# 验证
ffmpeg -filters | grep rubberband
```

### 2. libsoxr - SoX重采样器
**功能**: 高质量采样率转换，特别适合多次采样率转换场景
```bash
# macOS
brew install soxr

# Ubuntu/Debian
sudo apt install libsoxr-dev

# 验证
ffmpeg -h filter=aresample | grep soxr
```

### 3. libfdk_aac - 高品质AAC编码器
**功能**: TikTok/直播常用AAC编码，音质显著优于默认AAC
```bash
# macOS
brew install fdk-aac

# Ubuntu/Debian
sudo apt install libfdk-aac-dev

# 验证
ffmpeg -encoders | grep fdk_aac
```

### 4. libopus - 优秀低码率语音编码
**功能**: 适合实时流或体积更小的备份
```bash
# macOS
brew install opus

# Ubuntu/Debian
sudo apt install libopus-dev

# 验证
ffmpeg -encoders | grep opus
```

### 5. libspeex - 语音编解码器
**功能**: 适合语音带宽小场景
```bash
# macOS
brew install speex

# Ubuntu/Debian
sudo apt install libspeex-dev

# 验证
ffmpeg -encoders | grep speex
```

## 🔧 完整编译配置

### macOS 编译
```bash
# 安装依赖
brew install pkg-config yasm nasm
brew install rubberband soxr fdk-aac opus speex vorbis

# 下载FFmpeg源码
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg

# 配置编译选项
./configure \
  --prefix=/usr/local \
  --enable-gpl --enable-version3 --enable-nonfree \
  --enable-libmp3lame --enable-libfdk-aac \
  --enable-libopus --enable-libvorbis --enable-libsoxr \
  --enable-librubberband --enable-libspeex \
  --enable-ladspa --enable-lv2 \
  --enable-shared --enable-pic

# 编译安装
make -j$(nproc)
sudo make install
```

### Ubuntu/Debian 编译
```bash
# 安装依赖
sudo apt update
sudo apt install build-essential pkg-config yasm nasm
sudo apt install libmp3lame-dev libfdk-aac-dev libopus-dev
sudo apt install libvorbis-dev libsoxr-dev librubberband-dev
sudo apt install libspeex-dev ladspa-sdk lv2-dev

# 下载FFmpeg源码
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg

# 配置编译选项
./configure \
  --prefix=/usr/local \
  --enable-gpl --enable-version3 --enable-nonfree \
  --enable-libmp3lame --enable-libfdk-aac \
  --enable-libopus --enable-libvorbis --enable-libsoxr \
  --enable-librubberband --enable-libspeex \
  --enable-ladspa --enable-lv2 \
  --enable-shared --enable-pic

# 编译安装
make -j$(nproc)
sudo make install
sudo ldconfig
```

## 🎛️ 高级功能验证

### 检查所有支持的功能
```bash
# 检查编码器
ffmpeg -encoders | grep -E "(mp3lame|fdk_aac|opus|speex|vorbis)"

# 检查滤镜
ffmpeg -filters | grep -E "(rubberband|ladspa|lv2)"

# 检查重采样器
ffmpeg -h filter=aresample | grep soxr

# 查看完整构建配置
ffmpeg -buildconf
```

### 测试高级功能
```bash
# 测试Rubberband时间伸缩
ffmpeg -i input.wav -af "rubberband=tempo=1.2:pitch=1.1:formant=preserve" output.wav

# 测试SoX重采样
ffmpeg -i input.wav -af "aresample=resampler=soxr:osr=48000" output.wav

# 测试FDK-AAC编码
ffmpeg -i input.wav -c:a libfdk_aac -b:a 192k -profile:a aac_low output.m4a
```

## 🎵 LADSPA/LV2 插件支持

### 安装常用LADSPA插件
```bash
# macOS
brew install ladspa-sdk swh-plugins cmt

# Ubuntu/Debian
sudo apt install ladspa-sdk swh-plugins cmt

# 验证插件
ls /usr/lib/ladspa/  # 或 /usr/local/lib/ladspa/
```

### 常用LADSPA插件
- **压缩器**: `sc4_1882.so` (SWH Compressor)
- **混响**: `revdelay_1883.so` (SWH Reverb)
- **去齿音**: `deesser_1903.so` (SWH De-esser)
- **EQ**: `eq_1902.so` (SWH EQ)

### 使用LADSPA插件
```bash
# 使用压缩器
ffmpeg -i input.wav -af "ladspa=sc4_1882.so:sc4:1882" output.wav

# 使用混响
ffmpeg -i input.wav -af "ladspa=revdelay_1883.so:revdelay:1883" output.wav
```

## 🚀 性能优化

### GPU加速支持（可选）
```bash
# NVIDIA CUDA
./configure --enable-cuda --enable-cuvid --enable-nvenc

# AMD OpenCL
./configure --enable-opencl

# Intel QuickSync
./configure --enable-vaapi --enable-hwaccel=vaapi
```

### 多线程优化
```bash
# 启用多线程
./configure --enable-pthreads

# 运行时使用多线程
ffmpeg -threads 8 -i input.wav output.wav
```

## 🔍 故障排除

### 常见问题

#### 1. 找不到库文件
```bash
# 检查库路径
ldconfig -p | grep rubberband
pkg-config --libs rubberband
```

#### 2. 编译错误
```bash
# 清理重新编译
make clean
make distclean
./configure [options]
make -j$(nproc)
```

#### 3. 运行时错误
```bash
# 检查动态库
ldd $(which ffmpeg) | grep rubberband
```

### 验证安装
```bash
# 运行我们的检测脚本
python3 process_audio.py --dry-run --preview 1
```

## 📊 功能对比

| 功能 | 默认FFmpeg | 高级FFmpeg | 提升效果 |
|------|------------|------------|----------|
| 时间伸缩 | atempo | rubberband | 音质显著提升 |
| 变调 | asetrate | rubberband | 保持共振峰 |
| 重采样 | aresample | soxr | 减少失真 |
| AAC编码 | aac | fdk_aac | 音质提升30% |
| 插件支持 | 无 | ladspa/lv2 | 专业级效果 |

## 🎯 推荐配置

### TikTok直播场景
```bash
# 优先使用这些编码器
1. libfdk_aac (最佳音质)
2. libopus (低码率)
3. libmp3lame (兼容性)
```

### 语音处理场景
```bash
# 优先使用这些滤镜
1. rubberband (时间伸缩/变调)
2. soxr (重采样)
3. ladspa (专业效果)
```

## 📝 注意事项

1. **许可证**: libfdk_aac需要--enable-nonfree
2. **性能**: 高级功能可能增加处理时间
3. **兼容性**: 某些编码器需要特定容器格式
4. **内存**: LADSPA插件可能增加内存使用

## 🔗 相关资源

- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [Rubberband文档](https://breakfastquay.com/rubberband/)
- [SoX文档](http://sox.sourceforge.net/)
- [LADSPA插件列表](https://ladspa.org/plugins)

---

安装完成后，运行 `python3 process_audio.py --dry-run --preview 1` 来验证所有功能是否正常工作。
