// ===========================
// FLOATING NOTIFICATION SYSTEM
// Toast-style push notifications for success, error, and warning
// ===========================

/**
 * Show a floating notification (toast)
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Set styles based on type
    const typeConfig = {
        success: {
            bg: 'linear-gradient(135deg, rgba(34, 197, 94, 0.95) 0%, rgba(22, 163, 74, 0.95) 100%)',
            icon: 'check_circle',
            border: '#22c55e'
        },
        error: {
            bg: 'linear-gradient(135deg, rgba(239, 68, 68, 0.95) 0%, rgba(220, 38, 38, 0.95) 100%)',
            icon: 'error',
            border: '#ef4444'
        },
        warning: {
            bg: 'linear-gradient(135deg, rgba(251, 191, 36, 0.95) 0%, rgba(245, 158, 11, 0.95) 100%)',
            icon: 'warning',
            border: '#fbbf24'
        },
        info: {
            bg: 'linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(37, 99, 235, 0.95) 100%)',
            icon: 'info',
            border: '#3b82f6'
        }
    };

    const config = typeConfig[type] || typeConfig.info;

    notification.style.cssText = `
        background: ${config.bg};
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid ${config.border};
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 300px;
        max-width: 450px;
        pointer-events: auto;
        animation: slideInRight 0.3s ease-out, fadeOut 0.3s ease-in 4.7s;
        font-family: 'Roboto Slab', sans-serif;
        font-size: 14px;
        line-height: 1.5;
        backdrop-filter: blur(10px);
        transform: translateX(0);
        opacity: 1;
    `;

    // Create icon
    const icon = document.createElement('span');
    icon.className = 'material-icons-round';
    icon.textContent = config.icon;
    icon.style.cssText = `
        font-size: 24px;
        flex-shrink: 0;
    `;

    // Create message container
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        flex: 1;
        word-wrap: break-word;
    `;
    messageDiv.textContent = message;

    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">close</span>';
    closeBtn.style.cssText = `
        background: rgba(255, 255, 255, 0.2);
        border: none;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        flex-shrink: 0;
        transition: all 0.2s;
        padding: 0;
        color: white;
    `;
    closeBtn.onmouseover = () => {
        closeBtn.style.background = 'rgba(255, 255, 255, 0.3)';
        closeBtn.style.transform = 'scale(1.1)';
    };
    closeBtn.onmouseout = () => {
        closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        closeBtn.style.transform = 'scale(1)';
    };
    closeBtn.onclick = () => {
        removeNotification(notification);
    };

    // Assemble notification
    notification.appendChild(icon);
    notification.appendChild(messageDiv);
    notification.appendChild(closeBtn);

    // Add to container
    container.appendChild(notification);

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            removeNotification(notification);
        }, duration);
    }

    // Add click to dismiss
    notification.addEventListener('click', (e) => {
        if (e.target === notification || e.target === messageDiv) {
            removeNotification(notification);
        }
    });

    return notification;
}

/**
 * Remove a notification
 * @param {HTMLElement} notification - Notification element to remove
 */
function removeNotification(notification) {
    if (!notification || !notification.parentNode) return;

    notification.style.animation = 'slideOutRight 0.3s ease-in';
    notification.style.opacity = '0';

    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * Show success notification
 * @param {string} message - Success message
 * @param {number} duration - Duration in milliseconds
 */
function showSuccessNotification(message, duration = 5000) {
    return showNotification(message, 'success', duration);
}

/**
 * Show error notification
 * @param {string} message - Error message
 * @param {number} duration - Duration in milliseconds
 */
function showErrorNotification(message, duration = 7000) {
    return showNotification(message, 'error', duration);
}

/**
 * Show warning notification
 * @param {string} message - Warning message
 * @param {number} duration - Duration in milliseconds
 */
function showWarningNotification(message, duration = 6000) {
    return showNotification(message, 'warning', duration);
}

/**
 * Show info notification
 * @param {string} message - Info message
 * @param {number} duration - Duration in milliseconds
 */
function showInfoNotification(message, duration = 5000) {
    return showNotification(message, 'info', duration);
}

// Add CSS animations if not already added
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0.7;
            }
        }

        @media (max-width: 768px) {
            #notification-container {
                top: 10px !important;
                right: 10px !important;
                left: 10px !important;
                max-width: calc(100% - 20px) !important;
            }

            .notification {
                min-width: auto !important;
                max-width: 100% !important;
            }
        }
    `;
    document.head.appendChild(style);
}

