# Appearance Tab - Comprehensive Plan & Analysis

## Overview
Create a new "Appearance" tab for chatbot customization including primary color (with gradient support), avatar management, and dynamic suggested messages.

---

## Tab Structure Decision

### ✅ Decision: Separate "Appearance" Tab
**Reasoning**:
- Better organization for future scalability
- Clear separation of concerns (Appearance vs. Personality)
- Professional structure
- Easier to find settings

**New Tab Order**:
1. Overview
2. LLM Configuration
3. Knowledge Base
4. Prompt Editor (Personality)
5. **Appearance** (NEW)
6. Widget Integration
7. System Management

---

## Feature 1: Primary Color with Gradient Support

### Current Implementation
- `primary_color` exists in backend (default: `#0891b2`)
- Used in widget for avatar background
- Hardcoded in widget code

### New Requirements
1. **Color Picker**: HTML5 color input
2. **Gradient Support**: Allow gradient colors (linear, radial)
3. **Contrast-Aware Text**: Auto-adjust text color based on background
   - Dark background → Light text (white/light gray)
   - Light background → Dark text (black/dark gray)

### Technical Implementation

#### Color Storage Format
```json
{
  "primary_color": {
    "type": "solid" | "gradient",
    "value": "#0891b2" | "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "contrast_text": "#ffffff" | "#000000"  // Auto-calculated
  }
}
```

#### Contrast Calculation Algorithm
```javascript
// Calculate relative luminance
function getLuminance(hex) {
    const rgb = hexToRgb(hex);
    const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(val => {
        val = val / 255;
        return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

// Calculate contrast ratio
function getContrast(color1, color2) {
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
}

// Determine text color
function getContrastText(backgroundColor) {
    const whiteContrast = getContrast(backgroundColor, '#ffffff');
    const blackContrast = getContrast(backgroundColor, '#000000');
    return whiteContrast > blackContrast ? '#ffffff' : '#000000';
}
```

#### Gradient Support
- **Linear Gradient**: `linear-gradient(direction, color1, color2, ...)`
- **Radial Gradient**: `radial-gradient(shape, color1, color2, ...)`
- **UI**: Gradient builder or CSS input
- **Preview**: Live preview in widget

#### Where Primary Color is Applied
1. **Widget Trigger Button** (`bot-widget-trigger`)
   - Background color
   - Border color (optional)
2. **Chatbox Header**
   - Background color
   - Text color (contrast-aware)
3. **Chatbox Buttons**
   - Primary action buttons
   - Send button
4. **Avatar Background** (if using ui-avatars)
   - Background color parameter

---

## Feature 2: Avatar Management

### Current Implementation
- Avatar generated via `ui-avatars.com` API
- Uses `bot_name` and `primary_color`
- Displayed in widget trigger button and chatbox

### New Requirements
1. **Preset Avatars** (Phase 1 - Implement First)
   - User selects from preset collection
   - Displayed in grid
   - Preview in widget
2. **Upload Avatar** (Phase 2 - UI Ready, Implementation Later)
   - File upload UI
   - Validation (format, size, dimensions)
   - Storage in `uploads/user_X/avatars/`

### Avatar Storage Format
```json
{
  "avatar": {
    "type": "preset" | "upload" | "generated",
    "value": "preset_1" | "uploads/user_2/avatars/avatar.png" | "ui-avatars",
    "fallback": "ui-avatars"  // If preset/upload fails
  }
}
```

### Avatar Display Locations
1. **Widget Trigger Button** (`bot-widget-trigger`)
   - Floating button icon
   - Size: 40-50px (circular)
2. **Chatbox Header**
   - Left side of header
   - Size: 32-40px (circular)
3. **Chat Messages** (optional)
   - Bot message avatar
   - Size: 24-32px (circular)

### Preset Avatar Implementation
- **Count**: 15-20 preset avatars
- **Format**: SVG (preferred) or PNG
- **Storage**: `static/img/avatars/preset_1.svg` to `preset_20.svg`
- **Naming**: `preset_1`, `preset_2`, ..., `preset_20`
- **Categories** (optional):
  - Robots/Tech (5)
  - Friendly Characters (5)
  - Abstract/Modern (5)
  - Professional (5)

### Upload Avatar (UI Ready, Implementation Later)
- **Accepted Formats**: PNG, JPG, SVG, WebP
- **Max Size**: 2MB
- **Recommended Dimensions**: 512x512px (square)
- **Validation**:
  - File type check
  - Size check
  - Auto-resize if too large
  - Auto-crop to square if needed
- **Storage Path**: `uploads/user_X/avatars/avatar_YYYYMMDD_HHMMSS.ext`

---

## Feature 3: Dynamic Suggested Messages

### Current Implementation
- Hardcoded in `config/constants.py` as `SUGGESTED_MESSAGES`
- Static list, same for all users
- Displayed in widget as buttons

### New Requirements
1. **Per-User Suggested Messages**
   - Each user/chatbot has their own set
   - Stored in `chatbot_config.json`
2. **CRUD Operations**
   - **Add**: Add new suggested message
   - **Remove**: Delete existing message
   - **Update**: Edit message text
   - **Reorder**: Drag-and-drop or up/down buttons
3. **Default Messages**
   - Provide 3-5 default messages on first setup
   - User can modify/remove defaults

### Storage Format
```json
{
  "suggested_messages": [
    {
      "id": "msg_1",
      "text": "What services do you offer?",
      "order": 1
    },
    {
      "id": "msg_2",
      "text": "How can I contact you?",
      "order": 2
    },
    {
      "id": "msg_3",
      "text": "Tell me more about your company",
      "order": 3
    }
  ]
}
```

### Default Suggested Messages
```javascript
const DEFAULT_SUGGESTED_MESSAGES = [
  { id: "default_1", text: "What can you help me with?", order: 1 },
  { id: "default_2", text: "Tell me more", order: 2 },
  { id: "default_3", text: "How can I get started?", order: 3 }
];
```

### UI Components
1. **List Display**
   - Editable list of messages
   - Each item: text input + delete button + drag handle
2. **Add Button**
   - Opens input field or modal
   - Adds new message to list
3. **Reorder Controls**
   - Drag-and-drop (preferred)
   - Or up/down arrow buttons
4. **Validation**
   - Max length: 50-60 characters (to fit button)
   - Min messages: 1 (at least one)
   - Max messages: 5-6 (UI space limit)

### Display in Widget
- Show first 3-5 messages (based on order)
- Horizontal scroll if more than 3
- Click sends message to chatbot

---

## Database/Config Structure

### Updated `chatbot_config.json` Structure
```json
{
  "bot_name": "Cortex",
  "short_info": "Your friendly AI assistant",
  "primary_color": {
    "type": "solid",
    "value": "#0891b2",
    "contrast_text": "#ffffff"
  },
  "avatar": {
    "type": "preset",
    "value": "preset_1",
    "fallback": "ui-avatars"
  },
  "suggested_messages": [
    {
      "id": "msg_1",
      "text": "What can you help me with?",
      "order": 1
    },
    {
      "id": "msg_2",
      "text": "Tell me more",
      "order": 2
    },
    {
      "id": "msg_3",
      "text": "How can I get started?",
      "order": 3
    }
  ],
  "prompt": "...",
  "prompt_preset_id": 1
}
```

---

## UI/UX Design

### Appearance Tab Layout
```
┌─────────────────────────────────────────────────────┐
│ Appearance                                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌─ Primary Color ─────────────────────────────────┐ │
│ │                                                   │ │
│ │ Type: ○ Solid  ● Gradient                        │ │
│ │                                                   │ │
│ │ [Color Picker: 🎨] #0891b2                       │ │
│ │                                                   │ │
│ │ Gradient Builder:                                 │ │
│ │ Direction: [135deg ▼]                            │ │
│ │ Colors: [#667eea] → [#764ba2] [+ Add Color]      │ │
│ │                                                   │ │
│ │ Preview:                                          │ │
│ │ [Button Preview] [Header Preview]                │ │
│ │ Text Color: #ffffff (Auto)                       │ │
│ └───────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─ Avatar ────────────────────────────────────────┐ │
│ │ Current Avatar: [🦾 Preview]                      │ │
│ │                                                   │ │
│ │ [Presets] [Upload] (Tabs)                        │ │
│ │                                                   │ │
│ │ Preset Grid:                                      │ │
│ │ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                   │ │
│ │ │🦾│ │🤖│ │👤│ │⭐│ │🎯│ ...                   │ │
│ │ └───┘ └───┘ └───┘ └───┘ └───┘                   │ │
│ │                                                   │ │
│ │ Upload (UI Ready):                               │ │
│ │ [Choose File] avatar.png (2MB max)               │ │
│ │ [Remove Current]                                 │ │
│ └───────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─ Suggested Messages ─────────────────────────────┐ │
│ │                                                   │ │
│ │ Default messages (customize as needed):          │ │
│ │                                                   │ │
│ │ ┌─────────────────────────────────────────────┐ │ │
│ │ │ 1. [What can you help me with?] [✏️] [🗑️] [☰]│ │ │
│ │ │ 2. [Tell me more] [✏️] [🗑️] [☰]            │ │ │
│ │ │ 3. [How can I get started?] [✏️] [🗑️] [☰]  │ │ │
│ │ └─────────────────────────────────────────────┘ │ │
│ │                                                   │ │
│ │ [+ Add Message] (Max: 6 messages)                │ │
│ │                                                   │ │
│ │ Preview:                                          │ │
│ │ [What can you help me with?] [Tell me more] ... │ │
│ └───────────────────────────────────────────────────┘ │
│                                                     │
│ [Save Appearance Settings]                          │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Tab Structure & Primary Color (Solid)
- [ ] Create new "Appearance" tab
- [ ] Add tab button to navigation
- [ ] Create `dashboard_appearance_tab.html`
- [ ] Implement solid color picker
- [ ] Implement contrast calculation
- [ ] Update widget to use new primary_color format
- [ ] Test contrast-aware text

### Phase 2: Gradient Support
- [ ] Add gradient type selector (Solid/Gradient)
- [ ] Implement gradient builder UI
- [ ] Update color storage format
- [ ] Update widget to support gradients
- [ ] Test gradient rendering

### Phase 3: Avatar Presets
- [ ] Create 15-20 preset avatar SVGs
- [ ] Store in `static/img/avatars/`
- [ ] Implement preset selection UI (grid)
- [ ] Update avatar storage format
- [ ] Update widget to use preset avatars
- [ ] Test avatar display in trigger button and chatbox

### Phase 4: Avatar Upload UI (Ready, Implementation Later)
- [ ] Add upload file input
- [ ] Add file validation UI feedback
- [ ] Add preview of uploaded avatar
- [ ] Add remove/clear button
- [ ] **Note**: Backend upload endpoint to be implemented later

### Phase 5: Dynamic Suggested Messages
- [ ] Update config service to handle `suggested_messages`
- [ ] Create default suggested messages
- [ ] Implement message list UI (editable)
- [ ] Implement add message functionality
- [ ] Implement remove message functionality
- [ ] Implement reorder functionality (drag-drop or arrows)
- [ ] Update widget to use dynamic messages
- [ ] Test message display and interaction

---

## Technical Details

### Contrast-Aware Text Implementation

#### Backend (Python)
```python
def calculate_contrast_text(background_color):
    """Calculate appropriate text color based on background"""
    # Convert hex to RGB
    rgb = hex_to_rgb(background_color)
    
    # Calculate relative luminance
    def get_luminance(val):
        val = val / 255.0
        if val <= 0.03928:
            return val / 12.92
        return ((val + 0.055) / 1.055) ** 2.4
    
    luminance = 0.2126 * get_luminance(rgb[0]) + \
                0.7152 * get_luminance(rgb[1]) + \
                0.0722 * get_luminance(rgb[2])
    
    # Return white for dark backgrounds, black for light
    return "#ffffff" if luminance < 0.5 else "#000000"
```

#### Frontend (JavaScript)
```javascript
function getContrastText(backgroundColor) {
    // Handle gradient - extract first color or average
    const color = extractColorFromGradient(backgroundColor);
    const rgb = hexToRgb(color);
    const luminance = 0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b;
    return luminance < 128 ? '#ffffff' : '#000000';
}
```

### Widget Integration Points

#### Primary Color Application
```javascript
// Widget trigger button
const triggerButton = document.querySelector('.bot-widget-trigger');
triggerButton.style.backgroundColor = primaryColor.value;
triggerButton.style.color = primaryColor.contrast_text;

// Chatbox header
const header = document.querySelector('.chatbot-header');
header.style.backgroundColor = primaryColor.value;
header.style.color = primaryColor.contrast_text;

// Buttons
const sendButton = document.querySelector('.send-button');
sendButton.style.backgroundColor = primaryColor.value;
sendButton.style.color = primaryColor.contrast_text;
```

#### Avatar Application
```javascript
// Widget trigger button
const triggerAvatar = document.querySelector('.bot-widget-trigger img');
if (avatar.type === 'preset') {
    triggerAvatar.src = `/static/img/avatars/${avatar.value}.svg`;
} else if (avatar.type === 'upload') {
    triggerAvatar.src = `/${avatar.value}`;
} else {
    // Fallback to ui-avatars
    triggerAvatar.src = `https://ui-avatars.com/api/?name=${botName}&background=${primaryColor}&color=fff&size=40`;
}

// Chatbox header avatar
const headerAvatar = document.querySelector('.chatbot-header .avatar');
// Same logic as above
```

#### Suggested Messages Application
```javascript
// Load from config
const suggestedMessages = config.suggested_messages || DEFAULT_MESSAGES;

// Render in widget
const messagesContainer = document.querySelector('.suggested-messages');
suggestedMessages.slice(0, 5).forEach(msg => {
    const button = document.createElement('button');
    button.textContent = msg.text;
    button.onclick = () => sendMessage(msg.text);
    messagesContainer.appendChild(button);
});
```

---

## API Endpoints Needed

### 1. Get Appearance Config
```
GET /api/user/appearance-config
Response: {
  "primary_color": {...},
  "avatar": {...},
  "suggested_messages": [...]
}
```

### 2. Save Appearance Config
```
POST /api/user/appearance-config
Body: {
  "primary_color": {...},
  "avatar": {...},
  "suggested_messages": [...]
}
```

### 3. Upload Avatar (Future)
```
POST /api/user/avatar/upload
Body: FormData with file
Response: {
  "avatar_path": "uploads/user_2/avatars/avatar.png"
}
```

---

## File Structure

```
chatbot/
├── templates/
│   └── components/
│       └── dashboard_appearance_tab.html (NEW)
├── static/
│   ├── img/
│   │   └── avatars/
│   │       ├── preset_1.svg (NEW)
│   │       ├── preset_2.svg (NEW)
│   │       └── ... (15-20 presets)
│   └── js/
│       └── dashboard/
│           └── dashboard-appearance.js (NEW)
├── services/
│   └── config_service.py (UPDATE)
└── blueprints/
    └── api.py (UPDATE - add appearance endpoints)
```

---

## Validation Rules

### Primary Color
- Must be valid hex color or CSS gradient
- Gradient must have at least 2 colors
- Auto-calculate contrast text

### Avatar
- Preset: Must be valid preset ID (preset_1 to preset_20)
- Upload: PNG/JPG/SVG/WebP, max 2MB, square recommended

### Suggested Messages
- Min: 1 message
- Max: 6 messages
- Max length: 60 characters per message
- Must be unique (no duplicates)

---

## Testing Checklist

### Primary Color
- [ ] Solid color picker works
- [ ] Gradient builder works
- [ ] Contrast text auto-calculates correctly
- [ ] Widget trigger button uses color
- [ ] Chatbox header uses color
- [ ] Buttons use color
- [ ] Text is readable on all backgrounds

### Avatar
- [ ] Preset selection works
- [ ] Avatar displays in trigger button
- [ ] Avatar displays in chatbox header
- [ ] Upload UI is ready (backend can be later)
- [ ] Fallback to ui-avatars works

### Suggested Messages
- [ ] Default messages load on first visit
- [ ] Add message works
- [ ] Remove message works
- [ ] Edit message works
- [ ] Reorder messages works
- [ ] Messages display in widget
- [ ] Clicking message sends to chatbot
- [ ] Validation (min/max/length) works

---

## Migration Plan

### Existing Users
- Migrate `primary_color` string to new format
- Set default avatar to `ui-avatars` (current behavior)
- Set default suggested messages from constants

### Backward Compatibility
- Support old `primary_color` format (string) during transition
- Auto-convert to new format on save

---

## Questions & Decisions

### ✅ Decided
1. **Tab**: Separate "Appearance" tab
2. **Primary Color**: Solid + Gradient support
3. **Avatar**: Presets first, upload UI ready
4. **Suggested Messages**: Dynamic, per-user

### 🤔 To Decide
1. **Gradient Builder**: Simple CSS input or visual builder?
2. **Avatar Presets**: How many? (Recommend: 15-20)
3. **Suggested Messages Max**: 5 or 6? (Recommend: 5 for UI)
4. **Message Reorder**: Drag-drop or arrow buttons? (Recommend: Drag-drop)

---

## Next Steps

1. **Review this plan** with team/user
2. **Decide on UI preferences** (gradient builder, reorder method)
3. **Create preset avatars** (or source them)
4. **Start Phase 1 implementation** (Tab + Primary Color)
5. **Iterate through phases** as planned

---

**Status**: Planning Complete - Ready for Review & Implementation

