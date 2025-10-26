#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TT-Live-AI 共享情感配置模块
统一管理情感参数、默认配置和工具函数
"""

import random
from typing import Dict, Any

# A3 标准情感参数配置
EMOTION_PARAMS = {
    "Calm": {"rate": "-6%", "pitch": "-2%", "volume": "0dB"},
    "Friendly": {"rate": "+2%", "pitch": "+2%", "volume": "0dB"},
    "Confident": {"rate": "+4%", "pitch": "+1%", "volume": "+1dB"},
    "Playful": {"rate": "+6%", "pitch": "+3%", "volume": "+1dB"},
    "Excited": {"rate": "+10%", "pitch": "+4%", "volume": "+2dB"},
    "Urgent": {"rate": "+12%", "pitch": "+3%", "volume": "+2dB"},
}

# 默认配置
DEFAULT_VOICE = "en-US-JennyNeural"
MAX_CONCURRENT = 5

def get_emotion_params(emotion: str) -> Dict[str, str]:
    """
    获取指定情感的参数配置
    
    Args:
        emotion: 情感名称
        
    Returns:
        情感参数字典
    """
    return EMOTION_PARAMS.get(emotion, EMOTION_PARAMS["Friendly"])

def add_random_variation(params: Dict[str, str]) -> Dict[str, str]:
    """
    为情感参数添加随机变化，避免语音过于机械
    
    Args:
        params: 原始情感参数
        
    Returns:
        添加随机变化后的参数（不影响原始参数）
    """
    # 创建副本避免修改原始参数
    varied = params.copy()
    
    # 为 rate 添加随机变化
    if varied["rate"].startswith("+"):
        base = int(varied["rate"][1:-1])
        delta = random.randint(-2, 2)
        varied["rate"] = f"+{base + delta}%" if base + delta >= 0 else f"{base + delta}%"
    elif varied["rate"].startswith("-"):
        base = int(varied["rate"][1:-1])
        delta = random.randint(-1, 1)
        varied["rate"] = f"-{base + delta}%" if base + delta >= 0 else f"{base + delta}%"
    
    # 为 pitch 添加随机变化
    if varied["pitch"].startswith("+"):
        base = int(varied["pitch"][1:-1])
        delta = random.randint(-2, 2)
        varied["pitch"] = f"+{base + delta}%" if base + delta >= 0 else f"{base + delta}%"
    elif varied["pitch"].startswith("-"):
        base = int(varied["pitch"][1:-1])
        delta = random.randint(-1, 1)
        varied["pitch"] = f"-{base + delta}%" if base + delta >= 0 else f"{base + delta}%"
    
    return varied

def get_supported_emotions() -> list:
    """
    获取所有支持的情感列表
    
    Returns:
        情感名称列表
    """
    return list(EMOTION_PARAMS.keys())

def validate_emotion(emotion: str) -> bool:
    """
    验证情感名称是否有效
    
    Args:
        emotion: 情感名称
        
    Returns:
        是否有效
    """
    return emotion in EMOTION_PARAMS
