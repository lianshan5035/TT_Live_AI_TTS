// TT-Live-AI 语音生成控制中心 JavaScript

class TTControlCenter {
    constructor() {
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkConnection();
        this.loadTasks();
        this.startLogUpdates();
    }

    setupEventListeners() {
        // 文件上传
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // 生成按钮
        document.getElementById('generateBtn').addEventListener('click', this.handleGenerate.bind(this));

        // 任务操作
        document.getElementById('refreshBtn').addEventListener('click', this.loadTasks.bind(this));
        document.getElementById('startAllBtn').addEventListener('click', this.startAllTasks.bind(this));

        // 日志操作
        document.getElementById('clearLogBtn').addEventListener('click', this.clearLogs.bind(this));
    }

    // 文件拖拽处理
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    // 文件上传
    async uploadFile(file) {
        if (!file.name.endsWith('.xlsx')) {
            this.showToast('只支持Excel文件', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading(true);
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('文件上传成功', 'success');
                this.addLog(`文件上传成功: ${result.filename}`);
            } else {
                this.showToast(result.error || '上传失败', 'error');
            }
        } catch (error) {
            this.showToast('上传失败: ' + error.message, 'error');
            this.addLog(`上传失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    // 生成语音
    async handleGenerate() {
        if (this.isGenerating) return;

        const productName = document.getElementById('productName').value.trim();
        const textContent = document.getElementById('textContent').value.trim();
        const emotion = document.getElementById('emotionSelect').value;

        if (!productName || !textContent) {
            this.showToast('请填写产品名称和文案内容', 'warning');
            return;
        }

        // 解析文案内容
        const scripts = textContent.split('\n')
            .filter(line => line.trim())
            .map((line, index) => ({
                english_script: line.trim(),
                emotion: emotion === 'random' ? this.getRandomEmotion() : emotion,
                voice: 'en-US-JennyNeural'
            }));

        if (scripts.length === 0) {
            this.showToast('请输入有效的文案内容', 'warning');
            return;
        }

        this.isGenerating = true;
        this.updateGenerateButton(true);

        try {
            this.showLoading(true);
            this.addLog(`开始生成语音: ${productName}, 共${scripts.length}条文案`);

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_name: productName,
                    scripts: scripts,
                    discount: 'Special offer available!'
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showToast('语音生成完成', 'success');
                this.addLog(`生成完成: 成功${result.summary.successful}个, 失败${result.summary.failed}个`);
                this.loadTasks(); // 刷新任务列表
            } else {
                this.showToast(result.error || '生成失败', 'error');
                this.addLog(`生成失败: ${result.error}`);
            }
        } catch (error) {
            this.showToast('生成失败: ' + error.message, 'error');
            this.addLog(`生成失败: ${error.message}`);
        } finally {
            this.isGenerating = false;
            this.updateGenerateButton(false);
            this.showLoading(false);
        }
    }

    // 获取随机情感
    getRandomEmotion() {
        const emotions = ['Calm', 'Friendly', 'Confident', 'Playful', 'Excited', 'Urgent'];
        return emotions[Math.floor(Math.random() * emotions.length)];
    }

    // 更新生成按钮状态
    updateGenerateButton(isGenerating) {
        const btn = document.getElementById('generateBtn');
        btn.disabled = isGenerating;
        btn.innerHTML = isGenerating 
            ? '<i class="fas fa-spinner fa-spin"></i> 生成中...'
            : '<i class="fas fa-play"></i> 开始生成';
    }

    // 检查连接状态
    async checkConnection() {
        try {
            const response = await fetch('/api/status');
            const result = await response.json();
            
            const statusElement = document.getElementById('connectionStatus');
            const statusText = statusElement.querySelector('.status-text');
            const statusIndicator = statusElement.querySelector('.status-indicator');

            if (result.status === 'connected') {
                statusText.textContent = '已连接';
                statusIndicator.className = 'status-indicator connected';
            } else {
                statusText.textContent = '连接断开';
                statusIndicator.className = 'status-indicator disconnected';
            }
        } catch (error) {
            const statusElement = document.getElementById('connectionStatus');
            const statusText = statusElement.querySelector('.status-text');
            const statusIndicator = statusElement.querySelector('.status-indicator');
            
            statusText.textContent = '连接失败';
            statusIndicator.className = 'status-indicator disconnected';
        }
    }

    // 加载任务列表
    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const result = await response.json();

            // 更新任务统计
            document.getElementById('totalTasks').textContent = result.total || 0;
            document.getElementById('completedTasks').textContent = result.completed || 0;
            document.getElementById('processingTasks').textContent = result.processing || 0;
            document.getElementById('errorTasks').textContent = result.error || 0;

        } catch (error) {
            console.error('加载任务失败:', error);
        }
    }

    // 启动所有任务
    async startAllTasks() {
        this.showToast('启动全部任务功能开发中...', 'warning');
    }

    // 清空日志
    clearLogs() {
        document.getElementById('logContent').innerHTML = '';
        this.addLog('日志已清空');
    }

    // 添加日志
    addLog(message) {
        const logContent = document.getElementById('logContent');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
    }

    // 开始日志更新
    startLogUpdates() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/logs');
                const result = await response.json();
                
                if (result.logs && result.logs.length > 0) {
                    const logContent = document.getElementById('logContent');
                    const lastLog = logContent.lastElementChild;
                    const lastLogText = lastLog ? lastLog.textContent : '';
                    
                    result.logs.forEach(log => {
                        if (log.trim() && !lastLogText.includes(log.trim())) {
                            this.addLog(log.trim());
                        }
                    });
                }
            } catch (error) {
                // 静默处理日志更新错误
            }
        }, 5000); // 每5秒更新一次
    }

    // 显示加载状态
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    // 显示消息提示
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new TTControlCenter();
});
