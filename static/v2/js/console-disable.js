// Disable console logging in production
// This script should be loaded before other scripts in production environment

(function() {
    'use strict';
    
    // Check if we're in production
    // Production: any hostname that's not localhost, 127.0.0.1, or local network
    const hostname = window.location.hostname.toLowerCase();
    const isLocal = hostname === 'localhost' || 
                   hostname === '127.0.0.1' ||
                   hostname.startsWith('192.168.') ||
                   hostname.startsWith('10.0.') ||
                   hostname.startsWith('172.16.') ||
                   hostname.startsWith('172.17.') ||
                   hostname.startsWith('172.18.') ||
                   hostname.startsWith('172.19.') ||
                   hostname.startsWith('172.20.') ||
                   hostname.startsWith('172.21.') ||
                   hostname.startsWith('172.22.') ||
                   hostname.startsWith('172.23.') ||
                   hostname.startsWith('172.24.') ||
                   hostname.startsWith('172.25.') ||
                   hostname.startsWith('172.26.') ||
                   hostname.startsWith('172.27.') ||
                   hostname.startsWith('172.28.') ||
                   hostname.startsWith('172.29.') ||
                   hostname.startsWith('172.30.') ||
                   hostname.startsWith('172.31.');
    
    const isProduction = !isLocal;
    
    if (isProduction) {
        // Override console methods to be no-ops in production
        const noop = function() {};
        
        // Disable verbose logging (keep console.error for critical errors)
        console.log = console.debug = console.info = noop;
        
        // Optionally disable console.warn as well (uncomment if needed)
        // console.warn = noop;
        
        // Keep console.error enabled for critical errors (can be disabled if needed)
        // console.error = noop;
    }
})();

