# API Key System - User Isolation

## ✅ Problem Solved

**Before:** All users shared the same embed script, causing chatbot confusion.

**After:** Each user gets a **unique API key** that isolates their chatbot completely.

## 🔑 How It Works

### 1. **API Key Generation**
- Each user gets a unique API key when they first access their chatbot config
- Stored in: `config/user_{id}/chatbot_config.json`
- Format: Secure random token (32 characters, URL-safe)

### 2. **Unique Embed Script**
Each user's embed script includes their unique API key:

```html
<script>
    (function() {
        var d = document, s = d.createElement('script');
        s.src = 'http://localhost:6001/embed.js?api_key=USER_UNIQUE_KEY_HERE';
        s.async = 1;
        d.getElementsByTagName('head')[0].appendChild(s);
    })();
</script>
```

### 3. **User Isolation Flow**

```
User A's Website
    ↓
Pastes script with api_key=USER_A_KEY
    ↓
/embed.js?api_key=USER_A_KEY
    ↓
Validates API key → Returns User A's chatbot
    ↓
Widget uses User A's:
    - Chatbot name
    - Prompt
    - Knowledge base
    - Settings

User B's Website
    ↓
Pastes script with api_key=USER_B_KEY
    ↓
/embed.js?api_key=USER_B_KEY
    ↓
Validates API key → Returns User B's chatbot
    ↓
Widget uses User B's:
    - Chatbot name
    - Prompt
    - Knowledge base
    - Settings
```

## 🔒 Security Features

### API Key Validation
- **Location**: `app.py` → `validate_api_key(api_key)`
- **Method**: Searches all user configs to find matching API key
- **Returns**: `user_id` if valid, `None` if invalid

### Endpoints Protected by API Key

1. **`/embed.js?api_key=XXX`**
   - Validates API key
   - Returns user-specific embed script
   - Error if invalid/missing

2. **`/widget?api_key=XXX`**
   - Validates API key
   - Returns user-specific widget HTML
   - Error if invalid/missing

3. **`/chat` (POST)**
   - Accepts API key in JSON body or header
   - Falls back to login if no API key
   - Uses user_id from API key validation

## 📋 Implementation Details

### API Key Functions

```python
# Generate new API key
generate_user_api_key(user_id) → (token, hash)

# Get or create API key for user
get_user_api_key(user_id) → api_key

# Validate API key
validate_api_key(api_key) → user_id or None

# Load user config (includes API key)
load_user_chatbot_config(user_id) → config dict
```

### Config File Structure

```json
{
  "bot_name": "MyChatbot",
  "prompt": "You are MyChatbot...",
  "api_key": "abc123xyz...",
  "api_key_hash": "sha256_hash..."
}
```

## 🎯 User Experience

### For Users (Dashboard)
1. Go to **Widget Integration** tab
2. See their unique embed script (auto-generated with API key)
3. Copy and paste on their website
4. Widget automatically uses their chatbot

### For Website Visitors
1. Visit website with embedded chatbot
2. Widget loads with correct chatbot name
3. Chat uses correct knowledge base
4. No confusion between different users' chatbots

## ⚠️ Important Notes

1. **API Key Security**
   - API keys are stored in plain text in config files (for now)
   - Consider encrypting in production
   - Consider API key rotation feature

2. **Key Regeneration**
   - Currently, keys are generated once and persist
   - Future: Add "Regenerate API Key" button in dashboard

3. **Key Exposure**
   - API keys are visible in embed script (in HTML source)
   - This is acceptable for public widget usage
   - Keys only identify which chatbot to use (not sensitive data)

4. **Rate Limiting** (Future)
   - Consider rate limiting per API key
   - Prevent abuse of chatbot endpoints

## 🧪 Testing

### Test User Isolation

1. **Create User A**
   - Login as User A
   - Set chatbot name: "SupportBot"
   - Get embed script with API key A

2. **Create User B**
   - Login as User B
   - Set chatbot name: "HelpBot"
   - Get embed script with API key B

3. **Test Both**
   - Paste User A's script on website A
   - Paste User B's script on website B
   - Verify each shows correct chatbot name
   - Verify each uses correct knowledge base

### Test API Key Validation

```bash
# Valid API key
curl "http://localhost:6001/embed.js?api_key=VALID_KEY"

# Invalid API key
curl "http://localhost:6001/embed.js?api_key=INVALID_KEY"
# Should return error script

# Missing API key
curl "http://localhost:6001/embed.js"
# Should return error script
```

## 📚 Related Files

- API Key Functions: `app.py` (lines ~700-800)
- Embed Endpoint: `app.py` → `/embed.js`
- Widget Endpoint: `app.py` → `/widget`
- Chat Endpoint: `app.py` → `/chat`
- Integration Tab: `static/v2/js/dashboard-system.js` → `updateIntegrationSnippet()`
- Config Storage: `config/user_{id}/chatbot_config.json`

## 🔮 Future Enhancements

1. **API Key Management**
   - Regenerate key button
   - Key expiration dates
   - Multiple keys per user

2. **Enhanced Security**
   - Key encryption at rest
   - Key rotation policies
   - Usage analytics per key

3. **Rate Limiting**
   - Per-API-key rate limits
   - Abuse detection
   - Usage quotas

---

**Status**: ✅ Implemented and Working
**Last Updated**: Phase 1 - User Isolation Fix

