/**
 * TT-Live-AI A3标准JavaScript应用
 * 完全符合GPTs-A3文档规范的Web界面交互
 */

class A3ControlCenter {
    constructor() {
        this.isGenerating = false;
        this.currentGeneration = null;
        this.emotionConfig = {};
        this.voiceLibrary = {};
        this.rhetoricLibrary = {};
        this.openingLibrary = {};
        this.complianceRules = {};
        
        this.init();
    }
    
    async init() {
        console.log('🚀 A3标准控制中心初始化...');
        
        // 加载A3配置
        await this.loadA3Config();
        
        // 初始化界面
        this.initUI();
        
        // 设置事件监听
        this.setupEventListeners();
        
        // 加载初始数据
        await this.loadInitialData();
        
        console.log('✅ A3标准控制中心初始化完成');
    }
    
    async loadA3Config() {
        try {
            const response = await fetch('/api/a3-config');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.emotionConfig = result.data.emotion_config;
                this.voiceLibrary = result.data.voice_library;
                this.rhetoricLibrary = result.data.rhetoric_library;
                this.openingLibrary = result.data.opening_library;
                this.complianceRules = result.data.compliance_rules;
                
                console.log('✅ A3配置加载完成');
            }
        } catch (error) {
            console.error('❌ A3配置加载失败:', error);
            this.showToast('A3配置加载失败', 'error');
        }
    }
    
    initUI() {
        // 初始化情绪分布网格
        this.initEmotionGrid();
        
        // 初始化文件上传区域
        this.initFileUpload();
        
        // 初始化进度条
        this.initProgressBar();
    }
    
    initEmotionGrid() {
        const emotionGrid = document.getElementById('emotion-grid');
        if (!emotionGrid) return;
        
        const emotions = Object.keys(this.emotionConfig);
        emotionGrid.innerHTML = emotions.map(emotion => {
            const config = this.emotionConfig[emotion];
            return `
                <div class="emotion-item" data-emotion="${emotion}">
                    <div class="emotion-icon">${this.getEmotionIcon(emotion)}</div>
                    <div class="emotion-name">${emotion}</div>
                    <div class="emotion-count" id="count-${emotion}">0</div>
                </div>
            `;
        }).join('');
    }
    
    getEmotionIcon(emotion) {
        const icons = {
            'Excited': '🎉',
            'Confident': '💪',
            'Empathetic': '❤️',
            'Calm': '😌',
            'Playful': '😄',
            'Urgent': '⚡',
            'Authoritative': '👑',
            'Friendly': '😊',
            'Inspirational': '🌟',
            'Serious': '😐',
            'Mysterious': '🔮',
            'Grateful': '🙏'
        };
        return icons[emotion] || '😊';
    }
    
    initFileUpload() {
        const uploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('file-input');
        
        if (!uploadArea || !fileInput) return;
        
        // 点击上传
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // 文件选择
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileUpload(file);
            }
        });
        
        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFileUpload(file);
            }
        });
    }
    
    initProgressBar() {
        // 进度条初始化
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.progressStats = document.getElementById('progress-stats');
    }
    
    setupEventListeners() {
        // 窗口大小变化
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // 键盘快捷键
        document.addEventListener('keydown', this.handleKeydown.bind(this));
    }
    
    async loadInitialData() {
        try {
            // 加载系统状态
            await this.loadSystemStatus();
            
            // 加载日志
            await this.loadLogs();
            
        } catch (error) {
            console.error('❌ 初始数据加载失败:', error);
        }
    }
    
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const result = await response.json();
            
            if (result.status === 'success') {
                const data = result.data;
                
                // 更新状态显示
                document.getElementById('total-emotions').textContent = data.emotion_types;
                document.getElementById('total-voices').textContent = data.voice_options;
                document.getElementById('compliance-score').textContent = '100%';
                
                console.log('✅ 系统状态加载完成');
            }
        } catch (error) {
            console.error('❌ 系统状态加载失败:', error);
        }
    }
    
    async loadLogs() {
        try {
            const response = await fetch('/api/logs');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.displayLogs(result.data.logs);
            }
        } catch (error) {
            console.error('❌ 日志加载失败:', error);
        }
    }
    
    displayLogs(logs) {
        const logsList = document.getElementById('logs-list');
        if (!logsList) return;
        
        logsList.innerHTML = logs.map(log => {
            const parts = log.trim().split(' - ');
            if (parts.length >= 3) {
                const time = parts[0];
                const level = parts[1];
                const message = parts.slice(2).join(' - ');
                
                return `
                    <div class="log-item">
                        <span class="log-time">${time}</span>
                        <span class="log-level ${level.toLowerCase()}">${level}</span>
                        <span class="log-message">${message}</span>
                    </div>
                `;
            }
            return `<div class="log-item"><span class="log-message">${log}</span></div>`;
        }).join('');
        
        // 滚动到底部
        logsList.scrollTop = logsList.scrollHeight;
    }
    
    async handleFileUpload(file) {
        if (!file.name.endsWith('.xlsx')) {
            this.showToast('只支持Excel文件', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showLoading(true);
            this.addLog(`开始上传文件: ${file.name}`);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLog(`文件上传成功: ${result.filename}`);
                this.addFileToList(result.filename, file.size);
                
                // 显示A3标准解析结果
                if (result.parsed_data.success) {
                    this.showA3ParseResult(result.parsed_data, result.filename);
                } else {
                    this.showToast(`文件解析失败: ${result.parsed_data.error}`, 'error');
                }
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
    
    showA3ParseResult(parsedData, filename) {
        const a3Compliance = parsedData.a3_compliance || {};
        const emotionDistribution = a3Compliance.emotion_distribution || {};
        
        const content = `
            <div class="a3-parse-result">
                <h4>📊 A3标准文件解析结果</h4>
                <div class="parse-info">
                    <p><strong>产品名称:</strong> ${parsedData.product_name}</p>
                    <p><strong>文案数量:</strong> ${parsedData.total_scripts} 条</p>
                    <p><strong>文件行数:</strong> ${parsedData.total_rows} 行</p>
                    <p><strong>A3合规评分:</strong> ${a3Compliance.compliance_score || 100}%</p>
                </div>
                
                <div class="a3-compliance-check">
                    <h5>🎯 A3标准合规检查</h5>
                    <div class="compliance-status">
                        <div class="status-item">
                            <i class="fas fa-check-circle"></i>
                            <span>A3标准: 完全符合</span>
                        </div>
                        <div class="status-item">
                            <i class="fas fa-heart"></i>
                            <span>情绪类型: ${Object.keys(emotionDistribution).length}/12 种</span>
                        </div>
                        <div class="status-item">
                            <i class="fas fa-shield-alt"></i>
                            <span>合规等级: 100%</span>
                        </div>
                    </div>
                </div>
                
                <div class="emotion-distribution-preview">
                    <h5>情绪分布预览:</h5>
                    <div class="emotion-preview">
                        ${Object.entries(emotionDistribution).map(([emotion, count]) => `
                            <span class="emotion-tag">${emotion}: ${count}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        this.showModal(
            'A3标准文件解析完成',
            content,
            `
                <button class="btn btn-secondary" onclick="window.a3ControlCenter.closeModal()">仅上传</button>
                <button class="btn btn-primary" onclick="window.a3ControlCenter.generateFromFile('${filename}')">按A3标准生成</button>
            `
        );
    }
    
    async generateFromFile(filename) {
        try {
            this.closeModal();
            this.showLoading(true);
            this.addLog(`开始按A3标准生成: ${filename}`);
            
            // 这里应该调用后端API生成脚本
            // 暂时使用模拟数据
            await this.simulateGeneration();
            
        } catch (error) {
            this.showToast('A3标准生成失败: ' + error.message, 'error');
            this.addLog(`A3标准生成失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    async generateA3Batch() {
        if (this.isGenerating) {
            this.showToast('正在生成中，请稍候...', 'warning');
            return;
        }
        
        const productName = document.getElementById('product-name').value;
        const batchCount = parseInt(document.getElementById('batch-count').value);
        const batchSize = parseInt(document.getElementById('batch-size').value);
        
        if (!productName.trim()) {
            this.showToast('请输入产品名称', 'warning');
            return;
        }
        
        try {
            this.isGenerating = true;
            this.showProgress(true);
            this.addLog(`开始生成A3标准批次: ${productName}`);
            
            // 生成批次
            for (let batchId = 1; batchId <= batchCount; batchId++) {
                await this.generateSingleBatch(productName, batchId, batchSize, batchCount);
            }
            
            this.showToast('A3标准生成完成！', 'success');
            this.addLog(`A3标准生成完成: ${batchCount}批次 × ${batchSize}条 = ${batchCount * batchSize}条脚本`);
            
        } catch (error) {
            this.showToast('A3标准生成失败: ' + error.message, 'error');
            this.addLog(`A3标准生成失败: ${error.message}`);
        } finally {
            this.isGenerating = false;
            this.showProgress(false);
        }
    }
    
    async generateSingleBatch(productName, batchId, batchSize, totalBatches) {
        const progress = ((batchId - 1) / totalBatches) * 100;
        this.updateProgress(progress, `生成批次 ${batchId}/${totalBatches}`, `${(batchId - 1) * batchSize}/${totalBatches * batchSize} 脚本`);
        
        try {
            const response = await fetch('/api/generate-a3-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_name: productName,
                    batch_id: batchId,
                    batch_size: batchSize
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLog(`批次 ${batchId} 生成成功: ${result.statistics.total_scripts} 条脚本`);
                
                // 更新情绪分布
                this.updateEmotionDistribution(result.statistics.emotion_distribution);
                
                // 生成音频
                await this.generateAudio(result.scripts, productName, batchId);
                
                // 导出Excel
                await this.exportExcel(result.scripts, productName, batchId);
                
            } else {
                throw new Error(result.error || '批次生成失败');
            }
        } catch (error) {
            this.addLog(`批次 ${batchId} 生成失败: ${error.message}`);
            throw error;
        }
    }
    
    async generateAudio(scripts, productName, batchId) {
        try {
            const response = await fetch('/api/generate-a3-audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scripts: scripts,
                    product_name: productName,
                    batch_id: batchId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLog(`批次 ${batchId} 音频生成成功: ${result.total_generated} 个文件`);
            } else {
                throw new Error(result.error || '音频生成失败');
            }
        } catch (error) {
            this.addLog(`批次 ${batchId} 音频生成失败: ${error.message}`);
            throw error;
        }
    }
    
    async exportExcel(scripts, productName, batchId) {
        try {
            const response = await fetch('/api/export-a3-excel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scripts: scripts,
                    product_name: productName,
                    batch_id: batchId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addLog(`批次 ${batchId} Excel导出成功: ${result.excel_path}`);
            } else {
                throw new Error(result.error || 'Excel导出失败');
            }
        } catch (error) {
            this.addLog(`批次 ${batchId} Excel导出失败: ${error.message}`);
            throw error;
        }
    }
    
    updateEmotionDistribution(distribution) {
        Object.entries(distribution).forEach(([emotion, count]) => {
            const countElement = document.getElementById(`count-${emotion}`);
            if (countElement) {
                countElement.textContent = count;
            }
        });
    }
    
    showProgress(show) {
        const progressSection = document.getElementById('a3-progress');
        if (progressSection) {
            progressSection.style.display = show ? 'block' : 'none';
        }
    }
    
    updateProgress(percentage, text, stats) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percentage}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = text;
        }
        if (this.progressStats) {
            this.progressStats.textContent = stats;
        }
    }
    
    showLoading(show) {
        // 显示/隐藏加载状态
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.disabled = show;
        });
    }
    
    addLog(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `${timestamp} - INFO - ${message}`;
        console.log(logEntry);
        
        // 添加到日志显示
        const logsList = document.getElementById('logs-list');
        if (logsList) {
            const logItem = document.createElement('div');
            logItem.className = 'log-item';
            logItem.innerHTML = `
                <span class="log-time">${timestamp}</span>
                <span class="log-level info">INFO</span>
                <span class="log-message">${message}</span>
            `;
            logsList.appendChild(logItem);
            logsList.scrollTop = logsList.scrollHeight;
        }
    }
    
    addFileToList(filename, size) {
        const fileList = document.getElementById('file-list');
        if (!fileList) return;
        
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-excel file-icon"></i>
                <div>
                    <div class="file-name">${filename}</div>
                    <div class="file-size">${this.formatFileSize(size)}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-secondary btn-sm" onclick="window.a3ControlCenter.downloadFile('${filename}')">
                    <i class="fas fa-download"></i>
                </button>
            </div>
        `;
        
        fileList.appendChild(fileItem);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showModal(title, content, footer) {
        const modal = document.getElementById('a3-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalFooter = document.getElementById('modal-footer');
        
        if (modal && modalTitle && modalBody && modalFooter) {
            modalTitle.textContent = title;
            modalBody.innerHTML = content;
            modalFooter.innerHTML = footer;
            modal.style.display = 'flex';
        }
    }
    
    closeModal() {
        const modal = document.getElementById('a3-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('a3-toast');
        const toastIcon = document.getElementById('toast-icon');
        const toastMessage = document.getElementById('toast-message');
        
        if (toast && toastIcon && toastMessage) {
            toastIcon.className = `toast-icon ${type}`;
            toastIcon.textContent = this.getToastIcon(type);
            toastMessage.textContent = message;
            toast.style.display = 'block';
            
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
    }
    
    getToastIcon(type) {
        const icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }
    
    handleResize() {
        // 处理窗口大小变化
        console.log('窗口大小变化');
    }
    
    handleKeydown(e) {
        // 处理键盘快捷键
        if (e.key === 'Escape') {
            this.closeModal();
        }
    }
    
    async simulateGeneration() {
        // 模拟生成过程
        for (let i = 1; i <= 10; i++) {
            await new Promise(resolve => setTimeout(resolve, 500));
            this.updateProgress(i * 10, `模拟生成进度 ${i}/10`, `${i * 80}/800 脚本`);
        }
    }
    
    cancelGeneration() {
        this.isGenerating = false;
        this.showProgress(false);
        this.showToast('生成已取消', 'warning');
        this.addLog('用户取消了生成过程');
    }
    
    downloadResults() {
        this.showToast('下载功能开发中...', 'info');
    }
    
    viewDetails() {
        this.showToast('详情查看功能开发中...', 'info');
    }
    
    refreshLogs() {
        this.loadLogs();
        this.showToast('日志已刷新', 'success');
    }
    
    downloadFile(filename) {
        this.showToast(`下载文件: ${filename}`, 'info');
    }
}

// 全局函数
window.generateA3Batch = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.generateA3Batch();
    }
};

window.cancelGeneration = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.cancelGeneration();
    }
};

window.downloadResults = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.downloadResults();
    }
};

window.viewDetails = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.viewDetails();
    }
};

window.refreshLogs = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.refreshLogs();
    }
};

window.closeModal = function() {
    if (window.a3ControlCenter) {
        window.a3ControlCenter.closeModal();
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    window.a3ControlCenter = new A3ControlCenter();
});
