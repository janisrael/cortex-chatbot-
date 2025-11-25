// ===========================
// CORTEX AI DASHBOARD - OVERVIEW TAB
// Tab Management & Statistics
// ===========================

const PROMPT_PRESET_METADATA = {
    'virtual_assistant': {
        label: 'Virtual Assistant',
        icon: 'support_agent',
        description: 'General-purpose helpful assistant'
    },
    '1': {
        label: 'Virtual Assistant',
        icon: 'support_agent',
        description: 'General-purpose helpful assistant'
    },
    'sales_agent': {
        label: 'Sales Agent',
        icon: 'shopping_cart',
        description: 'Sales and product recommendations'
    },
    '3': {
        label: 'Sales Agent',
        icon: 'shopping_cart',
        description: 'Sales and product recommendations'
    },
    'tech_support': {
        label: 'Tech Support',
        icon: 'computer',
        description: 'Technical support and troubleshooting'
    },
    '2': {
        label: 'Tech Support',
        icon: 'computer',
        description: 'Technical support and troubleshooting'
    },
    'customer_service': {
        label: 'Customer Service',
        icon: 'headset_mic',
        description: 'Customer support and inquiries'
    },
    '4': {
        label: 'Customer Service',
        icon: 'headset_mic',
        description: 'Customer support and inquiries'
    },
    'educator': {
        label: 'Educator',
        icon: 'school',
        description: 'Educational content and tutoring'
    },
    '5': {
        label: 'Educator',
        icon: 'school',
        description: 'Educational content and tutoring'
    }
};

// ===========================
// TAB MANAGEMENT
// ===========================

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    currentTab = tabName;
    
    // Load tab-specific data
    if (tabName === 'overview') {
        loadStats();
    } else if (tabName === 'knowledge') {
        refreshFileList(); // Load files when knowledge tab is opened
    } else if (tabName === 'llm') {
        // Initialize LLM provider selection when LLM tab is opened
        console.log('📑 LLM tab opened, initializing provider selection...');
        setTimeout(() => {
            if (typeof window.initializeLLMProvider === 'function') {
                console.log('✅ Calling window.initializeLLMProvider...');
                window.initializeLLMProvider();
            } else if (typeof initializeLLMProvider === 'function') {
                console.log('✅ Calling initializeLLMProvider...');
                initializeLLMProvider();
            } else {
                console.error('❌ initializeLLMProvider function not found!');
                // Try to manually populate models
                if (typeof onProviderChange === 'function') {
                    console.log('🔄 Trying onProviderChange directly...');
                    onProviderChange();
                } else if (typeof window.onProviderChange === 'function') {
                    console.log('🔄 Trying window.onProviderChange directly...');
                    window.onProviderChange();
                }
            }
        }, 200);
    } else if (tabName === 'prompt') {
        loadPrompt();
        loadPresets(); // Load prompt presets
    } else if (tabName === 'appearance') {
        if (typeof initializeAppearance === 'function') {
            initializeAppearance();
        }
    } else if (tabName === 'integration') {
        updateIntegrationSnippet();
    }
}

// ===========================
// WEBSITE MANAGEMENT
// ===========================

async function loadWebsites() {
    // Simulate website loading - replace with actual API call if needed
    websites = {
        'default': { name: 'Default Configuration', active: true },
        'ecommerce-store.com': { name: 'E-Commerce Store', active: true },
        'tech-support.com': { name: 'Tech Support Portal', active: true },
        'healthcare-clinic.com': { name: 'Healthcare Clinic', active: true }
    };
    
    updateWebsiteTabs();
    selectWebsite('default');
}

function updateWebsiteTabs() {
    const websiteTabs = document.getElementById('websiteTabs');
    if (!websiteTabs) return;
    
    websiteTabs.innerHTML = '';
    
    Object.keys(websites).forEach(websiteId => {
        const website = websites[websiteId];
        const tab = document.createElement('div');
        tab.className = `website-tab ${websiteId === currentWebsiteId ? 'active' : ''}`;
        tab.textContent = website.name;
        tab.setAttribute('data-website-id', websiteId);
        tab.onclick = () => selectWebsite(websiteId);
        websiteTabs.appendChild(tab);
    });
}

function selectWebsite(websiteId) {
    currentWebsiteId = websiteId;
    
    // Update tab highlighting
    document.querySelectorAll('.website-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('data-website-id') === websiteId) {
            tab.classList.add('active');
        }
    });
    
    // Update displays
    const currentWebsiteName = document.getElementById('currentWebsiteName');
    if (currentWebsiteName) {
        currentWebsiteName.textContent = websites[websiteId]?.name || websiteId;
    }
    
    // Reload configuration for this website
    loadLLMConfig();
    loadStats();
    
    console.log(`Switched to website: ${websiteId}`);
}

// ===========================
// STATISTICS AND OVERVIEW
// ===========================

async function loadStats() {
    try {
        const [statsResponse, crawledResponse, configResponse] = await Promise.all([
            fetch('/api/knowledge-stats'),
            fetch('/api/crawled-urls'),
            fetch('/api/user/chatbot-config')
        ]);
        
        const stats = await statsResponse.json();
        if (!statsResponse.ok) {
            console.error('Failed to load stats:', stats);
            return;
        }
        
        stats.llm_model = stats.llm_model || 'gpt-4o-mini';
        
        const crawledData = crawledResponse.ok ? await crawledResponse.json() : { urls: [], total: 0 };
        const configPayload = configResponse.ok ? await configResponse.json() : {};
        const config = configPayload.config || configPayload || {};
        
        updateOverviewMetrics(stats, crawledData, config);
        
        // Update system management stats
        const vectorCount = document.getElementById('vectorCount');
        const fileCount = document.getElementById('fileCount');
        const chatLogCount = document.getElementById('chatLogCount');
        const backupCount = document.getElementById('backupCount');
        const websiteIdDisplay = document.getElementById('websiteIdDisplay');
        
        if (vectorCount) vectorCount.textContent = stats.total_documents || 0;
        if (fileCount) fileCount.textContent = stats.uploaded_files?.length || 0;
        if (chatLogCount) chatLogCount.textContent = stats.chat_logs || 0;
        if (backupCount) backupCount.textContent = stats.backups || 0;
        if (websiteIdDisplay) websiteIdDisplay.textContent = currentWebsiteId;
        
        // Load files from /api/files endpoint (user-specific)
        await refreshFileList();
        
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadFiles() {
    try {
        const response = await fetch('/api/files');
        if (!response.ok) {
            console.error('Failed to load files');
            return [];
        }
        const data = await response.json();
        return data.files || [];
    } catch (error) {
        console.error('Error loading files:', error);
        return [];
    }
}

// Make deleteFile globally accessible
window.deleteFile = async function(filename, category) {
    if (!confirm(`Are you sure you want to delete "${filename}"?\n\nThis will remove the file and all its knowledge from your chatbot.`)) {
        return false;
    }
    
    try {
        const response = await fetch(`/api/files/${encodeURIComponent(filename)}?category=${encodeURIComponent(category)}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete file');
        }
        
        const result = await response.json();
        alert(`✅ ${result.message || 'File deleted successfully'}`);
        
        // Reload file list
        await refreshFileList();
        await loadStats();
        
        return true;
    } catch (error) {
        alert(`❌ Error deleting file: ${error.message}`);
        console.error('Delete file error:', error);
        return false;
    }
}

async function deleteFile(filename, category) {
    return window.deleteFile(filename, category);
}

// Make refreshFileList globally accessible
window.refreshFileList = async function() {
    const files = await loadFiles();
    updateFileList(files);
}

async function refreshFileList() {
    return window.refreshFileList();
}

function updateFileList(files) {
    // Update both overview file list and knowledge tab file list
    const overviewFileList = document.getElementById('overviewFileList');
    const fileList = document.getElementById('fileList');
    
    // If files is undefined or not an array, reload files
    if (!files || !Array.isArray(files)) {
        console.log('updateFileList called without files, reloading...');
        refreshFileList();
        return;
    }
    
    const emptyMessage = '<div style="text-align: center; color: #999; padding: 20px;">No files uploaded yet</div>';
    
    const fileHTML = files.length === 0 ? emptyMessage : files.map((file, index) => {
        const filename = file.filename || file.name;
        const category = file.category || 'company_details';
        const size = file.size || 0;
        const uploaded = file.uploaded_at || file.modified || 'Unknown';
        const fileId = `file-${index}-${Date.now()}`;
        
        // Escape filename and category for HTML
        const safeFilename = filename.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const safeCategory = category.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        
        return `
        <div class="file-item" id="${fileId}" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #e1e5e9;">
            <div class="file-info" style="flex: 1;">
                <div class="file-name" style="font-weight: 600; margin-bottom: 4px;">${filename}</div>
                <div class="file-size" style="font-size: 12px; color: #666;">
                    ${formatFileSize(size)} • ${category} • ${new Date(uploaded).toLocaleDateString()}
                </div>
            </div>
            <button 
                class="btn btn-danger delete-file-btn" 
                data-filename="${safeFilename}"
                data-category="${safeCategory}"
                style="padding: 6px 12px; font-size: 12px; margin-left: 10px;"
                title="Delete file and remove from knowledge base">
                🗑️ Delete
            </button>
        </div>
        `;
    }).join('');
    
    // Add event listeners to delete buttons after rendering
    setTimeout(() => {
        document.querySelectorAll('.delete-file-btn').forEach(btn => {
            btn.addEventListener('click', async function() {
                const filename = this.getAttribute('data-filename');
                const category = this.getAttribute('data-category');
                await deleteFile(filename, category);
            });
        });
    }, 100);
    
    if (overviewFileList) overviewFileList.innerHTML = fileHTML;
    if (fileList) fileList.innerHTML = fileHTML;
}

function updateOverviewMetrics(stats, crawledData, config) {
    const uploadedFiles = Array.isArray(stats.uploaded_files) ? stats.uploaded_files : [];
    const crawledList = Array.isArray(crawledData?.urls) ? crawledData.urls : [];
    const crawledCount = typeof crawledData?.total === 'number' ? crawledData.total : crawledList.length;
    const ingestedCount = crawledList.filter(url => url.status === 'ingested').length;
    const faqCount = getFaqCountFromFiles(uploadedFiles);
    
    setTextContent('crawledSitesCount', crawledCount ?? '—');
    setTextContent('uploadedFilesCount', uploadedFiles.length ?? '—');
    setTextContent('faqEntriesCount', faqCount ?? '—');
    setTextContent('crawledSitesSubtext', `${ingestedCount} ingested`);
    setTextContent('uploadedFilesSubtext', `${stats.total_documents || 0} knowledge chunks`);
    setTextContent('faqEntriesSubtext', faqCount > 0 ? 'Auto-tagged from uploads' : 'Add FAQ documents');
    
    updateChatbotOverviewCard(config, stats);
}

function updateChatbotOverviewCard(config, stats) {
    const botName = config.bot_name || 'Cortex';
    setTextContent('overviewBotName', botName);
    setTextContent('overviewBotDescription', config.short_info || 'Customize this description from the Appearance tab.');
    
    const presetId = (config.prompt_preset_id !== undefined && config.prompt_preset_id !== null)
        ? String(config.prompt_preset_id)
        : 'virtual_assistant';
    const personaMeta = PROMPT_PRESET_METADATA[presetId] || {
        label: 'Custom Persona',
        icon: 'emoji_objects',
        description: 'Custom instructions applied to this chatbot'
    };
    setTextContent('overviewBotPersona', personaMeta.label);
    setTextContent('overviewPersonaTitle', personaMeta.label);
    setTextContent('overviewPersonaDescription', personaMeta.description);
    const personaIcon = document.getElementById('overviewPersonaIcon');
    if (personaIcon) {
        personaIcon.textContent = personaMeta.icon;
    }
    
    const llmModel = config.llm_model || stats.llm_model || 'gpt-4o-mini';
    setTextContent('overviewLLMModel', llmModel);
    
    const primaryColorValue = extractPrimaryColorValue(config.primary_color);
    const knowledgeChip = document.getElementById('overviewKnowledgeChip');
    if (knowledgeChip) {
        knowledgeChip.textContent = `${stats.total_documents || 0} knowledge chunks`;
    }
    
    const websiteChip = document.getElementById('overviewWebsiteChip');
    if (websiteChip) {
        const websiteName = websites[currentWebsiteId]?.name || currentWebsiteId || 'Default Website';
        websiteChip.textContent = websiteName;
    }
    
    updateOverviewAvatar(config, primaryColorValue, botName);
}

function updateOverviewAvatar(config, primaryColorValue, botName) {
    const avatarWrapper = document.getElementById('overviewBotAvatar');
    const avatarImg = document.getElementById('overviewBotAvatarImg');
    if (!avatarWrapper || !avatarImg) return;
    
    let avatarUrl = null;
    if (config.avatar) {
        if (config.avatar.type === 'preset' && config.avatar.value) {
            avatarUrl = `/static/img/avatar/${config.avatar.value}.png`;
        } else if (config.avatar.src) {
            avatarUrl = config.avatar.src;
        }
    }
    
    if (!avatarUrl) {
        const hex = extractPrimaryColorHex(primaryColorValue);
        avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(botName)}&background=${hex}&color=fff&size=128`;
    }
    
    avatarImg.src = avatarUrl;
    avatarImg.alt = `${botName} Avatar`;
    
    if (primaryColorValue && avatarWrapper) {
        const borderHex = primaryColorValue.startsWith('#') ? primaryColorValue : `#${extractPrimaryColorHex(primaryColorValue)}`;
        avatarWrapper.style.borderColor = borderHex;
    }
}

function getFaqCountFromFiles(files) {
    if (!Array.isArray(files)) return 0;
    return files.filter(file => {
        const category = (file.category || '').toLowerCase();
        const filename = (file.filename || file.name || '').toLowerCase();
        return category.includes('faq') || filename.includes('faq');
    }).length;
}

function extractPrimaryColorValue(primaryColor) {
    if (!primaryColor) return '#0891b2';
    if (typeof primaryColor === 'string') return primaryColor;
    if (typeof primaryColor === 'object') {
        if (primaryColor.value) return primaryColor.value;
        if (primaryColor.hex) return primaryColor.hex;
    }
    return '#0891b2';
}

function extractPrimaryColorHex(colorValue) {
    if (!colorValue) return '0891b2';
    if (colorValue.startsWith('#')) {
        return colorValue.replace('#', '').substring(0, 6) || '0891b2';
    }
    const match = colorValue.match(/#([0-9A-Fa-f]{6})/);
    if (match) {
        return match[1];
    }
    return '0891b2';
}

function setTextContent(elementId, value) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const displayValue = (value === undefined || value === null || value === '') ? '—' : value;
    el.textContent = displayValue;
}

