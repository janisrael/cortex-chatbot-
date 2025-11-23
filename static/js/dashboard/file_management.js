// Dashboard File Management - File Upload and Categories

// ====================================
// FILE MANAGEMENT FUNCTIONS
// ====================================
async function initializeFileManagement() {
    try {
        await loadCategories();
        await loadFilesByCategory();
        await refreshCrawledUrls(); // Load crawled URLs
        setupFileUpload();
    } catch (error) {
        console.error('Failed to initialize file management:', error);
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

function renderCategoryTabs() {
    const tabsContainer = document.getElementById('categoryTabs');
    if (!tabsContainer) return;
    
    tabsContainer.innerHTML = '';
    
    Object.entries(categories).forEach(([categoryId, categoryInfo]) => {
        const tab = document.createElement('div');
        tab.className = 'category-tab' + (categoryId === selectedCategory ? ' active' : '');
        tab.onclick = () => selectCategory(categoryId);
        
        const nameDiv = document.createElement('div');
        nameDiv.textContent = categoryInfo.name;
        
        const descDiv = document.createElement('div');
        descDiv.className = 'category-description';
        descDiv.textContent = categoryInfo.description;
        
        tab.appendChild(nameDiv);
        tab.appendChild(descDiv);
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
                fileName.textContent = file.name;
                
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

function setupFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    const fileInput = document.getElementById('fileInput');
    
    if (!fileUpload || !fileInput) return;

    fileUpload.addEventListener('click', () => fileInput.click());

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
        handleFileUpload(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFileUpload(e.target.files);
    });
}

async function handleFileUpload(files) {
    const uploadLoading = document.getElementById('uploadLoading');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const uploadError = document.getElementById('uploadError');
    
    if (uploadSuccess) uploadSuccess.style.display = 'none';
    if (uploadError) uploadError.style.display = 'none';
    
    for (let file of files) {
        if (uploadLoading) uploadLoading.style.display = 'block';
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', selectedCategory);
        if (currentWebsiteId !== 'default') {
            formData.append('website_id', currentWebsiteId);
        }

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                if (uploadSuccess) {
                    uploadSuccess.textContent = result.message;
                    uploadSuccess.style.display = 'block';
                }
                setTimeout(() => {
                    loadFilesByCategory();
                }, 1000);
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            if (uploadError) {
                uploadError.textContent = 'Failed to upload ' + file.name + ': ' + error.message;
                uploadError.style.display = 'block';
            }
        }
    }
    
    if (uploadLoading) uploadLoading.style.display = 'none';
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
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
}

