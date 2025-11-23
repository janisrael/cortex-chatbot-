# 💳 Payment & Subscription System Plan

**Version:** 1.0  
**Date:** 2025-11-23  
**Status:** Planning

---

## 🎯 Overview

Implement a subscription-based payment system that:
1. Allows users to subscribe to different tiers
2. Automatically provisions OpenAI API keys when users subscribe to OpenAI-enabled plans
3. Manages subscription lifecycle (active, cancelled, expired)
4. Integrates with current LLM selection system

---

## 📋 Subscription Tiers

### Tier 1: Free Tier (Demo/Trial)
- **Price:** $0/month
- **Features:**
  - **No LLM access** (read-only mode)
  - Limited knowledge base (5 files max, testing only)
  - View-only dashboard
  - 10 demo API calls/month
  - Community support
  - **Purpose:** Marketing tool to showcase features before subscription
- **Note:** Ollama removed - too resource-intensive for hosting. Free tier is now a demo/trial tier.

### Tier 2: Starter
- **Price:** $9.99/month
- **Features:**
  - OpenAI GPT-4o-mini (auto-provisioned API key)
  - Unlimited knowledge base
  - Standard chatbot features
  - Email support

### Tier 3: Professional
- **Price:** $29.99/month
- **Features:**
  - Choice of LLM: OpenAI GPT-4o-mini, Claude, Gemini, or DeepSeek
  - Auto-provisioned API keys for selected provider
  - Unlimited knowledge base
  - Advanced features (analytics, custom branding)
  - Priority support

### Tier 4: Enterprise
- **Price:** $99.99/month
- **Features:**
  - All LLM providers (multiple keys)
  - Unlimited everything
  - Custom integrations
  - Dedicated support
  - SLA guarantee

---

## 🏗️ Architecture

### Database Schema

#### `subscriptions` Table
```sql
CREATE TABLE subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    tier VARCHAR(50) NOT NULL,  -- 'free', 'starter', 'professional', 'enterprise'
    status ENUM('active', 'cancelled', 'expired', 'trial') DEFAULT 'trial',
    payment_provider VARCHAR(50),  -- 'stripe', 'paypal'
    payment_subscription_id VARCHAR(255),  -- External subscription ID
    current_period_start DATETIME,
    current_period_end DATETIME,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    trial_end DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

#### `api_keys_provisioned` Table
```sql
CREATE TABLE api_keys_provisioned (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- 'openai', 'anthropic', 'google', 'deepseek'
    api_key VARCHAR(255) NOT NULL,  -- Encrypted
    api_key_hash VARCHAR(255),  -- For verification
    status ENUM('active', 'expired', 'revoked') DEFAULT 'active',
    usage_limit DECIMAL(10,2) NULL,  -- Monthly limit in USD
    current_usage DECIMAL(10,2) DEFAULT 0,  -- Current month usage
    provisioned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_provider (user_id, provider),
    INDEX idx_status (status)
);
```

#### `payment_transactions` Table
```sql
CREATE TABLE payment_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    subscription_id INT,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_provider VARCHAR(50),
    transaction_id VARCHAR(255),
    status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    metadata JSON,  -- Store additional payment data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

---

## 💰 Payment Provider Integration

### Option 1: Stripe (Recommended)
**Pros:**
- Excellent API and documentation
- Webhook support for subscription events
- Handles recurring payments automatically
- Strong security and compliance
- Supports multiple payment methods

**Cons:**
- Transaction fees (2.9% + $0.30 per transaction)
- Requires Stripe account setup

### Option 2: PayPal
**Pros:**
- Widely recognized
- Good for international payments
- Lower fees for some regions

**Cons:**
- More complex webhook handling
- Less developer-friendly API

### Recommendation: **Stripe**

---

## 🔑 OpenAI API Key Auto-Provisioning

### Approach 1: Master API Key Pool (Recommended)
**How it works:**
1. System maintains a pool of OpenAI API keys (purchased in bulk)
2. When user subscribes, assign them a key from the pool
3. Monitor usage per key
4. Rotate keys if usage limits are reached

**Pros:**
- Immediate provisioning
- Better cost control
- Can monitor usage centrally

**Cons:**
- Requires upfront investment in API keys
- Need to manage key rotation

### Approach 2: Direct OpenAI Account Creation
**How it works:**
1. User subscribes
2. System creates OpenAI account for user (via API if available)
3. System provisions API key
4. User gets their own OpenAI account

**Pros:**
- User owns their account
- Better isolation

**Cons:**
- OpenAI may not have account creation API
- More complex implementation

### Approach 3: Stripe + OpenAI Partnership
**How it works:**
1. Use Stripe's OpenAI integration (if available)
2. Stripe handles billing and OpenAI provisioning

**Pros:**
- Simplified integration
- Handled by payment provider

**Cons:**
- May not be available
- Less control

### **Recommended: Approach 1 (Master API Key Pool)**

---

## 🔄 User Flow

### Subscription Flow
1. User selects subscription tier
2. User enters payment details (Stripe Checkout)
3. Payment processed
4. Webhook received → Create subscription record
5. **Auto-provision OpenAI API key** (if tier requires it)
6. Update user's LLM config with provisioned key
7. User can immediately use OpenAI model

### Auto-Provisioning Flow
```
User Subscribes (Starter/Professional/Enterprise)
    ↓
Payment Successful (Webhook)
    ↓
Check Subscription Tier
    ↓
If OpenAI-enabled tier:
    ├─ Check if user already has OpenAI key
    ├─ If not, assign key from pool
    ├─ Store in api_keys_provisioned table
    ├─ Update user's chatbot_config.json
    └─ Enable OpenAI in LLM selection
    ↓
If other LLM providers:
    ├─ Provision API key for selected provider
    └─ Update user config
```

### Usage Monitoring
1. Track API calls per user
2. Monitor usage against limits
3. Alert if approaching limits
4. Auto-upgrade option if limit reached

---

## 🛠️ Implementation Plan

### Phase 1: Database & Models (Week 1)
- [ ] Create database migrations for subscription tables
- [ ] Create Subscription model
- [ ] Create ApiKeyProvisioned model
- [ ] Create PaymentTransaction model
- [ ] Add subscription status to User model

### Phase 2: Stripe Integration (Week 2)
- [ ] Set up Stripe account and API keys
- [ ] Create Stripe products and prices
- [ ] Implement Stripe Checkout
- [ ] Create webhook endpoint for Stripe events
- [ ] Handle subscription events (created, updated, cancelled, payment_succeeded, payment_failed)

### Phase 3: OpenAI Key Pool Management (Week 2-3)
- [ ] Create OpenAI API key pool system
- [ ] Implement key assignment logic
- [ ] Create key rotation mechanism
- [ ] Implement usage tracking
- [ ] Create admin interface for key management

### Phase 4: Auto-Provisioning Logic (Week 3)
- [ ] Create provisioning service
- [ ] Integrate with subscription webhook
- [ ] Auto-assign API keys on subscription
- [ ] Update user's LLM config automatically
- [ ] Handle key revocation on cancellation

### Phase 5: UI/UX (Week 4)
- [ ] Create subscription selection page
- [ ] Create billing/payment page
- [ ] Add subscription status to dashboard
- [ ] Create usage dashboard
- [ ] Add upgrade/downgrade UI

### Phase 6: Additional LLM Providers (Week 5)
- [ ] Claude (Anthropic) integration
- [ ] Gemini (Google) integration
- [ ] DeepSeek integration
- [ ] Provider selection UI
- [ ] Multi-provider key management

### Phase 7: Testing & Security (Week 6)
- [ ] Test subscription flows
- [ ] Test webhook handling
- [ ] Test API key provisioning
- [ ] Security audit (encrypt API keys)
- [ ] Load testing

---

## 🔐 Security Considerations

### API Key Storage
- **Encrypt API keys** at rest (use encryption library)
- Store encrypted keys in database
- Never log API keys
- Use environment variables for master keys

### Payment Security
- Use Stripe's secure checkout (no card data on our servers)
- Validate webhook signatures
- Implement idempotency for webhooks
- Rate limit webhook endpoints

### Access Control
- Verify subscription status before API calls
- Check usage limits before each request
- Implement rate limiting per user
- Monitor for abuse

---

## 📊 Usage Tracking

### Metrics to Track
- API calls per user
- Cost per user (based on provider pricing)
- Token usage (if available)
- Response times
- Error rates

### Alerts
- Usage approaching limit (80%, 90%, 100%)
- Payment failures
- Subscription expiring soon
- API key issues

---

## 💡 OpenAI Key Pool Management

### Initial Setup
1. Purchase OpenAI API keys in bulk (e.g., $1000 worth)
2. Store keys securely (encrypted)
3. Create pool management system

### Key Assignment Strategy
- Round-robin assignment
- Or assign based on expected usage
- Monitor usage per key
- Rotate if key hits limit

### Cost Management
- Track cost per user
- Set usage limits per tier
- Auto-upgrade if user exceeds limit
- Alert admins if pool is running low

---

## 🔄 Subscription Lifecycle

### States
1. **Trial** - User in trial period (e.g., 7 days)
2. **Active** - Subscription active, payment successful
3. **Cancelled** - User cancelled, but still has access until period end
4. **Expired** - Subscription expired, no access

### Transitions
- Trial → Active (payment successful)
- Active → Cancelled (user cancels)
- Cancelled → Expired (period ends)
- Expired → Active (user resubscribes)

### Actions on State Change
- **Active:** Provision API keys, enable features
- **Cancelled:** Mark for expiration, notify user
- **Expired:** Revoke API keys, disable features, downgrade to free tier

---

## 📝 API Endpoints Needed

### Subscription Management
- `POST /api/subscription/subscribe` - Create subscription
- `GET /api/subscription/status` - Get user's subscription status
- `POST /api/subscription/cancel` - Cancel subscription
- `POST /api/subscription/upgrade` - Upgrade tier
- `POST /api/subscription/downgrade` - Downgrade tier

### Webhooks
- `POST /api/webhooks/stripe` - Stripe webhook handler
- `POST /api/webhooks/paypal` - PayPal webhook handler (if used)

### API Key Management
- `GET /api/keys/provisioned` - Get user's provisioned keys
- `POST /api/keys/revoke` - Revoke a key (admin)
- `GET /api/keys/usage` - Get usage statistics

---

## 🎨 UI Components Needed

### Subscription Page
- Tier comparison table
- "Select Plan" buttons
- Feature list per tier
- Pricing display

### Billing Dashboard
- Current subscription status
- Usage statistics
- Payment history
- Upgrade/downgrade options
- Cancel subscription

### LLM Selection (Enhanced)
- Show available providers based on subscription
- Display provisioned keys status
- Show usage limits
- Provider selection dropdown

---

## 💰 Cost Structure

### Revenue Model
- Subscription fees (primary)
- Usage-based overage (optional)
- Enterprise custom pricing

### Cost Management
- OpenAI API costs (passed through or absorbed)
- Payment processing fees (Stripe: 2.9% + $0.30)
- Infrastructure costs
- Support costs

### Pricing Strategy
- Free tier: Loss leader (Ollama only, no API costs)
- Starter: Break even or small profit
- Professional: Good margin
- Enterprise: High margin

---

## 🚀 Quick Start Implementation

### Step 1: Set Up Stripe
1. Create Stripe account
2. Get API keys (test and live)
3. Create products and prices in Stripe dashboard
4. Set up webhook endpoint

### Step 2: Database Setup
1. Run migrations for subscription tables
2. Seed initial subscription tiers
3. Set up encryption for API keys

### Step 3: Basic Subscription Flow
1. Create subscription selection page
2. Implement Stripe Checkout
3. Create webhook handler
4. Test subscription creation

### Step 4: OpenAI Key Pool
1. Purchase initial OpenAI credits
2. Create key pool management
3. Implement key assignment
4. Test provisioning

### Step 5: Integration
1. Connect subscription to LLM selection
2. Auto-provision on subscription
3. Update user config
4. Test end-to-end flow

---

## 📋 Checklist

### Pre-Launch
- [ ] Stripe account set up
- [ ] Database migrations created
- [ ] Webhook endpoints secured
- [ ] API key encryption implemented
- [ ] Usage tracking in place
- [ ] Email notifications configured
- [ ] Terms of Service and Privacy Policy
- [ ] Refund policy defined

### Post-Launch
- [ ] Monitor subscription conversions
- [ ] Track API usage and costs
- [ ] Handle payment failures
- [ ] Customer support process
- [ ] Regular cost analysis

---

## 🔮 Future Enhancements

1. **Usage Analytics Dashboard**
   - Detailed usage charts
   - Cost breakdown
   - Predictive analytics

2. **Multi-Currency Support**
   - Support different currencies
   - Localized pricing

3. **Annual Plans**
   - Discounted annual subscriptions
   - Better cash flow

4. **Team/Organization Plans**
   - Multiple users per subscription
   - Shared API keys
   - Team management

5. **Pay-as-You-Go Option**
   - Alternative to subscription
   - Usage-based billing

---

## 📚 Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [OpenAI Usage Limits](https://platform.openai.com/docs/guides/rate-limits)

---

**Next Steps:** Review plan, select payment provider, begin Phase 1 implementation.

