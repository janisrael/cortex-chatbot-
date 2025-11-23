// Dashboard File Management - File Upload and Categories

// ====================================
// FILE MANAGEMENT FUNCTIONS
// ====================================
async function initializeFileManagement() {
    try {
        await loadCategories();
        await loadFilesByCategory();
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
async function crawlUrl() {
    const urlInput = document.getElementById('urlInput');
    const maxPages = document.getElementById('maxPages');
    const crawlBtn = document.getElementById('crawlBtn');
    const crawlLoading = document.getElementById('crawlLoading');
    const crawlSuccess = document.getElementById('crawlSuccess');
    const crawlError = document.getElementById('crawlError');
    
    if (!urlInput) return;
    
    const url = urlInput.value.trim();
    const maxPagesValue = parseInt(maxPages && maxPages.value ? maxPages.value : '10') || 10;
    
    if (!url) {
        if (crawlError) {
            crawlError.textContent = 'Please enter a valid URL';
            crawlError.style.display = 'block';
        }
        return;
    }
    
    if (crawlSuccess) crawlSuccess.style.display = 'none';
    if (crawlError) crawlError.style.display = 'none';
    
    if (crawlBtn) crawlBtn.disabled = true;
    if (crawlLoading) crawlLoading.style.display = 'block';
    
    try {
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                max_pages: maxPagesValue,
                category: 'company_details',
                website_id: currentWebsiteId !== 'default' ? currentWebsiteId : undefined
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (crawlSuccess) {
                crawlSuccess.textContent = result.message;
                crawlSuccess.style.display = 'block';
            }
            urlInput.value = '';
            setTimeout(loadFilesByCategory, 1000);
        } else {
            throw new Error(result.error);
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

