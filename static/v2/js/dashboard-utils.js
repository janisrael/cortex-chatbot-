// ===========================
// CORTEX AI DASHBOARD - UTILITIES
// Helper Functions & Event Listeners
// ===========================

/**
 * Format file size from bytes to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size (e.g., "2.5 MB")
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Show alert message
 * @param {string} alertId - ID of the alert element
 * @param {string} message - Message to display
 */
function showAlert(alertId, message) {
    console.log(`showAlert called: ${alertId}, message: ${message}`);
    const alertElement = document.getElementById(alertId);
    console.log('Alert element found:', alertElement);
    
    if (alertElement) {
        alertElement.textContent = message;
        alertElement.style.display = 'block';
        alertElement.style.opacity = '1';
        alertElement.style.visibility = 'visible';
        
        console.log('Alert display set to:', window.getComputedStyle(alertElement).display);
        console.log('Alert classes:', alertElement.className);
        
        // Scroll alert into view
        alertElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
        console.error(`Alert element not found: ${alertId}`);
    }
}

/**
 * Hide alert message
 * @param {string} alertId - ID of the alert element
 */
function hideAlert(alertId) {
    const alertElement = document.getElementById(alertId);
    if (alertElement) {
        alertElement.style.display = 'none';
    }
}

/**
 * Initialize utility features after all scripts are loaded
 * Call this function at the end of the main script
 */
function initializeUtils() {
    // Initialize hamburger menu
    initializeHamburgerMenu();
    
    // Auto-refresh stats every 30 seconds
    setInterval(function() {
        if (typeof loadStats === 'function') {
            loadStats();
        }
    }, 30000);

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            if (currentTab === 'prompt' && typeof savePrompt === 'function') {
                savePrompt();
            }
        }
    });
    
    console.log('✅ Utils initialized');
}

// ===========================
// MOBILE HAMBURGER MENU
// ===========================

function initializeHamburgerMenu() {
    const hamburger = document.getElementById('hamburgerBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (!hamburger || !navLinks) return;
    
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', function() {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!hamburger.contains(event.target) && !navLinks.contains(event.target)) {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
    
    console.log('✅ Hamburger menu initialized');
}
