/**
 * Admin Dashboard JavaScript
 * Handles loading and displaying admin statistics and user list
 */

// Admin tab switching
function switchAdminTab(tabName) {
    try {
        // Hide all admin tab contents
        const contents = document.querySelectorAll('.admin-tab-content');
        contents.forEach(el => {
            el.classList.remove('active');
            el.style.display = 'none';
        });

        // Show selected tab
        const activeContent = document.getElementById(`admin-tab-${tabName}`);
        if (activeContent) {
            activeContent.classList.add('active');
            activeContent.style.display = 'block';
            
            // Load system API keys when tab is switched to api-keys
            if (tabName === 'api-keys') {
                loadSystemAPIKeys();
            }
        }

        // Update tab button states
        const buttons = document.querySelectorAll('.admin-tab-button');
        buttons.forEach(btn => btn.classList.remove('active'));

        const activeButton = document.querySelector(`.admin-tab-button[data-tab="${tabName}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    } catch (err) {
    }
}

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

// Pagination state
let allUsers = [];
let currentUsersPage = 1;
const usersPerPage = 20;

let allSubscriptions = [];
let currentSubscriptionsPage = 1;
const subscriptionsPerPage = 20;

// Load users list
async function loadUsers() {
    try {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        // Show loading state
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #64748b;">                                                               
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
            allUsers = data.users;
            currentUsersPage = 1; // Reset to first page
            renderUsersPage();
        } else {
            throw new Error(data.error || 'Failed to load users');
        }
    } catch (error) {
        
        // Show error in UI
        if (typeof showErrorNotification === 'function') {
            showErrorNotification('Failed to load users list', 5000);
        }
        
        // Show error in table
        const tbody = document.getElementById('usersTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #dc2626;">                                                           
                        <span class="material-icons-round" style="font-size: 48px; color: #dc2626; display: block; margin-bottom: 10px;">error_outline</span>                                                                          
                        Error loading users. Please try again.
                    </td>
                </tr>
            `;
        }
    }
}

// Render users page with pagination
function renderUsersPage() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    if (allUsers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #64748b;">                                                       
                    <span class="material-icons-round" style="font-size: 48px; color: #cbd5e1; display: block; margin-bottom: 10px;">people_outline</span>                                                                     
                    No users found
                </td>
            </tr>
        `;
        updateUsersPagination();
        return;
    }

    // Calculate pagination
    const totalPages = Math.ceil(allUsers.length / usersPerPage);
    const startIndex = (currentUsersPage - 1) * usersPerPage;
    const endIndex = startIndex + usersPerPage;
    const pageUsers = allUsers.slice(startIndex, endIndex);

    // Render users table with row numbers
    tbody.innerHTML = pageUsers.map((user, index) => {
        const rowNumber = startIndex + index + 1;
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
                <td style="padding: 12px; text-align: center; color: #64748b; font-weight: 600;">${rowNumber}</td>
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

    updateUsersPagination();
}

// Update users pagination controls
function updateUsersPagination() {
    const paginationEl = document.getElementById('usersPagination');
    if (!paginationEl) return;

    const totalPages = Math.ceil(allUsers.length / usersPerPage);
    const startIndex = (currentUsersPage - 1) * usersPerPage;
    const endIndex = Math.min(startIndex + usersPerPage, allUsers.length);

    if (totalPages <= 1) {
        paginationEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px; color: #64748b; font-size: 14px;">
                <span>Showing ${allUsers.length} of ${allUsers.length} users</span>
            </div>
        `;
        return;
    }

    paginationEl.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px;">
            <div style="color: #64748b; font-size: 14px;">
                Showing ${startIndex + 1} to ${endIndex} of ${allUsers.length} users
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <button 
                    onclick="goToUsersPage(${currentUsersPage - 1})" 
                    ${currentUsersPage === 1 ? 'disabled' : ''}
                    style="padding: 8px 16px; border: 1px solid #e1e5e9; background: ${currentUsersPage === 1 ? '#f1f5f9' : 'white'}; color: ${currentUsersPage === 1 ? '#94a3b8' : '#1e293b'}; border-radius: 6px; cursor: ${currentUsersPage === 1 ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.2s;"
                    ${currentUsersPage === 1 ? 'disabled' : ''}
                >
                    Previous
                </button>
                <div style="display: flex; gap: 4px;">
                    ${Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                            pageNum = i + 1;
                        } else if (currentUsersPage <= 3) {
                            pageNum = i + 1;
                        } else if (currentUsersPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                        } else {
                            pageNum = currentUsersPage - 2 + i;
                        }
                        return `
                            <button 
                                onclick="goToUsersPage(${pageNum})" 
                                style="padding: 8px 12px; border: 1px solid #e1e5e9; background: ${pageNum === currentUsersPage ? '#0891b2' : 'white'}; color: ${pageNum === currentUsersPage ? 'white' : '#1e293b'}; border-radius: 6px; cursor: pointer; font-size: 14px; min-width: 40px; transition: all 0.2s;"
                            >
                                ${pageNum}
                            </button>
                        `;
                    }).join('')}
                </div>
                <button 
                    onclick="goToUsersPage(${currentUsersPage + 1})" 
                    ${currentUsersPage === totalPages ? 'disabled' : ''}
                    style="padding: 8px 16px; border: 1px solid #e1e5e9; background: ${currentUsersPage === totalPages ? '#f1f5f9' : 'white'}; color: ${currentUsersPage === totalPages ? '#94a3b8' : '#1e293b'}; border-radius: 6px; cursor: ${currentUsersPage === totalPages ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.2s;"
                    ${currentUsersPage === totalPages ? 'disabled' : ''}
                >
                    Next
                </button>
            </div>
        </div>
    `;
}

// Navigate to users page
function goToUsersPage(page) {
    const totalPages = Math.ceil(allUsers.length / usersPerPage);
    if (page < 1 || page > totalPages) return;
    currentUsersPage = page;
    renderUsersPage();
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

// Load sample subscription data
async function loadSubscriptions() {
    try {
        const tbody = document.getElementById('subscriptionsTableBody');
        if (!tbody) return;

        // Sample subscription data - expanded to show pagination
        const sampleSubscriptions = [
            { username: 'john_doe', email: 'john@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-15', started: '2023-08-15' },
            { username: 'jane_smith', email: 'jane@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Monthly', nextBilling: '2024-02-20', started: '2023-11-20' },
            { username: 'bob_wilson', email: 'bob@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-02-10', started: '2024-01-10' },
            { username: 'alice_brown', email: 'alice@example.com', plan: 'Pro', status: 'cancelled', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-05', started: '2023-09-05' },
            { username: 'charlie_davis', email: 'charlie@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Yearly', nextBilling: '2025-01-25', started: '2024-01-25' },
            { username: 'diana_miller', email: 'diana@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-02-12', started: '2023-12-12' },
            { username: 'edward_taylor', email: 'edward@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-18', started: '2023-10-18' },
            { username: 'fiona_anderson', email: 'fiona@example.com', plan: 'Starter', status: 'expired', amount: 9.99, billingCycle: 'Monthly', nextBilling: 'N/A', started: '2023-06-01' },
            { username: 'george_martin', email: 'george@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-22', started: '2023-11-22' },
            { username: 'helen_jones', email: 'helen@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Yearly', nextBilling: '2025-03-01', started: '2024-03-01' },
            { username: 'ivan_lee', email: 'ivan@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-02-25', started: '2023-12-25' },
            { username: 'julia_wang', email: 'julia@example.com', plan: 'Pro', status: 'cancelled', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-08', started: '2023-09-08' },
            { username: 'kevin_zhang', email: 'kevin@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Monthly', nextBilling: '2024-02-28', started: '2023-10-28' },
            { username: 'lisa_chen', email: 'lisa@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-03-05', started: '2024-01-05' },
            { username: 'mike_kim', email: 'mike@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-03-10', started: '2023-11-10' },
            { username: 'nancy_park', email: 'nancy@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Yearly', nextBilling: '2025-04-15', started: '2024-04-15' },
            { username: 'oscar_liu', email: 'oscar@example.com', plan: 'Starter', status: 'expired', amount: 9.99, billingCycle: 'Monthly', nextBilling: 'N/A', started: '2023-05-20' },
            { username: 'patricia_nguyen', email: 'patricia@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-03-15', started: '2023-11-15' },
            { username: 'quinn_tran', email: 'quinn@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Monthly', nextBilling: '2024-03-20', started: '2023-12-20' },
            { username: 'rachel_pham', email: 'rachel@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-03-25', started: '2024-01-25' },
            { username: 'steve_vo', email: 'steve@example.com', plan: 'Pro', status: 'cancelled', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-02-12', started: '2023-09-12' },
            { username: 'tina_huang', email: 'tina@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Yearly', nextBilling: '2025-05-01', started: '2024-05-01' },
            { username: 'umar_ali', email: 'umar@example.com', plan: 'Starter', status: 'active', amount: 9.99, billingCycle: 'Monthly', nextBilling: '2024-04-05', started: '2024-02-05' },
            { username: 'violet_singh', email: 'violet@example.com', plan: 'Pro', status: 'active', amount: 29.99, billingCycle: 'Monthly', nextBilling: '2024-04-10', started: '2023-12-10' },
            { username: 'william_patel', email: 'william@example.com', plan: 'Enterprise', status: 'active', amount: 99.99, billingCycle: 'Monthly', nextBilling: '2024-04-15', started: '2023-12-15' }
        ];

        allSubscriptions = sampleSubscriptions;
        currentSubscriptionsPage = 1; // Reset to first page
        renderSubscriptionsPage();
    } catch (error) {
        const tbody = document.getElementById('subscriptionsTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #dc2626;">                                                           
                        <span class="material-icons-round" style="font-size: 48px; color: #dc2626; display: block; margin-bottom: 10px;">error_outline</span>                                                                          
                        Error loading subscriptions. Please try again.
                    </td>
                </tr>
            `;
        }
    }
}

// Render subscriptions page with pagination
function renderSubscriptionsPage() {
    const tbody = document.getElementById('subscriptionsTableBody');
    if (!tbody) return;

    if (allSubscriptions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #64748b;">                                                           
                    <span class="material-icons-round" style="font-size: 48px; color: #cbd5e1; display: block; margin-bottom: 10px;">receipt_long</span>                                                                           
                    No subscriptions found
                </td>
            </tr>
        `;
        updateSubscriptionsPagination();
        return;
    }

    // Calculate pagination
    const totalPages = Math.ceil(allSubscriptions.length / subscriptionsPerPage);
    const startIndex = (currentSubscriptionsPage - 1) * subscriptionsPerPage;
    const endIndex = startIndex + subscriptionsPerPage;
    const pageSubscriptions = allSubscriptions.slice(startIndex, endIndex);

    // Render subscriptions table with row numbers
    tbody.innerHTML = pageSubscriptions.map((sub, index) => {
        const rowNumber = startIndex + index + 1;
        const nextBillingDate = sub.nextBilling === 'N/A' ? 'N/A' : new Date(sub.nextBilling).toLocaleDateString();                                   
        const startedDate = new Date(sub.started).toLocaleDateString();

        // Status badge color
        let statusBadgeColor = '#64748b';
        let statusText = sub.status;
        if (sub.status === 'active') {
            statusBadgeColor = '#22c55e';
        } else if (sub.status === 'cancelled') {
            statusBadgeColor = '#f59e0b';
        } else if (sub.status === 'expired') {
            statusBadgeColor = '#ef4444';
        }

        return `
            <tr style="border-bottom: 1px solid #e1e5e9; transition: background-color 0.2s;">                                                         
                <td style="padding: 12px; text-align: center; color: #64748b; font-weight: 600;">${rowNumber}</td>
                <td style="padding: 12px;">
                    <div style="font-weight: 600; color: #1e293b; margin-bottom: 4px;">${escapeHtml(sub.username)}</div>                              
                    <div style="font-size: 12px; color: #64748b;">${escapeHtml(sub.email)}</div>                                                      
                </td>
                <td style="padding: 12px;">
                    <span style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; background: #0891b2; color: white;">                                                            
                        ${escapeHtml(sub.plan)}
                    </span>
                </td>
                <td style="padding: 12px;">
                    <span style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; background: ${statusBadgeColor}; color: white;">                                                
                        ${escapeHtml(statusText.charAt(0).toUpperCase() + statusText.slice(1))}                                                       
                    </span>
                </td>
                <td style="padding: 12px; color: #1e293b; font-weight: 600;">$${sub.amount.toFixed(2)}</td>                                           
                <td style="padding: 12px; color: #64748b; font-size: 14px;">${escapeHtml(sub.billingCycle)}</td>                                      
                <td style="padding: 12px; color: #64748b; font-size: 14px;">${nextBillingDate}</td>                                                   
                <td style="padding: 12px; color: #64748b; font-size: 14px;">${startedDate}</td>                                                       
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

    updateSubscriptionsPagination();
}

// Update subscriptions pagination controls
function updateSubscriptionsPagination() {
    const paginationEl = document.getElementById('subscriptionsPagination');
    if (!paginationEl) return;

    const totalPages = Math.ceil(allSubscriptions.length / subscriptionsPerPage);
    const startIndex = (currentSubscriptionsPage - 1) * subscriptionsPerPage;
    const endIndex = Math.min(startIndex + subscriptionsPerPage, allSubscriptions.length);

    if (totalPages <= 1) {
        paginationEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px; color: #64748b; font-size: 14px;">
                <span>Showing ${allSubscriptions.length} of ${allSubscriptions.length} subscriptions</span>
            </div>
        `;
        return;
    }

    paginationEl.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px;">
            <div style="color: #64748b; font-size: 14px;">
                Showing ${startIndex + 1} to ${endIndex} of ${allSubscriptions.length} subscriptions
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <button 
                    onclick="goToSubscriptionsPage(${currentSubscriptionsPage - 1})" 
                    ${currentSubscriptionsPage === 1 ? 'disabled' : ''}
                    style="padding: 8px 16px; border: 1px solid #e1e5e9; background: ${currentSubscriptionsPage === 1 ? '#f1f5f9' : 'white'}; color: ${currentSubscriptionsPage === 1 ? '#94a3b8' : '#1e293b'}; border-radius: 6px; cursor: ${currentSubscriptionsPage === 1 ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.2s;"
                    ${currentSubscriptionsPage === 1 ? 'disabled' : ''}
                >
                    Previous
                </button>
                <div style="display: flex; gap: 4px;">
                    ${Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let pageNum;
                        if (totalPages <= 5) {
                            pageNum = i + 1;
                        } else if (currentSubscriptionsPage <= 3) {
                            pageNum = i + 1;
                        } else if (currentSubscriptionsPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                        } else {
                            pageNum = currentSubscriptionsPage - 2 + i;
                        }
                        return `
                            <button 
                                onclick="goToSubscriptionsPage(${pageNum})" 
                                style="padding: 8px 12px; border: 1px solid #e1e5e9; background: ${pageNum === currentSubscriptionsPage ? '#0891b2' : 'white'}; color: ${pageNum === currentSubscriptionsPage ? 'white' : '#1e293b'}; border-radius: 6px; cursor: pointer; font-size: 14px; min-width: 40px; transition: all 0.2s;"
                            >
                                ${pageNum}
                            </button>
                        `;
                    }).join('')}
                </div>
                <button 
                    onclick="goToSubscriptionsPage(${currentSubscriptionsPage + 1})" 
                    ${currentSubscriptionsPage === totalPages ? 'disabled' : ''}
                    style="padding: 8px 16px; border: 1px solid #e1e5e9; background: ${currentSubscriptionsPage === totalPages ? '#f1f5f9' : 'white'}; color: ${currentSubscriptionsPage === totalPages ? '#94a3b8' : '#1e293b'}; border-radius: 6px; cursor: ${currentSubscriptionsPage === totalPages ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.2s;"
                    ${currentSubscriptionsPage === totalPages ? 'disabled' : ''}
                >
                    Next
                </button>
            </div>
        </div>
    `;
}

// Navigate to subscriptions page
function goToSubscriptionsPage(page) {
    const totalPages = Math.ceil(allSubscriptions.length / subscriptionsPerPage);
    if (page < 1 || page > totalPages) return;
    currentSubscriptionsPage = page;
    renderSubscriptionsPage();
}

// Initialize admin dashboard
async function initializeAdminDashboard() {
    
    // Ensure Users tab is active by default
    switchAdminTab('users');

    // Load system statistics
    await loadSystemStats();
    
    // Load users list
    await loadUsers();
    
    // Load subscriptions (for Sales tab)
    await loadSubscriptions();
    
    // Set up refresh buttons
    const refreshUsersBtn = document.getElementById('refreshUsersBtn');
    if (refreshUsersBtn) {
        refreshUsersBtn.addEventListener('click', async () => {
            refreshUsersBtn.disabled = true;
            refreshUsersBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refreshing...';
            await refreshUsers();
            refreshUsersBtn.disabled = false;
            refreshUsersBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refresh';
        });
    }

    const refreshSubscriptionsBtn = document.getElementById('refreshSubscriptionsBtn');
    if (refreshSubscriptionsBtn) {
        refreshSubscriptionsBtn.addEventListener('click', async () => {
            refreshSubscriptionsBtn.disabled = true;
            refreshSubscriptionsBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refreshing...';
            await loadSubscriptions();
            refreshSubscriptionsBtn.disabled = false;
            refreshSubscriptionsBtn.innerHTML = '<span class="material-icons-round" style="font-size: 18px;">refresh</span> Refresh';
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification('Subscriptions refreshed', 2000);
            }
        });
    }
    
    // Initialize analytics charts when Analytics tab is first opened
    let analyticsInitialized = false;
    const analyticsTabBtn = document.querySelector('[data-tab="analytics"]');
    if (analyticsTabBtn) {
        analyticsTabBtn.addEventListener('click', () => {
            if (!analyticsInitialized) {
                initializeAnalyticsCharts();
                analyticsInitialized = true;
            }
        });
    }
    
}

// Initialize Analytics Charts using ApexCharts
function initializeAnalyticsCharts() {

    // User Growth Over Time (Line Chart)
    const userGrowthEl = document.getElementById('userGrowthChart');
    if (userGrowthEl) {
        const userGrowthChart = new ApexCharts(userGrowthEl, {
            series: [{
                name: 'New Users',
                data: [5, 8, 12, 15, 18, 22, 25, 28, 32, 35, 38, 42]
            }],
            chart: {
                type: 'area',
                height: 300,
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            colors: ['#0891b2'],
            stroke: {
                curve: 'smooth',
                width: 3
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.4,
                    opacityTo: 0.1,
                    stops: [0, 90, 100]
                }
            },
            dataLabels: { enabled: false },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 0,
                xaxis: { lines: { show: false } }
            },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                labels: { style: { colors: '#64748b' } }
            },
            yaxis: {
                labels: { style: { colors: '#64748b' } }
            },
            tooltip: {
                theme: 'light',
                style: { fontSize: '12px' }
            }
        });
        userGrowthChart.render();
    }

    // Revenue Trend (Line Chart)
    const revenueTrendEl = document.getElementById('revenueTrendChart');
    if (revenueTrendEl) {
        const revenueTrendChart = new ApexCharts(revenueTrendEl, {
            series: [{
                name: 'Revenue',
                data: [850, 1200, 1500, 1800, 2100, 2400, 2800, 3200, 3600, 3900, 4200, 4500]
            }],
            chart: {
                type: 'area',
                height: 300,
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            colors: ['#22c55e'],
            stroke: {
                curve: 'smooth',
                width: 3
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.4,
                    opacityTo: 0.1,
                    stops: [0, 90, 100]
                }
            },
            dataLabels: { enabled: false },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 0,
                xaxis: { lines: { show: false } }
            },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                labels: { style: { colors: '#64748b' } }
            },
            yaxis: {
                labels: {
                    style: { colors: '#64748b' },
                    formatter: function(val) { return '$' + val; }
                }
            },
            tooltip: {
                theme: 'light',
                y: { formatter: function(val) { return '$' + val; } }
            }
        });
        revenueTrendChart.render();
    }

    // Plan Distribution (Donut Chart)
    const planDistributionEl = document.getElementById('planDistributionChart');
    if (planDistributionEl) {
        const planDistributionChart = new ApexCharts(planDistributionEl, {
            series: [25, 15, 7],
            chart: {
                type: 'donut',
                height: 300,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            labels: ['Starter', 'Pro', 'Enterprise'],
            colors: ['#0891b2', '#8b5cf6', '#22c55e'],
            legend: {
                position: 'bottom',
                fontSize: '14px',
                labels: { colors: '#64748b' }
            },
            dataLabels: {
                enabled: true,
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '65%'
                    }
                }
            },
            tooltip: {
                theme: 'light',
                y: { formatter: function(val) { return val + ' users'; } }
            }
        });
        planDistributionChart.render();
    }

    // Knowledge Base Usage (Bar Chart)
    const knowledgeBaseEl = document.getElementById('knowledgeBaseChart');
    if (knowledgeBaseEl) {
        const knowledgeBaseChart = new ApexCharts(knowledgeBaseEl, {
            series: [{
                name: 'Total Count',
                data: [342, 187, 156]
            }],
            chart: {
                type: 'bar',
                height: 300,
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            colors: ['#0891b2', '#8b5cf6', '#22c55e'],
            plotOptions: {
                bar: {
                    borderRadius: 8,
                    columnWidth: '60%',
                    distributed: true
                }
            },
            dataLabels: {
                enabled: true,
                style: {
                    fontSize: '12px',
                    fontWeight: 600,
                    colors: ['#fff']
                }
            },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 0,
                xaxis: { lines: { show: false } }
            },
            xaxis: {
                categories: ['Files', 'Crawled URLs', 'FAQs'],
                labels: { style: { colors: '#64748b' } }
            },
            yaxis: {
                labels: { style: { colors: '#64748b' } }
            },
            tooltip: {
                theme: 'light'
            }
        });
        knowledgeBaseChart.render();
    }

    // Active Users (Area Chart)
    const activeUsersEl = document.getElementById('activeUsersChart');
    if (activeUsersEl) {
        // Generate last 30 days labels
        const last30Days = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            last30Days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }

        // Generate sample active users data
        const activeUsersData = Array.from({ length: 30 }, () => Math.floor(Math.random() * 20) + 15);

        const activeUsersChart = new ApexCharts(activeUsersEl, {
            series: [{
                name: 'Active Users',
                data: activeUsersData
            }],
            chart: {
                type: 'area',
                height: 300,
                toolbar: { show: false },
                zoom: { enabled: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            colors: ['#8b5cf6'],
            stroke: {
                curve: 'smooth',
                width: 3
            },
            fill: {
                type: 'gradient',
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.4,
                    opacityTo: 0.1,
                    stops: [0, 90, 100]
                }
            },
            dataLabels: { enabled: false },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 0,
                xaxis: { lines: { show: false } }
            },
            xaxis: {
                categories: last30Days,
                labels: {
                    style: { colors: '#64748b' },
                    rotate: -45,
                    rotateAlways: true
                }
            },
            yaxis: {
                labels: { style: { colors: '#64748b' } }
            },
            tooltip: {
                theme: 'light'
            }
        });
        activeUsersChart.render();
    }

    // Revenue by Plan (Bar Chart)
    const revenueByPlanEl = document.getElementById('revenueByPlanChart');
    if (revenueByPlanEl) {
        const revenueByPlanChart = new ApexCharts(revenueByPlanEl, {
            series: [{
                name: 'Monthly Revenue',
                data: [249.75, 449.85, 699.93]
            }],
            chart: {
                type: 'bar',
                height: 300,
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 1500
                }
            },
            colors: ['#0891b2', '#8b5cf6', '#22c55e'],
            plotOptions: {
                bar: {
                    borderRadius: 8,
                    columnWidth: '60%',
                    distributed: true
                }
            },
            dataLabels: {
                enabled: true,
                style: {
                    fontSize: '12px',
                    fontWeight: 600,
                    colors: ['#fff']
                },
                formatter: function(val) { return '$' + val.toFixed(2); }
            },
            grid: {
                borderColor: '#f1f5f9',
                strokeDashArray: 0,
                xaxis: { lines: { show: false } }
            },
            xaxis: {
                categories: ['Starter', 'Pro', 'Enterprise'],
                labels: { style: { colors: '#64748b' } }
            },
            yaxis: {
                labels: {
                    style: { colors: '#64748b' },
                    formatter: function(val) { return '$' + val; }
                }
            },
            tooltip: {
                theme: 'light',
                y: { formatter: function(val) { return '$' + val.toFixed(2); } }
            }
        });
        revenueByPlanChart.render();
    }

}

// System API Key Management Functions (LLM Provider Default Keys)
const SYSTEM_PROVIDERS = ['openai', 'gemini', 'groq']; // Removed deepseek (not free, requires funding)

async function loadSystemAPIKeys() {
    try {
        const loadingEl = document.getElementById('apiKeysLoading');
        const successEl = document.getElementById('apiKeysSuccess');
        const errorEl = document.getElementById('apiKeysError');
        
        if (loadingEl) loadingEl.style.display = 'block';
        if (successEl) successEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';
        
        // Load keys for all providers
        const keys = {};
        for (const provider of SYSTEM_PROVIDERS) {
            try {
                const response = await fetch(`/admin/api/system-api-key/${provider}`, {
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.api_key) {
                        keys[provider] = data.api_key;
                    }
                }
            } catch (err) {
                console.error(`Error loading ${provider} key:`, err);
            }
        }
        
        // Update UI to show masked keys (if they exist)
        for (const provider of SYSTEM_PROVIDERS) {
            const inputEl = document.getElementById(`${provider}-api-key`);
            if (inputEl && keys[provider] && keys[provider].has_key) {
                // Populate input with masked key to show that a key exists
                const masked = keys[provider].key_value_masked || '••••••••••••••••••••';
                inputEl.value = masked;
                inputEl.type = 'password'; // Keep as password type
                inputEl.placeholder = `Current key exists (enter new key to update)`;
                
                // Update status to Active
                const statusEl = document.getElementById(`${provider}-status`);
                if (statusEl) {
                    const statusDot = statusEl.querySelector('.status-dot');
                    const statusText = statusEl.querySelector('.status-text');
                    if (statusDot && statusText) {
                        statusDot.style.background = '#22c55e';
                        statusText.textContent = 'Active';
                        statusEl.style.background = '#dcfce7';
                        statusEl.style.color = '#166534';
                    }
                }
            } else {
                // No key exists - clear input and set status to Inactive
                if (inputEl) {
                    inputEl.value = '';
                    inputEl.placeholder = `Enter ${provider.charAt(0).toUpperCase() + provider.slice(1)} API key`;
                }
                
                const statusEl = document.getElementById(`${provider}-status`);
                if (statusEl) {
                    const statusDot = statusEl.querySelector('.status-dot');
                    const statusText = statusEl.querySelector('.status-text');
                    if (statusDot && statusText) {
                        statusDot.style.background = '#94a3b8';
                        statusText.textContent = 'Inactive';
                        statusEl.style.background = '#f1f5f9';
                        statusEl.style.color = '#64748b';
                    }
                }
            }
        }
        
        if (loadingEl) loadingEl.style.display = 'none';
    } catch (error) {
        console.error('Error loading system API keys:', error);
        const loadingEl = document.getElementById('apiKeysLoading');
        const errorEl = document.getElementById('apiKeysError');
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) {
            errorEl.textContent = 'Failed to load API keys. Please refresh the page.';
            errorEl.style.display = 'block';
        }
    }
}

// Test API key with provider before saving
async function testSystemAPIKey(provider, apiKey) {
    try {
        // Get default model for provider (matching LLM_PROVIDERS config)
        // For Gemini, try multiple models in order of compatibility
        const defaultModels = {
            'openai': 'gpt-4o-mini',
            'gemini': 'gemini-2.5-flash', // Updated: Use latest available model
            'deepseek': 'deepseek-chat',
            'groq': 'llama-3.1-8b-instant' // Using 8B for faster testing
        };
        
        // For Gemini, try multiple models if first one fails
        // Updated to use available models: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
        let model = defaultModels[provider] || 'gpt-4o-mini';
        const geminiFallbackModels = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-flash-latest', 'gemini-pro-latest'];
        
        let lastError = null;
        let response = null;
        
        if (provider === 'gemini') {
            // Try each Gemini model until one works
            for (const testModel of geminiFallbackModels) {
                try {
                    response = await fetch('/api/test-llm', {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            provider: provider,
                            model: testModel,
                            api_key: apiKey
                        })
                    });
                    
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        lastError = 'Server returned invalid response. Please check your login status.';
                        continue;
                    }
                    
                    const result = await response.json();
                    
                    if (response.ok && result.status === 'success') {
                        // Success! Use this model and return
                        return { success: true, result: result, model: testModel };
                    } else {
                        // This model failed, try next one
                        lastError = result.error || result.message || 'API key test failed';
                        continue;
                    }
                } catch (error) {
                    lastError = error.message;
                    continue;
                }
            }
            
            // If we get here, all models failed
            return { success: false, error: lastError || 'All Gemini models failed. Please check your API key.' };
        } else {
            // For non-Gemini providers, use single model
            response = await fetch('/api/test-llm', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    provider: provider,
                    model: model,
                    api_key: apiKey
                })
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                return { success: false, error: 'Server returned invalid response. Please check your login status.' };
            }
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                return { success: true, result: result };
            } else {
                const errorMsg = result.error || result.message || 'API key test failed';
                return { success: false, error: errorMsg };
            }
        }
    } catch (error) {
        let errorMsg = error.message;
        if (errorMsg.includes('JSON') || errorMsg.includes('Unexpected token')) {
            errorMsg = 'Server returned an invalid response. Please check your login status and try again.';
        }
        return { success: false, error: errorMsg };
    }
}

async function saveSystemAPIKey(provider) {
    try {
        const inputEl = document.getElementById(`${provider}-api-key`);
        const loadingEl = document.getElementById('apiKeysLoading');
        const successEl = document.getElementById('apiKeysSuccess');
        const errorEl = document.getElementById('apiKeysError');
        const saveBtn = document.getElementById(`save${provider.charAt(0).toUpperCase() + provider.slice(1)}KeyBtn`);
        
        if (!inputEl) {
            console.error(`Input element not found for provider: ${provider}`);
            return;
        }
        
        const apiKey = inputEl.value.trim();
        
        // If empty, don't update (keep current key)
        if (!apiKey) {
            const errorMsg = 'Please enter an API key to save.';
            if (errorEl) {
                errorEl.textContent = errorMsg;
                errorEl.style.display = 'block';
                setTimeout(() => {
                    if (errorEl) errorEl.style.display = 'none';
                }, 3000);
            }
            // Always show toast notification
            if (typeof showWarningNotification === 'function') {
                showWarningNotification(errorMsg, 4000);
            }
            return;
        }
        
        // Check if input contains masked value (don't test masked keys)
        if (apiKey.includes('••••') || apiKey.length < 10) {
            const errorMsg = 'Please enter a valid API key (not a masked value).';
            if (errorEl) {
                errorEl.textContent = errorMsg;
                errorEl.style.display = 'block';
                setTimeout(() => {
                    if (errorEl) errorEl.style.display = 'none';
                }, 3000);
            }
            // Always show toast notification
            if (typeof showWarningNotification === 'function') {
                showWarningNotification(errorMsg, 4000);
            }
            return;
        }
        
        // Show loading state
        if (loadingEl) loadingEl.style.display = 'block';
        if (successEl) successEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 20px;">hourglass_empty</span> Testing...';
        }
        
        // STEP 1: Test the API key first
        // Show info toast that testing is starting
        const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
        if (typeof showInfoNotification === 'function') {
            showInfoNotification(`Testing ${providerName} API key...`, 3000);
        }
        
        const testResult = await testSystemAPIKey(provider, apiKey);
        
        if (!testResult.success) {
            // Test failed - don't save
            const errorMsg = `API key test failed: ${testResult.error}`;
            if (errorEl) {
                errorEl.textContent = errorMsg;
                errorEl.style.display = 'block';
            }
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 20px;">save</span> Save ' + providerName + ' Key';
            }
            if (loadingEl) loadingEl.style.display = 'none';
            
            // Always show error toast notification
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMsg, 6000);
            }
            return;
        }
        
        // STEP 2: Test passed - now save the API key
        if (saveBtn) {
            saveBtn.innerHTML = '<span class="material-icons-round" style="vertical-align: middle; font-size: 20px;">hourglass_empty</span> Saving...';
        }
        
        const response = await fetch('/admin/api/system-api-key', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider: provider,
                api_key: apiKey,
                key_type: 'default'
            })
        });
        
        const data = await response.json();
        
        if (loadingEl) loadingEl.style.display = 'none';
        
        if (data.success) {
            // Reload API keys to update UI with masked key and status
            await loadSystemAPIKeys();
            
            // Show success message
            const successMsg = `${providerName} API key tested and saved successfully!`;
            if (successEl) {
                successEl.textContent = successMsg;
                successEl.style.display = 'block';
                setTimeout(() => {
                    if (successEl) successEl.style.display = 'none';
                }, 3000);
            }
            
            // Always show success toast notification
            if (typeof showSuccessNotification === 'function') {
                showSuccessNotification(successMsg, 4000);
            }
        } else {
            // Show error message
            const errorMsg = data.error || 'Failed to save API key. Please try again.';
            if (errorEl) {
                errorEl.textContent = errorMsg;
                errorEl.style.display = 'block';
                setTimeout(() => {
                    if (errorEl) errorEl.style.display = 'none';
                }, 5000);
            }
            
            // Always show error toast notification
            if (typeof showErrorNotification === 'function') {
                showErrorNotification(errorMsg, 6000);
            }
        }
        
        // Restore button
        if (saveBtn) {
            saveBtn.disabled = false;
            const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
            saveBtn.innerHTML = `<span class="material-icons-round" style="vertical-align: middle; font-size: 20px;">save</span> Save ${providerName} Key`;
        }
    } catch (error) {
        console.error(`Error saving ${provider} API key:`, error);
        
        const loadingEl = document.getElementById('apiKeysLoading');
        const errorEl = document.getElementById('apiKeysError');
        const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
        const saveBtn = document.getElementById(`save${providerName}KeyBtn`);
        const errorMsg = 'Error saving API key. Please try again.';
        
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) {
            errorEl.textContent = errorMsg;
            errorEl.style.display = 'block';
            setTimeout(() => {
                if (errorEl) errorEl.style.display = 'none';
            }, 5000);
        }
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = `<span class="material-icons-round" style="vertical-align: middle; font-size: 20px;">save</span> Save ${providerName} Key`;
        }
        
        // Always show error toast notification
        if (typeof showErrorNotification === 'function') {
            showErrorNotification(errorMsg, 6000);
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle password visibility for API key inputs
function togglePasswordVisibility(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (!input || !iconElement) {
        console.error('togglePasswordVisibility: Input or icon element not found');
        return;
    }
    
    if (input.type === 'password') {
        input.type = 'text';
        iconElement.textContent = 'visibility';
        iconElement.style.color = '#0891b2'; // Blue when visible
    } else {
        input.type = 'password';
        iconElement.textContent = 'visibility_off';
        iconElement.style.color = '#64748b'; // Gray when hidden
    }
}

// Expose functions to global scope for onclick handlers
window.saveSystemAPIKey = saveSystemAPIKey;
window.loadSystemAPIKeys = loadSystemAPIKeys;
window.togglePasswordVisibility = togglePasswordVisibility;

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdminDashboard);
} else {
    initializeAdminDashboard();
}

