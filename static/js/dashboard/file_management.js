// Dashboard File Management - File Upload and Categories

// ====================================
// FILE MANAGEMENT FUNCTIONS
// ====================================
async function initializeFileManagement() {
    try {
        await loadCategories();
        await loadFilesByCategory();
        await refreshCrawledUrls(); // Load crawled URLs
        await loadKnowledgeStats(); // Load stats cards
        setupFileUpload();
    } catch (error) {
        console.error('Failed to initialize file management:', error);
    }
}

async function loadKnowledgeStats() {
    try {
        const response = await fetch('/api/knowledge-stats', {
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            console.error('Failed to load knowledge stats');
            return;
        }
        
        const stats = await response.json();
        
        // Update Files Card
        const filesCountEl = document.getElementById('knowledgeFilesCount');
        const filesLimitEl = document.getElementById('knowledgeFilesLimit');
        if (filesCountEl) {
            const fileCount = stats.file_count || 0;
            const maxFiles = stats.max_files || 100;
            filesCountEl.textContent = `${fileCount}/${maxFiles}`;
        }
        if (filesLimitEl) {
            filesLimitEl.textContent = `Limit: ${stats.max_files || 100} files`;
        }
        
        // Update Crawled Websites Card
        const crawledCountEl = document.getElementById('knowledgeCrawledCount');
        const crawledLimitEl = document.getElementById('knowledgeCrawledLimit');
        if (crawledCountEl) {
            const crawledCount = stats.crawled_count || 0;
            const maxCrawled = stats.max_crawled || 200;
            crawledCountEl.textContent = `${crawledCount}/${maxCrawled}`;
        }
        if (crawledLimitEl) {
            crawledLimitEl.textContent = `Limit: ${stats.max_crawled || 200} websites`;
        }
        
        // Update FAQ Card
        const faqCountEl = document.getElementById('knowledgeFaqCount');
        const faqLimitEl = document.getElementById('knowledgeFaqLimit');
        if (faqCountEl) {
            const faqCount = stats.faq_count || 0;
            const maxFaqs = stats.max_faqs || 500;
            faqCountEl.textContent = `${faqCount}/${maxFaqs}`;
        }
        if (faqLimitEl) {
            faqLimitEl.textContent = `Limit: ${stats.max_faqs || 500} FAQs`;
        }
        
    } catch (error) {
        console.error('Failed to load knowledge stats:', error);
    }
}

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

function renderCategoryTabs() {
    const tabsContainer = document.getElementById('categoryTabs');
    if (!tabsContainer) return;
    
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
            categoryData.files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                const fileInfo = document.createElement('div');
                
                const fileName = document.createElement('div');
                fileName.style.fontWeight = '500';
                // Safely get filename - handle both file.name and file.filename
                const filename = file.filename || file.name || 'Unknown File';
                // Fix if filename is just extension like ".pdf"
                const safeFilename = (filename.startsWith('.') && filename.length < 10) 
                    ? `Document${filename}` 
                    : (filename && filename !== 'undefined' && filename !== 'null' ? filename : 'Unknown File');
                fileName.textContent = safeFilename;
                
                const fileDetails = document.createElement('div');
                fileDetails.style.cssText = 'color: #666; font-size: 11px;';
                fileDetails.textContent = formatFileSize(file.size) + ' • ' + file.modified;
                
                fileInfo.appendChild(fileName);
                fileInfo.appendChild(fileDetails);
                fileItem.appendChild(fileInfo);
                filesDiv.appendChild(fileItem);
            });
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
        if (crawlError) {
            crawlError.textContent = 'Please enter a valid URL';
            crawlError.style.display = 'block';
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
        } else {
            throw new Error(result.error || 'Failed to crawl URL');
        }
    } catch (error) {
        if (crawlError) {
            crawlError.textContent = 'Failed to crawl URL: ' + error.message;
            crawlError.style.display = 'block';
        }
    }
    
    if (crawlBtn) crawlBtn.disabled = false;
    if (crawlLoading) crawlLoading.style.display = 'none';
}

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
        alert('Text cannot be empty');
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
            if (crawlSuccess) {
                crawlSuccess.textContent = result.message;
                crawlSuccess.style.display = 'block';
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
        if (crawlError) {
            crawlError.textContent = 'Failed to ingest: ' + error.message;
            crawlError.style.display = 'block';
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
            const statusBadge = url.status === 'ingested' 
                ? '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px;">Ingested</span>'
                : '<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px;">Preview</span>';
            
            const crawledDate = url.crawled_at ? new Date(url.crawled_at).toLocaleDateString() : 'N/A';
            
            return `
                <div class="crawled-url-item" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #333; background: #252525; border-radius: 4px; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; margin-bottom: 4px; color: white;">${url.url}</div>
                        <div style="font-size: 12px; color: #999;">
                            ${statusBadge}
                            ${url.word_count.toLocaleString()} words • 
                            ${url.char_count.toLocaleString()} chars • 
                            ${crawledDate}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-secondary" onclick="viewCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px;">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">visibility</span> View
                        </button>
                        <button class="btn btn-danger" onclick="deleteCrawledUrl(${url.id})" style="padding: 6px 12px; font-size: 12px; background: #dc3545; color: white;">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">delete</span> Delete
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
            alert('Failed to load crawled URL: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteCrawledUrl(crawledId) {
    if (!confirm('Are you sure you want to delete this crawled URL?')) {
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
            await refreshCrawledUrls();
            if (crawlSuccess) {
                crawlSuccess.textContent = result.message;
                crawlSuccess.style.display = 'block';
            }
        } else {
            throw new Error(result.error || 'Failed to delete');
        }
    } catch (error) {
        if (crawlError) {
            crawlError.textContent = 'Error: ' + error.message;
            crawlError.style.display = 'block';
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
        const response = await fetch(`/api/files/${fileId}`);
        const data = await response.json();
        
        if (response.ok) {
            filePreviewData = data;
            showFilePreview(data);
        } else {
            alert('Failed to load file: ' + data.error);
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: editedText
            })
        });
        
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
            method: 'DELETE'
        });
        
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

