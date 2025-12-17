// ===========================
// CORTEX AI DASHBOARD - CORE
// Global Variables & Initialization
// ===========================

// Global variables
let currentTab = 'overview';
let currentWebsiteId = 'default';
let llmConfig = {};
let websites = {};
let selectedCategory = 'company_details';
let categories = {
    'company_details': {
        'name': 'Company Details',
        'description': 'Business information, services, team details, contact info',
        'color': '#007bff'
    },
    'sales_training': {
        'name': 'Sales Training', 
        'description': 'Sales scripts, objection handling, conversation examples',
        'color': '#28a745'
    },
    'product_info': {
        'name': 'Product Information',
        'description': 'Product specs, pricing, features, documentation', 
        'color': '#ffc107'
    },
    'policies_legal': {
        'name': 'Policies & Legal',
        'description': 'Terms of service, privacy policy, legal documents',
        'color': '#dc3545'
    }
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Helper function to safely call a function if it exists
function safeCall(fnName, isAsync = false) {
    try {
        const fn = window[fnName] || (typeof eval !== 'undefined' ? eval(fnName) : null);
        if (typeof fn === 'function') {
            return isAsync ? fn() : fn();
        }
    } catch (e) {
        // Function doesn't exist or can't be accessed - that's okay
        return isAsync ? Promise.resolve() : undefined;
    }
    return isAsync ? Promise.resolve() : undefined;
}

async function initializeDashboard() {
    try {
        // Only initialize dashboard features if we're on the dashboard page
        // Safely check and call functions - they may not exist on all pages (e.g., feedback page)
        try {
            if (typeof window.loadWebsites === 'function') {
                await window.loadWebsites();
            }
        } catch (e) {
            // loadWebsites not available - skip it
        }
        
        try {
            if (typeof window.loadLLMConfig === 'function') {
                await window.loadLLMConfig();
            }
        } catch (e) {
            // loadLLMConfig not available - skip it
        }
        
        try {
            if (typeof window.loadStats === 'function') {
                window.loadStats();
            }
        } catch (e) {
            // loadStats not available - skip it
        }
        
        try {
            if (typeof window.setupFileUpload === 'function') {
                window.setupFileUpload();
            }
        } catch (e) {
            // setupFileUpload not available - skip it
        }
        
        try {
            if (typeof window.setupCategoryTabs === 'function') {
                window.setupCategoryTabs();
            }
        } catch (e) {
            // setupCategoryTabs not available - skip it
        }
        
        // Initialize file management (includes crawl functionality)
        try {
            if (typeof window.initializeFileManagement === 'function') {
                await window.initializeFileManagement();
            }
        } catch (e) {
            // initializeFileManagement not available - skip it
        }
        
        // Update integration snippet when dashboard loads
        try {
            if (typeof window.updateIntegrationSnippet === 'function') {
                await window.updateIntegrationSnippet();
            }
        } catch (e) {
            // updateIntegrationSnippet not available - skip it
        }
        
    } catch (error) {
        // Final catch-all - don't let initialization errors break the page
    }
}
