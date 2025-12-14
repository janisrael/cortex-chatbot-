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
            
            // Load API keys when tab is switched to api-keys
            if (tabName === 'api-keys') {
                loadAPIKeys();
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

// API Key Management Functions
let currentEditingKeyId = null;

async function loadAPIKeys() {
    try {
        const response = await fetch('/admin/api/api-keys');
        const data = await response.json();
        
        if (data.success) {
            renderAPIKeys(data.api_keys);
        } else {
            console.error('Failed to load API keys:', data.error);
        }
    } catch (error) {
        console.error('Error loading API keys:', error);
    }
}

function renderAPIKeys(keys) {
    const container = document.getElementById('api-keys-list');
    if (!container) return;
    
    if (keys.length === 0) {
        container.innerHTML = '<p style="color: #6b7280;">No API keys found. Create one to get started.</p>';
        return;
    }
    
    container.innerHTML = keys.map(key => `
        <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; background: white;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <h4 style="margin: 0 0 4px 0; font-size: 16px;">${escapeHtml(key.name || 'Untitled Key')}</h4>
                    <span style="font-size: 12px; color: #6b7280; padding: 2px 8px; background: #f3f4f6; border-radius: 4px; display: inline-block;">
                        ${escapeHtml(key.key_type || 'custom')}
                    </span>
                    <span style="font-size: 12px; color: ${key.is_active ? '#10b981' : '#ef4444'}; margin-left: 8px;">
                        ${key.is_active ? '● Active' : '○ Inactive'}
                    </span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="toggleAPIKey(${key.id}, ${!key.is_active})" 
                            style="padding: 6px 12px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        ${key.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button onclick="deleteAPIKey(${key.id})" 
                            style="padding: 6px 12px; border: 1px solid #ef4444; background: white; color: #ef4444; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        Delete
                    </button>
                </div>
            </div>
            <div style="font-size: 12px; color: #6b7280;">
                Created: ${key.created_at ? new Date(key.created_at).toLocaleDateString() : 'N/A'}
            </div>
        </div>
    `).join('');
}

function createNewAPIKey() {
    currentEditingKeyId = null;
    document.getElementById('api-key-modal-title').textContent = 'Create API Key';
    document.getElementById('api-key-form').reset();
    document.getElementById('api-key-token-display').style.display = 'none';
    document.getElementById('api-key-modal').style.display = 'flex';
}

function closeAPIKeyModal() {
    document.getElementById('api-key-modal').style.display = 'none';
    currentEditingKeyId = null;
}

async function handleAPIKeySubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('api-key-name').value;
    const keyType = document.getElementById('api-key-type').value;
    
    try {
        const response = await fetch('/admin/api/api-keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                key_type: keyType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('api-key-token').value = data.api_key.token;
            document.getElementById('api-key-token-display').style.display = 'block';
            const submitBtn = document.getElementById('api-key-form').querySelector('button[type="submit"]');
            submitBtn.textContent = 'Close';
            submitBtn.onclick = closeAPIKeyModal;
            submitBtn.type = 'button';
            
            await loadAPIKeys();
        } else {
            alert('Failed to create API key: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error creating API key:', error);
        alert('Error creating API key. Please try again.');
    }
}

function copyAPIKey() {
    const tokenInput = document.getElementById('api-key-token');
    tokenInput.select();
    document.execCommand('copy');
    alert('API key copied to clipboard!');
}

async function toggleAPIKey(keyId, isActive) {
    try {
        const response = await fetch(`/admin/api/api-keys/${keyId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_active: isActive
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadAPIKeys();
        } else {
            alert('Failed to update API key: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error updating API key:', error);
        alert('Error updating API key. Please try again.');
    }
}

async function deleteAPIKey(keyId) {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/api/api-keys/${keyId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadAPIKeys();
        } else {
            alert('Failed to delete API key: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting API key:', error);
        alert('Error deleting API key. Please try again.');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdminDashboard);
} else {
    initializeAdminDashboard();
}

