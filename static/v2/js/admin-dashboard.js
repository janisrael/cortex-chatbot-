/**
 * Admin Dashboard JavaScript
 * Handles loading and displaying admin statistics and user list
 */

// Load system statistics
async function loadSystemStats() {
    try {
        const response = await fetch('/admin/api/stats', {
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Response is not JSON');
        }

        const data = await response.json();

        if (data.success && data.stats) {
            const stats = data.stats;

            // Update statistics cards
            document.getElementById('totalUsers').textContent = stats.total_users || 0;
            document.getElementById('activeUsers').textContent = `Active: ${stats.active_users || 0}`;
            document.getElementById('totalFiles').textContent = stats.total_files || 0;
            document.getElementById('totalCrawls').textContent = stats.total_crawls || 0;
            document.getElementById('totalFaqs').textContent = stats.total_faqs || 0;
        } else {
            throw new Error(data.error || 'Failed to load statistics');
        }
    } catch (error) {
        console.error('❌ Error loading system stats:', error);
        
        // Show error in UI
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('Failed to load system statistics', 5000);
        }
        
        // Set default values
        document.getElementById('totalUsers').textContent = 'Error';
        document.getElementById('activeUsers').textContent = 'Active: -';
        document.getElementById('totalFiles').textContent = 'Error';
        document.getElementById('totalCrawls').textContent = 'Error';
        document.getElementById('totalFaqs').textContent = 'Error';
    }
}

// Load users list
async function loadUsers() {
    try {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        // Show loading state
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: #64748b;">
                    <span class="material-icons-round" style="font-size: 48px; color: #cbd5e1; display: block; margin-bottom: 10px;">hourglass_empty</span>
                    Loading users...
                </td>
            </tr>
        `;

        const response = await fetch('/admin/api/users', {
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Response is not JSON');
        }

        const data = await response.json();

        if (data.success && data.users) {
            const users = data.users;

            if (users.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px; color: #64748b;">
                            <span class="material-icons-round" style="font-size: 48px; color: #cbd5e1; display: block; margin-bottom: 10px;">people_outline</span>
                            No users found
                        </td>
                    </tr>
                `;
                return;
            }

            // Render users table
            tbody.innerHTML = users.map(user => {
                const createdDate = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A';
                const lastLogin = user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never';

                // Role badge color
                let roleBadgeColor = '#64748b';
                if (user.role === 'admin') {
                    roleBadgeColor = '#dc2626';
                } else if (user.role === 'user') {
                    roleBadgeColor = '#0891b2';
                }

                return `
                    <tr style="border-bottom: 1px solid #e1e5e9; transition: background-color 0.2s;">
                        <td style="padding: 12px;">
                            <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">${escapeHtml(user.username || 'N/A')}</div>
                            <div style="font-size: 12px; color: #64748b;">${escapeHtml(user.email || 'N/A')}</div>
                        </td>
                        <td style="padding: 12px;">
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; background: ${roleBadgeColor}; color: white;">
                                ${escapeHtml(user.role || 'user')}
                            </span>
                        </td>
                        <td style="padding: 12px; color: #1e293b; font-weight: 500;">${user.files_count || 0}</td>
                        <td style="padding: 12px; color: #1e293b; font-weight: 500;">${user.crawls_count || 0}</td>
                        <td style="padding: 12px; color: #1e293b; font-weight: 500;">${user.faqs_count || 0}</td>
                        <td style="padding: 12px; color: #64748b; font-size: 14px;">${createdDate}</td>
                        <td style="padding: 12px; color: #64748b; font-size: 14px;">${lastLogin}</td>
                    </tr>
                `;
            }).join('');

            // Add hover effect to rows
            const rows = tbody.querySelectorAll('tr');
            rows.forEach(row => {
                row.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = '#f8fafc';
                });
                row.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = 'transparent';
                });
            });

        } else {
            throw new Error(data.error || 'Failed to load users');
        }
    } catch (error) {
        console.error('❌ Error loading users:', error);
        
        // Show error in UI
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('Failed to load users list', 5000);
        }
        
        // Show error in table
        const tbody = document.getElementById('usersTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 40px; color: #dc2626;">
                        <span class="material-icons-round" style="font-size: 48px; color: #dc2626; display: block; margin-bottom: 10px;">error_outline</span>
                        Error loading users. Please try again.
                    </td>
                </tr>
            `;
        }
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Refresh users list
async function refreshUsers() {
    await loadUsers();
    if (typeof showSuccessNotification === 'function') {
        showSuccessNotification('Users list refreshed', 2000);
    }
}

// Initialize admin dashboard
async function initializeAdminDashboard() {
    console.log('✅ Initializing admin dashboard...');
    
    // Load system statistics
    await loadSystemStats();
    
    // Load users list
    await loadUsers();
    
    // Set up refresh button
    const refreshBtn = document.getElementById('refreshUsersBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refreshing...';
            await refreshUsers();
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refresh';
        });
    }
    
    console.log('✅ Admin dashboard initialized');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdminDashboard);
} else {
    initializeAdminDashboard();
}

