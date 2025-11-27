// Dashboard File Management - File Upload and Categories

// ====================================
// FILE MANAGEMENT FUNCTIONS
// ====================================
async function initializeFileManagement() {
    try {
        await loadCategories();
        // Use refreshFileList instead of loadFilesByCategory for consistency
        // refreshFileList uses updateFileList which has the new design with status icons
        if (typeof refreshFileList === 'function') {
            await refreshFileList();
        } else {
            // Fallback to old method if refreshFileList not available
            await loadFilesByCategory();
        }
        await refreshCrawledUrls(); // Load crawled URLs
        await loadKnowledgeStats(); // Load stats cards
        setupFileUpload();
    } catch (error) {
        console.error('Failed to initialize file management:', error);
    }
}

async function loadKnowledgeStats() {
    try {
        console.log('📊 Loading knowledge stats...');
        const response = await fetch('/api/knowledge-stats', {
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            console.error('❌ Failed to load knowledge stats:', response.status, response.statusText);
            // Set default values on error
            const filesCountEl = document.getElementById('knowledgeFilesCount');
            const crawledCountEl = document.getElementById('knowledgeCrawledCount');
            const faqCountEl = document.getElementById('knowledgeFaqCount');
            if (filesCountEl) filesCountEl.textContent = '0';
            if (crawledCountEl) crawledCountEl.textContent = '0';
            if (faqCountEl) faqCountEl.textContent = '0';
            return;
        }
        
        const stats = await response.json();
        console.log('📊 Knowledge stats received:', stats);
        
        // Update Files Card
        const filesCountEl = document.getElementById('knowledgeFilesCount');
        const filesLimitEl = document.getElementById('knowledgeFilesLimit');
        if (filesCountEl) {
            const fileCount = (stats.file_count !== undefined && stats.file_count !== null) ? stats.file_count : 0;
            const maxFiles = stats.max_files || 100;
            filesCountEl.textContent = `${fileCount}/${maxFiles}`;
            console.log(`✅ Updated files count: ${fileCount}/${maxFiles}`);
        } else {
            console.warn('⚠️ knowledgeFilesCount element not found');
        }
        if (filesLimitEl) {
            filesLimitEl.textContent = `Limit: ${stats.max_files || 100} files`;
        }
        
        // Update Crawled Websites Card
        const crawledCountEl = document.getElementById('knowledgeCrawledCount');
        const crawledLimitEl = document.getElementById('knowledgeCrawledLimit');
        if (crawledCountEl) {
            const crawledCount = (stats.crawled_count !== undefined && stats.crawled_count !== null) ? stats.crawled_count : 0;
            const maxCrawled = stats.max_crawled || 200;
            crawledCountEl.textContent = `${crawledCount}/${maxCrawled}`;
            console.log(`✅ Updated crawled count: ${crawledCount}/${maxCrawled}`);
        } else {
            console.warn('⚠️ knowledgeCrawledCount element not found');
        }
        if (crawledLimitEl) {
            crawledLimitEl.textContent = `Limit: ${stats.max_crawled || 200} websites`;
        }
        
        // Update FAQ Card
        const faqCountEl = document.getElementById('knowledgeFaqCount');
        const faqLimitEl = document.getElementById('knowledgeFaqLimit');
        if (faqCountEl) {
            const faqCount = (stats.faq_count !== undefined && stats.faq_count !== null) ? stats.faq_count : 0;
            const maxFaqs = stats.max_faqs || 500;
            faqCountEl.textContent = `${faqCount}/${maxFaqs}`;
            console.log(`✅ Updated FAQ count: ${faqCount}/${maxFaqs}`);
        } else {
            console.warn('⚠️ knowledgeFaqCount element not found');
        }
        if (faqLimitEl) {
            faqLimitEl.textContent = `Limit: ${stats.max_faqs || 500} FAQs`;
        }
        
    } catch (error) {
        console.error('❌ Failed to load knowledge stats:', error);
        // Set default values on error
        const filesCountEl = document.getElementById('knowledgeFilesCount');
        const crawledCountEl = document.getElementById('knowledgeCrawledCount');
        const faqCountEl = document.getElementById('knowledgeFaqCount');
        if (filesCountEl) filesCountEl.textContent = '0';
        if (crawledCountEl) crawledCountEl.textContent = '0';
        if (faqCountEl) faqCountEl.textContent = '0';
    }
}

// Make loadKnowledgeStats globally accessible
window.loadKnowledgeStats = loadKnowledgeStats;

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        categories = data.categories || {};
        renderCategoryTabs();
        updateSelectedCategoryInfo();
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

// Category icons mapping
const CATEGORY_ICONS = {
    'company_details': 'business',
    'sales_training': 'school',
    'product_info': 'inventory',
    'policies_legal': 'gavel',
    'faq': 'help_center'
};

// FAQ category selection (global)
let selectedFaqCategory = 'company_details';
window.selectedFaqCategory = selectedFaqCategory; // Make globally accessible

// Make selectFaqCategory globally accessible
window.selectFaqCategory = function(categoryId) {
    selectedFaqCategory = categoryId;
    window.selectedFaqCategory = categoryId; // Update global reference
    renderCategoryTabs();
    // Reload FAQs filtered by category
    if (typeof loadFAQs === 'function') {
        loadFAQs();
    }
};

function renderCategoryTabs() {
    // Render for file upload section
    const tabsContainer = document.getElementById('categoryTabs');
    if (tabsContainer) {
        tabsContainer.innerHTML = '';
        Object.entries(categories).forEach(([categoryId, categoryInfo]) => {
            const tab = document.createElement('div');
            tab.className = 'category-tab' + (categoryId === selectedCategory ? ' active' : '');
            tab.onclick = () => selectCategory(categoryId);
            tab.title = categoryInfo.description; // Tooltip with description
            
            // Icon
            const iconDiv = document.createElement('span');
            iconDiv.className = 'material-icons-round category-icon';
            iconDiv.textContent = CATEGORY_ICONS[categoryId] || 'folder';
            
            // Name
            const nameDiv = document.createElement('div');
            nameDiv.className = 'category-name';
            nameDiv.textContent = categoryInfo.name;
            
            tab.appendChild(iconDiv);
            tab.appendChild(nameDiv);
            tabsContainer.appendChild(tab);
        });
    }
    
    // Render for FAQ section
    const faqTabsContainer = document.getElementById('faqCategoryTabs');
    if (faqTabsContainer) {
        faqTabsContainer.innerHTML = '';
        Object.entries(categories).forEach(([categoryId, categoryInfo]) => {
            const tab = document.createElement('div');
            tab.className = 'category-tab' + (categoryId === selectedFaqCategory ? ' active' : '');
            tab.onclick = () => selectFaqCategory(categoryId);
            tab.title = categoryInfo.description;
            
            // Icon
            const iconDiv = document.createElement('span');
            iconDiv.className = 'material-icons-round category-icon';
            iconDiv.textContent = CATEGORY_ICONS[categoryId] || 'folder';
            
            // Name
            const nameDiv = document.createElement('div');
            nameDiv.className = 'category-name';
            nameDiv.textContent = categoryInfo.name;
            
            tab.appendChild(iconDiv);
            tab.appendChild(nameDiv);
            faqTabsContainer.appendChild(tab);
        });
    }
}


function selectCategory(categoryId) {
    selectedCategory = categoryId;
    renderCategoryTabs();
    updateSelectedCategoryInfo();
}

function updateSelectedCategoryInfo() {
    const info = document.getElementById('selectedCategoryInfo');
    if (!info) return;
    
    const categoryInfo = categories[selectedCategory];
    if (categoryInfo) {
        const nameDiv = document.createElement('div');
        nameDiv.className = 'selected-category-name';
        nameDiv.textContent = categoryInfo.name;
        
        const descDiv = document.createElement('div');
        descDiv.className = 'category-description';
        descDiv.textContent = categoryInfo.description;
        
        info.innerHTML = '';
        info.appendChild(nameDiv);
        info.appendChild(descDiv);
    }
}

async function loadFilesByCategory() {
    try {
        const url = '/api/files-by-category' + (currentWebsiteId !== 'default' ? '?website_id=' + currentWebsiteId : '');
        const response = await fetch(url);
        const categoriesWithFiles = await response.json();
        renderFilesByCategory(categoriesWithFiles);
    } catch (error) {
        console.error('Failed to load files by category:', error);
    }
}

function renderFilesByCategory(categoriesWithFiles) {
    const container = document.getElementById('filesByCategory');
    if (!container) return;
    
    if (Object.keys(categoriesWithFiles).length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No files uploaded yet</p>';
        return;
    }
    
    container.innerHTML = '';
    
    Object.entries(categoriesWithFiles).forEach(([categoryId, categoryData]) => {
        const section = document.createElement('div');
        section.className = 'category-section';
        
        // Create header
        const header = document.createElement('div');
        header.className = 'category-header';
        header.onclick = () => toggleCategoryFiles(categoryId);
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'category-name';
        nameDiv.textContent = categoryData.name;
        
        const countBadge = document.createElement('div');
        countBadge.className = 'file-count-badge';
        countBadge.textContent = categoryData.file_count + ' files';
        
        header.appendChild(nameDiv);
        header.appendChild(countBadge);
        
        // Create files container
        const filesDiv = document.createElement('div');
        filesDiv.className = 'category-files';
        filesDiv.id = 'files-' + categoryId;
        
        if (categoryData.files.length === 0) {
            const noFilesP = document.createElement('p');
            noFilesP.style.cssText = 'padding: 15px; text-align: center; color: #666;';
            noFilesP.textContent = 'No files in this category';
            filesDiv.appendChild(noFilesP);
        } else {
            categoryData.files.forEach((file, index) => {
                const fileId = file.id || `${categoryId}-${index}`;
                const filename = file.filename || file.name || 'Unknown File';
                const safeFilename = (filename.startsWith('.') && filename.length < 10) 
                    ? `Document${filename}` 
                    : (filename && filename !== 'undefined' && filename !== 'null' ? filename : 'Unknown File');
                const category = file.category || categoryId;
                const size = file.size || 0;
                const uploaded = file.uploaded_at || file.modified || file.uploaded || 'Unknown';
                const status = file.status || 'preview';
                
                // Format uploaded date
                let uploadedDate = 'Unknown';
                try {
                    if (uploaded && uploaded !== 'Unknown') {
                        uploadedDate = new Date(uploaded).toLocaleDateString();
                    }
                } catch (e) {
                    uploadedDate = 'Unknown';
                }
                
                // Status icon and badge
                let statusIcon = '';
                let statusIconBg = '';
                let statusBadge = '';
                if (status === 'ingested') {
                    statusIcon = 'check_circle';
                    statusIconBg = '#22c55e';
                    statusBadge = '<span class="status-badge status-ingested" style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Ingest</span>';
                } else if (status === 'error' || status === 'failed') {
                    statusIcon = 'error';
                    statusIconBg = '#ef4444';
                    statusBadge = '<span class="status-badge status-error" style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Error</span>';
                } else {
                    statusIcon = 'visibility';
                    statusIconBg = '#f59e0b';
                    statusBadge = '<span class="status-badge status-preview" style="background: #f59e0b; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Preview</span>';
                }
                
                const wordCount = (file.word_count !== undefined && file.word_count !== null) ? file.word_count : 0;
                const charCount = (file.char_count !== undefined && file.char_count !== null) ? file.char_count : 0;
                
                // Escape HTML
                const escapedFilename = safeFilename.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const escapedCategory = category.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                
                const fileItemHTML = `
                    <div class="file-item" id="file-${fileId}" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; border-bottom: 1px solid #e1e5e9; background: white; border-radius: 8px; margin-bottom: 8px; gap: 12px; position: relative !important;">
                        <!-- Status Icon with Circle Background (Top Left) -->
                        <div class="file-status-icon" style="width: 40px; height: 40px; border-radius: 50%; background: ${statusIconBg}; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; position: relative; z-index: 1;">
                            <span class="material-icons-round" style="font-size: 22px; color: white;">${statusIcon}</span>
                        </div>
                        
                        <div class="file-info" style="flex: 1; min-width: 0;">
                            <div class="file-name" style="font-weight: 600; margin-bottom: 6px; color: #1e293b; font-size: 14px;">${escapedFilename}</div>
                            <div class="file-size" style="font-size: 12px; color: #64748b; display: flex; flex-wrap: wrap; align-items: center; gap: 4px;">
                                ${statusBadge}
                                <span>${typeof formatFileSize === 'function' ? formatFileSize(size) : (size ? (size / 1024).toFixed(1) + ' KB' : '0 B')}</span>
                                <span>•</span>
                                <span>${wordCount.toLocaleString()} words</span>
                                <span>•</span>
                                <span>${charCount.toLocaleString()} chars</span>
                                <span>•</span>
                                <span>${escapedCategory}</span>
                                <span>•</span>
                                <span>${uploadedDate}</span>
                            </div>
                        </div>
                        <div class="file-actions" style="display: flex; gap: 8px; flex-shrink: 0;">
                            <button class="btn btn-secondary view-file-btn" data-file-id="${fileId}" style="padding: 6px 12px; font-size: 12px; white-space: nowrap;" title="View file preview">
                                <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">visibility</span> <span class="btn-text">View</span>
                            </button>
                            ${status === 'preview' ? `
                            <button class="btn ingest-file-btn" data-file-id="${fileId}" style="padding: 6px 12px; font-size: 12px; background: #0891b2; color: white; white-space: nowrap;" title="Ingest to knowledge base">
                                <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">save</span> <span class="btn-text">Ingest</span>
                            </button>
                            ` : ''}
                            <button class="btn btn-danger delete-file-btn" data-file-id="${fileId}" data-filename="${escapedFilename}" data-category="${escapedCategory}" style="padding: 6px 12px; font-size: 12px; background: #dc3545; color: white; white-space: nowrap;" title="Delete file and remove from knowledge base">
                                <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">delete</span> <span class="btn-text">Delete</span>
                            </button>
                        </div>
                    </div>
                `;
                
                filesDiv.innerHTML += fileItemHTML;
            });
            
            // Add event listeners after rendering
            setTimeout(() => {
                try {
                    // View file buttons
                    filesDiv.querySelectorAll('.view-file-btn').forEach(btn => {
                        btn.addEventListener('click', async function() {
                            const fileId = parseInt(this.getAttribute('data-file-id'));
                            if (typeof viewFile === 'function') {
                                await viewFile(fileId);
                            }
                        });
                    });
                    
                    // Ingest file buttons
                    filesDiv.querySelectorAll('.ingest-file-btn').forEach(btn => {
                        btn.addEventListener('click', async function() {
                            const fileId = parseInt(this.getAttribute('data-file-id'));
                            if (typeof viewFile === 'function') {
                                await viewFile(fileId); // Show preview first, then user can ingest
                            }
                        });
                    });
                    
                    // Delete file buttons
                    filesDiv.querySelectorAll('.delete-file-btn').forEach(btn => {
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
        }
        
        section.appendChild(header);
        section.appendChild(filesDiv);
        container.appendChild(section);
    });
}

function toggleCategoryFiles(categoryId) {
    const filesDiv = document.getElementById('files-' + categoryId);
    if (filesDiv) {
        filesDiv.classList.toggle('collapsed');
    }
}

let fileUploadInitialized = false;

function setupFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    const fileInput = document.getElementById('fileInput');
    
    if (!fileUpload || !fileInput) return;
    
    // Prevent multiple initializations
    if (fileUploadInitialized) {
        console.log('File upload already initialized, skipping...');
        return;
    }
    fileUploadInitialized = true;

    fileUpload.addEventListener('click', () => {
        if (!fileInput.disabled) {
            fileInput.click();
        }
    });

    fileUpload.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUpload.classList.add('dragover');
    });

    fileUpload.addEventListener('dragleave', () => {
        fileUpload.classList.remove('dragover');
    });

    fileUpload.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUpload.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileUpload(e.target.files);
        }
    });
}

let isUploading = false;

async function handleFileUpload(files) {
    // Prevent multiple simultaneous uploads
    if (isUploading) {
        console.log('Upload already in progress, ignoring...');
        return;
    }
    
    if (!files || files.length === 0) {
        return;
    }
    
    isUploading = true;
    const uploadLoading = document.getElementById('uploadLoading');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const uploadError = document.getElementById('uploadError');
    const fileInput = document.getElementById('fileInput');
    
    // Disable file input during upload
    if (fileInput) {
        fileInput.disabled = true;
    }
    
    if (uploadSuccess) uploadSuccess.style.display = 'none';
    if (uploadError) uploadError.style.display = 'none';
    if (uploadLoading) uploadLoading.style.display = 'block';
    
    try {
        // Get AI cleaning preference
        const aiCleaningCheckbox = document.getElementById('fileAiCleaningEnabled');
        const useAiCleaning = aiCleaningCheckbox ? aiCleaningCheckbox.checked : true;
        
        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('category', selectedCategory || 'company_details');
            formData.append('use_ai_cleaning', useAiCleaning); // Add AI cleaning preference
            if (currentWebsiteId !== 'default') {
                formData.append('website_id', currentWebsiteId);
            }

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    credentials: 'same-origin',
                    body: formData
                });
                
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                let result;
                
                if (contentType && contentType.includes('application/json')) {
                    result = await response.json();
                } else {
                    const text = await response.text();
                    throw new Error(`Server returned non-JSON response. Status: ${response.status}. Please check your login status.`);
                }
                
                if (response.ok) {
                    const message = result.message || `File "${file.name}" uploaded successfully. Please review and ingest.`;
                    
                    // Show toast notification
                    if (typeof showSuccessNotification === 'function') {
                        showSuccessNotification(message, 5000);
                    } else if (uploadSuccess) {
                        uploadSuccess.textContent = message;
                        uploadSuccess.style.display = 'block';
                    }
                } else {
                    throw new Error(result.error || `Upload failed with status ${response.status}`);
                }
                
            } catch (error) {
                console.error('Upload error:', error);
                const errorMessage = 'Failed to upload ' + file.name + ': ' + error.message;
                
                // Show toast notification
                if (typeof showErrorNotification === 'function') {
                    showErrorNotification(errorMessage, 6000);
                } else if (uploadError) {
                    uploadError.textContent = errorMessage;
                    uploadError.style.display = 'block';
                }
            }
        }
        
        // Refresh file list and stats after all uploads complete
        if (typeof refreshFileList === 'function') {
            await refreshFileList();
        } else if (typeof loadFilesByCategory === 'function') {
            await loadFilesByCategory();
        }
        
        // Refresh knowledge stats
        if (typeof loadKnowledgeStats === 'function') {
            await loadKnowledgeStats();
        }
        
    } finally {
        // Re-enable file input and clear it
        if (fileInput) {
            fileInput.disabled = false;
            fileInput.value = '';
        }
        if (uploadLoading) uploadLoading.style.display = 'none';
        isUploading = false;
    }
}

// ====================================
// API FUNCTIONS
// ====================================
let crawledPreviewData = null;

function normalizeUrl(url) {
    // Normalize URL by adding protocol if missing
    url = url.trim();
    
    // If URL doesn't start with http:// or https://, add https://
    if (!url.match(/^https?:\/\//i)) {
        url = 'https://' + url;
    }
    
    return url;
}

async function crawlUrl() {
    const urlInput = document.getElementById('urlInput');
    const crawlBtn = document.getElementById('crawlBtn');
    const crawlLoading = document.getElementById('crawlLoading');
    const crawlError = document.getElementById('crawlError');
    
    if (!urlInput) return;
    
    let url = urlInput.value.trim();
    
    if (!url) {
        const errorMessage = 'Please enter a valid URL';
        if (crawlError) {
            crawlError.textContent = errorMessage;
            crawlError.style.display = 'block';
        }
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    
    // Normalize URL (add https:// if missing)
    url = normalizeUrl(url);
    
    if (crawlError) crawlError.style.display = 'none';
    if (crawlBtn) crawlBtn.disabled = true;
    if (crawlLoading) crawlLoading.style.display = 'block';
    
    try {
        // Get AI cleaning preference
        const aiCleaningCheckbox = document.getElementById('aiCleaningEnabled');
        const useAiCleaning = aiCleaningCheckbox ? aiCleaningCheckbox.checked : true;
        
        // Call preview endpoint (saves to DB, status='preview')
        const response = await fetch('/api/crawl-preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                category: selectedCategory || 'company_details',
                use_ai_cleaning: useAiCleaning
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Show preview modal
            crawledPreviewData = result;
            showCrawlPreview(result);
            
            // Clear input
            urlInput.value = '';
            
            // Refresh crawled URLs list
            await refreshCrawledUrls();
            
            // Show success toast notification
            const message = `URL crawled successfully. ${result.word_count || 0} words extracted.`;
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
        } else {
            throw new Error(result.error || 'Failed to crawl URL');
        }
    } catch (error) {
        const errorMessage = 'Failed to crawl URL: ' + error.message;
        if (crawlError) {
            crawlError.textContent = errorMessage;
            crawlError.style.display = 'block';
        }
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
    
    if (crawlBtn) crawlBtn.disabled = false;
    if (crawlLoading) crawlLoading.style.display = 'none';
}

function showRecrawlConfirm() {
    // Show confirmation popup
    if (confirm('Are you sure you want to recrawl all websites on the lists?')) {
        // Future: Implement recrawl functionality
        // For now, just close the popup
        if (typeof showSuccessNotification === 'function') {
            showSuccessNotification('Recrawl feature coming soon!', 3000);
        }
    }
}

function showUploadSitemapInfo() {
    // Show info about upload sitemap feature
    if (typeof showSuccessNotification === 'function') {
        showSuccessNotification('Upload Sitemap feature coming soon! This will allow you to crawl multiple URLs from a sitemap file.', 5000);
    } else {
        alert('Upload Sitemap feature coming soon! This will allow you to crawl multiple URLs from a sitemap file.');
    }
}

// Make functions globally accessible
window.showRecrawlConfirm = showRecrawlConfirm;
window.showUploadSitemapInfo = showUploadSitemapInfo;

function showCrawlPreview(data) {
    const modal = document.getElementById('crawlPreviewModal');
    const urlSpan = document.getElementById('previewUrl');
    const wordCountSpan = document.getElementById('previewWordCount');
    const charCountSpan = document.getElementById('previewCharCount');
    const textArea = document.getElementById('previewText');
    
    if (urlSpan) urlSpan.textContent = data.url || 'N/A';
    if (wordCountSpan) wordCountSpan.textContent = (data.word_count || 0).toLocaleString();
    if (charCountSpan) charCountSpan.textContent = (data.char_count || 0).toLocaleString();
    if (textArea) textArea.value = data.full_text || data.extracted_text || ''; // Full text for editing
    
    if (modal) modal.style.display = 'block';
}

function closeCrawlPreview() {
    const modal = document.getElementById('crawlPreviewModal');
    if (modal) modal.style.display = 'none';
    crawledPreviewData = null;
}

async function ingestCrawledContent() {
    const textArea = document.getElementById('previewText');
    if (!textArea || !crawledPreviewData) return;
    
    const editedText = textArea.value.trim();
    if (!editedText) {
        const errorMessage = 'Text cannot be empty';
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        } else {
            alert(errorMessage);
        }
        return;
    }
    
    const crawledId = crawledPreviewData.id;
    const crawlSuccess = document.getElementById('crawlSuccess');
    const crawlError = document.getElementById('crawlError');
    
    if (crawlError) crawlError.style.display = 'none';
    
    try {
        const response = await fetch(`/api/crawled-urls/${crawledId}/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: editedText
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const message = result.message || 'URL content ingested successfully!';
            if (crawlSuccess) {
                crawlSuccess.textContent = message;
                crawlSuccess.style.display = 'block';
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            closeCrawlPreview();
            await refreshCrawledUrls();
            await refreshFileList(); // Refresh file list too
            // Refresh knowledge stats
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(result.error || 'Failed to ingest');
        }
    } catch (error) {
        const errorMessage = 'Failed to ingest: ' + error.message;
        if (crawlError) {
            crawlError.textContent = errorMessage;
            crawlError.style.display = 'block';
        }
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

async function refreshCrawledUrls() {
    const listDiv = document.getElementById('crawledUrlsList');
    if (!listDiv) return;
    
    try {
        const response = await fetch('/api/crawled-urls');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to load crawled URLs');
        }
        
        if (data.urls.length === 0) {
            listDiv.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">No crawled URLs yet</div>';
            return;
        }
        
        const html = data.urls.map(url => {
            // Status icon and badge
            let statusIcon = '';
            let statusBadge = '';
            let statusBg = '';
            
            if (url.status === 'ingested') {
                statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">check_circle</span>';
                statusBadge = '<span class="status-badge status-ingested" style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Ingest</span>';
                statusBg = '#22c55e';
            } else if (url.status === 'preview') {
                statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">visibility</span>';
                statusBadge = '<span class="status-badge status-preview" style="background: #f59e0b; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Preview</span>';
                statusBg = '#f59e0b';
            } else {
                statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">error</span>';
                statusBadge = '<span class="status-badge status-error" style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Error</span>';
                statusBg = '#dc3545';
            }
            
            const crawledDate = url.crawled_at ? new Date(url.crawled_at).toLocaleDateString() : 'N/A';
            const displayUrl = url.url.length > 60 ? url.url.substring(0, 60) + '...' : url.url;
            
            return `
                <div class="crawled-url-item" id="crawled-url-${url.id}" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; border-bottom: 1px solid #e1e5e9; background: white; border-radius: 8px; margin-bottom: 8px; gap: 12px; position: relative;">
                    <!-- Status Icon with Circle Background (Top Left) -->
                    <div class="url-status-icon" style="width: 40px; height: 40px; border-radius: 50%; background: ${statusBg}; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">
                        ${statusIcon}
                    </div>
                    
                    <div class="url-info" style="flex: 1; min-width: 0;">
                        <div class="url-name" style="font-weight: 600; margin-bottom: 6px; color: #1e293b; font-size: 14px; word-break: break-all;">${displayUrl}</div>
                        <div class="url-size" style="font-size: 12px; color: #64748b; display: flex; flex-wrap: wrap; align-items: center; gap: 4px; flex-direction: inherit;">
                            ${statusBadge}
                            <span>${url.word_count.toLocaleString()} words</span>
                            <span>•</span>
                            <span>${url.char_count.toLocaleString()} chars</span>
                            <span>•</span>
                            <span>${crawledDate}</span>
                        </div>
                    </div>
                    <div class="url-actions" style="display: flex; gap: 8px; flex-shrink: 0;">
                        <button class="btn btn-secondary view-url-btn" data-url-id="${url.id}" onclick="viewCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px; white-space: nowrap;" title="View URL preview">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">visibility</span> <span class="btn-text">View</span>
                        </button>
                        <button class="btn btn-danger delete-url-btn" data-url-id="${url.id}" onclick="deleteCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px; background: #dc3545; color: white; white-space: nowrap;" title="Delete URL and remove from knowledge base">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">delete</span> <span class="btn-text">Delete</span>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        listDiv.innerHTML = html;
    } catch (error) {
        console.error('Failed to load crawled URLs:', error);
        listDiv.innerHTML = `<div style="text-align: center; color: #dc3545; padding: 20px;">Error: ${error.message}</div>`;
    }
}

async function viewCrawledUrl(crawledId) {
    try {
        const response = await fetch(`/api/crawled-urls/${crawledId}`);
        const data = await response.json();
        
        if (response.ok) {
            crawledPreviewData = data;
            showCrawlPreview(data);
        } else {
            const errorMessage = 'Failed to load crawled URL: ' + data.error;
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMessage, 5000);
            } else {
                alert(errorMessage);
            }
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 5000);
        } else {
            alert(errorMessage);
        }
    }
}

async function deleteCrawledUrl(crawledId) {
    if (!confirm('Are you sure you want to delete this crawled URL? This will also remove it from the knowledge base.')) {
        return;
    }
    
    const crawlSuccess = document.getElementById('crawlSuccess');
    const crawlError = document.getElementById('crawlError');
    
    if (crawlError) crawlError.style.display = 'none';
    
    try {
        const response = await fetch(`/api/crawled-urls/${crawledId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const message = result.message || 'Crawled URL deleted successfully';
            await refreshCrawledUrls();
            if (crawlSuccess) {
                crawlSuccess.textContent = message;
                crawlSuccess.style.display = 'block';
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            // Refresh knowledge stats
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(result.error || 'Failed to delete');
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        if (crawlError) {
            crawlError.textContent = errorMessage;
            crawlError.style.display = 'block';
        }
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('crawlPreviewModal');
    if (event.target === modal) {
        closeCrawlPreview();
    }
    const fileModal = document.getElementById('filePreviewModal');
    if (event.target === fileModal) {
        closeFilePreview();
    }
}

// ====================================
// FILE PREVIEW AND INGEST FUNCTIONS
// ====================================
let filePreviewData = null;

async function viewFile(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}`, {
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const text = await response.text();
            if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                throw new Error('Authentication required. Please refresh the page and try again.');
            }
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (response.ok) {
            filePreviewData = data;
            showFilePreview(data);
        } else {
            alert('Failed to load file: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function showFilePreview(data) {
    const modal = document.getElementById('filePreviewModal');
    const fileNameSpan = document.getElementById('previewFileName');
    const categorySpan = document.getElementById('previewFileCategory');
    const wordCountSpan = document.getElementById('previewFileWordCount');
    const charCountSpan = document.getElementById('previewFileCharCount');
    const textArea = document.getElementById('previewFileText');
    
    if (fileNameSpan) fileNameSpan.textContent = data.filename || 'N/A';
    if (categorySpan) categorySpan.textContent = data.category || 'N/A';
    if (wordCountSpan) wordCountSpan.textContent = (data.word_count || 0).toLocaleString();
    if (charCountSpan) charCountSpan.textContent = (data.char_count || 0).toLocaleString();
    if (textArea) textArea.value = data.extracted_text || '';
    
    if (modal) modal.style.display = 'block';
}

function closeFilePreview() {
    const modal = document.getElementById('filePreviewModal');
    if (modal) modal.style.display = 'none';
    filePreviewData = null;
}

async function ingestFileContent() {
    const textArea = document.getElementById('previewFileText');
    if (!textArea || !filePreviewData) return;
    
    const editedText = textArea.value.trim();
    if (!editedText) {
        alert('Text cannot be empty');
        return;
    }
    
    const fileId = filePreviewData.id;
    const uploadSuccess = document.getElementById('uploadSuccess');
    const uploadError = document.getElementById('uploadError');
    
    if (uploadError) uploadError.style.display = 'none';
    
    try {
        const response = await fetch(`/api/files/${fileId}/ingest`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: editedText
            })
        });
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const text = await response.text();
            if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                throw new Error('Authentication required. Please refresh the page and try again.');
            }
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (response.ok) {
            const message = result.message || 'File ingested successfully to knowledge base';
            
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            } else if (uploadSuccess) {
                uploadSuccess.textContent = message;
                uploadSuccess.style.display = 'block';
            }
            
            closeFilePreview();
            await refreshFileList();
            if (typeof refreshCrawledUrls === 'function') {
                await refreshCrawledUrls();
            }
            // Refresh knowledge stats
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(result.error || 'Failed to ingest');
        }
    } catch (error) {
        const errorMessage = 'Failed to ingest: ' + error.message;
        
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        } else if (uploadError) {
            uploadError.textContent = errorMessage;
            uploadError.style.display = 'block';
        }
    }
}

async function deleteFileById(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) {
        return;
    }
    
    const uploadSuccess = document.getElementById('uploadSuccess');
    const uploadError = document.getElementById('uploadError');
    
    if (uploadError) uploadError.style.display = 'none';
    
    try {
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            // Got HTML instead of JSON - likely authentication issue
            const text = await response.text();
            if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                throw new Error('Authentication required. Please refresh the page and try again.');
            }
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (response.ok) {
            const message = result.message || 'File deleted successfully';
            
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 4000);
            } else if (uploadSuccess) {
                uploadSuccess.textContent = message;
                uploadSuccess.style.display = 'block';
            }
            
            await refreshFileList();
            // Refresh knowledge stats
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(result.error || 'Failed to delete');
        }
    } catch (error) {
        const errorMessage = 'Error deleting file: ' + error.message;
        
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        } else if (uploadError) {
            uploadError.textContent = errorMessage;
            uploadError.style.display = 'block';
        }
    }
}

// Make functions globally accessible
if (typeof window !== 'undefined') {
    window.viewFile = viewFile;
    window.closeFilePreview = closeFilePreview;
    window.ingestFileContent = ingestFileContent;
    window.deleteFileById = deleteFileById;
}

