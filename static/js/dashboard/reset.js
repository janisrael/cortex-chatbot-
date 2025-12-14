// Dashboard Reset System - Backup and Reset Functions

// ====================================
// RESET SYSTEM FUNCTIONS
// ====================================
function initializeResetSystem() {
    setupResetEventListeners();
}

function setupResetEventListeners() {
    // Confirmation input
    const confirmationInput = document.getElementById('confirmationInput');
    if (confirmationInput) {
        confirmationInput.addEventListener('input', function(e) {
            const confirmBtn = document.getElementById('confirmResetBtn');
            if (confirmBtn) {
                confirmBtn.disabled = e.target.value !== 'RESET ALL KNOWLEDGE';
            }
        });
    }
    
    // Reset modal click outside
    const resetModal = document.getElementById('resetModal');
    if (resetModal) {
        resetModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeResetModal();
            }
        });
    }
}

// ====================================
// RESET FUNCTIONS
// ====================================
async function createBackup() {
    const backupBtn = document.getElementById('backupBtn');
    const backupLoading = document.getElementById('backupLoading');
    const resetSuccess = document.getElementById('resetSuccess');
    const resetError = document.getElementById('resetError');
    
    if (resetSuccess) resetSuccess.style.display = 'none';
    if (resetError) resetError.style.display = 'none';
    
    if (backupBtn) backupBtn.disabled = true;
    if (backupLoading) backupLoading.style.display = 'block';
    
    try {
        const response = await fetch('/api/backup-knowledge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (resetSuccess) {
                resetSuccess.textContent = '✅ Backup created: ' + result.backup_location;
                resetSuccess.style.display = 'block';
            }
            if (typeof loadKnowledgeStats === 'function') {
                loadKnowledgeStats(); // Refresh stats
            }
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        if (resetError) {
            resetError.textContent = 'Failed to create backup: ' + error.message;
            resetError.style.display = 'block';
        }
    }
    
    if (backupBtn) backupBtn.disabled = false;
    if (backupLoading) backupLoading.style.display = 'none';
}

async function loadBackupList() {
    try {
        const response = await fetch('/api/list-backups');
        const result = await response.json();
        
        const backupsList = document.getElementById('backupsList');
        const backupsContainer = document.getElementById('backupsContainer');
        
        if (!backupsList || !backupsContainer) return;
        
        backupsContainer.innerHTML = '';
        
        if (result.backups && result.backups.length > 0) {
            result.backups.forEach(backup => {
                const backupItem = document.createElement('div');
                backupItem.className = 'backup-item';
                
                const backupInfo = document.createElement('div');
                backupInfo.className = 'backup-info';
                
                const backupName = document.createElement('div');
                backupName.className = 'backup-name';
                backupName.textContent = backup.name;
                
                const backupDate = document.createElement('div');
                backupDate.className = 'backup-date';
                backupDate.textContent = backup.created + ' • ' + formatFileSize(backup.size);
                
                const backupActions = document.createElement('div');
                backupActions.className = 'backup-actions';
                
                const restoreBtn = document.createElement('button');
                restoreBtn.className = 'restore-btn';
                restoreBtn.textContent = 'Restore';
                restoreBtn.onclick = () => restoreBackup(backup.path);
                
                backupInfo.appendChild(backupName);
                backupInfo.appendChild(backupDate);
                backupActions.appendChild(restoreBtn);
                backupItem.appendChild(backupInfo);
                backupItem.appendChild(backupActions);
                backupsContainer.appendChild(backupItem);
            });
        } else {
            const noBackupsP = document.createElement('p');
            noBackupsP.style.cssText = 'text-align: center; color: #666; padding: 20px;';
            noBackupsP.textContent = 'No backups found';
            backupsContainer.appendChild(noBackupsP);
        }
        
        backupsList.style.display = 'block';
        
    } catch (error) {
    }
}

async function restoreBackup(backupPath) {
    if (!confirm('Are you sure you want to restore from this backup? This will overwrite current data.')) {
        return;
    }
    
    const resetSuccess = document.getElementById('resetSuccess');
    const resetError = document.getElementById('resetError');
    
    if (resetSuccess) resetSuccess.style.display = 'none';
    if (resetError) resetError.style.display = 'none';
    
    try {
        const response = await fetch('/api/restore-knowledge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup_path: backupPath })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            if (resetSuccess) {
                resetSuccess.textContent = '✅ Knowledge base restored successfully!';
                resetSuccess.style.display = 'block';
            }
            if (typeof loadKnowledgeStats === 'function') {
                loadKnowledgeStats();
            }
            if (typeof loadPrompt === 'function') {
                loadPrompt(); // Reload prompt if it was restored
            }
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        if (resetError) {
            resetError.textContent = 'Failed to restore backup: ' + error.message;
            resetError.style.display = 'block';
        }
    }
}

function showResetModal(resetType) {
    currentResetType = resetType;
    
    const modal = document.getElementById('resetModal');
    const title = document.getElementById('modalTitle');
    const description = document.getElementById('modalDescription');
    const buttonText = document.getElementById('resetButtonText');
    
    if (!modal) return;
    
    const resetTypes = {
        'files': {
            title: '🗂️ Reset Files',
            description: 'This will permanently delete all uploaded files from all categories. Vector embeddings and chat logs will remain.',
            buttonText: 'Delete Files'
        },
        'vectors': {
            title: '🧠 Reset Vector Database', 
            description: 'This will clear the bot\'s learned embeddings and knowledge. Uploaded files will remain but need to be re-processed.',
            buttonText: 'Clear Vectors'
        },
        'logs': {
            title: '📊 Reset Logs',
            description: 'This will delete all chat logs, analytics data, and learning information.',
            buttonText: 'Clear Logs'
        },
        'database': {
            title: '💾 Reset Database',
            description: 'This will delete all conversation history and user data from the database.',
            buttonText: 'Clear Database'
        },
        'prompt': {
            title: '📝 Reset Prompt',
            description: 'This will restore the system prompt to its default state.',
            buttonText: 'Reset Prompt'
        },
        'all': {
            title: '💥 COMPLETE RESET',
            description: 'This will delete EVERYTHING: all files, vector database, logs, database records, and reset the prompt. The bot will be completely fresh.',
            buttonText: 'RESET EVERYTHING'
        }
    };
    
    const config = resetTypes[resetType];
    if (title) title.textContent = config.title;
    if (description) description.textContent = config.description;
    if (buttonText) buttonText.textContent = config.buttonText;
    
    const confirmationInput = document.getElementById('confirmationInput');
    const confirmResetBtn = document.getElementById('confirmResetBtn');
    
    if (confirmationInput) confirmationInput.value = '';
    if (confirmResetBtn) confirmResetBtn.disabled = true;
    
    modal.style.display = 'flex';
}

function closeResetModal() {
    const modal = document.getElementById('resetModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentResetType = '';
}

async function executeReset() {
    const confirmBtn = document.getElementById('confirmResetBtn');
    const resetLoading = document.getElementById('resetLoading');
    const loadingText = document.getElementById('resetLoadingText');
    
    if (confirmBtn) confirmBtn.disabled = true;
    if (resetLoading) resetLoading.style.display = 'block';
    if (loadingText) loadingText.textContent = 'Resetting ' + currentResetType + '...';
    
    try {
        const response = await fetch('/api/reset-knowledge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reset_type: currentResetType,
                confirm_phrase: 'RESET ALL KNOWLEDGE'
            })
        });
        
        const result = await response.json();
        
        if (resetLoading) resetLoading.style.display = 'none';
        closeResetModal();
        
        if (response.ok) {
            const resetSuccess = document.getElementById('resetSuccess');
            if (resetSuccess) {
                resetSuccess.textContent = '✅ ' + result.message;
                resetSuccess.style.display = 'block';
            }
            
            // Refresh relevant data
            if (typeof loadKnowledgeStats === 'function') {
                loadKnowledgeStats();
            }
            if (currentResetType === 'all' || currentResetType === 'files') {
                if (typeof loadFilesByCategory === 'function') {
                    loadFilesByCategory();
                }
            }
            if (currentResetType === 'all' || currentResetType === 'prompt') {
                if (typeof loadPrompt === 'function') {
                    loadPrompt();
                }
            }
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        if (resetLoading) resetLoading.style.display = 'none';
        closeResetModal();
        
        const resetError = document.getElementById('resetError');
        if (resetError) {
            resetError.textContent = 'Failed to reset: ' + error.message;
            resetError.style.display = 'block';
        }
    }
}

// ====================================
// AUTO-REFRESH
// ====================================
setInterval(() => {
    if (typeof loadKnowledgeStats === 'function') {
        loadKnowledgeStats();
    }
    if (typeof loadFilesByCategory === 'function') {
        loadFilesByCategory();
    }
}, 30000); // Refresh every 30 seconds

