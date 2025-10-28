#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS参数实时调整Web界面
提供Web界面进行实时参数调整
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSConfigWebManager:
    """TTS配置Web管理器"""
    
    def __init__(self, config_file="29_配置管理_实时参数调整和系统配置/tts_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self):
        """默认配置"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "emotion_settings": {
                "emotion_parameters": {
                    "Urgent": {"rate_range": [0.8, 1.2], "pitch_range": [0.9, 1.1], "volume_range": [0.8, 1.0]},
                    "Calm": {"rate_range": [0.7, 0.9], "pitch_range": [0.8, 1.0], "volume_range": [0.7, 0.9]},
                    "Warm": {"rate_range": [0.8, 1.0], "pitch_range": [0.9, 1.1], "volume_range": [0.8, 1.0]},
                    "Excited": {"rate_range": [1.0, 1.3], "pitch_range": [1.0, 1.2], "volume_range": [0.9, 1.1]},
                    "Professional": {"rate_range": [0.8, 1.0], "pitch_range": [0.9, 1.0], "volume_range": [0.8, 1.0]}
                }
            },
            "system_settings": {
                "max_concurrent": 12,
                "batch_size": 80,
                "batch_delay": 2,
                "file_delay": 5
            }
        }
    
    def save_config(self):
        """保存配置"""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        return True
    
    def update_emotion_parameter(self, emotion, parameter, value):
        """更新情绪参数"""
        if emotion in self.config["emotion_settings"]["emotion_parameters"]:
            self.config["emotion_settings"]["emotion_parameters"][emotion][parameter] = value
            return self.save_config()
        return False

# 创建配置管理器实例
config_manager = TTSConfigWebManager()

@app.route('/')
def index():
    """主页"""
    return render_template('config_index.html', config=config_manager.config)

@app.route('/api/config')
def get_config():
    """获取配置API"""
    return jsonify(config_manager.config)

@app.route('/api/update_emotion', methods=['POST'])
def update_emotion():
    """更新情绪参数API"""
    try:
        data = request.json
        emotion = data.get('emotion')
        parameter = data.get('parameter')
        value = data.get('value')
        
        if config_manager.update_emotion_parameter(emotion, parameter, value):
            return jsonify({"success": True, "message": "参数更新成功"})
        else:
            return jsonify({"success": False, "message": "参数更新失败"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/update_system', methods=['POST'])
def update_system():
    """更新系统参数API"""
    try:
        data = request.json
        parameter = data.get('parameter')
        value = data.get('value')
        
        config_manager.config["system_settings"][parameter] = value
        if config_manager.save_config():
            return jsonify({"success": True, "message": "系统参数更新成功"})
        else:
            return jsonify({"success": False, "message": "系统参数更新失败"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/reset_config', methods=['POST'])
def reset_config():
    """重置配置API"""
    try:
        config_manager.config = config_manager.get_default_config()
        if config_manager.save_config():
            return jsonify({"success": True, "message": "配置已重置"})
        else:
            return jsonify({"success": False, "message": "配置重置失败"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    # 确保模板目录存在
    os.makedirs('templates', exist_ok=True)
    
    # 创建简单的HTML模板
    html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTS参数实时调整</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .emotion-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .emotion-card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; background: #f9f9f9; }
        .parameter-group { margin-bottom: 15px; }
        .parameter-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .parameter-group input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
        .button.danger { background: #dc3545; }
        .button.danger:hover { background: #c82333; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .system-params { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 TTS参数实时调整系统</h1>
            <p>实时调整语音生成参数，无需重启服务</p>
        </div>

        <div id="status"></div>

        <div class="section">
            <h2>🎭 情绪参数调整</h2>
            <div class="emotion-grid" id="emotionGrid">
                <!-- 情绪参数将在这里动态加载 -->
            </div>
        </div>

        <div class="section">
            <h2>📊 系统参数调整</h2>
            <div class="system-params" id="systemParams">
                <!-- 系统参数将在这里动态加载 -->
            </div>
        </div>

        <div class="section">
            <h2>🛠️ 系统操作</h2>
            <button class="button" onclick="refreshConfig()">🔄 刷新配置</button>
            <button class="button danger" onclick="resetConfig()">🔄 重置为默认</button>
            <button class="button" onclick="exportConfig()">📥 导出配置</button>
        </div>
    </div>

    <script>
        let currentConfig = null;

        // 页面加载时获取配置
        window.onload = function() {
            loadConfig();
        };

        // 加载配置
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                currentConfig = await response.json();
                renderEmotionParams();
                renderSystemParams();
            } catch (error) {
                showStatus('配置加载失败: ' + error.message, 'error');
            }
        }

        // 渲染情绪参数
        function renderEmotionParams() {
            const grid = document.getElementById('emotionGrid');
            grid.innerHTML = '';

            const emotions = currentConfig.emotion_settings.emotion_parameters;
            const emotionNames = {
                'Urgent': '紧迫型',
                'Calm': '舒缓型', 
                'Warm': '温暖型',
                'Excited': '兴奋型',
                'Professional': '专业型'
            };

            for (const [emotion, params] of Object.entries(emotions)) {
                const card = document.createElement('div');
                card.className = 'emotion-card';
                
                card.innerHTML = `
                    <h3>${emotionNames[emotion] || emotion}</h3>
                    <div class="parameter-group">
                        <label>语速范围 (Rate Range)</label>
                        <input type="number" id="${emotion}_rate_min" value="${params.rate_range[0]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'rate_range', 0, this.value)">
                        <input type="number" id="${emotion}_rate_max" value="${params.rate_range[1]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'rate_range', 1, this.value)">
                    </div>
                    <div class="parameter-group">
                        <label>音调范围 (Pitch Range)</label>
                        <input type="number" id="${emotion}_pitch_min" value="${params.pitch_range[0]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'pitch_range', 0, this.value)">
                        <input type="number" id="${emotion}_pitch_max" value="${params.pitch_range[1]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'pitch_range', 1, this.value)">
                    </div>
                    <div class="parameter-group">
                        <label>音量范围 (Volume Range)</label>
                        <input type="number" id="${emotion}_volume_min" value="${params.volume_range[0]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'volume_range', 0, this.value)">
                        <input type="number" id="${emotion}_volume_max" value="${params.volume_range[1]}" step="0.1" min="0.1" max="2.0" onchange="updateEmotionParam('${emotion}', 'volume_range', 1, this.value)">
                    </div>
                `;
                
                grid.appendChild(card);
            }
        }

        // 渲染系统参数
        function renderSystemParams() {
            const container = document.getElementById('systemParams');
            container.innerHTML = '';

            const systemParams = currentConfig.system_settings;
            for (const [param, value] of Object.entries(systemParams)) {
                const paramDiv = document.createElement('div');
                paramDiv.className = 'parameter-group';
                
                paramDiv.innerHTML = `
                    <label>${param}</label>
                    <input type="number" id="system_${param}" value="${value}" onchange="updateSystemParam('${param}', this.value)">
                `;
                
                container.appendChild(paramDiv);
            }
        }

        // 更新情绪参数
        async function updateEmotionParam(emotion, parameter, index, value) {
            try {
                const params = currentConfig.emotion_settings.emotion_parameters[emotion];
                params[parameter][index] = parseFloat(value);
                
                const response = await fetch('/api/update_emotion', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        emotion: emotion,
                        parameter: parameter,
                        value: params[parameter]
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus(`${emotion} 的 ${parameter} 已更新`, 'success');
                } else {
                    showStatus(`更新失败: ${result.message}`, 'error');
                }
            } catch (error) {
                showStatus('更新失败: ' + error.message, 'error');
            }
        }

        // 更新系统参数
        async function updateSystemParam(parameter, value) {
            try {
                const response = await fetch('/api/update_system', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        parameter: parameter,
                        value: parseInt(value)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus(`系统参数 ${parameter} 已更新`, 'success');
                } else {
                    showStatus(`更新失败: ${result.message}`, 'error');
                }
            } catch (error) {
                showStatus('更新失败: ' + error.message, 'error');
            }
        }

        // 刷新配置
        function refreshConfig() {
            loadConfig();
            showStatus('配置已刷新', 'success');
        }

        // 重置配置
        async function resetConfig() {
            if (confirm('确认重置为默认配置？')) {
                try {
                    const response = await fetch('/api/reset_config', {method: 'POST'});
                    const result = await response.json();
                    if (result.success) {
                        showStatus('配置已重置', 'success');
                        loadConfig();
                    } else {
                        showStatus(`重置失败: ${result.message}`, 'error');
                    }
                } catch (error) {
                    showStatus('重置失败: ' + error.message, 'error');
                }
            }
        }

        // 导出配置
        function exportConfig() {
            const dataStr = JSON.stringify(currentConfig, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'tts_config.json';
            link.click();
            URL.revokeObjectURL(url);
            showStatus('配置已导出', 'success');
        }

        // 显示状态消息
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 3000);
        }
    </script>
</body>
</html>
    '''
    
    # 保存HTML模板
    with open('templates/config_index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("🚀 TTS参数实时调整Web界面启动中...")
    print("📡 访问地址: http://localhost:5002")
    print("🔧 功能: 实时调整情绪参数、系统参数")
    print("💡 提示: 修改参数后需要重启TTS服务以生效")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
