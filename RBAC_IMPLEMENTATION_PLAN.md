# RBAC Implementation Plan

## Overview
Implement Role-Based Access Control (RBAC) system with Admin Dashboard and OTP verification.

---

## Current Status

### ✅ Already Implemented:
- User model has `role` field (`'admin'`, `'user'`, `'viewer'`)
- `is_admin()`, `is_user()`, `is_viewer()` methods exist
- Database schema supports roles
- `@login_required` decorator used extensively

### ❌ Missing:
- `@admin_required` decorator
- Admin dashboard routes/blueprints
- Admin statistics API endpoints
- Admin dashboard UI
- OTP verification system

---

## Implementation Phases

### Phase 1: Admin Authorization (Priority 1)
**Goal**: Protect admin routes and create admin decorator

**Tasks:**
1. Create `decorators.py` with `@admin_required` decorator
2. Test decorator with existing routes
3. Update navigation to show admin link (only for admins)

**Files to Create:**
- `decorators.py`

**Files to Modify:**
- `templates/dashboard/dashboard.html` (add admin link)

**Estimated Time**: 30 minutes

---

### Phase 2: Admin Service Layer (Priority 1)
**Goal**: Create service for admin statistics and user management

**Tasks:**
1. Create `services/admin_service.py`
2. Implement functions:
   - `get_all_users()` - Get all users with stats
   - `get_user_stats(user_id)` - Get user-specific stats
   - `get_system_stats()` - Get overall system statistics
   - `get_user_files_count(user_id)` - Count uploaded files
   - `get_user_crawls_count(user_id)` - Count crawled URLs
   - `get_user_faqs_count(user_id)` - Count FAQs

**Files to Create:**
- `services/admin_service.py`

**Files to Modify:**
- None (new service)

**Estimated Time**: 1-2 hours

---

### Phase 3: Admin API Endpoints (Priority 1)
**Goal**: Create REST API for admin dashboard data

**Tasks:**
1. Create `blueprints/admin.py`
2. Implement routes:
   - `GET /admin/dashboard` - Admin dashboard page
   - `GET /api/admin/users` - Get all users with stats (JSON)
   - `GET /api/admin/stats` - Get system statistics (JSON)
   - `GET /api/admin/user/<user_id>/stats` - Get user-specific stats (JSON)
3. Register blueprint in `app.py`
4. Add `@admin_required` to all admin routes

**Files to Create:**
- `blueprints/admin.py`

**Files to Modify:**
- `app.py` (register admin blueprint)

**Estimated Time**: 2-3 hours

---

### Phase 4: Admin Dashboard UI (Priority 1)
**Goal**: Create admin dashboard interface

**Tasks:**
1. Create `templates/admin/dashboard.html`
2. Create `static/v2/js/admin-dashboard.js`
3. Implement features:
   - Total users count
   - Total files uploaded (all users)
   - Total URLs crawled (all users)
   - Total FAQs created
   - User list table with:
     - Username/Email
     - Registration date
     - Files uploaded count
     - URLs crawled count
     - FAQs count
     - Last login
     - Status (active/inactive)
4. Add styling (extend existing dashboard.css)

**Files to Create:**
- `templates/admin/dashboard.html`
- `static/v2/js/admin-dashboard.js`

**Files to Modify:**
- `static/v2/css/dashboard.css` (add admin styles if needed)

**Estimated Time**: 3-4 hours

---

### Phase 5: OTP Database Schema (Priority 2)
**Goal**: Create OTP verification table

**Tasks:**
1. Create migration script for `otp_verifications` table
2. Test migration on local database
3. Document migration process

**Files to Create:**
- `migrations/create_otp_table.py` (or add to existing migration)

**Files to Modify:**
- None (new table)

**Estimated Time**: 30 minutes

---

### Phase 6: OTP Model (Priority 2)
**Goal**: Create OTP database model

**Tasks:**
1. Create `models/otp.py`
2. Implement methods:
   - `create_otp(user_id, email, purpose)` - Create OTP
   - `verify_otp(email, otp_code, purpose)` - Verify OTP
   - `is_expired(otp_id)` - Check expiration
   - `cleanup_expired()` - Remove expired OTPs
   - `get_otp_by_code(otp_code)` - Get OTP by code

**Files to Create:**
- `models/otp.py`

**Files to Modify:**
- None (new model)

**Estimated Time**: 1 hour

---

### Phase 7: OTP Service (Priority 2)
**Goal**: Create OTP generation and email sending service

**Tasks:**
1. Create `services/otp_service.py`
2. Implement functions:
   - `generate_otp()` - Generate 6-digit random OTP
   - `send_otp_email(email, otp_code, purpose)` - Send OTP via email
   - `verify_otp(email, otp_code, purpose)` - Verify OTP code
   - `resend_otp(email, purpose)` - Resend OTP
   - `cleanup_expired_otps()` - Clean up expired OTPs
3. Integrate with email service (SendGrid or SMTP)

**Files to Create:**
- `services/otp_service.py`

**Files to Modify:**
- `utils/email_utils.py` (add OTP email template)

**Estimated Time**: 2 hours

---

### Phase 8: OTP Registration Flow (Priority 2)
**Goal**: Integrate OTP into registration process

**Tasks:**
1. Update `blueprints/auth.py`:
   - Modify registration to generate OTP
   - Add OTP verification route
   - Add resend OTP route
   - Update registration flow:
     - User registers → OTP generated → Email sent → User verifies → Account activated
2. Update `templates/auth/register.html`:
   - Add OTP verification step (initially hidden)
   - Add "Resend OTP" button
   - Add countdown timer for expiration
   - Show success message after verification

**Files to Modify:**
- `blueprints/auth.py`
- `templates/auth/register.html`
- `static/v2/js/auth.js` (if exists, or create)

**Estimated Time**: 3-4 hours

---

## Implementation Order

### Week 1: Admin Dashboard (Priority 1)
1. ✅ Phase 1: Admin Authorization (30 min)
2. ✅ Phase 2: Admin Service Layer (1-2 hours)
3. ✅ Phase 3: Admin API Endpoints (2-3 hours)
4. ✅ Phase 4: Admin Dashboard UI (3-4 hours)

**Total: ~7-10 hours**

### Week 2: OTP System (Priority 2)
5. ✅ Phase 5: OTP Database Schema (30 min)
6. ✅ Phase 6: OTP Model (1 hour)
7. ✅ Phase 7: OTP Service (2 hours)
8. ✅ Phase 8: OTP Registration Flow (3-4 hours)

**Total: ~6-8 hours**

---

## File Structure

```
chatbot/
├── decorators.py                    # NEW - Admin decorator
├── services/
│   ├── admin_service.py            # NEW - Admin statistics
│   └── otp_service.py               # NEW - OTP management
├── models/
│   └── otp.py                       # NEW - OTP model
├── blueprints/
│   ├── admin.py                     # NEW - Admin routes
│   └── auth.py                      # MODIFY - Add OTP flow
├── templates/
│   ├── admin/
│   │   └── dashboard.html           # NEW - Admin dashboard
│   └── auth/
│       └── register.html            # MODIFY - Add OTP step
├── static/v2/
│   ├── js/
│   │   └── admin-dashboard.js       # NEW - Admin dashboard JS
│   └── css/
│       └── dashboard.css            # MODIFY - Add admin styles
└── migrations/
    └── create_otp_table.py          # NEW - OTP migration
```

---

## Testing Checklist

### Admin Dashboard:
- [ ] Admin can access `/admin/dashboard`
- [ ] Non-admin users cannot access admin routes
- [ ] Admin dashboard shows correct user counts
- [ ] Admin dashboard shows correct file/URL/FAQ counts
- [ ] User list displays correctly
- [ ] Statistics are accurate

### OTP System:
- [ ] OTP is generated on registration
- [ ] OTP email is sent successfully
- [ ] OTP verification works
- [ ] Expired OTPs are rejected
- [ ] Resend OTP works
- [ ] User cannot login without OTP verification
- [ ] OTP cleanup works (expired OTPs removed)

---

## Security Considerations

1. **Admin Routes**:
   - All admin routes must use `@admin_required`
   - Verify admin role on every request
   - Rate limit admin API endpoints

2. **OTP Security**:
   - OTP expires after 10-15 minutes
   - OTP is 6 digits (random)
   - Limit OTP resend attempts (3 per hour per email)
   - Clean up expired OTPs regularly
   - Store OTP hashed (optional but recommended)

3. **Data Privacy**:
   - Admin dashboard should not expose sensitive user data
   - Only show aggregated statistics
   - User list should not show passwords or API keys

---

## Next Steps

1. **Start with Phase 1**: Create admin decorator
2. **Continue with Phase 2-4**: Build admin dashboard
3. **Then Phase 5-8**: Implement OTP system

Let's begin!

