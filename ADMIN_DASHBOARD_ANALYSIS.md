# Admin Dashboard & OTP Implementation Analysis

## Current RBAC Status

### ✅ Already Implemented:
1. **User Model** (`models/user.py`):
   - Role field with values: `'admin'`, `'user'`, `'viewer'`
   - Methods: `is_admin()`, `is_user()`, `is_viewer()`
   - Database schema supports role-based access

2. **Database Schema**:
   - `users` table has `role` column with CHECK constraint
   - `uploaded_files` table has `user_id` (FOREIGN KEY)
   - `crawled_urls` table has `user_id` (FOREIGN KEY)
   - All data is user-isolated

3. **Authentication**:
   - `@login_required` decorator used extensively
   - Flask-Login integration working
   - `current_user` available in routes

### ❌ Missing:
1. **Admin Authorization Decorator**:
   - No `@admin_required` decorator
   - No admin route protection

2. **Admin Dashboard**:
   - No admin routes/blueprints
   - No admin templates
   - No admin statistics API endpoints

3. **OTP Verification**:
   - No OTP model/table
   - No OTP generation/sending
   - No OTP verification in registration flow

---

## Files That Will Be Affected

### 1. **New Files to Create:**

#### Backend:
- `blueprints/admin.py` - Admin routes and API endpoints
- `models/otp.py` - OTP model for email verification
- `services/admin_service.py` - Admin statistics and user management logic
- `services/otp_service.py` - OTP generation, sending, and verification
- `utils/email_utils.py` - Already exists, will add OTP email sending
- `decorators.py` - Admin authorization decorator

#### Frontend:
- `templates/admin/dashboard.html` - Admin dashboard page
- `templates/admin/users.html` - User management page
- `static/v2/js/admin-dashboard.js` - Admin dashboard JavaScript
- `static/v2/css/admin-dashboard.css` - Admin dashboard styles (or extend existing)

#### Database:
- New table: `otp_verifications` (for OTP storage)
- Migration script to add OTP table

### 2. **Files to Modify:**

#### Backend:
- `blueprints/auth.py`:
  - Add OTP generation after registration
  - Add OTP verification route
  - Modify registration to require OTP verification
  - Add email verification status to user model (optional)

- `models/user.py`:
  - Add `email_verified` field (optional, for future)
  - Add `verified_at` timestamp (optional)

- `app.py`:
  - Register admin blueprint
  - Add admin route to navigation (if needed)

#### Frontend:
- `templates/auth/register.html`:
  - Add OTP input field (initially hidden)
  - Add OTP verification step
  - Add resend OTP button

- `templates/dashboard/dashboard.html`:
  - Add "Admin Dashboard" link in header (only for admins)
  - Add admin menu item

- `static/v2/js/dashboard-core.js`:
  - Add admin dashboard initialization (if needed)

---

## Implementation Plan

### Phase 1: Admin Authorization & Dashboard (Priority 1)

#### Step 1.1: Create Admin Decorator
**File**: `decorators.py` (new)
```python
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
```

#### Step 1.2: Create Admin Service
**File**: `services/admin_service.py` (new)
- `get_all_users()` - Get all users with stats
- `get_user_stats(user_id)` - Get user-specific stats
- `get_system_stats()` - Get overall system statistics
- `get_user_files_count(user_id)` - Count uploaded files
- `get_user_crawls_count(user_id)` - Count crawled URLs
- `get_user_faqs_count(user_id)` - Count FAQs

#### Step 1.3: Create Admin Blueprint
**File**: `blueprints/admin.py` (new)
Routes:
- `GET /admin/dashboard` - Admin dashboard page
- `GET /api/admin/users` - Get all users (JSON)
- `GET /api/admin/stats` - Get system statistics (JSON)
- `GET /api/admin/user/<user_id>/stats` - Get user-specific stats (JSON)

#### Step 1.4: Create Admin Dashboard Template
**File**: `templates/admin/dashboard.html` (new)
Features:
- Total users count
- Total files uploaded (all users)
- Total URLs crawled (all users)
- Total FAQs created
- User list with:
  - Username/Email
  - Registration date
  - Files uploaded count
  - URLs crawled count
  - FAQs count
  - Last login
- Charts/graphs (optional, future enhancement)

#### Step 1.5: Update Navigation
**File**: `templates/dashboard/dashboard.html`
- Add admin dashboard link (only visible to admins)
- Check: `{% if current_user.is_admin() %}`

### Phase 2: OTP Verification (Priority 2)

#### Step 2.1: Create OTP Model
**File**: `models/otp.py` (new)
- Table: `otp_verifications`
- Fields: `id`, `user_id`, `email`, `otp_code`, `purpose` (registration/forgot-password), `expires_at`, `verified`, `created_at`
- Methods: `create_otp()`, `verify_otp()`, `is_expired()`, `cleanup_expired()`

#### Step 2.2: Create OTP Service
**File**: `services/otp_service.py` (new)
- `generate_otp()` - Generate 6-digit OTP
- `send_otp_email(email, otp_code)` - Send OTP via email
- `verify_otp(email, otp_code, purpose)` - Verify OTP
- `resend_otp(email, purpose)` - Resend OTP

#### Step 2.3: Update Registration Flow
**File**: `blueprints/auth.py`
- After successful registration:
  1. Create user (status: unverified)
  2. Generate OTP
  3. Send OTP email
  4. Redirect to OTP verification page
- Add route: `POST /verify-otp` - Verify OTP
- Add route: `POST /resend-otp` - Resend OTP
- After OTP verification:
  1. Mark user as verified
  2. Auto-login user
  3. Redirect to dashboard

#### Step 2.4: Update Registration Template
**File**: `templates/auth/register.html`
- Add OTP verification step (initially hidden)
- Add "Resend OTP" button
- Add countdown timer for OTP expiration
- Show success message after verification

#### Step 2.5: Update Email Utils
**File**: `utils/email_utils.py`
- Add `send_otp_email(email, otp_code)` function
- Use existing SMTP configuration

---

## Database Changes

### New Table: `otp_verifications`
```sql
CREATE TABLE otp_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK(purpose IN ('registration', 'forgot_password', 'email_change')),
    expires_at DATETIME NOT NULL,
    verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_otp_email ON otp_verifications(email);
CREATE INDEX idx_otp_code ON otp_verifications(otp_code);
CREATE INDEX idx_otp_expires ON otp_verifications(expires_at);
```

### Optional: Add to `users` table (for future)
```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN verified_at DATETIME;
```

---

## API Endpoints Summary

### Admin Endpoints:
- `GET /admin/dashboard` - Admin dashboard page
- `GET /api/admin/users` - Get all users with stats
- `GET /api/admin/stats` - Get system-wide statistics
- `GET /api/admin/user/<user_id>/stats` - Get user-specific stats

### OTP Endpoints:
- `POST /api/verify-otp` - Verify OTP code
- `POST /api/resend-otp` - Resend OTP email

---

## Security Considerations

1. **Admin Routes**:
   - All admin routes must use `@admin_required` decorator
   - Verify admin role on every request
   - Rate limit admin API endpoints

2. **OTP Security**:
   - OTP expires after 10-15 minutes
   - OTP is 6 digits (random)
   - Limit OTP resend attempts (e.g., 3 per hour per email)
   - Clean up expired OTPs regularly
   - Store OTP hashed (optional, but recommended)

3. **Data Privacy**:
   - Admin dashboard should not expose sensitive user data
   - Only show aggregated statistics
   - User list should not show passwords or API keys

---

## Implementation Order

### Recommended Sequence:
1. ✅ Create admin decorator (`decorators.py`)
2. ✅ Create admin service (`services/admin_service.py`)
3. ✅ Create admin blueprint (`blueprints/admin.py`)
4. ✅ Create admin dashboard template (`templates/admin/dashboard.html`)
5. ✅ Update navigation to show admin link
6. ✅ Test admin dashboard
7. ✅ Create OTP model (`models/otp.py`)
8. ✅ Create OTP service (`services/otp_service.py`)
9. ✅ Update registration flow with OTP
10. ✅ Update registration template
11. ✅ Test OTP flow

---

## Estimated Impact

### Files to Create: ~10 files
### Files to Modify: ~5 files
### Database Changes: 1 new table (+ optional user table columns)
### Testing Required: Admin dashboard, OTP verification flow

---

## Future Enhancements (Not in Scope Now)

1. User management (edit/delete users) from admin dashboard
2. Email verification badge in user profile
3. OTP for password reset
4. OTP for email change
5. Admin activity logs
6. User activity tracking
7. Advanced charts/graphs for statistics
8. Export statistics to CSV/PDF

