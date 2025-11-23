# Widget Integration Guide

## 📋 Overview

The Widget Integration tab provides everything you need to integrate your chatbot into any website. Since you have **1 chatbot per user**, the integration is simple - just copy and paste the code snippet!

## 🔌 How It Works

### Step 1: Copy the Integration Code

1. Go to **Dashboard → Widget Integration** tab
2. The integration code snippet is automatically generated with:
   - Your server URL (current domain)
   - Your chatbot configuration
   - No website ID needed (1 chatbot per user)

3. Click **📋 Copy Code** button

### Step 2: Paste on Your Website

Add the code snippet just before the closing `</body>` tag on any page where you want the chatbot to appear:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <!-- Your website content -->
    
    <!-- Paste the chatbot code here -->
    <script>
        (function() {
            var d = document, s = d.createElement('script');
            s.src = 'http://localhost:6001/embed.js';
            s.async = 1;
            d.getElementsByTagName('head')[0].appendChild(s);
        })();
    </script>
</body>
</html>
```

### Step 3: Test It

1. **Preview in Dashboard**: Click "🔄 Refresh" or "↗️ Open Full Preview" in the Widget Integration tab
2. **Test on Your Website**: Visit your website and look for the chat button in the bottom-right corner
3. **Visit Demo Page**: Go to `/demo` to see how it looks

## 🎯 What Gets Loaded

When the embed script loads, it automatically:
- ✅ Uses your chatbot name (from Prompt Editor)
- ✅ Uses your custom prompt (from Prompt Editor)
- ✅ Uses your knowledge base (uploaded files)
- ✅ Uses your LLM settings
- ✅ No configuration needed!

## 🔧 Current Implementation

### Integration Snippet
- **Location**: `static/v2/js/dashboard-system.js` → `updateIntegrationSnippet()`
- **Updates**: Automatically when you visit the Integration tab
- **Format**: Simple script tag that loads `/embed.js`

### Embed Script Endpoint
- **Route**: `/embed.js`
- **File**: `app.py` → `serve_embed_script_multi()`
- **Function**: Generates dynamic JavaScript that loads the widget
- **Config**: Uses user's chatbot config if logged in

### Widget Endpoint
- **Route**: `/widget`
- **File**: `app.py` → `widget_multi()`
- **Function**: Serves the widget HTML with user's config
- **Template**: `templates/widget.html`

### Demo Page
- **Route**: `/demo`
- **File**: `app.py` → `demo_chatbox()`
- **Function**: Shows preview of widget with user's chatbot name
- **Template**: `demo_chatbox.html`

## 📝 Code Flow

```
User's Website
    ↓
Pastes embed script
    ↓
Script loads /embed.js
    ↓
embed.js loads widget
    ↓
Widget uses user's config:
    - Chatbot name
    - Prompt
    - Knowledge base
    - Settings
```

## 🎨 Customization

Currently, customization is done through:
1. **Prompt Editor Tab**: Set chatbot name and prompt
2. **Knowledge Management Tab**: Upload files for knowledge base
3. **LLM Settings**: Configure AI model and settings

The widget automatically uses all these settings - no additional configuration needed!

## 🚀 Testing

### Local Testing
1. Start server: `python3 app.py`
2. Login to dashboard
3. Go to Widget Integration tab
4. Copy the code snippet
5. Create a test HTML file:
   ```html
   <!DOCTYPE html>
   <html>
   <body>
       <h1>Test Page</h1>
       <!-- Paste embed code here -->
   </body>
   </html>
   ```
6. Open the HTML file in browser
7. Chat widget should appear!

### Production Testing
1. Deploy your chatbot server
2. Update the embed script URL in Integration tab
3. Copy the updated code
4. Paste on your production website
5. Test on live site

## ⚠️ Important Notes

1. **Authentication**: The widget needs to work on external websites. Currently, `/embed.js` requires login. This might need adjustment for public websites.

2. **CORS**: Make sure CORS is configured properly in `app.py` to allow your website domain.

3. **HTTPS**: For production, use HTTPS URLs in the embed script.

4. **Domain Restrictions**: You may want to restrict which domains can use your chatbot (future enhancement).

## 🔮 Future Enhancements (See PHASE2.md)

- Multiple chatbots per user
- Custom colors and themes
- Position options (bottom-left, top-right, etc.)
- Auto-open on page load
- Custom welcome messages
- Domain whitelisting
- API key authentication for public websites

## 📚 Related Files

- Integration Tab: `templates/dashboard_v1.html` (lines 379-520)
- Integration JS: `static/v2/js/dashboard-system.js`
- Embed Endpoint: `app.py` → `/embed.js`
- Widget Endpoint: `app.py` → `/widget`
- Demo Page: `app.py` → `/demo`
- Widget Template: `templates/widget.html`

---

**Last Updated**: Phase 1 Implementation
**Status**: ✅ Working - Ready for testing

