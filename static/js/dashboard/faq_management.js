// Dashboard FAQ Management

// ====================================
// FAQ MANAGEMENT FUNCTIONS
// ====================================

let currentEditingFaqId = null;

// Initialize FAQ management
async function initializeFAQManagement() {
    try {
        // Ensure category tabs are rendered
        if (typeof renderCategoryTabs === 'function') {
            renderCategoryTabs();
        }
        await loadFAQs();
    } catch (error) {
        console.error('Failed to initialize FAQ management:', error);
    }
}

// Load FAQs from API
async function loadFAQs() {
    try {
        const response = await fetch('/api/faqs', {
            method: 'GET',
            credentials: 'same-origin', // Include session cookies
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            // Response is not JSON (likely HTML error page or redirect)
            const text = await response.text();
            console.error('API returned non-JSON response:', text.substring(0, 200));
            
            if (response.status === 302 || response.status === 401 || response.status === 403) {
                throw new Error('Authentication required. Please refresh the page and log in again.');
            } else if (response.status === 404) {
                throw new Error('FAQ API endpoint not found. Please check server configuration.');
            } else if (response.status >= 500) {
                throw new Error(`Server error (${response.status}). Please check server logs.`);
            } else {
                throw new Error(`Unexpected response (${response.status}). Please try again.`);
            }
        }
        
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            renderFAQList(data.faqs || []);
        } else {
            throw new Error(data.error || 'Failed to load FAQs');
        }
    } catch (error) {
        console.error('Failed to load FAQs:', error);
        const faqList = document.getElementById('faqList');
        if (faqList) {
            faqList.innerHTML = `<div style="color: #f44336; padding: 20px; text-align: center; background: #fee; border: 1px solid #f44336; border-radius: 8px;">
                <strong>Error loading FAQs:</strong><br>
                ${error.message}<br>
                <small style="color: #999; margin-top: 10px; display: block;">Please refresh the page or check your login status.</small>
            </div>`;
        }
    }
}

// Render FAQ list
function renderFAQList(faqs) {
    const faqList = document.getElementById('faqList');
    if (!faqList) return;
    
    // Filter by selected category if available
    let filteredFaqs = faqs;
    const currentCategory = (typeof window.selectedFaqCategory !== 'undefined' && window.selectedFaqCategory) 
        ? window.selectedFaqCategory 
        : 'company_details';
    if (currentCategory) {
        filteredFaqs = faqs.filter(faq => faq.category === currentCategory);
    }
    
    if (filteredFaqs.length === 0) {
        faqList.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">No FAQs yet. Create your first FAQ above!</div>';
        return;
    }
    
    faqList.innerHTML = filteredFaqs.map(faq => {
        // Safely extract all values with defaults
        const faqId = faq && faq.id ? String(faq.id) : '0';
        const status = (faq && faq.status) ? String(faq.status) : 'draft';
        const category = (faq && faq.category) ? String(faq.category) : 'company_details';
        const categoryLabel = getCategoryLabel(category);
        const isIngested = status === 'active' && faq.ingested_at;
        
        // Safely get question and answer
        const question = (faq && faq.question) ? String(faq.question) : 'No question';
        const answer = (faq && faq.answer) ? String(faq.answer) : 'No answer';
        const answerPreview = answer.length > 100 ? answer.substring(0, 100) + '...' : answer;
        
        // Status icon and badge
        let statusIcon = '';
        let statusBadge = '';
        let statusBg = '';
        
        if (isIngested) {
            statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">check_circle</span>';
            statusBadge = '<span class="status-badge status-ingested" style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Ingest</span>';
            statusBg = '#22c55e';
        } else if (status === 'preview' || status === 'draft') {
            statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">visibility</span>';
            statusBadge = '<span class="status-badge status-preview" style="background: #f59e0b; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Preview</span>';
            statusBg = '#f59e0b';
        } else {
            statusIcon = '<span class="material-icons-round" style="font-size: 22px; color: white;">error</span>';
            statusBadge = '<span class="status-badge status-error" style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; font-weight: 500;">Error</span>';
            statusBg = '#dc3545';
        }
        
        // Format dates
        const createdDate = faq.created_at ? new Date(faq.created_at).toLocaleDateString() : 'N/A';
        const wordCount = answer.split(/\s+/).length;
        const charCount = answer.length;
        
        return `
            <div class="faq-item" id="faq-${faqId}" data-faq-id="${faqId}" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; border-bottom: 1px solid #e1e5e9; background: white; border-radius: 8px; margin-bottom: 8px; gap: 12px; position: relative;">
                <!-- Status Icon with Circle Background (Top Left) -->
                <div class="faq-status-icon" style="width: 40px; height: 40px; border-radius: 50%; background: ${statusBg}; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;">
                    ${statusIcon}
                </div>
                
                <div class="faq-info" style="flex: 1; min-width: 0;">
                    <div class="faq-question" style="font-weight: 600; margin-bottom: 6px; color: #1e293b; font-size: 14px; line-height: 1.4;">
                        ${escapeHtml(question)}
                    </div>
                    <div class="faq-answer-preview" style="font-size: 12px; color: #64748b; margin-bottom: 6px; line-height: 1.4;">
                        ${escapeHtml(answerPreview)}
                    </div>
                    <div class="faq-size" style="font-size: 12px; color: #64748b; display: flex; flex-wrap: wrap; align-items: center; gap: 4px; flex-direction: inherit;">
                        ${statusBadge}
                        <span>${wordCount} words</span>
                        <span>•</span>
                        <span>${charCount} chars</span>
                        <span>•</span>
                        <span>${categoryLabel}</span>
                        <span>•</span>
                        <span>${createdDate}</span>
                    </div>
                </div>
                <div class="faq-actions" style="display: flex; gap: 8px; flex-shrink: 0;">
                    <button class="btn btn-secondary edit-faq-btn" data-faq-id="${faqId}" onclick="editFAQ(${faqId})" style="padding: 6px 12px; font-size: 12px; white-space: nowrap;" title="Edit FAQ">
                        <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">edit</span> <span class="btn-text">Edit</span>
                    </button>
                    ${!isIngested ? `
                        <button class="btn ingest-faq-btn" data-faq-id="${faqId}" onclick="ingestFAQ(${faqId})" style="padding: 6px 12px; font-size: 12px; background: #0891b2; color: white; white-space: nowrap;" title="Ingest FAQ to knowledge base">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">cloud_upload</span> <span class="btn-text">Ingest</span>
                        </button>
                    ` : `
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px; opacity: 0.6; cursor: not-allowed; white-space: nowrap;" disabled title="Already ingested">
                            <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">check_circle</span> <span class="btn-text">Ingested</span>
                        </button>
                    `}
                    <button class="btn btn-danger delete-faq-btn" data-faq-id="${faqId}" onclick="deleteFAQ(${faqId})" style="padding: 6px 12px; font-size: 12px; background: #dc3545; color: white; white-space: nowrap;" title="Delete FAQ">
                        <span class="material-icons-round" style="font-size: 16px; vertical-align: middle;">delete</span> <span class="btn-text">Delete</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'draft': '<span style="background: #666; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Draft</span>',
        'active': '<span style="background: #4caf50; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Active</span>',
        'deleted': '<span style="background: #f44336; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Deleted</span>'
    };
    return badges[status] || badges['draft'];
}

// Get category label
function getCategoryLabel(category) {
    const labels = {
        'company_details': 'Company Details',
        'products_services': 'Products & Services',
        'support': 'Support',
        'pricing': 'Pricing',
        'other': 'Other'
    };
    return labels[category] || category;
}

// Create FAQ
async function createFAQ() {
    const questionInput = document.getElementById('faqQuestion');
    const answerInput = document.getElementById('faqAnswer');
    const successAlert = document.getElementById('faqSuccess');
    const errorAlert = document.getElementById('faqError');
    const createBtn = document.getElementById('createFaqBtn');
    
    if (!questionInput || !answerInput) {
        showFAQError('Form fields not found. Please refresh the page.');
        return;
    }
    
    const question = questionInput.value.trim();
    const answer = answerInput.value.trim();
    // Use selected category from tabs (fallback to company_details)
    const category = (typeof window.selectedFaqCategory !== 'undefined' && window.selectedFaqCategory) 
        ? window.selectedFaqCategory 
        : 'company_details';
    
    // Validation
    if (!question) {
        const errorMessage = 'Please enter a question';
        showFAQError(errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    if (!answer) {
        const errorMessage = 'Please enter an answer';
        showFAQError(errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    
    // Hide alerts
    if (successAlert) successAlert.style.display = 'none';
    if (errorAlert) errorAlert.style.display = 'none';
    
    // Disable button
    if (createBtn) {
        createBtn.disabled = true;
        createBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">hourglass_empty</span> Creating...';
    }
    
    try {
        const response = await fetch('/api/faqs', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                answer: answer,
                category: category
            })
        });
        
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            // Clear form
            questionInput.value = '';
            answerInput.value = '';
            
            // Show success
            const message = data.message || 'FAQ created successfully!';
            if (successAlert) {
                successAlert.textContent = message;
                successAlert.style.display = 'block';
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Refresh knowledge stats
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
            
            // Scroll to FAQ list
            const faqList = document.getElementById('faqList');
            if (faqList) {
                faqList.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } else {
            throw new Error(data.error || 'Failed to create FAQ');
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        showFAQError(errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    } finally {
        // Re-enable button
        if (createBtn) {
            createBtn.disabled = false;
            createBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 18px;">add</span> Add FAQ';
        }
    }
}

// Helper function to check if response is JSON
async function checkJSONResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
        const text = await response.text();
        console.error('API returned non-JSON response:', text.substring(0, 200));
        
        if (response.status === 302 || response.status === 401 || response.status === 403) {
            throw new Error('Authentication required. Please refresh the page and log in again.');
        } else if (response.status === 404) {
            throw new Error('API endpoint not found.');
        } else if (response.status >= 500) {
            throw new Error(`Server error (${response.status}). Please check server logs.`);
        } else {
            throw new Error(`Unexpected response (${response.status}).`);
        }
    }
    return await response.json();
}

// Edit FAQ
async function editFAQ(faqId) {
    try {
        const response = await fetch(`/api/faqs/${faqId}`, {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json'
            }
        });
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            currentEditingFaqId = faqId;
            
            // Populate edit modal
            const editQuestion = document.getElementById('editFaqQuestion');
            const editAnswer = document.getElementById('editFaqAnswer');
            const editCategory = document.getElementById('editFaqCategory');
            const editModal = document.getElementById('faqEditModal');
            
            if (editQuestion) editQuestion.value = data.question || '';
            if (editAnswer) editAnswer.value = data.answer || '';
            if (editCategory) editCategory.value = data.category || 'company_details';
            if (editModal) editModal.style.display = 'block';
        } else {
            throw new Error(data.error || 'Failed to load FAQ');
        }
    } catch (error) {
        const errorMessage = 'Error loading FAQ: ' + error.message;
        showFAQError(errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 5000);
        }
    }
}

// Save FAQ edit
async function saveFAQEdit() {
    if (!currentEditingFaqId) return;
    
    const editQuestion = document.getElementById('editFaqQuestion');
    const editAnswer = document.getElementById('editFaqAnswer');
    const editCategory = document.getElementById('editFaqCategory');
    
    if (!editQuestion || !editAnswer || !editCategory) return;
    
    const question = editQuestion.value.trim();
    const answer = editAnswer.value.trim();
    const category = editCategory.value;
    
    // Validation
    if (!question) {
        const errorMessage = 'Please enter a question';
        showFAQError(errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    if (!answer) {
        const errorMessage = 'Please enter an answer';
        showFAQError(errorMessage);
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 4000);
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/faqs/${currentEditingFaqId}`, {
            method: 'PUT',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                answer: answer,
                category: category
            })
        });
        
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            // Close modal
            closeFAQEditModal();
            
            // Show success
            const message = data.message || 'FAQ updated successfully!';
            const successAlert = document.getElementById('faqSuccess');
            if (successAlert) {
                successAlert.textContent = message;
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            
            // Reload FAQs
            await loadFAQs();
        } else {
            throw new Error(data.error || 'Failed to update FAQ');
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        showFAQError(errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

// Close FAQ edit modal
function closeFAQEditModal() {
    const editModal = document.getElementById('faqEditModal');
    if (editModal) editModal.style.display = 'none';
    currentEditingFaqId = null;
}

// Ingest FAQ
async function ingestFAQ(faqId) {
    if (!confirm('Ingest this FAQ to the knowledge base? It will be available for the chatbot to use.')) {
        return;
    }
    
    const successAlert = document.getElementById('faqSuccess');
    const errorAlert = document.getElementById('faqError');
    
    // Hide alerts
    if (successAlert) successAlert.style.display = 'none';
    if (errorAlert) errorAlert.style.display = 'none';
    
    try {
        const response = await fetch(`/api/faqs/${faqId}/ingest`, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            // Show success
            const message = data.message || 'FAQ ingested successfully!';
            if (successAlert) {
                successAlert.textContent = message;
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Refresh knowledge stats if function exists
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(data.error || 'Failed to ingest FAQ');
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        showFAQError(errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

// Delete FAQ
async function deleteFAQ(faqId) {
    if (!confirm('Are you sure you want to delete this FAQ? This action cannot be undone.')) {
        return;
    }
    
    const successAlert = document.getElementById('faqSuccess');
    const errorAlert = document.getElementById('faqError');
    
    // Hide alerts
    if (successAlert) successAlert.style.display = 'none';
    if (errorAlert) errorAlert.style.display = 'none';
    
    try {
        const response = await fetch(`/api/faqs/${faqId}`, {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await checkJSONResponse(response);
        
        if (response.ok) {
            // Show success
            const message = data.message || 'FAQ deleted successfully!';
            if (successAlert) {
                successAlert.textContent = message;
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            // Show toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(message, 5000);
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Refresh knowledge stats if function exists
            if (typeof loadKnowledgeStats === 'function') {
                await loadKnowledgeStats();
            }
        } else {
            throw new Error(data.error || 'Failed to delete FAQ');
        }
    } catch (error) {
        const errorMessage = 'Error: ' + error.message;
        showFAQError(errorMessage);
        // Show toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMessage, 6000);
        }
    }
}

// Refresh FAQ list
async function refreshFAQList() {
    await loadFAQs();
    // Refresh knowledge stats
    if (typeof loadKnowledgeStats === 'function') {
        await loadKnowledgeStats();
    }
}

// Show FAQ error
function showFAQError(message) {
    const errorAlert = document.getElementById('faqError');
    if (errorAlert) {
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 5000);
    }
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Make functions globally accessible
window.createFAQ = createFAQ;
window.editFAQ = editFAQ;
window.saveFAQEdit = saveFAQEdit;
window.closeFAQEditModal = closeFAQEditModal;
window.ingestFAQ = ingestFAQ;
window.deleteFAQ = deleteFAQ;
window.refreshFAQList = refreshFAQList;
window.loadFAQs = loadFAQs;

// Initialize when Knowledge tab is opened
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the knowledge tab
    const knowledgeTab = document.getElementById('knowledge-tab');
    if (knowledgeTab) {
        // Initialize FAQ management
        initializeFAQManagement();
    }
});

// Also initialize when tab is switched to knowledge
if (typeof window.addEventListener === 'function') {
    // Listen for tab changes (if tab switching is implemented)
    const observer = new MutationObserver(function(mutations) {
        const knowledgeTab = document.getElementById('knowledge-tab');
        if (knowledgeTab && knowledgeTab.classList.contains('active')) {
            // Reload FAQs when knowledge tab becomes active
            loadFAQs();
        }
    });
    
    // Observe tab content changes
    const tabContainer = document.querySelector('.tab-content');
    if (tabContainer) {
        observer.observe(tabContainer, { attributes: true, attributeFilter: ['class'] });
    }
}

