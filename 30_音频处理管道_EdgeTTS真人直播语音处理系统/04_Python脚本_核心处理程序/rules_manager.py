#!/usr/bin/env python3
"""
EdgeTTS音频处理规则管理器
实时修改处理规则的工具
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import click
from datetime import datetime

class RulesManager:
    """规则管理器"""
    
    def __init__(self, config_file: str = "rules_config.json"):
        self.config_file = Path(config_file)
        self.rules = self.load_rules()
    
    def load_rules(self) -> Dict[str, Any]:
        """加载规则配置"""
        if not self.config_file.exists():
            self.create_default_rules()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载规则配置失败: {e}")
            return self.create_default_rules()
    
    def save_rules(self) -> bool:
        """保存规则配置"""
        try:
            # 更新最后修改时间
            self.rules['audio_processing_rules']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存规则配置失败: {e}")
            return False
    
    def create_default_rules(self) -> Dict[str, Any]:
        """创建默认规则"""
        return {
            "audio_processing_rules": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "description": "EdgeTTS音频处理实时规则配置"
            }
        }
    
    def get_rule(self, path: str) -> Any:
        """获取规则值"""
        keys = path.split('.')
        value = self.rules['audio_processing_rules']
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def set_rule(self, path: str, value: Any) -> bool:
        """设置规则值"""
        keys = path.split('.')
        current = self.rules['audio_processing_rules']
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值
        current[keys[-1]] = value
        return self.save_rules()
    
    def list_rules(self, category: Optional[str] = None) -> None:
        """列出所有规则"""
        rules = self.rules['audio_processing_rules']
        
        if category:
            if category in rules:
                self._print_category(category, rules[category], 0)
            else:
                print(f"未找到类别: {category}")
        else:
            for key, value in rules.items():
                if isinstance(value, dict):
                    print(f"\n📁 {key}:")
                    self._print_category(key, value, 1)
    
    def _print_category(self, name: str, data: Dict[str, Any], indent: int = 0) -> None:
        """打印类别内容"""
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}📁 {key}:")
                self._print_category(key, value, indent + 1)
            elif isinstance(value, list):
                print(f"{prefix}📋 {key}: {value}")
            else:
                print(f"{prefix}⚙️  {key}: {value}")
    
    def validate_rules(self) -> bool:
        """验证规则配置"""
        required_sections = [
            'tempo_adjustment',
            'pitch_adjustment', 
            'background_sounds',
            'event_sounds',
            'audio_enhancement',
            'quality_control',
            'output_settings'
        ]
        
        rules = self.rules['audio_processing_rules']
        missing = []
        
        for section in required_sections:
            if section not in rules:
                missing.append(section)
        
        if missing:
            print(f"❌ 缺少必要的规则配置: {', '.join(missing)}")
            return False
        
        print("✅ 规则配置验证通过")
        return True
    
    def reset_to_default(self) -> bool:
        """重置为默认规则"""
        self.rules = self.create_default_rules()
        return self.save_rules()
    
    def backup_rules(self) -> bool:
        """备份当前规则"""
        backup_file = f"rules_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
            print(f"✅ 规则已备份到: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    
    def restore_rules(self, backup_file: str) -> bool:
        """从备份恢复规则"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            return self.save_rules()
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

@click.group()
def cli():
    """EdgeTTS音频处理规则管理器"""
    pass

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
def list_rules(config):
    """列出所有规则"""
    manager = RulesManager(config)
    manager.list_rules()

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
@click.argument('path')
def get(config, path):
    """获取规则值"""
    manager = RulesManager(config)
    value = manager.get_rule(path)
    if value is not None:
        print(f"{path}: {value}")
    else:
        print(f"❌ 未找到规则: {path}")

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
@click.argument('path')
@click.argument('value')
def set(config, path, value):
    """设置规则值"""
    manager = RulesManager(config)
    
    # 尝试转换值类型
    try:
        # 尝试转换为数字
        if '.' in value:
            converted_value = float(value)
        else:
            converted_value = int(value)
    except ValueError:
        # 尝试转换为布尔值
        if value.lower() in ['true', 'false']:
            converted_value = value.lower() == 'true'
        else:
            # 保持字符串
            converted_value = value
    
    if manager.set_rule(path, converted_value):
        print(f"✅ 已设置 {path} = {converted_value}")
    else:
        print(f"❌ 设置失败")

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
def validate(config):
    """验证规则配置"""
    manager = RulesManager(config)
    manager.validate_rules()

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
def backup(config):
    """备份当前规则"""
    manager = RulesManager(config)
    manager.backup_rules()

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
@click.argument('backup_file')
def restore(config, backup_file):
    """从备份恢复规则"""
    manager = RulesManager(config)
    if manager.restore_rules(backup_file):
        print(f"✅ 已从 {backup_file} 恢复规则")
    else:
        print(f"❌ 恢复失败")

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
@click.confirmation_option(prompt='确定要重置为默认规则吗？')
def reset(config):
    """重置为默认规则"""
    manager = RulesManager(config)
    if manager.reset_to_default():
        print("✅ 已重置为默认规则")
    else:
        print("❌ 重置失败")

@cli.command()
@click.option('--config', default='rules_config.json', help='配置文件路径')
def interactive(config):
    """交互式规则编辑器"""
    manager = RulesManager(config)
    
    print("🎛️  EdgeTTS音频处理规则交互式编辑器")
    print("=" * 50)
    
    while True:
        print("\n可用命令:")
        print("1. list - 列出所有规则")
        print("2. get <path> - 获取规则值")
        print("3. set <path> <value> - 设置规则值")
        print("4. validate - 验证规则")
        print("5. backup - 备份规则")
        print("6. quit - 退出")
        
        try:
            command = input("\n请输入命令: ").strip().split()
            
            if not command:
                continue
            
            if command[0] == 'quit':
                break
            elif command[0] == 'list':
                manager.list_rules()
            elif command[0] == 'get' and len(command) > 1:
                value = manager.get_rule(command[1])
                if value is not None:
                    print(f"{command[1]}: {value}")
                else:
                    print(f"❌ 未找到规则: {command[1]}")
            elif command[0] == 'set' and len(command) > 2:
                path = command[1]
                value = ' '.join(command[2:])
                
                # 转换值类型
                try:
                    if '.' in value:
                        converted_value = float(value)
                    else:
                        converted_value = int(value)
                except ValueError:
                    if value.lower() in ['true', 'false']:
                        converted_value = value.lower() == 'true'
                    else:
                        converted_value = value
                
                if manager.set_rule(path, converted_value):
                    print(f"✅ 已设置 {path} = {converted_value}")
                else:
                    print(f"❌ 设置失败")
            elif command[0] == 'validate':
                manager.validate_rules()
            elif command[0] == 'backup':
                manager.backup_rules()
            else:
                print("❌ 无效命令")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == '__main__':
    cli()
