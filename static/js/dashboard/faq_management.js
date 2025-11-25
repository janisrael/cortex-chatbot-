// Dashboard FAQ Management

// ====================================
// FAQ MANAGEMENT FUNCTIONS
// ====================================

let currentEditingFaqId = null;

// Initialize FAQ management
async function initializeFAQManagement() {
    try {
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
    
    if (faqs.length === 0) {
        faqList.innerHTML = '<div style="color: #999; padding: 20px; text-align: center;">No FAQs yet. Create your first FAQ above!</div>';
        return;
    }
    
    faqList.innerHTML = faqs.map(faq => {
        const status = faq.status || 'draft';
        const statusBadge = getStatusBadge(status);
        const category = faq.category || 'company_details';
        const categoryLabel = getCategoryLabel(category);
        const isIngested = status === 'active' && faq.ingested_at;
        
        return `
            <div class="faq-item" data-faq-id="${faq.id}" style="background: #2a2a2a; border: 1px solid #333; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #fff; margin-bottom: 8px; font-size: 16px;">
                            <span class="material-icons-round" style="vertical-align: middle; font-size: 18px; margin-right: 6px; color: #0891b2;">help_outline</span>
                            ${escapeHtml(faq.question)}
                        </div>
                        <div style="color: #ccc; font-size: 14px; line-height: 1.5; margin-bottom: 8px;">
                            ${escapeHtml(faq.answer.length > 150 ? faq.answer.substring(0, 150) + '...' : faq.answer)}
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                            <span style="background: #444; color: #ccc; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${categoryLabel}</span>
                            ${statusBadge}
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; padding-top: 12px; border-top: 1px solid #333;">
                    <button class="btn btn-secondary" onclick="editFAQ(${faq.id})" style="padding: 6px 12px; font-size: 12px;">
                        <span class="material-icons-round" style="vertical-align: middle; font-size: 16px;">edit</span> Edit
                    </button>
                    ${!isIngested ? `
                        <button class="btn" onclick="ingestFAQ(${faq.id})" style="padding: 6px 12px; font-size: 12px; background: #0891b2; color: white;">
                            <span class="material-icons-round" style="vertical-align: middle; font-size: 16px;">cloud_upload</span> Ingest
                        </button>
                    ` : `
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px; opacity: 0.6; cursor: not-allowed;" disabled>
                            <span class="material-icons-round" style="vertical-align: middle; font-size: 16px;">check_circle</span> Ingested
                        </button>
                    `}
                    <button class="btn btn-danger" onclick="deleteFAQ(${faq.id})" style="padding: 6px 12px; font-size: 12px;">
                        <span class="material-icons-round" style="vertical-align: middle; font-size: 16px;">delete</span> Delete
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
    const categorySelect = document.getElementById('faqCategory');
    const successAlert = document.getElementById('faqSuccess');
    const errorAlert = document.getElementById('faqError');
    const createBtn = document.getElementById('createFaqBtn');
    
    if (!questionInput || !answerInput || !categorySelect) return;
    
    const question = questionInput.value.trim();
    const answer = answerInput.value.trim();
    const category = categorySelect.value;
    
    // Validation
    if (!question) {
        showFAQError('Please enter a question');
        return;
    }
    if (!answer) {
        showFAQError('Please enter an answer');
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
            categorySelect.value = 'company_details';
            
            // Show success
            if (successAlert) {
                successAlert.textContent = data.message || 'FAQ created successfully!';
                successAlert.style.display = 'block';
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Scroll to FAQ list
            const faqList = document.getElementById('faqList');
            if (faqList) {
                faqList.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } else {
            throw new Error(data.error || 'Failed to create FAQ');
        }
    } catch (error) {
        showFAQError('Error: ' + error.message);
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
        showFAQError('Error loading FAQ: ' + error.message);
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
        showFAQError('Please enter a question');
        return;
    }
    if (!answer) {
        showFAQError('Please enter an answer');
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
            const successAlert = document.getElementById('faqSuccess');
            if (successAlert) {
                successAlert.textContent = data.message || 'FAQ updated successfully!';
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            
            // Reload FAQs
            await loadFAQs();
        } else {
            throw new Error(data.error || 'Failed to update FAQ');
        }
    } catch (error) {
        showFAQError('Error: ' + error.message);
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
            if (successAlert) {
                successAlert.textContent = data.message || 'FAQ ingested successfully!';
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Refresh knowledge stats if function exists
            if (typeof refreshKnowledgeStats === 'function') {
                await refreshKnowledgeStats();
            }
        } else {
            throw new Error(data.error || 'Failed to ingest FAQ');
        }
    } catch (error) {
        showFAQError('Error: ' + error.message);
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
            if (successAlert) {
                successAlert.textContent = data.message || 'FAQ deleted successfully!';
                successAlert.style.display = 'block';
                setTimeout(() => {
                    successAlert.style.display = 'none';
                }, 3000);
            }
            
            // Reload FAQs
            await loadFAQs();
            
            // Refresh knowledge stats if function exists
            if (typeof refreshKnowledgeStats === 'function') {
                await refreshKnowledgeStats();
            }
        } else {
            throw new Error(data.error || 'Failed to delete FAQ');
        }
    } catch (error) {
        showFAQError('Error: ' + error.message);
    }
}

// Refresh FAQ list
async function refreshFAQList() {
    await loadFAQs();
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
    const div = document.createElement('div');
    div.textContent = text;
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

