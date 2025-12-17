// Dashboard Website Management - Multi-Website Functions

// ====================================
// MULTI-WEBSITE FUNCTIONS
// ====================================
async function initializeMultiWebsite() {
    try {
        await loadWebsites();
        setupMultiWebsiteEventListeners();
    } catch (error) {
    }
}

async function loadWebsites() {
    try {
        const response = await fetch('/api/websites');
        const data = await response.json();
        websites = data.websites || {};
        
        updateWebsiteSelector();
        updateWebsiteStatsGrid();
        
        // Set initial website
        const firstWebsite = Object.keys(websites)[0];
        if (firstWebsite) {
            selectWebsite(firstWebsite);
        }
        
    } catch (error) {
        // Initialize with default if API fails
        websites = {};
        currentWebsiteId = 'default';
    }
}

function updateWebsiteSelector() {
    const selector = document.getElementById('websiteSelector');
    if (!selector) return;
    
    selector.innerHTML = '';
    
    if (Object.keys(websites).length === 0) {
        const option = document.createElement('option');
        option.value = 'default';
        option.textContent = 'Default Website';
        selector.appendChild(option);
        return;
    }
    
    Object.entries(websites).forEach(([websiteId, website]) => {
        const option = document.createElement('option');
        option.value = websiteId;
        option.textContent = website.name + ' (' + website.bot_name + ')';
        selector.appendChild(option);
    });
}

function updateWebsiteStatsGrid() {
    const statsGrid = document.getElementById('websiteStats');
    if (!statsGrid) return;
    
    if (Object.keys(websites).length === 0) {
        statsGrid.innerHTML = '<div class="card" style="text-align: center; padding: 40px;"><p>No websites configured yet. <a href="#" onclick="showAddWebsiteModal()">Add your first website</a></p></div>';
        return;
    }
    
    const cards = Object.entries(websites).map(([websiteId, website]) => {
        const isActive = websiteId === currentWebsiteId ? 'active' : '';
        return '<div class="website-stat-card ' + isActive + '" onclick="selectWebsite(\'' + websiteId + '\')">' +
                    '<div class="website-stat-name">' + website.name + '</div>' +
                    '<div class="website-stat-bot">Bot: ' + website.bot_name + '</div>' +
                    '<div class="website-stat-value" id="docs-' + websiteId + '">-</div>' +
                    '<div class="website-stat-label">Documents</div>' +
                    '<div style="margin-top: 8px;">' +
                        '<span class="website-stat-value" style="font-size: 16px;" id="files-' + websiteId + '">-</span>' +
                        '<div class="website-stat-label">Files</div>' +
                    '</div>' +
                '</div>';
    });
    
    statsGrid.innerHTML = cards.join('');
    
    // Load stats for all websites
    Object.keys(websites).forEach(websiteId => {
        loadWebsiteStats(websiteId);
    });
}

function selectWebsite(websiteId) {
    currentWebsiteId = websiteId;
    
    // Update selector
    const selector = document.getElementById('websiteSelector');
    if (selector) selector.value = websiteId;
    
    // Update active card
    document.querySelectorAll('.website-stat-card').forEach(card => {
        card.classList.remove('active');
    });
    const activeCard = document.querySelector('[onclick="selectWebsite(\'' + websiteId + '\')"]');
    if (activeCard) activeCard.classList.add('active');
    
    // Update page for website
    updatePageForWebsite(websiteId);
    
    // Reload data for selected website
    loadWebsiteSpecificData(websiteId);
}

async function loadWebsiteStats(websiteId) {
    try {
        const response = await fetch('/api/website/' + websiteId + '/stats');
        const stats = await response.json();
        
        const docsElement = document.getElementById('docs-' + websiteId);
        const filesElement = document.getElementById('files-' + websiteId);
        
        if (docsElement) docsElement.textContent = stats.documents || 0;
        if (filesElement) filesElement.textContent = stats.files || 0;
        
    } catch (error) {
    }
}

function updatePageForWebsite(websiteId) {
    const website = websites[websiteId];
    if (!website) return;
    
    // Update page title
    document.title = website.name + ' - AI Dashboard';
    
    // Update any website-specific UI elements
    const websiteNameElements = document.querySelectorAll('.website-name');
    websiteNameElements.forEach(element => {
        element.textContent = website.name;
    });
}

function loadWebsiteSpecificData(websiteId) {
    // Reload files by category for this website
    if (typeof loadFilesByCategory === 'function') {
        loadFilesByCategory();
    }
    
    // Reload other website-specific data
    if (typeof loadKnowledgeStats === 'function') {
        loadKnowledgeStats();
    }
}

function setupMultiWebsiteEventListeners() {
    // Website selector change
    const selector = document.getElementById('websiteSelector');
    if (selector) {
        selector.addEventListener('change', function() {
            selectWebsite(this.value);
        });
    }
    
    // Add website button
    const addBtn = document.getElementById('addWebsiteBtn');
    if (addBtn) {
        addBtn.addEventListener('click', showAddWebsiteModal);
    }
    
    // Add website modal events
    const modal = document.getElementById('addWebsiteModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddWebsiteModal();
            }
        });
    }
    
    // Add embed code button after delay
    setTimeout(addEmbedCodeButton, 1000);
}

// ====================================
// MULTI-WEBSITE MODAL FUNCTIONS
// ====================================
function showAddWebsiteModal() {
    const modal = document.getElementById('addWebsiteModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeAddWebsiteModal() {
    const modal = document.getElementById('addWebsiteModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Clear form
    const fields = ['newWebsiteId', 'newWebsiteName', 'newBotName', 'newAllowedOrigins'];
    fields.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.value = '';
    });
    
    const colorField = document.getElementById('newPrimaryColor');
    if (colorField) colorField.value = '#28a745';
}

async function addNewWebsite() {
    const websiteId = document.getElementById('newWebsiteId');
    const websiteName = document.getElementById('newWebsiteName');
    const botName = document.getElementById('newBotName');
    const primaryColor = document.getElementById('newPrimaryColor');
    const allowedOrigins = document.getElementById('newAllowedOrigins');
    
    const websiteIdValue = websiteId ? websiteId.value.trim() : '';
    const websiteNameValue = websiteName ? websiteName.value.trim() : '';
    const botNameValue = botName ? botName.value.trim() : '';
    const primaryColorValue = primaryColor ? primaryColor.value : '#28a745';
    const allowedOriginsValue = allowedOrigins ? allowedOrigins.value.trim().split('\n').filter(o => o.trim()) : [];
    
    if (!websiteIdValue || !websiteNameValue || !botNameValue) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (websites[websiteIdValue]) {
        alert('Website ID already exists');
        return;
    }
    
    try {
        const response = await fetch('/api/websites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                website_id: websiteIdValue,
                name: websiteNameValue,
                bot_name: botNameValue,
                primary_color: primaryColorValue,
                allowed_origins: allowedOriginsValue
            })
        });
        
        if (response.ok) {
            closeAddWebsiteModal();
            loadWebsites(); // Reload websites
            alert('Website "' + websiteNameValue + '" added successfully!');
        } else {
            const error = await response.json();
            alert('Failed to add website: ' + error.error);
        }
        
    } catch (error) {
        alert('Error adding website: ' + error.message);
    }
}

function showEmbedCode() {
    const website = websites[currentWebsiteId];
    if (!website) return;
    
    const embedCode = '<!-- Add this to ' + website.name + ' -->\n' +
                     '<scr' + 'ipt src="' + window.location.origin + '/embed.js?website_id=' + currentWebsiteId + '"></scr' + 'ipt>';
    
    alert('Embed code for ' + website.name + ':\n\n' + embedCode);
}

function addEmbedCodeButton() {
    const headerContent = document.querySelector('.header-content .nav-links');
    if (headerContent && !document.getElementById('embedCodeBtn')) {
        const embedBtn = document.createElement('a');
        embedBtn.id = 'embedCodeBtn';
        embedBtn.href = '#';
        embedBtn.textContent = 'Get Embed Code';
        embedBtn.style.color = 'white';
        embedBtn.style.textDecoration = 'none';
        embedBtn.style.marginRight = '20px';
        embedBtn.onclick = showEmbedCode;
        headerContent.appendChild(embedBtn);
    }
}

