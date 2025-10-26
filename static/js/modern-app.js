// TT-Live-AI 现代化控制中心 JavaScript - Codex设计风格

class ModernTTControlCenter {
    constructor() {
        this.isGenerating = false;
        this.currentSection = 'dashboard';
        this.charts = {};
        this.notifications = [];
        this.isSidebarCollapsed = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.checkConnection();
        this.loadDashboardData();
        this.startRealTimeUpdates();
        this.setupFileUpload();
        this.setupSliders();
        this.setupNavigation();
    }

    setupEventListeners() {
        // 导航菜单
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // 侧边栏切换
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // 生成按钮
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.handleGenerate();
        });

        // 快速操作按钮
        document.getElementById('quickGenerate').addEventListener('click', () => {
            this.switchSection('generator');
        });

        document.getElementById('batchUpload').addEventListener('click', () => {
            this.switchSection('files');
        });

        document.getElementById('exportData').addEventListener('click', () => {
            this.exportData();
        });

        document.getElementById('systemRestart').addEventListener('click', () => {
            this.restartSystem();
        });

        // 任务管理
        document.getElementById('refreshTasks').addEventListener('click', () => {
            this.loadTasks();
        });

        document.getElementById('startAllTasks').addEventListener('click', () => {
            this.startAllTasks();
        });

        // 日志操作
        document.getElementById('clearLogs').addEventListener('click', () => {
            this.clearLogs();
        });

        document.getElementById('pauseLogs').addEventListener('click', () => {
            this.toggleLogPause();
        });

        // 文件上传
        document.getElementById('uploadFiles').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        // 模态框
        document.getElementById('modalClose').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('modalCancel').addEventListener('click', () => {
            this.closeModal();
        });

        // 任务筛选
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.filterTasks(btn.dataset.status);
            });
        });

        // 文本区域字符计数
        document.getElementById('textContent').addEventListener('input', () => {
            this.updateTextCount();
        });
    }

    setupNavigation() {
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.switchSection('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.switchSection('generator');
                        break;
                    case '3':
                        e.preventDefault();
                        this.switchSection('tasks');
                        break;
                    case '4':
                        e.preventDefault();
                        this.switchSection('files');
                        break;
                    case '5':
                        e.preventDefault();
                        this.switchSection('analytics');
                        break;
                    case '6':
                        e.preventDefault();
                        this.switchSection('settings');
                        break;
                }
            }
        });
    }

    switchSection(sectionName) {
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // 更新内容区域
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        // 更新页面标题
        const titles = {
            dashboard: '控制台',
            generator: '语音生成',
            tasks: '任务管理',
            files: '文件管理',
            analytics: '数据分析',
            settings: '系统设置'
        };
        document.getElementById('pageTitle').textContent = titles[sectionName];

        this.currentSection = sectionName;

        // 加载对应数据
        switch(sectionName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }

    toggleSidebar() {
        this.isSidebarCollapsed = !this.isSidebarCollapsed;
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (this.isSidebarCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
        }
    }

    async checkConnection() {
        try {
            const response = await fetch('/api/status');
            const result = await response.json();
            
            const indicator = document.getElementById('connectionIndicator');
            const text = document.getElementById('connectionText');

            if (result.status === 'connected') {
                indicator.className = 'status-indicator connected';
                text.textContent = '已连接';
            } else {
                indicator.className = 'status-indicator disconnected';
                text.textContent = '连接断开';
            }
        } catch (error) {
            const indicator = document.getElementById('connectionIndicator');
            const text = document.getElementById('connectionText');
            
            indicator.className = 'status-indicator disconnected';
            text.textContent = '连接失败';
        }
    }

    async loadDashboardData() {
        try {
            // 加载任务统计
            const tasksResponse = await fetch('/api/tasks');
            const tasksData = await tasksResponse.json();
            
            document.getElementById('totalTasks').textContent = tasksData.total || 0;
            document.getElementById('completedTasks').textContent = tasksData.completed || 0;
            document.getElementById('processingTasks').textContent = tasksData.processing || 0;
            document.getElementById('errorTasks').textContent = tasksData.error || 0;

            // 模拟系统状态数据
            this.updateSystemStatus();

        } catch (error) {
            console.error('加载仪表板数据失败:', error);
        }
    }

    updateSystemStatus() {
        // 模拟实时系统状态更新
        const cpuUsage = Math.floor(Math.random() * 30) + 30;
        const memoryUsage = (Math.random() * 2 + 1).toFixed(1);
        const diskUsage = Math.floor(Math.random() * 50) + 100;
        
        document.getElementById('cpuUsage').textContent = `${cpuUsage}%`;
        document.getElementById('memoryUsage').textContent = `${memoryUsage}GB`;
        document.getElementById('diskUsage').textContent = `${diskUsage}GB`;
        document.getElementById('networkStatus').textContent = '正常';
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            const tbody = document.getElementById('taskTableBody');
            tbody.innerHTML = '';

            if (data.tasks && data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const row = this.createTaskRow(task);
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-tertiary);">暂无任务</td></tr>';
            }
        } catch (error) {
            console.error('加载任务失败:', error);
        }
    }

    createTaskRow(task) {
        const row = document.createElement('tr');
        
        const statusClass = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'error': 'error'
        }[task.status] || 'secondary';

        row.innerHTML = `
            <td>${task.id}</td>
            <td>${task.productName}</td>
            <td><span class="badge badge-${statusClass}">${this.getStatusText(task.status)}</span></td>
            <td>
                <div class="progress">
                    <div class="progress-bar" style="width: ${task.progress || 0}%"></div>
                </div>
            </td>
            <td>${new Date(task.createdAt).toLocaleString()}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon small" onclick="this.viewTask('${task.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon small" onclick="this.deleteTask('${task.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        return row;
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '等待中',
            'processing': '处理中',
            'completed': '已完成',
            'error': '错误'
        };
        return statusMap[status] || status;
    }

    filterTasks(status) {
        // 更新筛选按钮状态
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-status="${status}"]`).classList.add('active');

        // 这里应该根据状态筛选任务
        console.log(`筛选任务状态: ${status}`);
    }

    async handleGenerate() {
        if (this.isGenerating) return;

        const productName = document.getElementById('productName').value.trim();
        const textContent = document.getElementById('textContent').value.trim();
        const emotion = document.getElementById('emotionSelect').value;
        const voiceModel = document.getElementById('voiceModel').value;

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
                voice: voiceModel
            }));

        if (scripts.length === 0) {
            this.showToast('请输入有效的文案内容', 'warning');
            return;
        }

        this.isGenerating = true;
        this.updateGenerateButton(true);
        this.showLoading(true);

        try {
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
                this.loadDashboardData(); // 刷新仪表板数据
                this.addToHistory(productName, scripts.length);
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

    updateGenerateButton(isGenerating) {
        const btn = document.getElementById('generateBtn');
        btn.disabled = isGenerating;
        btn.innerHTML = isGenerating 
            ? '<i class="fas fa-spinner fa-spin"></i> 生成中...'
            : '<i class="fas fa-play"></i> 开始生成';
    }

    getRandomEmotion() {
        const emotions = ['Calm', 'Friendly', 'Confident', 'Playful', 'Excited', 'Urgent'];
        return emotions[Math.floor(Math.random() * emotions.length)];
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        
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
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
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
            
            // 先上传并解析文件
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const uploadResult = await uploadResponse.json();
            
            if (uploadResult.success) {
                this.addLog(`文件上传成功: ${uploadResult.filename}`);
                this.addFileToList(uploadResult.filename, file.size);
                
                // 检查解析结果
                if (uploadResult.parsed_data.success) {
                    const parsedData = uploadResult.parsed_data;
                    this.addLog(`解析成功: 产品"${parsedData.product_name}", 共${parsedData.total_scripts}条文案`);
                    
                    // 显示解析结果并询问是否自动生成
                    this.showParseResult(parsedData, uploadResult.filename);
                } else {
                    this.showToast(`文件解析失败: ${uploadResult.parsed_data.error}`, 'error');
                    this.addLog(`解析失败: ${uploadResult.parsed_data.error}`);
                }
            } else {
                this.showToast(uploadResult.error || '上传失败', 'error');
                this.addLog(`上传失败: ${uploadResult.error}`);
            }
        } catch (error) {
            this.showToast('上传失败: ' + error.message, 'error');
            this.addLog(`上传失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    showParseResult(parsedData, filename) {
        // 显示A3标准合规信息
        const a3Compliance = parsedData.a3_compliance || {};
        
        const content = `
            <div class="parse-result">
                <h4>📊 Excel文件解析结果 (A3标准)</h4>
                <div class="parse-info">
                    <p><strong>产品名称:</strong> ${parsedData.product_name}</p>
                    <p><strong>文案数量:</strong> ${parsedData.total_scripts} 条</p>
                    <p><strong>文件名:</strong> ${parsedData.filename}</p>
                    <p><strong>文件格式:</strong> ${parsedData.file_format || '未知'}</p>
                    <p><strong>自动选择情绪:</strong> ${parsedData.emotion}</p>
                    <p><strong>自动选择语音:</strong> ${parsedData.voice}</p>
                    <p><strong>包含中文翻译:</strong> ${parsedData.has_chinese_translation ? '是' : '否'}</p>
                    <p><strong>字段映射:</strong> ${JSON.stringify(parsedData.field_mapping || {}, null, 2)}</p>
                    <p><strong>GPTs兼容:</strong> ${parsedData.file_format === '.txt' || parsedData.filename.includes('GPT') || parsedData.filename.includes('AI') ? '✅ 支持' : '✅ 支持'}</p>
                </div>
                
                <div class="a3-compliance">
                    <h5>🎯 A3标准合规检查</h5>
                    <div class="compliance-grid">
                        <div class="compliance-item">
                            <span class="compliance-label">情绪有效性:</span>
                            <span class="compliance-status">${a3Compliance.emotion_valid ? '✅ 有效' : '❌ 无效'}</span>
                        </div>
                        <div class="compliance-item">
                            <span class="compliance-label">语音有效性:</span>
                            <span class="compliance-status">${a3Compliance.voice_valid ? '✅ 有效' : '❌ 无效'}</span>
                        </div>
                        <div class="compliance-item">
                            <span class="compliance-label">文案长度:</span>
                            <span class="compliance-status">${a3Compliance.scripts_length_valid ? '✅ 符合' : '❌ 不符合'}</span>
                        </div>
                        <div class="compliance-item">
                            <span class="compliance-label">产品名称:</span>
                            <span class="compliance-status">${a3Compliance.product_name_extracted ? '✅ 已提取' : '❌ 未提取'}</span>
                        </div>
                        <div class="compliance-item">
                            <span class="compliance-label">文件格式:</span>
                            <span class="compliance-status">${a3Compliance.file_format_supported ? '✅ 支持' : '❌ 不支持'}</span>
                        </div>
                        <div class="compliance-item">
                            <span class="compliance-label">字段映射:</span>
                            <span class="compliance-status">${a3Compliance.fields_mapped ? '✅ 成功' : '❌ 失败'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="parse-preview">
                    <h5>文案预览 (English Script):</h5>
                    <div class="preview-list">
                        ${parsedData.scripts.slice(0, 3).map((script, index) => `
                            <div class="preview-item">
                                <span class="preview-number">${index + 1}</span>
                                <span class="preview-text">${script}</span>
                                <span class="preview-emotion">${parsedData.emotion}</span>
                            </div>
                        `).join('')}
                        ${parsedData.scripts.length > 3 ? `<p class="preview-more">... 还有 ${parsedData.scripts.length - 3} 条文案</p>` : ''}
                    </div>
                </div>
            </div>
        `;

        this.showModal(
            'A3标准文件解析完成',
            content,
            `
                <button class="btn btn-secondary" onclick="window.ttControlCenter.closeModal()">仅上传</button>
                <button class="btn btn-primary" onclick="window.ttControlCenter.autoGenerateFromFile('${filename}')">按A3标准生成语音</button>
            `
        );
    }

    async autoGenerateFromFile(filename) {
        try {
            this.closeModal();
            this.showLoading(true);
            this.addLog(`开始自动生成语音: ${filename}`);
            
            const response = await fetch('/api/generate-from-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: filename
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('语音生成完成！', 'success');
                this.addLog(`自动生成完成: 成功${result.generation_result.summary.successful}个, 失败${result.generation_result.summary.failed}个`);
                
                // 刷新仪表板数据
                this.loadDashboardData();
                
                // 显示生成结果
                this.showGenerationResult(result.generation_result);
            } else {
                this.showToast(`自动生成失败: ${result.error}`, 'error');
                this.addLog(`自动生成失败: ${result.error}`);
            }
        } catch (error) {
            this.showToast('自动生成失败: ' + error.message, 'error');
            this.addLog(`自动生成失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    showGenerationResult(result) {
        const content = `
            <div class="generation-result">
                <h4>🎉 语音生成完成</h4>
                <div class="result-summary">
                    <div class="result-item success">
                        <i class="fas fa-check-circle"></i>
                        <span>成功: ${result.summary.successful} 个</span>
                    </div>
                    <div class="result-item error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>失败: ${result.summary.failed} 个</span>
                    </div>
                    <div class="result-item info">
                        <i class="fas fa-clock"></i>
                        <span>耗时: ${result.summary.duration_seconds.toFixed(1)} 秒</span>
                    </div>
                </div>
                <div class="result-actions">
                    <p><strong>输出目录:</strong> ${result.audio_directory}</p>
                    <p><strong>Excel文件:</strong> ${result.output_excel}</p>
                </div>
            </div>
        `;

        this.showModal(
            '生成结果',
            content,
            `
                <button class="btn btn-secondary" onclick="window.ttControlCenter.closeModal()">关闭</button>
                <button class="btn btn-primary" onclick="window.ttControlCenter.downloadResults('${result.audio_directory}')">下载结果</button>
            `
        );
    }

    async downloadResults(audioDirectory) {
        try {
            this.closeModal();
            this.showToast('开始下载生成结果...', 'info');
            
            // 这里应该实现下载功能
            // 可以创建一个zip文件包含所有生成的音频文件
            console.log('下载目录:', audioDirectory);
            this.showToast('下载功能开发中...', 'warning');
        } catch (error) {
            this.showToast('下载失败: ' + error.message, 'error');
        }
    }

    addFileToList(filename, size) {
        const fileList = document.getElementById('fileList');
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const sizeText = this.formatFileSize(size);
        const dateText = new Date().toLocaleDateString();
        
        fileItem.innerHTML = `
            <div class="file-icon">
                <i class="fas fa-file-excel"></i>
            </div>
            <div class="file-info">
                <span class="file-name">${filename}</span>
                <span class="file-size">${sizeText}</span>
                <span class="file-date">${dateText}</span>
            </div>
            <div class="file-actions">
                <button class="btn-icon" onclick="this.downloadFile('${filename}')">
                    <i class="fas fa-download"></i>
                </button>
                <button class="btn-icon" onclick="this.deleteFile('${filename}')">
                    <i class="fas fa-trash"></i>
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

    setupSliders() {
        const sliders = ['speedSlider', 'pitchSlider', 'volumeSlider'];
        
        sliders.forEach(sliderId => {
            const slider = document.getElementById(sliderId);
            const valueDisplay = document.getElementById(sliderId.replace('Slider', 'Value'));
            
            slider.addEventListener('input', () => {
                const value = slider.value;
                let displayValue;
                
                switch(sliderId) {
                    case 'speedSlider':
                    case 'pitchSlider':
                        displayValue = `${value > 0 ? '+' : ''}${value}%`;
                        break;
                    case 'volumeSlider':
                        displayValue = `${value > 0 ? '+' : ''}${value}dB`;
                        break;
                }
                
                valueDisplay.textContent = displayValue;
            });
        });
    }

    updateTextCount() {
        const textarea = document.getElementById('textContent');
        const text = textarea.value;
        const lines = text.split('\n').filter(line => line.trim()).length;
        
        document.getElementById('charCount').textContent = `${text.length} 字符`;
        document.getElementById('lineCount').textContent = `${lines} 行`;
    }

    addToHistory(productName, scriptCount) {
        const historyList = document.getElementById('historyList');
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        historyItem.innerHTML = `
            <div class="history-info">
                <span class="history-name">${productName}</span>
                <span class="history-time">刚刚</span>
            </div>
            <div class="history-actions">
                <button class="btn-icon small" onclick="this.playHistory('${productName}')">
                    <i class="fas fa-play"></i>
                </button>
                <button class="btn-icon small" onclick="this.downloadHistory('${productName}')">
                    <i class="fas fa-download"></i>
                </button>
            </div>
        `;
        
        historyList.insertBefore(historyItem, historyList.firstChild);
    }

    initializeCharts() {
        // 初始化图表（使用Chart.js）
        this.initTrendChart();
        this.initEmotionChart();
    }

    initTrendChart() {
        const ctx = document.getElementById('trendCanvas');
        if (!ctx) return;

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{
                    label: '生成数量',
                    data: [12, 19, 3, 5, 2, 3, 8],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initEmotionChart() {
        const ctx = document.getElementById('emotionCanvas');
        if (!ctx) return;

        this.charts.emotion = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['平静', '友好', '自信', '活泼', '兴奋', '紧急'],
                datasets: [{
                    data: [20, 25, 15, 10, 20, 10],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6',
                        '#f97316'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    loadAnalytics() {
        // 更新图表数据
        if (this.charts.trend) {
            // 模拟数据更新
            const newData = Array.from({length: 7}, () => Math.floor(Math.random() * 20) + 5);
            this.charts.trend.data.datasets[0].data = newData;
            this.charts.trend.update();
        }
    }

    addLog(message) {
        const logContainer = document.getElementById('logContainer');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const timestamp = new Date().toLocaleTimeString();
        const level = message.includes('失败') ? 'error' : 
                     message.includes('成功') ? 'success' : 
                     message.includes('警告') ? 'warning' : 'info';
        
        logEntry.innerHTML = `
            <span class="log-time">[${timestamp}]</span>
            <span class="log-level ${level}">${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // 限制日志条数
        const entries = logContainer.querySelectorAll('.log-entry');
        if (entries.length > 100) {
            entries[0].remove();
        }
    }

    clearLogs() {
        document.getElementById('logContainer').innerHTML = '';
        this.addLog('日志已清空');
    }

    toggleLogPause() {
        // 实现日志暂停/恢复功能
        console.log('切换日志暂停状态');
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';
        
        toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // 显示动画
        setTimeout(() => toast.classList.add('show'), 100);
        
        // 自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    showModal(title, content, actions = null) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = content;
        
        if (actions) {
            document.getElementById('modalFooter').innerHTML = actions;
        }
        
        document.getElementById('modal').classList.add('show');
    }

    closeModal() {
        document.getElementById('modal').classList.remove('show');
    }

    startRealTimeUpdates() {
        // 每5秒更新一次系统状态
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.updateSystemStatus();
            }
        }, 5000);

        // 每10秒检查连接状态
        setInterval(() => {
            this.checkConnection();
        }, 10000);

        // 每30秒更新任务数据
        setInterval(() => {
            if (this.currentSection === 'tasks' || this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000);
    }

    async exportData() {
        try {
            const response = await fetch('/api/export');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tt-live-ai-data-${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showToast('数据导出成功', 'success');
        } catch (error) {
            this.showToast('数据导出失败', 'error');
        }
    }

    async restartSystem() {
        this.showModal(
            '重启系统',
            '<p>确定要重启系统吗？这将停止所有正在进行的任务。</p>',
            `
                <button class="btn btn-secondary" onclick="this.closeModal()">取消</button>
                <button class="btn btn-primary" onclick="this.confirmRestart()">确认重启</button>
            `
        );
    }

    async confirmRestart() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/restart', { method: 'POST' });
            
            if (response.ok) {
                this.showToast('系统重启中...', 'info');
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                this.showToast('重启失败', 'error');
            }
        } catch (error) {
            this.showToast('重启失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
            this.closeModal();
        }
    }

    async startAllTasks() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/tasks/start-all', { method: 'POST' });
            
            if (response.ok) {
                this.showToast('所有任务已启动', 'success');
                this.loadTasks();
            } else {
                this.showToast('启动任务失败', 'error');
            }
        } catch (error) {
            this.showToast('启动任务失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.ttControlCenter = new ModernTTControlCenter();
});

// 全局函数（供HTML调用）
window.viewTask = function(taskId) {
    console.log('查看任务:', taskId);
};

window.deleteTask = function(taskId) {
    console.log('删除任务:', taskId);
};

window.playHistory = function(productName) {
    console.log('播放历史:', productName);
};

window.downloadHistory = function(productName) {
    console.log('下载历史:', productName);
};

window.downloadFile = function(filename) {
    console.log('下载文件:', filename);
};

window.deleteFile = function(filename) {
    console.log('删除文件:', filename);
};
