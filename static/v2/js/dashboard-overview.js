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

// Make switchTab globally accessible
window.switchTab = function(tabName) {
    console.log('🔵 switchTab called with:', tabName);
    
    // Update tab buttons - find the button by its onclick attribute
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        // Check if this button corresponds to the tabName
        const onclickAttr = btn.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(`'${tabName}'`)) {
            btn.classList.add('active');
            console.log('✅ Tab button activated:', tabName);
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        console.log('Removed active from:', content.id);
    });
    
    const targetTab = document.getElementById(`${tabName}-tab`);
    console.log('Looking for tab:', `${tabName}-tab`, 'Found:', targetTab);
    
    if (targetTab) {
        targetTab.classList.add('active');
        console.log('✅ Tab content activated:', targetTab.id, 'Has active class:', targetTab.classList.contains('active'));
        
        // Force display to check if CSS is the issue
        const computedStyle = window.getComputedStyle(targetTab);
        console.log('Tab display style:', computedStyle.display);
    } else {
        console.error(`❌ Tab with id "${tabName}-tab" not found`);
        console.log('Available tabs:', Array.from(document.querySelectorAll('.tab-content')).map(t => t.id));
        return; // Exit early if tab not found
    }
    
    currentTab = tabName;
    
    // Load tab-specific data
    if (tabName === 'overview') {
        if (typeof loadStats === 'function') {
            loadStats();
        }
    } else if (tabName === 'knowledge') {
        if (typeof refreshFileList === 'function') {
            refreshFileList().catch(err => {
                console.error('Error loading files in knowledge tab:', err);
            });
        }
        // Load knowledge stats when knowledge tab is opened
        if (typeof loadKnowledgeStats === 'function') {
            loadKnowledgeStats().catch(err => {
                console.error('Error loading knowledge stats:', err);
            });
        }
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
        if (typeof loadPrompt === 'function') {
            loadPrompt();
        }
        if (typeof loadPresets === 'function') {
            loadPresets(); // Load prompt presets
        }
    } else if (tabName === 'appearance') {
        if (typeof initializeAppearance === 'function') {
            initializeAppearance();
        }
    } else if (tabName === 'integration') {
        if (typeof updateIntegrationSnippet === 'function') {
            updateIntegrationSnippet();
        }
        // Load preview automatically when integration tab is opened
        setTimeout(() => {
            const iframe = document.getElementById('previewFrame');
            if (iframe && (!iframe.src || iframe.src === 'about:blank')) {
                iframe.src = '/demo';
            }
        }, 100);
    }
};

// Also create a non-window version for backwards compatibility
function switchTab(tabName) {
    return window.switchTab(tabName);
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
            fetch('/api/knowledge-stats', { credentials: 'same-origin' }),
            fetch('/api/crawled-urls', { credentials: 'same-origin' }),
            fetch('/api/user/chatbot-config', { credentials: 'same-origin' })
        ]);
        
        // Check if response is JSON before parsing
        let stats = {};
        if (statsResponse.ok) {
            const contentType = statsResponse.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                try {
                    stats = await statsResponse.json();
                } catch (jsonError) {
                    // If JSON parse fails, might be HTML redirect
                    const text = await statsResponse.clone().text();
                    if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                        console.error('❌ Received HTML instead of JSON - user may not be authenticated');
                        return; // Don't try to parse HTML as JSON
                    }
                    throw jsonError; // Re-throw if it's a different error
                }
            } else {
                console.warn('⚠️ Stats response is not JSON (content-type:', contentType, '), might be redirected to login');
                return;
            }
        } else {
            console.error('❌ Failed to load stats:', statsResponse.status, statsResponse.statusText);
            return;
        }
        
        stats.llm_model = stats.llm_model || 'gpt-4o-mini';
        
        // Safely parse crawled data
        let crawledData = { urls: [], total: 0 };
        if (crawledResponse.ok) {
            const contentType = crawledResponse.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                crawledData = await crawledResponse.json();
            }
        }
        
        // Safely parse config
        let config = {};
        if (configResponse.ok) {
            const contentType = configResponse.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const configPayload = await configResponse.json();
                config = configPayload.config || configPayload || {};
            }
        }
        
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
        console.error('❌ Failed to load stats:', error);
        // Don't show error if it's a JSON parse error from HTML redirect
        if (error.message && error.message.includes('JSON')) {
            console.warn('⚠️ JSON parse error - likely authentication issue. User may need to refresh page.');
        }
    }
}

async function loadFiles() {
    try {
        const response = await fetch('/api/files', {
            credentials: 'same-origin'
        });
        if (!response.ok) {
            console.error('Failed to load files:', response.status, response.statusText);
            return [];
        }
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Response is not JSON, might be redirected to login');
            return [];
        }
        const data = await response.json();
        return data.files || [];
    } catch (error) {
        console.error('Error loading files:', error);
        return []; // Return empty array instead of throwing
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
    try {
        const files = await loadFiles();
        updateFileList(files);
    } catch (error) {
        console.error('Error in refreshFileList:', error);
        // Show error in file list
        const fileList = document.getElementById('fileList');
        if (fileList) {
            fileList.innerHTML = '<div style="text-align: center; color: #dc3545; padding: 20px;">Error loading files. Please try again.</div>';
        }
    }
}

async function refreshFileList() {
    return window.refreshFileList();
}

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function updateFileList(files) {
    // Update both overview file list and knowledge tab file list
    const overviewFileList = document.getElementById('overviewFileList');
    const fileList = document.getElementById('fileList');
    
    try {
        // If files is undefined or not an array, set empty array to prevent infinite loop
        if (!files || !Array.isArray(files)) {
            console.warn('updateFileList called without valid files array, using empty array');
            files = [];
        }
    
    const emptyMessage = '<div style="text-align: center; color: #999; padding: 20px;">No files uploaded yet</div>';
    
    const fileHTML = files.length === 0 ? emptyMessage : files.map((file, index) => {
        // Safely extract filename - handle undefined, null, or empty values
        let filename = file.filename || file.name || 'Unknown File';
        // If filename is just an extension like ".pdf", use a default name
        if (filename.startsWith('.') && filename.length < 10) {
            filename = `Document${filename}`;
        }
        // Ensure filename is not undefined
        if (!filename || filename === 'undefined' || filename === 'null') {
            filename = 'Unknown File';
        }
        
        const category = file.category || 'company_details';
        const size = file.size || 0;
        const uploaded = file.uploaded_at || file.modified || file.uploaded || 'Unknown';
        const fileId = file.id || index;
        
        // Format uploaded date safely
        let uploadedDate = 'Unknown';
        try {
            if (uploaded && uploaded !== 'Unknown') {
                uploadedDate = new Date(uploaded).toLocaleDateString();
            }
        } catch (e) {
            uploadedDate = 'Unknown';
        }
        
        // Escape filename and category for HTML
        const safeFilename = String(filename).replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const safeCategory = String(category).replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const status = file.status || 'preview';
        
        // Status icon with circle background
        let statusIcon = '';
        let statusIconBg = '';
        if (status === 'ingested') {
            statusIcon = 'check_circle';
            statusIconBg = '#22c55e'; // Green
        } else if (status === 'error' || status === 'failed') {
            statusIcon = 'error';
            statusIconBg = '#ef4444'; // Red
        } else {
            statusIcon = 'visibility';
            statusIconBg = '#f59e0b'; // Yellow/Amber
        }
        
        // Status badge text
        let statusBadge = '';
        if (status === 'ingested') {
            statusBadge = '<span class="status-badge status-ingested" style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Ingest</span>';
        } else if (status === 'error' || status === 'failed') {
            statusBadge = '<span class="status-badge status-error" style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Error</span>';
        } else {
            statusBadge = '<span class="status-badge status-preview" style="background: #f59e0b; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Preview</span>';
        }
        
        const wordCount = (file.word_count !== undefined && file.word_count !== null) ? file.word_count : 0;
        const charCount = (file.char_count !== undefined && file.char_count !== null) ? file.char_count : 0;
        
        return `
        <div class="file-item" id="file-${fileId}" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; border-bottom: 1px solid #e1e5e9; background: white; border-radius: 8px; margin-bottom: 8px; gap: 12px; position: relative !important;">
            <!-- Status Icon with Circle Background (Top Left) -->
            <div class="file-status-icon" style="width: 40px; height: 40px; border-radius: 50%; background: ${statusIconBg}; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; position: relative; z-index: 1;">
                <span class="material-icons-round" style="font-size: 22px; color: white;">${statusIcon}</span>
            </div>
            
            <div class="file-info" style="flex: 1; min-width: 0;">
                <div class="file-name" style="font-weight: 600; margin-bottom: 6px; color: #1e293b; font-size: 14px;">${escapeHtml(filename)}</div>
                <div class="file-size" style="font-size: 12px; color: #64748b; display: flex; flex-wrap: wrap; align-items: center; gap: 4px;">
                    ${statusBadge}
                    <span>${typeof formatFileSize === 'function' ? formatFileSize(size) : (size ? (size / 1024).toFixed(1) + ' KB' : '0 B')}</span>
                    <span>•</span>
                    <span>${wordCount.toLocaleString()} words</span>
                    <span>•</span>
                    <span>${charCount.toLocaleString()} chars</span>
                    <span>•</span>
                    <span>${escapeHtml(category)}</span>
                    <span>•</span>
                    <span>${uploadedDate}</span>
                </div>
            </div>
            <div class="file-actions" style="display: flex; gap: 8px; flex-shrink: 0;">
                <button 
                    class="btn btn-secondary view-file-btn" 
                    data-file-id="${fileId}"
                    style="padding: 6px 12px; font-size: 12px; white-space: nowrap;"
                    title="View file preview">
                    <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">visibility</span> <span class="btn-text">View</span>
                </button>
                ${status === 'preview' ? `
                <button 
                    class="btn ingest-file-btn" 
                    data-file-id="${fileId}"
                    style="padding: 6px 12px; font-size: 12px; background: #0891b2; color: white; white-space: nowrap;"
                    title="Ingest to knowledge base">
                    <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">save</span> <span class="btn-text">Ingest</span>
                </button>
                ` : ''}
                <button 
                    class="btn btn-danger delete-file-btn" 
                    data-file-id="${fileId}"
                    data-filename="${safeFilename}"
                    data-category="${safeCategory}"
                    style="padding: 6px 12px; font-size: 12px; background: #dc3545; color: white; white-space: nowrap;"
                    title="Delete file and remove from knowledge base">
                    <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">delete</span> <span class="btn-text">Delete</span>
                </button>
            </div>
        </div>
        `;
    }).join('');
    
        // Add event listeners after rendering
        setTimeout(() => {
            try {
                // View file buttons
                document.querySelectorAll('.view-file-btn').forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const fileId = parseInt(this.getAttribute('data-file-id'));
                        if (typeof viewFile === 'function') {
                            await viewFile(fileId);
                        }
                    });
                });
                
                // Ingest file buttons
                document.querySelectorAll('.ingest-file-btn').forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const fileId = parseInt(this.getAttribute('data-file-id'));
                        if (typeof viewFile === 'function') {
                            await viewFile(fileId); // Show preview first, then user can ingest
                        }
                    });
                });
                
                // Delete file buttons
                document.querySelectorAll('.delete-file-btn').forEach(btn => {
                    btn.addEventListener('click', async function() {
                        const fileId = this.getAttribute('data-file-id');
                        const filename = this.getAttribute('data-filename');
                        const category = this.getAttribute('data-category');
                        if (fileId && typeof deleteFileById === 'function') {
                            await deleteFileById(fileId);
                        } else if (filename && typeof deleteFile === 'function') {
                            await deleteFile(filename, category);
                        }
                    });
                });
            } catch (eventError) {
                console.error('Error setting up file list event listeners:', eventError);
            }
        }, 100);
        // Update both file lists
        if (overviewFileList) overviewFileList.innerHTML = fileHTML;
        if (fileList) fileList.innerHTML = fileHTML;
    } catch (error) {
        console.error('Error in updateFileList:', error);
        // Show error message in file list
        const errorMessage = '<div style="text-align: center; color: #dc3545; padding: 20px;">Error loading files. Please refresh the page.</div>';
        if (fileList) {
            fileList.innerHTML = errorMessage;
        }
        if (overviewFileList) {
            overviewFileList.innerHTML = errorMessage;
        }
    }
}

function updateOverviewMetrics(stats, crawledData, config) {
    const uploadedFiles = Array.isArray(stats.uploaded_files) ? stats.uploaded_files : [];
    const crawledList = Array.isArray(crawledData?.urls) ? crawledData.urls : [];
    // Use stats.crawled_count from API if available, otherwise fallback to crawledData
    const crawledCount = typeof stats.crawled_count === 'number' ? stats.crawled_count : (typeof crawledData?.total === 'number' ? crawledData.total : crawledList.length);
    const ingestedCount = crawledList.filter(url => url.status === 'ingested').length;
    const faqCount = typeof stats.faq_count === 'number' ? stats.faq_count : 0;
    const ingestedFaqCount = typeof stats.ingested_faq_count === 'number' ? stats.ingested_faq_count : 0;
    
    // Show 0 instead of "—" when values are 0 (better UX)
    setTextContent('crawledSitesCount', crawledCount !== null && crawledCount !== undefined ? crawledCount : 0);
    setTextContent('uploadedFilesCount', uploadedFiles.length !== null && uploadedFiles.length !== undefined ? uploadedFiles.length : 0);
    setTextContent('faqEntriesCount', faqCount !== null && faqCount !== undefined ? faqCount : 0);
    setTextContent('crawledSitesSubtext', `${ingestedCount} ingested`);
    setTextContent('uploadedFilesSubtext', `${stats.total_documents || 0} knowledge chunks`);
    setTextContent('faqEntriesSubtext', ingestedFaqCount > 0 ? `${ingestedFaqCount} ingested` : 'Add FAQ entries');
    
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

