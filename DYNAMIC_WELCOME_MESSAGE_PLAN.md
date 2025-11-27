# Dynamic Welcome Message Implementation Plan

## Overview
Make the chatbot welcome message dynamic based on user's saved settings:
- Bot name (from chatbot config)
- Avatar (from appearance settings)
- Welcome message (based on persona/prompt preset)

## Current State Analysis

### 1. Welcome Message Location
- **File**: `static/embed.js` (line 435)
- **Current**: Hardcoded as `"Hi! I'm ${botName}, your intelligent AI assistant. How can I help you today?"`
- **Avatar**: Uses UI Avatars API with bot name (line 431)

### 2. Widget Configuration Flow
- **Route**: `/widget` in `blueprints/widget.py`
- **Template**: `templates/widget/widget_embed.html`
- **Config Passed**: bot_name, avatar, primary_color, suggested messages
- **JavaScript Config**: `window.CHATBOT_CONFIG` set in widget_embed.html

### 3. Persona/Preset System
- **Model**: `models/prompt_preset.py`
- **Presets Available**:
  - Virtual Assistant (id: 1, slug: 'virtual_assistant')
  - Tech Support (id: 2, slug: 'tech_support')
  - Sales Agent (id: 3, slug: 'sales_agent')
  - Customer Service (id: 4, slug: 'customer_service')
  - Educator (id: 5, slug: 'educator')
- **User Config**: `prompt_preset_id` stored in chatbot_config.json

## Implementation Plan

### Phase 1: Backend - Get Persona Info
**File**: `blueprints/widget.py`

1. **Get prompt_preset_id from user config**
   ```python
   prompt_preset_id = user_config.get('prompt_preset_id')
   ```

2. **Fetch preset details**
   ```python
   from models.prompt_preset import PromptPreset
   preset = PromptPreset.get_by_id(prompt_preset_id) if prompt_preset_id else None
   persona_name = preset.get('name') if preset else 'Virtual Assistant'
   ```

3. **Generate welcome message based on persona**
   - Create mapping function: `get_welcome_message(bot_name, persona_name)`
   - Map persona types to appropriate messages:
     - Sales Agent → "Hi! I'm {bot_name}, your intelligent AI sales representative. How can I help you today?"
     - Tech Support → "Hi! I'm {bot_name}, your technical support specialist. How can I assist you today?"
     - Customer Service → "Hi! I'm {bot_name}, your customer service representative. How can I help you today?"
     - Educator → "Hi! I'm {bot_name}, your educational assistant. How can I help you learn today?"
     - Virtual Assistant (default) → "Hi! I'm {bot_name}, your intelligent AI assistant. How can I help you today?"

4. **Build avatar URL**
   - Check appearance settings for avatar type
   - If preset: `/static/img/avatar/avatar_{value}.png`
   - If custom: use custom URL
   - If ui-avatars: build URL with bot_name and primary_color

### Phase 2: Pass Config to Template
**File**: `blueprints/widget.py` → `widget_embed.html`

1. **Add to render_template**:
   ```python
   welcome_message = get_welcome_message(bot_name, persona_name)
   avatar_url = build_avatar_url(avatar, bot_name, primary_color)
   ```

2. **Pass to template**:
   ```python
   return render_template("widget/widget_embed.html",
       ...
       welcome_message=welcome_message,
       avatar_url=avatar_url
   )
   ```

### Phase 3: Update Template
**File**: `templates/widget/widget_embed.html`

1. **Add to CHATBOT_CONFIG**:
   ```javascript
   window.CHATBOT_CONFIG = {
       botName: '{{ bot_name }}',
       avatarUrl: '{{ avatar_url }}',
       welcomeMessage: '{{ welcome_message }}',
       ...
   };
   ```

### Phase 4: Update JavaScript
**File**: `static/embed.js`

1. **Update showWelcomeMessage()** (line 414):
   ```javascript
   const botName = window.CHATBOT_CONFIG?.botName || WIDGET_CONFIG.botName || 'Cortex';
   const avatarUrl = window.CHATBOT_CONFIG?.avatarUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(botName)}&background=667eea&color=fff&size=40&rounded=true`;
   const welcomeMessage = window.CHATBOT_CONFIG?.welcomeMessage || `Hi! I'm ${botName}, your intelligent AI assistant. How can I help you today?`;
   ```

2. **Update avatar in welcome message**:
   ```javascript
   <img src="${avatarUrl}" alt="${botName}" class="bobot-welcome-avatar">
   ```

3. **Update welcome message text**:
   ```javascript
   <p>${welcomeMessage}</p>
   ```

## Files to Modify

1. ✅ `blueprints/widget.py` - Add persona detection and welcome message generation
2. ✅ `templates/widget/widget_embed.html` - Pass welcome_message and avatar_url to JS
3. ✅ `static/embed.js` - Use dynamic welcome message and avatar

## Testing Checklist

- [ ] Sales Agent persona shows "sales representative" message
- [ ] Tech Support persona shows "technical support specialist" message
- [ ] Customer Service persona shows "customer service representative" message
- [ ] Educator persona shows "educational assistant" message
- [ ] Virtual Assistant (default) shows "AI assistant" message
- [ ] Avatar displays correctly (preset, custom, or ui-avatars)
- [ ] Bot name is dynamic
- [ ] Welcome message appears in widget preview

## Example Welcome Messages

| Persona | Welcome Message |
|---------|----------------|
| Sales Agent | "Hi! I'm {bot_name}, your intelligent AI sales representative. How can I help you today?" |
| Tech Support | "Hi! I'm {bot_name}, your technical support specialist. How can I assist you today?" |
| Customer Service | "Hi! I'm {bot_name}, your customer service representative. How can I help you today?" |
| Educator | "Hi! I'm {bot_name}, your educational assistant. How can I help you learn today?" |
| Virtual Assistant | "Hi! I'm {bot_name}, your intelligent AI assistant. How can I help you today?" |

