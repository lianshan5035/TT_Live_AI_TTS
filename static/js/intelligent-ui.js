document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.nav-link');
    const chips = document.querySelectorAll('.chip[data-section]');
    const drawerToggle = document.getElementById('drawerToggle');
    const navToggle = document.getElementById('navToggle');
    const sideNav = document.querySelector('.side-nav');
    const scriptInput = document.getElementById('scriptInput');
    const charCounter = document.getElementById('charCounter');
    const lineCounter = document.getElementById('lineCounter');
    const sliders = [
        { input: 'rateSlider', label: 'rateValue', suffix: '%' },
        { input: 'pitchSlider', label: 'pitchValue', suffix: '%' },
        { input: 'volumeSlider', label: 'volumeValue', suffix: 'dB' }
    ];
    const floatingPanel = document.getElementById('floatingPanel');
    const floatingTrigger = floatingPanel?.querySelector('.floating-trigger');
    const themeToggle = document.getElementById('themeToggle');
    
    // Excel上传相关元素
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const activityFeed = document.getElementById('activityFeed');
    const previewList = document.getElementById('previewList');

    const activateSection = (target) => {
        if (!target) return;
        sections.forEach(section => {
            section.classList.toggle('active', section.id === target);
        });
        navLinks.forEach(link => {
            link.classList.toggle('active', link.dataset.section === target);
        });
        chips.forEach(chip => {
            chip.classList.toggle('active', chip.dataset.section === target);
        });
    };

    const updateCounters = () => {
        if (!scriptInput || !charCounter || !lineCounter) return;
        const text = scriptInput.value;
        charCounter.textContent = text.replace(/\s/g, '').length;
        const lines = text.length ? text.split(/\r?\n/).length : 0;
        lineCounter.textContent = lines;
    };

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const target = link.dataset.section;
            activateSection(target);
            if (window.innerWidth < 768) {
                sideNav?.classList.remove('active');
            }
        });
    });

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const target = chip.dataset.section;
            activateSection(target);
        });
    });

    drawerToggle?.addEventListener('click', () => {
        sideNav?.classList.toggle('active');
    });

    navToggle?.addEventListener('click', () => {
        sideNav?.classList.toggle('collapsed');
    });

    scriptInput?.addEventListener('input', updateCounters);
    updateCounters();

    sliders.forEach(({ input, label, suffix }) => {
        const inputEl = document.getElementById(input);
        const labelEl = document.getElementById(label);
        if (!inputEl || !labelEl) return;
        const update = () => {
            labelEl.textContent = `${inputEl.value}${suffix}`;
        };
        inputEl.addEventListener('input', update);
        update();
    });

    floatingTrigger?.addEventListener('click', () => {
        floatingPanel.classList.toggle('active');
    });

    document.addEventListener('click', (event) => {
        if (!floatingPanel.contains(event.target) && floatingPanel.classList.contains('active')) {
            floatingPanel.classList.remove('active');
        }
    });

    themeToggle?.addEventListener('click', () => {
        const current = document.documentElement.dataset.theme;
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = next;
        themeToggle.innerHTML = next === 'dark'
            ? '<i class="fa-solid fa-sun"></i>'
            : '<i class="fa-solid fa-moon"></i>';
    });

    // ==================== Excel上传和自动生成功能 ====================
    
    // 文件上传处理
    const handleFileUpload = async (file) => {
        if (!file) return;
        
        // 检查文件类型
        const allowedTypes = ['.xlsx', '.xls', '.csv', '.tsv', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            showToast('不支持的文件格式，请上传Excel、CSV或TXT文件', 'error');
            return;
        }
        
        // 显示上传进度
        showToast(`正在上传 ${file.name}...`, 'info');
        addActivityItem(file.name, '上传中', 'warning');
        
        try {
            // 上传文件
            const formData = new FormData();
            formData.append('file', file);
            
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                throw new Error(`上传失败: ${uploadResponse.status}`);
            }
            
            const uploadResult = await uploadResponse.json();
            showToast('文件上传成功，开始解析...', 'success');
            updateActivityItem(file.name, '解析中', 'warning');
            
            // 显示解析进度条
            showParseProgress(file.name, uploadResult);
            
            // 解析成功后直接开始生成，不显示模态框
            if (uploadResult.success) {
                showToast('解析完成，开始生成语音...', 'info');
                updateActivityItem(file.name, '生成中', 'warning');
                
                await autoGenerateFromFile(uploadResult.filename);
            } else {
                throw new Error(uploadResult.error || '文件解析失败');
            }
            
        } catch (error) {
            console.error('文件上传错误:', error);
            showToast(`上传失败: ${error.message}`, 'error');
            updateActivityItem(file.name, '失败', 'danger');
        }
    };
    
    // 显示解析进度条
    const showParseProgress = (filename, result) => {
        // 创建进度条容器
        const progressContainer = document.createElement('div');
        progressContainer.className = 'parse-progress-container';
        progressContainer.innerHTML = `
            <div class="parse-progress">
                <div class="progress-header">
                    <h3><i class="fa-solid fa-file-excel"></i> ${filename}</h3>
                    <span class="progress-status">解析中...</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <div class="progress-details">
                    <div class="detail-item">
                        <strong>产品名称:</strong> <span class="product-name">${result.product_name || '未识别'}</span>
                    </div>
                    <div class="detail-item">
                        <strong>文件格式:</strong> <span class="file-format">${result.file_format}</span>
                    </div>
                    <div class="detail-item">
                        <strong>脚本数量:</strong> <span class="script-count">${result.scripts ? result.scripts.length : 0} 条</span>
                    </div>
                    <div class="detail-item">
                        <strong>推荐音色:</strong> <span class="voice">${result.voice || '自动选择'}</span>
                    </div>
                    <div class="detail-item">
                        <strong>推荐情绪:</strong> <span class="emotion">${result.emotion || '平衡'}</span>
                    </div>
                    <div class="detail-item">
                        <strong>A3标准:</strong> <span class="a3-compliance">${result.a3_compliance ? '✅ 符合' : '❌ 不符合'}</span>
                    </div>
                </div>
            </div>
        `;
        
        // 插入到活动区域
        const activityFeed = document.getElementById('activityFeed');
        if (activityFeed) {
            activityFeed.insertBefore(progressContainer, activityFeed.firstChild);
        }
        
        // 模拟进度条动画
        const progressFill = progressContainer.querySelector('.progress-fill');
        const progressStatus = progressContainer.querySelector('.progress-status');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            progressFill.style.width = progress + '%';
            
            if (progress < 30) {
                progressStatus.textContent = '解析中...';
            } else if (progress < 60) {
                progressStatus.textContent = '分析字段...';
            } else if (progress < 90) {
                progressStatus.textContent = '提取脚本...';
            } else if (progress < 100) {
                progressStatus.textContent = '完成解析...';
            } else {
                progressStatus.textContent = '解析完成';
                clearInterval(interval);
                
                // 3秒后自动移除进度条
                setTimeout(() => {
                    if (progressContainer.parentNode) {
                        progressContainer.remove();
                    }
                }, 3000);
            }
        }, 200);
    };
    
    // 自动生成语音
    const autoGenerateFromFile = async (filename) => {
        try {
            const response = await fetch('/api/generate-from-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename })
            });
            
            if (!response.ok) {
                throw new Error(`生成失败: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                showToast('语音生成完成！', 'success');
                updateActivityItem(filename, '已完成', 'success');
                
                // 更新预览列表
                updatePreviewList(result.generated_files || []);
                
                // 显示生成结果
                showGenerationResult(result);
            } else {
                throw new Error(result.error || '生成失败');
            }
            
        } catch (error) {
            console.error('自动生成错误:', error);
            showToast(`生成失败: ${error.message}`, 'error');
            updateActivityItem(filename, '失败', 'danger');
        }
    };
    
    // 显示生成结果
    const showGenerationResult = (result) => {
        const modal = createModal('生成完成', `
            <div class="generation-result">
                <div class="result-summary">
                    <div class="summary-item success">
                        <i class="fa-solid fa-check-circle"></i>
                        <span>成功: ${result.successful || 0} 个文件</span>
                    </div>
                    <div class="summary-item error">
                        <i class="fa-solid fa-times-circle"></i>
                        <span>失败: ${result.failed || 0} 个文件</span>
                    </div>
                    <div class="summary-item info">
                        <i class="fa-solid fa-clock"></i>
                        <span>耗时: ${result.duration || '未知'}</span>
                    </div>
                </div>
                ${result.generated_files ? `
                <div class="file-list">
                    <h4>生成的文件:</h4>
                    <ul>
                        ${result.generated_files.map(file => `
                            <li>
                                <i class="fa-solid fa-file-audio"></i>
                                <span>${file}</span>
                                <button class="btn btn-sm btn-outline" onclick="downloadFile('${file}')">
                                    <i class="fa-solid fa-download"></i>
                                </button>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `);
        
        document.body.appendChild(modal);
    };
    
    // 更新预览列表
    const updatePreviewList = (files) => {
        if (!previewList) return;
        
        previewList.innerHTML = files.map((file, index) => `
            <li class="preview-item ${index === 0 ? 'active' : ''}">
                <button class="icon-btn small" onclick="playPreview('${file}')">
                    <i class="fa-solid fa-play"></i>
                </button>
                <div>
                    <p>片段 ${String(index + 1).padStart(2, '0')} · ${getFileDuration(file)}</p>
                    <span>自动生成</span>
                </div>
                <button class="icon-btn small" onclick="downloadFile('${file}')">
                    <i class="fa-solid fa-download"></i>
                </button>
            </li>
        `).join('');
    };
    
    // 添加活动项
    const addActivityItem = (name, status, type) => {
        if (!activityFeed) return;
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        const item = document.createElement('li');
        item.innerHTML = `
            <span class="feed-time">${timeStr}</span>
            <div>
                <p>${name}</p>
                <span class="chip subtle ${type}" data-status="${status}">${status}</span>
            </div>
        `;
        
        activityFeed.insertBefore(item, activityFeed.firstChild);
    };
    
    // 更新活动项状态
    const updateActivityItem = (name, status, type) => {
        if (!activityFeed) return;
        
        const items = activityFeed.querySelectorAll('li');
        for (const item of items) {
            const nameElement = item.querySelector('p');
            if (nameElement && nameElement.textContent === name) {
                const statusElement = item.querySelector('.chip');
                if (statusElement) {
                    statusElement.textContent = status;
                    statusElement.className = `chip subtle ${type}`;
                }
                break;
            }
        }
    };
    
    // 创建模态框
    const createModal = (title, content) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fa-solid fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        return modal;
    };
    
    // 显示Toast消息
    const showToast = (message, type = 'info') => {
        const toastStack = document.getElementById('toastStack');
        if (!toastStack) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fa-solid fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        toastStack.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            toast.remove();
        }, 5000);
    };
    
    // 文件拖拽处理
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput?.click();
        });
    }
    
    // 文件输入处理
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });
    }
    
    // 上传按钮处理
    if (fileUploadBtn) {
        fileUploadBtn.addEventListener('click', () => {
            fileInput?.click();
        });
    }
    
    // 全局函数
    window.playPreview = (filename) => {
        // 播放预览音频
        const audio = new Audio(`/api/play/${filename}`);
        audio.play().catch(e => console.error('播放失败:', e));
    };
    
    window.downloadFile = (filename) => {
        // 下载文件
        const link = document.createElement('a');
        link.href = `/api/download/${filename}`;
        link.download = filename;
        link.click();
    };
    
    window.getFileDuration = (filename) => {
        // 模拟获取文件时长
        return '00:12';
    };
});
