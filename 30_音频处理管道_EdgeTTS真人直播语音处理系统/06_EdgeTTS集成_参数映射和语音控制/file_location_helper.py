#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件位置显示工具
确保每次输出文件时都明确显示文件位置
"""

import os
import logging

def show_file_location(file_path: str, file_type: str = "文件") -> None:
    """
    显示文件的详细位置信息
    
    Args:
        file_path: 文件路径
        file_type: 文件类型描述
    """
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        full_path = os.path.abspath(file_path)
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        
        print("=" * 60)
        print(f"📁 {file_type}输出完成")
        print("=" * 60)
        print(f"📄 文件名: {filename}")
        print(f"📊 文件大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"📍 完整路径: {full_path}")
        print(f"📂 所在目录: {directory}")
        print("=" * 60)
        print(f"🎧 快速播放命令:")
        print(f"   open \"{full_path}\"")
        print("=" * 60)
        
        # 同时记录到日志
        logging.info(f"✅ {file_type}输出完成: {filename}")
        logging.info(f"📊 文件大小: {file_size:,} bytes")
        logging.info(f"📍 完整路径: {full_path}")
        logging.info(f"📁 所在目录: {directory}")
    else:
        print(f"❌ 文件不存在: {file_path}")
        logging.error(f"❌ 文件不存在: {file_path}")

def show_multiple_files(files: list, file_type: str = "文件") -> None:
    """
    显示多个文件的位置信息
    
    Args:
        files: 文件路径列表
        file_type: 文件类型描述
    """
    if not files:
        print(f"❌ 没有{file_type}输出")
        return
    
    print("=" * 60)
    print(f"📁 {file_type}批量输出完成 - 共{len(files)}个文件")
    print("=" * 60)
    
    for i, file_path in enumerate(files, 1):
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            full_path = os.path.abspath(file_path)
            filename = os.path.basename(full_path)
            
            print(f"{i}. 📄 {filename}")
            print(f"   📊 大小: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"   📍 路径: {full_path}")
            print()
        else:
            print(f"{i}. ❌ 文件不存在: {file_path}")
    
    print("=" * 60)
    print("🎧 批量播放命令:")
    for i, file_path in enumerate(files, 1):
        if os.path.exists(file_path):
            full_path = os.path.abspath(file_path)
            print(f"   {i}. open \"{full_path}\"")
    print("=" * 60)

def get_file_info(file_path: str) -> dict:
    """
    获取文件的详细信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        包含文件信息的字典
    """
    if not os.path.exists(file_path):
        return {"exists": False, "error": "文件不存在"}
    
    stat = os.stat(file_path)
    full_path = os.path.abspath(file_path)
    
    return {
        "exists": True,
        "filename": os.path.basename(full_path),
        "full_path": full_path,
        "directory": os.path.dirname(full_path),
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / 1024 / 1024,
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime
    }

if __name__ == "__main__":
    # 测试功能
    print("🧪 文件位置显示工具测试")
    
    # 测试单个文件
    test_file = "/Volumes/M2/TT_Live_AI_TTS/30_音频处理管道_EdgeTTS真人直播语音处理系统/06_EdgeTTS集成_参数映射和语音控制/test_specific_file_final.py"
    show_file_location(test_file, "测试脚本")
    
    # 测试文件信息获取
    info = get_file_info(test_file)
    if info["exists"]:
        print(f"📋 文件信息: {info}")
