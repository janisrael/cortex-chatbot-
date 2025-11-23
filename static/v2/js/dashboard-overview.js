// ===========================
// CORTEX AI DASHBOARD - OVERVIEW TAB
// Tab Management & Statistics
// ===========================

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
    } else if (tabName === 'prompt') {
        loadPrompt();
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
        // Fetch real stats from API
        const response = await fetch('/api/knowledge-stats');
        const stats = await response.json();
        
        // If API call fails, return early
        if (!response.ok) {
            console.error('Failed to load stats:', stats);
            return;
        }
        
        // Add LLM model display name
        stats.llm_model = stats.llm_model || 'GPT-4o Mini';
        
        // Update overview stats
        const totalDocs = document.getElementById('totalDocs');
        const totalFiles = document.getElementById('totalFiles');
        const llmModel = document.getElementById('llmModel');
        const currentWebsite = document.getElementById('currentWebsite');
        
        if (totalDocs) totalDocs.textContent = stats.total_documents || 0;
        if (totalFiles) totalFiles.textContent = stats.uploaded_files?.length || 0;
        if (llmModel) llmModel.textContent = stats.llm_model || 'Unknown';
        if (currentWebsite) currentWebsite.textContent = websites[currentWebsiteId]?.name || currentWebsiteId;
        
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
