#!/usr/bin/env python3
"""
EdgeTTS音频处理规则快速编辑器
简化版规则修改工具
"""

import json
import os
from pathlib import Path
from datetime import datetime

class QuickRulesEditor:
    """快速规则编辑器"""
    
    def __init__(self, config_file: str = "rules_config.json"):
        self.config_file = Path(config_file)
        self.rules = self.load_rules()
    
    def load_rules(self):
        """加载规则配置"""
        if not self.config_file.exists():
            print("❌ 规则配置文件不存在")
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载规则配置失败: {e}")
            return None
    
    def save_rules(self):
        """保存规则配置"""
        if not self.rules:
            return False
        
        try:
            self.rules['audio_processing_rules']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存规则配置失败: {e}")
            return False
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🎛️  EdgeTTS音频处理规则快速编辑器")
        print("="*60)
        print("1. 📊 语速调整设置")
        print("2. 🎵 音高调整设置") 
        print("3. 🌍 背景音效设置")
        print("4. 🔊 事件音效设置")
        print("5. ⚡ 音频增强设置")
        print("6. 📁 输出设置")
        print("7. 🔧 处理设置")
        print("8. 🎲 随机化设置")
        print("9. 📋 查看当前规则")
        print("0. 💾 保存并退出")
        print("="*60)
    
    def edit_tempo_settings(self):
        """编辑语速调整设置"""
        print("\n📊 语速调整设置")
        print("-" * 30)
        
        tempo = self.rules['audio_processing_rules']['tempo_adjustment']
        
        print(f"当前基础范围: {tempo['base_range']}")
        new_range = input("输入新的语速范围 (格式: 0.88,1.12): ").strip()
        
        if new_range:
            try:
                min_val, max_val = map(float, new_range.split(','))
                tempo['base_range'] = [min_val, max_val]
                print(f"✅ 已更新语速范围为: {tempo['base_range']}")
            except ValueError:
                print("❌ 输入格式错误")
        
        print(f"当前启用状态: {tempo['enabled']}")
        enable = input("是否启用语速调整? (y/n): ").strip().lower()
        if enable in ['y', 'yes']:
            tempo['enabled'] = True
        elif enable in ['n', 'no']:
            tempo['enabled'] = False
    
    def edit_pitch_settings(self):
        """编辑音高调整设置"""
        print("\n🎵 音高调整设置")
        print("-" * 30)
        
        pitch = self.rules['audio_processing_rules']['pitch_adjustment']
        
        print(f"当前基础范围: {pitch['base_range']}")
        new_range = input("输入新的音高范围 (格式: -0.4,0.4): ").strip()
        
        if new_range:
            try:
                min_val, max_val = map(float, new_range.split(','))
                pitch['base_range'] = [min_val, max_val]
                print(f"✅ 已更新音高范围为: {pitch['base_range']}")
            except ValueError:
                print("❌ 输入格式错误")
        
        print(f"当前启用状态: {pitch['enabled']}")
        enable = input("是否启用音高调整? (y/n): ").strip().lower()
        if enable in ['y', 'yes']:
            pitch['enabled'] = True
        elif enable in ['n', 'no']:
            pitch['enabled'] = False
    
    def edit_background_settings(self):
        """编辑背景音效设置"""
        print("\n🌍 背景音效设置")
        print("-" * 30)
        
        bg = self.rules['audio_processing_rules']['background_sounds']
        
        print(f"当前添加概率: {bg['probability']}")
        new_prob = input("输入新的添加概率 (0.0-1.0): ").strip()
        
        if new_prob:
            try:
                prob = float(new_prob)
                if 0.0 <= prob <= 1.0:
                    bg['probability'] = prob
                    print(f"✅ 已更新添加概率为: {bg['probability']}")
                else:
                    print("❌ 概率必须在0.0-1.0之间")
            except ValueError:
                print("❌ 输入格式错误")
        
        print(f"当前音量范围: {bg['volume_range']}")
        new_volume = input("输入新的音量范围 (格式: 0.15,0.35): ").strip()
        
        if new_volume:
            try:
                min_val, max_val = map(float, new_volume.split(','))
                bg['volume_range'] = [min_val, max_val]
                print(f"✅ 已更新音量范围为: {bg['volume_range']}")
            except ValueError:
                print("❌ 输入格式错误")
    
    def edit_event_settings(self):
        """编辑事件音效设置"""
        print("\n🔊 事件音效设置")
        print("-" * 30)
        
        events = self.rules['audio_processing_rules']['event_sounds']
        
        print(f"当前添加概率: {events['probability']}")
        new_prob = input("输入新的添加概率 (0.0-1.0): ").strip()
        
        if new_prob:
            try:
                prob = float(new_prob)
                if 0.0 <= prob <= 1.0:
                    events['probability'] = prob
                    print(f"✅ 已更新添加概率为: {events['probability']}")
                else:
                    print("❌ 概率必须在0.0-1.0之间")
            except ValueError:
                print("❌ 输入格式错误")
        
        print(f"当前最大事件数: {events['max_events_per_file']}")
        new_max = input("输入新的最大事件数: ").strip()
        
        if new_max:
            try:
                max_events = int(new_max)
                events['max_events_per_file'] = max_events
                print(f"✅ 已更新最大事件数为: {events['max_events_per_file']}")
            except ValueError:
                print("❌ 输入格式错误")
    
    def edit_enhancement_settings(self):
        """编辑音频增强设置"""
        print("\n⚡ 音频增强设置")
        print("-" * 30)
        
        enhancement = self.rules['audio_processing_rules']['audio_enhancement']
        
        print("1. 动态压缩器")
        print(f"   当前阈值: {enhancement['compressor']['threshold']}")
        new_threshold = input("输入新的阈值 (建议: -18): ").strip()
        if new_threshold:
            try:
                enhancement['compressor']['threshold'] = int(new_threshold)
                print(f"✅ 已更新压缩器阈值为: {enhancement['compressor']['threshold']}")
            except ValueError:
                print("❌ 输入格式错误")
        
        print("2. EQ设置")
        for i, band in enumerate(enhancement['equalizer']['bands']):
            print(f"   频段 {i+1}: {band['frequency']}Hz, 增益范围: {band['gain_range']}")
        
        print("3. 高通滤波器")
        print(f"   当前频率: {enhancement['highpass_filter']['frequency']}")
        new_freq = input("输入新的截止频率 (建议: 80): ").strip()
        if new_freq:
            try:
                enhancement['highpass_filter']['frequency'] = int(new_freq)
                print(f"✅ 已更新高通滤波器频率为: {enhancement['highpass_filter']['frequency']}")
            except ValueError:
                print("❌ 输入格式错误")
    
    def edit_output_settings(self):
        """编辑输出设置"""
        print("\n📁 输出设置")
        print("-" * 30)
        
        output = self.rules['audio_processing_rules']['output_settings']
        
        print(f"当前输出格式: {output['format']}")
        new_format = input("输入新的输出格式 (m4a/mp3/wav): ").strip().lower()
        if new_format in ['m4a', 'mp3', 'wav']:
            output['format'] = new_format
            print(f"✅ 已更新输出格式为: {output['format']}")
        
        print(f"当前比特率: {output['bitrate']}")
        new_bitrate = input("输入新的比特率 (建议: 192): ").strip()
        if new_bitrate:
            try:
                output['bitrate'] = int(new_bitrate)
                print(f"✅ 已更新比特率为: {output['bitrate']}")
            except ValueError:
                print("❌ 输入格式错误")
    
    def edit_processing_settings(self):
        """编辑处理设置"""
        print("\n🔧 处理设置")
        print("-" * 30)
        
        processing = self.rules['audio_processing_rules']['processing_settings']
        
        print(f"当前最大并行数: {processing['max_workers']}")
        new_workers = input("输入新的最大并行数 (建议: 4): ").strip()
        if new_workers:
            try:
                processing['max_workers'] = int(new_workers)
                print(f"✅ 已更新最大并行数为: {processing['max_workers']}")
            except ValueError:
                print("❌ 输入格式错误")
        
        print(f"当前超时时间: {processing['timeout']}")
        new_timeout = input("输入新的超时时间(秒) (建议: 600): ").strip()
        if new_timeout:
            try:
                processing['timeout'] = int(new_timeout)
                print(f"✅ 已更新超时时间为: {processing['timeout']}")
            except ValueError:
                print("❌ 输入格式错误")
    
    def edit_randomization_settings(self):
        """编辑随机化设置"""
        print("\n🎲 随机化设置")
        print("-" * 30)
        
        random_settings = self.rules['audio_processing_rules']['randomization']
        
        print(f"当前变化程度: {random_settings['variation_level']}")
        new_level = input("输入新的变化程度 (low/medium/high): ").strip().lower()
        if new_level in ['low', 'medium', 'high']:
            random_settings['variation_level'] = new_level
            print(f"✅ 已更新变化程度为: {random_settings['variation_level']}")
        
        print(f"当前种子模式: {random_settings['seed_mode']}")
        new_mode = input("输入新的种子模式 (auto/固定/随机): ").strip().lower()
        if new_mode in ['auto', '固定', '随机']:
            random_settings['seed_mode'] = new_mode
            print(f"✅ 已更新种子模式为: {random_settings['seed_mode']}")
    
    def show_current_rules(self):
        """显示当前规则"""
        print("\n📋 当前规则概览")
        print("-" * 30)
        
        rules = self.rules['audio_processing_rules']
        
        print(f"版本: {rules['version']}")
        print(f"最后更新: {rules['last_updated']}")
        print()
        
        print("📊 语速调整:")
        tempo = rules['tempo_adjustment']
        print(f"  启用: {tempo['enabled']}")
        print(f"  范围: {tempo['base_range']}")
        print()
        
        print("🎵 音高调整:")
        pitch = rules['pitch_adjustment']
        print(f"  启用: {pitch['enabled']}")
        print(f"  范围: {pitch['base_range']}")
        print()
        
        print("🌍 背景音效:")
        bg = rules['background_sounds']
        print(f"  启用: {bg['enabled']}")
        print(f"  概率: {bg['probability']}")
        print(f"  音量范围: {bg['volume_range']}")
        print()
        
        print("🔊 事件音效:")
        events = rules['event_sounds']
        print(f"  启用: {events['enabled']}")
        print(f"  概率: {events['probability']}")
        print(f"  最大事件数: {events['max_events_per_file']}")
        print()
        
        print("📁 输出设置:")
        output = rules['output_settings']
        print(f"  格式: {output['format']}")
        print(f"  比特率: {output['bitrate']}")
        print()
        
        print("🔧 处理设置:")
        processing = rules['processing_settings']
        print(f"  最大并行数: {processing['max_workers']}")
        print(f"  超时时间: {processing['timeout']}")
    
    def run(self):
        """运行编辑器"""
        if not self.rules:
            return
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\n请选择操作 (0-9): ").strip()
                
                if choice == '0':
                    if self.save_rules():
                        print("✅ 规则已保存")
                    else:
                        print("❌ 保存失败")
                    break
                elif choice == '1':
                    self.edit_tempo_settings()
                elif choice == '2':
                    self.edit_pitch_settings()
                elif choice == '3':
                    self.edit_background_settings()
                elif choice == '4':
                    self.edit_event_settings()
                elif choice == '5':
                    self.edit_enhancement_settings()
                elif choice == '6':
                    self.edit_output_settings()
                elif choice == '7':
                    self.edit_processing_settings()
                elif choice == '8':
                    self.edit_randomization_settings()
                elif choice == '9':
                    self.show_current_rules()
                else:
                    print("❌ 无效选择")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

if __name__ == '__main__':
    editor = QuickRulesEditor()
    editor.run()
