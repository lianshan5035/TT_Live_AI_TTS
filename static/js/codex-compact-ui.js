// Codex设计的紧凑型单页面UI交互逻辑
class CompactVoiceGenerator {
    constructor() {
        this.currentFiles = [];
        this.isGenerating = false;
        this.generationQueue = [];
        this.currentSettings = {
            voice: 'en-US-JennyNeural',
            emotion: 'Friendly',
            rate: 0,
            pitch: 0,
            volume: 0
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupThemeToggle();
        this.checkSystemStatus();
        this.loadSettings();
        this.updateUI();
    }

    setupEventListeners() {
        // 文件上传
        const fileInput = document.getElementById('fileInput');
        const fileUploadBtn = document.getElementById('fileUploadBtn');
        const dropzone = document.getElementById('dropzone');

        fileUploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));

        // 拖拽上传
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
        });

        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // 预设按钮
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectPreset(e.target.dataset.emotion));
        });

        // 滑块控制
        document.getElementById('pitchSlider').addEventListener('input', (e) => {
            this.currentSettings.pitch = parseInt(e.target.value);
            document.getElementById('pitchValue').textContent = `${e.target.value > 0 ? '+' : ''}${e.target.value}Hz`;
            this.saveSettings();
        });

        document.getElementById('rateSlider').addEventListener('input', (e) => {
            this.currentSettings.rate = parseInt(e.target.value);
            document.getElementById('rateValue').textContent = `${e.target.value > 0 ? '+' : ''}${e.target.value}%`;
            this.saveSettings();
        });

        document.getElementById('volumeSlider').addEventListener('input', (e) => {
            this.currentSettings.volume = parseInt(e.target.value);
            document.getElementById('volumeValue').textContent = `${e.target.value > 0 ? '+' : ''}${e.target.value}%`;
            this.saveSettings();
        });

        // 音色选择
        document.getElementById('voiceSelect').addEventListener('change', (e) => {
            this.currentSettings.voice = e.target.value;
            this.saveSettings();
        });

        // 操作按钮
        document.getElementById('testVoiceBtn').addEventListener('click', () => this.testVoice());
        document.getElementById('generateBtn').addEventListener('click', () => this.startGeneration());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pauseGeneration());
        document.getElementById('retryBtn').addEventListener('click', () => this.retryFailed());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadAll());

        // 新增：打开文件夹按钮
        this.setupOpenFolderButton();

        // 日志控制
        document.getElementById('clearLogBtn').addEventListener('click', () => this.clearLog());
        document.getElementById('exportLogBtn').addEventListener('click', () => this.exportLog());

        // 错误查看
        document.getElementById('viewErrorsBtn').addEventListener('click', () => this.viewErrors());
    }

    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const savedTheme = localStorage.getItem('theme') || 'dark';
        
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeToggle.innerHTML = savedTheme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.innerHTML = newTheme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        });
    }

    async checkSystemStatus() {
        try {
            // 检查TTS服务 - 使用相对路径避免跨域问题
            let ttsOk = false;
            try {
                const ttsResponse = await fetch('/api/tts-health', {
                    method: 'GET',
                    timeout: 5000
                });
                ttsOk = ttsResponse.ok;
            } catch (e) {
                console.warn('TTS服务检查失败:', e);
                ttsOk = false;
            }
            
            // 使用Web服务返回的TTS状态，如果Web服务正常的话
            const finalTtsOk = webOk ? ttsOkFromWeb : ttsOk;
            const ttsStatus = finalTtsOk ? '正常' : '离线';
            const ttsIndicator = document.getElementById('ttsIndicator');
            document.getElementById('ttsStatus').textContent = ttsStatus;
            ttsIndicator.className = `status-indicator ${finalTtsOk ? '' : 'error'}`;

            // 检查Web服务
            let webOk = false;
            let ttsOkFromWeb = false;
            try {
                const webResponse = await fetch('/api/status', {
                    method: 'GET',
                    timeout: 5000
                });
                webOk = webResponse.ok;
                if (webOk) {
                    const webData = await webResponse.json();
                    ttsOkFromWeb = webData.tts_service?.status === 'healthy';
                }
            } catch (e) {
                console.warn('Web服务检查失败:', e);
                webOk = false;
            }
            
            const webStatus = webOk ? '正常' : '离线';
            const webIndicator = document.getElementById('webIndicator');
            document.getElementById('webStatus').textContent = webStatus;
            webIndicator.className = `status-indicator ${webOk ? '' : 'error'}`;

            // 更新系统状态
            const systemStatus = document.getElementById('systemStatus');
            if (finalTtsOk && webOk) {
                systemStatus.className = 'status-pill ok';
                systemStatus.innerHTML = '<i class="fa-solid fa-circle"></i><span>系统正常</span>';
            } else {
                systemStatus.className = 'status-pill error';
                systemStatus.innerHTML = '<i class="fa-solid fa-circle"></i><span>系统异常</span>';
            }

        } catch (error) {
            console.error('状态检查失败:', error);
            document.getElementById('ttsStatus').textContent = '离线';
            document.getElementById('webStatus').textContent = '离线';
            document.getElementById('ttsIndicator').className = 'status-indicator error';
            document.getElementById('webIndicator').className = 'status-indicator error';
            
            const systemStatus = document.getElementById('systemStatus');
            systemStatus.className = 'status-pill error';
            systemStatus.innerHTML = '<i class="fa-solid fa-circle"></i><span>系统离线</span>';
        }
    }

    async handleFileSelect(files) {
        if (!files.length) return;

        const allowedTypes = ['.xlsx', '.xls', '.csv', '.tsv', '.txt'];
        
        for (const file of files) {
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(fileExtension)) {
                this.showToast(`不支持的文件格式: ${file.name}`, 'error');
                continue;
            }

            this.addFileToList(file);
            await this.uploadFile(file);
        }
    }

    addFileToList(file) {
        const fileList = document.getElementById('fileList');
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fa-solid fa-file-excel file-icon"></i>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <div class="file-meta">${this.formatFileSize(file.size)} • ${file.type || '未知类型'}</div>
                </div>
            </div>
            <div class="file-status processing">处理中</div>
        `;
        
        fileList.appendChild(fileItem);
        fileList.style.display = 'block';
        
        this.currentFiles.push({
            file: file,
            element: fileItem,
            status: 'processing'
        });
    }

    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            this.showToast(`正在上传 ${file.name}...`, 'info');
            this.addLogEntry('info', '文件上传', `开始上传文件: ${file.name}`);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`上传失败: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.showToast(`文件上传成功: ${file.name}`, 'success');
                this.addLogEntry('success', '文件解析', `成功解析文件: ${file.name}`);
                
                // 更新文件状态
                const fileItem = this.currentFiles.find(f => f.file === file);
                if (fileItem) {
                    fileItem.element.querySelector('.file-status').textContent = '解析完成';
                    fileItem.element.querySelector('.file-status').className = 'file-status success';
                    fileItem.status = 'parsed';
                }

                // 自动开始生成
                await this.startGenerationFromFile(result);
            } else {
                throw new Error(result.error || '文件解析失败');
            }

        } catch (error) {
            console.error('文件上传错误:', error);
            this.showToast(`上传失败: ${error.message}`, 'error');
            this.addLogEntry('error', '文件上传', `上传失败: ${error.message}`);
            
            // 更新文件状态
            const fileItem = this.currentFiles.find(f => f.file === file);
            if (fileItem) {
                fileItem.element.querySelector('.file-status').textContent = '失败';
                fileItem.element.querySelector('.file-status').className = 'file-status error';
                fileItem.status = 'error';
            }
        }
    }

    async startGenerationFromFile(uploadResult) {
        try {
            this.showToast('开始生成语音...', 'info');
            this.addLogEntry('info', '语音生成', `开始为 ${uploadResult.product_name || '未知产品'} 生成语音`);

            const response = await fetch('/api/generate-from-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: uploadResult.filename,
                    voice: this.currentSettings.voice,
                    emotion: this.currentSettings.emotion,
                    rate: this.currentSettings.rate,
                    pitch: this.currentSettings.pitch,
                    volume: this.currentSettings.volume
                })
            });

            if (!response.ok) {
                throw new Error(`生成失败: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.showToast('语音生成完成！', 'success');
                this.addLogEntry('success', '生成完成', `成功生成 ${result.generated_files?.length || 0} 个音频文件`);
                
                // 更新进度
                this.updateProgress(result);
                
                // 更新历史记录
                this.addToHistory(result);
                
                // 启用下载按钮
                document.getElementById('downloadBtn').disabled = false;
            } else {
                throw new Error(result.error || '语音生成失败');
            }

        } catch (error) {
            console.error('语音生成错误:', error);
            this.showToast(`生成失败: ${error.message}`, 'error');
            this.addLogEntry('error', '生成失败', `生成失败: ${error.message}`);
        }
    }

    updateProgress(result) {
        const progressSection = document.getElementById('overallProgress');
        const progressBar = document.getElementById('progressBar');
        const progressDetails = document.getElementById('progressDetails');
        
        progressSection.style.display = 'block';
        
        const totalFiles = result.total_scripts || 0;
        const successFiles = result.summary?.successful || 0;
        const failedFiles = result.summary?.failed || 0;
        const progressPercent = totalFiles > 0 ? Math.round((successFiles + failedFiles) / totalFiles * 100) : 100;
        
        progressBar.value = progressPercent;
        document.querySelector('.progress-percent').textContent = `${progressPercent}%`;
        
        progressDetails.innerHTML = `
            <span class="success-count">成功: ${successFiles} 个文件</span>
            <span class="failed-count">失败: ${failedFiles} 个文件</span>
        `;
    }

    switchTab(tabName) {
        // 切换标签页
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
        document.getElementById(`${tabName}Tab`).style.display = 'block';
    }

    selectPreset(emotion) {
        // 选择预设情绪
        document.querySelectorAll('.preset-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-emotion="${emotion}"]`).classList.add('active');
        
        this.currentSettings.emotion = emotion;
        this.saveSettings();
        
        this.showToast(`已选择情绪: ${emotion}`, 'info');
    }

    async testVoice() {
        const testText = "这是一个语音测试，请检查音色和参数设置。";
        
        try {
            this.showToast('正在生成试听音频...', 'info');
            
            const response = await fetch('http://127.0.0.1:5001/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scripts: [testText],
                    voice: this.currentSettings.voice,
                    emotion: this.currentSettings.emotion,
                    rate: this.currentSettings.rate,
                    pitch: this.currentSettings.pitch,
                    volume: this.currentSettings.volume
                })
            });

            if (response.ok) {
                this.showToast('试听音频生成成功！', 'success');
                this.addLogEntry('success', '试听测试', '语音参数测试完成');
            } else {
                throw new Error('试听生成失败');
            }
        } catch (error) {
            this.showToast(`试听失败: ${error.message}`, 'error');
            this.addLogEntry('error', '试听测试', `试听失败: ${error.message}`);
        }
    }

    async startGeneration() {
        if (this.currentFiles.length === 0) {
            this.showToast('请先上传Excel文件', 'warning');
            return;
        }

        this.isGenerating = true;
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        
        this.showToast('开始批量生成语音...', 'info');
        this.addLogEntry('info', '批量生成', '开始批量语音生成任务');
    }

    pauseGeneration() {
        this.isGenerating = false;
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        
        this.showToast('生成已暂停', 'warning');
        this.addLogEntry('warning', '生成暂停', '用户暂停了语音生成任务');
    }

    retryFailed() {
        const failedFiles = this.currentFiles.filter(f => f.status === 'error');
        if (failedFiles.length === 0) {
            this.showToast('没有失败的文件需要重试', 'info');
            return;
        }

        this.showToast(`重试 ${failedFiles.length} 个失败文件`, 'info');
        this.addLogEntry('info', '重试任务', `重试 ${failedFiles.length} 个失败文件`);
        
        // 重新处理失败的文件
        failedFiles.forEach(fileItem => {
            this.uploadFile(fileItem.file);
        });
    }

    downloadAll() {
        this.showToast('准备下载所有音频文件...', 'info');
        this.addLogEntry('info', '音频文件下载', '开始下载所有生成的音频文件');
        
        // 这里可以实现批量下载逻辑
        window.open('/api/download-all', '_blank');
    }

    setupOpenFolderButton() {
        // 在快速操作区域添加打开文件夹按钮
        const quickActions = document.querySelector('.quick-actions .actions');
        const openFolderBtn = document.createElement('button');
        openFolderBtn.className = 'btn btn-secondary';
        openFolderBtn.innerHTML = '<i class="fa-solid fa-folder-open"></i> 打开音频文件夹';
        openFolderBtn.id = 'openFolderBtn';
        
        // 插入到下载按钮之前
        const downloadBtn = document.getElementById('downloadBtn');
        quickActions.insertBefore(openFolderBtn, downloadBtn);
        
        // 添加事件监听器
        openFolderBtn.addEventListener('click', () => this.openOutputFolder());
        
        // 添加文件列表刷新按钮
        const refreshFilesBtn = document.createElement('button');
        refreshFilesBtn.className = 'btn btn-outline';
        refreshFilesBtn.innerHTML = '<i class="fa-solid fa-refresh"></i> 刷新音频';
        refreshFilesBtn.id = 'refreshFilesBtn';
        
        quickActions.insertBefore(refreshFilesBtn, openFolderBtn);
        refreshFilesBtn.addEventListener('click', () => this.refreshOutputFiles());
    }

    async openOutputFolder() {
        try {
            this.showToast('正在打开音频输出文件夹...', 'info');
            this.addLogEntry('info', '打开音频文件夹', '正在打开音频输出文件夹');
            
            const response = await fetch('/api/open-output-folder');
            const result = await response.json();
            
            if (result.success) {
                this.showToast('音频输出文件夹已打开！', 'success');
                this.addLogEntry('success', '音频文件夹打开', `成功打开音频输出文件夹: ${result.path}`);
                
                // 同时刷新文件列表
                await this.refreshOutputFiles();
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('打开文件夹失败:', error);
            this.showToast(`打开音频文件夹失败: ${error.message}`, 'error');
            this.addLogEntry('error', '音频文件夹打开', `打开失败: ${error.message}`);
        }
    }

    async refreshOutputFiles() {
        try {
            this.showToast('正在刷新音频文件列表...', 'info');
            
            const response = await fetch('/api/get-output-files');
            const result = await response.json();
            
            if (result.success) {
                this.updateFileList(result.files);
                this.showToast(`音频文件列表已刷新，共 ${result.total_count} 个音频文件`, 'success');
                this.addLogEntry('success', '音频文件刷新', `刷新完成，共 ${result.total_count} 个音频文件`);
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('刷新文件列表失败:', error);
            this.showToast(`音频文件刷新失败: ${error.message}`, 'error');
            this.addLogEntry('error', '音频文件刷新', `刷新失败: ${error.message}`);
        }
    }

    updateFileList(files) {
        // 更新历史表格中的文件信息
        const historyBody = document.getElementById('historyBody');
        const existingRows = historyBody.querySelectorAll('tr:not(.empty-row)');
        
        // 清除现有行
        existingRows.forEach(row => row.remove());
        
        if (files.length === 0) {
            // 如果没有文件，显示空状态
            const emptyRow = document.createElement('tr');
            emptyRow.className = 'empty-row';
            emptyRow.innerHTML = `
                <td colspan="6" class="empty-state">
                    <i class="fa-solid fa-file-circle-plus"></i>
                    <p>暂无音频文件</p>
                </td>
            `;
            historyBody.appendChild(emptyRow);
            return;
        }
        
        // 按产品分组显示文件
        const productGroups = {};
        files.forEach(file => {
            const productName = this.extractProductName(file.name);
            if (!productGroups[productName]) {
                productGroups[productName] = [];
            }
            productGroups[productName].push(file);
        });
        
        // 为每个产品组创建一行
        Object.entries(productGroups).forEach(([productName, productFiles]) => {
            const totalSize = productFiles.reduce((sum, file) => sum + file.size, 0);
            const latestFile = productFiles[0]; // 已按时间排序
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${productName}</td>
                <td>${productFiles.length}</td>
                <td>${productFiles.length}</td>
                <td><span class="file-status success">完成</span></td>
                <td>${new Date(latestFile.modified * 1000).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="this.openProductFolder('${productName}')" title="打开产品音频文件夹">
                        <i class="fa-solid fa-folder-open"></i>
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="this.downloadProductFiles('${productName}')" title="下载产品音频文件">
                        <i class="fa-solid fa-download"></i>
                    </button>
                </td>
            `;
            
            historyBody.appendChild(row);
        });
    }

    extractProductName(filename) {
        // 从文件名中提取产品名称
        // 例如: tts_0001_Friendly.mp3 -> 从路径中提取产品名
        const parts = filename.split('_');
        if (parts.length >= 3) {
            return parts[0] || '未知产品';
        }
        return '未知产品';
    }

    addToHistory(result) {
        const historyBody = document.getElementById('historyBody');
        const emptyRow = historyBody.querySelector('.empty-row');
        
        if (emptyRow) {
            emptyRow.remove();
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${result.product_name || '未知产品'}</td>
            <td>${result.total_scripts || 0}</td>
            <td>${result.summary?.successful || 0}</td>
            <td><span class="file-status success">完成</span></td>
            <td>${new Date().toLocaleTimeString()}</td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="this.downloadFile('${result.product_name}')">
                    <i class="fa-solid fa-download"></i>
                </button>
            </td>
        `;
        
        historyBody.insertBefore(row, historyBody.firstChild);
    }

    addLogEntry(type, action, message) {
        const logContainer = document.getElementById('activityLog');
        const logEntry = document.createElement('li');
        logEntry.className = 'log-entry';
        
        const time = new Date().toLocaleTimeString();
        logEntry.innerHTML = `
            <span class="time">${time}</span>
            <div class="event ${type}">
                <strong>${action}</strong>
                <p>${message}</p>
            </div>
        `;
        
        logContainer.insertBefore(logEntry, logContainer.firstChild);
        
        // 限制日志条目数量
        const maxEntries = 50;
        while (logContainer.children.length > maxEntries) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }

    clearLog() {
        const logContainer = document.getElementById('activityLog');
        logContainer.innerHTML = `
            <li class="log-entry">
                <span class="time">${new Date().toLocaleTimeString()}</span>
                <div class="event info">
                    <strong>日志清空</strong>
                    <p>活动日志已清空</p>
                </div>
            </li>
        `;
        
        this.showToast('活动日志已清空', 'info');
    }

    exportLog() {
        const logContainer = document.getElementById('activityLog');
        const logs = Array.from(logContainer.children).map(entry => {
            const time = entry.querySelector('.time').textContent;
            const event = entry.querySelector('.event');
            const action = event.querySelector('strong').textContent;
            const message = event.querySelector('p').textContent;
            return `${time} - ${action}: ${message}`;
        }).join('\n');
        
        const blob = new Blob([logs], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity-log-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showToast('日志已导出', 'success');
    }

    viewErrors() {
        this.showToast('显示错误详情', 'info');
        // 这里可以实现错误详情查看功能
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    saveSettings() {
        localStorage.setItem('voiceSettings', JSON.stringify(this.currentSettings));
    }

    loadSettings() {
        const saved = localStorage.getItem('voiceSettings');
        if (saved) {
            this.currentSettings = { ...this.currentSettings, ...JSON.parse(saved) };
            
            // 更新UI
            document.getElementById('voiceSelect').value = this.currentSettings.voice;
            document.getElementById('pitchSlider').value = this.currentSettings.pitch;
            document.getElementById('rateSlider').value = this.currentSettings.rate;
            document.getElementById('volumeSlider').value = this.currentSettings.volume;
            
            document.getElementById('pitchValue').textContent = `${this.currentSettings.pitch > 0 ? '+' : ''}${this.currentSettings.pitch}Hz`;
            document.getElementById('rateValue').textContent = `${this.currentSettings.rate > 0 ? '+' : ''}${this.currentSettings.rate}%`;
            document.getElementById('volumeValue').textContent = `${this.currentSettings.volume > 0 ? '+' : ''}${this.currentSettings.volume}%`;
            
            // 选择对应的预设
            const presetBtn = document.querySelector(`[data-emotion="${this.currentSettings.emotion}"]`);
            if (presetBtn) {
                presetBtn.classList.add('active');
            }
        }
    }

    updateUI() {
        // 定期更新系统状态
        setInterval(() => {
            this.checkSystemStatus();
        }, 30000);
        
        // 更新存储信息
        this.updateStorageInfo();
    }

    updateStorageInfo() {
        // 这里可以实现存储使用情况更新
        document.getElementById('storageInfo').textContent = '存储使用: 0%';
        document.getElementById('lastSync').textContent = `上次同步: ${new Date().toLocaleTimeString()}`;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new CompactVoiceGenerator();
});
