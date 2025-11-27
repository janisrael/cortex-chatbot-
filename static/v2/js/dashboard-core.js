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

async function initializeDashboard() {
    try {
        // Only initialize dashboard features if we're on the dashboard page
        // Check if required functions exist before calling them
        if (typeof loadWebsites === 'function') {
            await loadWebsites();
        }
        if (typeof loadLLMConfig === 'function') {
            await loadLLMConfig();
        }
        if (typeof loadStats === 'function') {
            loadStats();
        }
        if (typeof setupFileUpload === 'function') {
            setupFileUpload();
        }
        if (typeof setupCategoryTabs === 'function') {
            setupCategoryTabs();
        }
        // Initialize file management (includes crawl functionality)
        if (typeof initializeFileManagement === 'function') {
            await initializeFileManagement();
        }
        // Update integration snippet when dashboard loads
        if (typeof updateIntegrationSnippet === 'function') {
            await updateIntegrationSnippet();
        }
        console.log('✅ Dashboard initialized successfully');
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
    }
}
