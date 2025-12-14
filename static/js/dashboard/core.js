// Dashboard Core - Global Variables and Initialization

// ====================================
// GLOBAL VARIABLES
// ====================================
let selectedCategory = 'company_details';
let categories = {};
let currentWebsiteId = 'default';
let websites = {};
let currentResetType = '';

// ====================================
// INITIALIZATION
// ====================================
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all components in proper order
    if (typeof initializeMultiWebsite === 'function') {
        initializeMultiWebsite();
    }
    if (typeof initializeFileManagement === 'function') {
        initializeFileManagement();
    }
    if (typeof initializeKnowledgeManagement === 'function') {
        initializeKnowledgeManagement();
    }
    if (typeof initializeResetSystem === 'function') {
        initializeResetSystem();
    }
    
});

