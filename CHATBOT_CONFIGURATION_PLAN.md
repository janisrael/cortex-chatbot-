# Chatbot Configuration Feature Plan

## Overview
Add comprehensive chatbot customization features including appearance, branding, and avatar management.

---

## Current State Analysis

### Existing Configuration
- **Location**: `Prompt Editor` tab (titled "Chatbot Configuration")
- **Current Features**:
  - Chatbot Name (`bot_name`)
  - Prompt Presets
  - System Prompt Editor
- **Backend Support**:
  - `bot_name` already stored in `chatbot_config.json`
  - `primary_color` already exists in widget code (default: `#0891b2`)
  - Avatar currently generated via `ui-avatars.com` API (text-based)

### Current Avatar Implementation
```javascript
// From widget.py - line 258
const avatarUrl = `https://ui-avatars.com/api/?name=${botName}&background=${primaryColor}&color=fff&size=24`;
```

---

## Proposed Features

### 1. Chatbot Short Info
- **Field**: `short_info` or `description`
- **Type**: Textarea (max 200-300 characters)
- **Purpose**: Brief description shown in widget/about section
- **Example**: "Your friendly AI assistant for customer support"

### 2. Primary Color
- **Field**: `primary_color` (already exists)
- **Type**: Color picker
- **Purpose**: Brand color for widget, buttons, accents
- **Current**: Hardcoded in widget, needs UI control

### 3. Avatar Customization
Three options to choose from:

#### Option A: Avatar Presets
- **Pros**: 
  - Fast implementation
  - No storage needed (just reference IDs)
  - Consistent quality
- **Cons**: 
  - Limited customization
  - Less unique
- **Implementation**: 
  - 10-20 preset avatar images (SVG/PNG)
  - Grid selection UI
  - Store `avatar_type: 'preset'` and `avatar_id: 'preset_1'`

#### Option B: Avatar Creator
- **Pros**: 
  - High customization
  - Unique avatars
  - User engagement
- **Cons**: 
  - Complex implementation
  - Requires canvas/editor library
  - More development time
- **Implementation**: 
  - Use libraries like `react-avatar-editor` or `fabric.js`
  - Or simple CSS-based builder (shapes, colors, accessories)
  - Store as SVG/PNG data

#### Option C: File Upload
- **Pros**: 
  - Maximum flexibility
  - Users can use any image
  - Simple implementation
- **Cons**: 
  - Storage required
  - File size management
  - Validation needed (format, size, dimensions)
- **Implementation**: 
  - Upload to `uploads/user_X/avatars/`
  - Validate: PNG/JPG/SVG, max 2MB, square recommended
  - Store path: `avatar_path: 'uploads/user_2/avatars/avatar.png'`

#### Option D: AI Avatar Generation (Hybrid)
- **Pros**: 
  - Modern, engaging feature
  - Unique avatars
  - Can combine with presets/upload
- **Cons**: 
  - API costs (if not free)
  - Response time
  - Quality varies
- **Free Options**:
  1. **Replicate API** (Free tier: 1000 requests/month)
     - Stable Diffusion models
     - Avatar-specific models available
  2. **HuggingFace Spaces** (Free)
     - Avatar generation models
     - Can be self-hosted
  3. **ui-avatars.com** (Already used, free, text-based)
  4. **DiceBear API** (Free, preset styles)
     - Multiple avatar styles
     - No API key needed
  5. **Nano Banana** (Google DeepMind)
     - Primarily for image editing/generation
     - Not specifically for avatars
     - May require API access

---

## Tab Placement Options

### Option 1: Expand "Prompt Editor" Tab
**Current Title**: "Chatbot Configuration"

**Structure**:
```
└── Prompt Editor Tab
    ├── Basic Info Section
    │   ├── Chatbot Name
    │   ├── Short Description (NEW)
    │   └── Primary Color (NEW)
    ├── Avatar Section (NEW)
    │   └── [Avatar options]
    └── Personality Section
        ├── Prompt Presets
        └── System Prompt Editor
```

**Pros**:
- All config in one place
- No new tab needed
- Logical grouping
- Current title already says "Configuration"

**Cons**:
- Tab might become too long
- Mixing appearance with personality

---

### Option 2: Create New "Appearance" Tab
**New Tab**: "Appearance" or "Customization"

**Structure**:
```
└── Appearance Tab (NEW)
    ├── Basic Info
    │   ├── Chatbot Name
    │   └── Short Description
    ├── Branding
    │   └── Primary Color
    └── Avatar
        └── [Avatar options]

└── Prompt Editor Tab (RENAMED)
    ├── Prompt Presets
    └── System Prompt Editor
```

**Pros**:
- Clear separation of concerns
- Appearance vs. Personality
- Better organization
- Easier to find settings

**Cons**:
- More tabs (7 total)
- Chatbot name in two places? (or move it)

---

### Option 3: Split into "Personality" and "Appearance"
**Rename**: "Prompt Editor" → "Personality"

**Structure**:
```
└── Personality Tab (RENAMED)
    ├── Prompt Presets
    └── System Prompt Editor

└── Appearance Tab (NEW)
    ├── Basic Info
    │   ├── Chatbot Name
    │   └── Short Description
    ├── Branding
    │   └── Primary Color
    └── Avatar
        └── [Avatar options]
```

**Pros**:
- Very clear separation
- Professional organization
- Scalable for future features

**Cons**:
- Chatbot name might need to be in both? (or just Appearance)

---

## Recommended Approach

### Tab Structure: **Option 1 (Expand Prompt Editor)**
**Reasoning**:
1. Current tab is already titled "Chatbot Configuration"
2. Keeps all chatbot settings in one place
3. Less navigation needed
4. Can organize with sections/collapsible cards

### Avatar Solution: **Hybrid Approach (Presets + Upload)**
**Reasoning**:
1. **Presets** for quick setup (10-15 options)
2. **Upload** for full customization
3. **AI Generation** as future enhancement (if needed)
4. Start simple, add complexity later

**Implementation Priority**:
1. ✅ Presets (easiest, fastest)
2. ✅ Upload (standard feature)
3. ⏳ AI Generation (nice-to-have, can add later)

---

## Detailed Feature Specifications

### 1. Chatbot Short Info
```json
{
  "bot_name": "Cortex",
  "short_info": "Your friendly AI assistant for customer support",
  "primary_color": "#0891b2",
  "avatar": {
    "type": "preset|upload|generated",
    "value": "preset_1" | "uploads/user_2/avatars/avatar.png" | "generated_hash"
  }
}
```

**UI Component**:
- Textarea: 3-4 rows, max 200 characters
- Character counter
- Preview in widget (optional)

---

### 2. Primary Color
**UI Component**:
- Color picker (HTML5 `<input type="color">`)
- Preset color swatches (5-10 common colors)
- Live preview in widget
- Current: Already in backend, needs UI

---

### 3. Avatar Management

#### Preset Avatars
- **Count**: 10-15 preset options
- **Format**: SVG (scalable, small size)
- **Styles**: 
  - Robot/tech themed
  - Friendly characters
  - Abstract shapes
  - Professional icons
- **Storage**: 
  - Store in `static/img/avatars/preset_1.svg`
  - Reference by ID: `preset_1`, `preset_2`, etc.

#### Upload Avatar
- **Accepted Formats**: PNG, JPG, SVG
- **Max Size**: 2MB
- **Recommended Dimensions**: 512x512px (square)
- **Storage Path**: `uploads/user_X/avatars/avatar_YYYYMMDD_HHMMSS.ext`
- **Validation**:
  - File type check
  - Size check
  - Auto-resize if too large
  - Crop to square if needed

#### AI Generation (Future)
- **Service**: Replicate API or HuggingFace
- **Prompt**: "Professional AI assistant avatar, friendly, modern"
- **Storage**: Same as upload
- **Cost**: Monitor API usage

---

## UI/UX Design

### Section Layout (Prompt Editor Tab)
```
┌─────────────────────────────────────────┐
│ Chatbot Configuration                   │
├─────────────────────────────────────────┤
│                                         │
│ ┌─ Basic Information ─────────────────┐ │
│ │ Chatbot Name: [_____________]       │ │
│ │ Short Info:   [_____________]       │ │
│ │                (200 chars max)       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Branding ──────────────────────────┐ │
│ │ Primary Color: [🎨] #0891b2         │ │
│ │ [Preset Colors: 🔵 🔴 🟢 🟡 🟣]     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Avatar ────────────────────────────┐ │
│ │ Current: [Avatar Preview]            │ │
│ │                                       │ │
│ │ [Presets] [Upload] [Generate] (tabs) │ │
│ │                                       │ │
│ │ Preset Grid:                          │ │
│ │ [🦾] [🤖] [👤] [⭐] [🎯] ...         │ │
│ │                                       │ │
│ │ Upload: [Choose File] [Remove]       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Personality ───────────────────────┐ │
│ │ [Prompt Presets Section]             │ │
│ │ [System Prompt Editor]               │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Save Configuration]                    │
└─────────────────────────────────────────┘
```

---

## Database/Storage Changes

### Config File Structure
```json
{
  "bot_name": "Cortex",
  "short_info": "Your friendly AI assistant",
  "primary_color": "#0891b2",
  "avatar": {
    "type": "preset",
    "value": "preset_1"
  },
  "prompt": "...",
  "prompt_preset_id": 1
}
```

### File Storage
```
uploads/
└── user_2/
    └── avatars/
        ├── avatar_20251123_143022.png
        └── avatar_20251123_150145.jpg
```

---

## Implementation Phases

### Phase 1: Basic Configuration (MVP)
- [ ] Add "Short Info" field to config
- [ ] Add Primary Color picker UI
- [ ] Update config service to handle new fields
- [ ] Update widget to use short_info and primary_color

### Phase 2: Avatar Presets
- [ ] Create 10-15 preset avatar SVGs
- [ ] Add avatar preset selection UI
- [ ] Store avatar config in chatbot_config.json
- [ ] Update widget to use preset avatars

### Phase 3: Avatar Upload
- [ ] Add file upload endpoint for avatars
- [ ] Add upload UI component
- [ ] Add image validation and processing
- [ ] Update widget to use uploaded avatars

### Phase 4: AI Generation (Optional)
- [ ] Research and select AI service
- [ ] Implement generation endpoint
- [ ] Add generation UI
- [ ] Monitor API costs

---

## Free AI Avatar Generation Options

### 1. Replicate API
- **Free Tier**: 1000 requests/month
- **Models**: 
  - `lucataco/realistic-vision-v5.1`
  - `fofr/avatar-generator`
- **Cost**: Free tier available, then pay-as-you-go
- **API**: RESTful, easy integration

### 2. HuggingFace Spaces
- **Free**: Yes (with rate limits)
- **Models**: 
  - `ByteDance/SDXL-Lightning`
  - Various avatar-specific models
- **API**: Inference API available
- **Self-hosted**: Possible

### 3. DiceBear API
- **Free**: Yes (no API key needed)
- **Styles**: 100+ avatar styles
- **Format**: SVG/PNG
- **Customization**: Limited but good variety
- **URL**: `https://api.dicebear.com/7.x/{style}/svg?seed={name}`

### 4. ui-avatars.com (Current)
- **Free**: Yes
- **Type**: Text-based initials
- **Customization**: Colors, size, format
- **Already integrated**: Just needs UI control

### 5. Nano Banana (Google DeepMind)
- **Status**: Not specifically for avatars
- **Purpose**: Image generation/editing
- **Access**: May require API access
- **Recommendation**: Not ideal for avatars

---

## Recommendations

### ✅ Recommended Solution

**Tab**: Expand "Prompt Editor" tab (Option 1)
- Keep all config in one place
- Use collapsible sections for organization

**Avatar**: Presets + Upload (Hybrid)
- Start with 10-15 presets (quick win)
- Add upload functionality (standard feature)
- Consider AI generation later if needed

**AI Service**: DiceBear API (if needed)
- Free, no API key
- Multiple styles
- Easy integration
- Good fallback option

---

## Next Steps

1. **Decision**: Choose tab placement option
2. **Decision**: Choose avatar solution (presets, upload, AI, or hybrid)
3. **Design**: Create UI mockup/wireframe
4. **Implementation**: Start with Phase 1 (Basic Configuration)
5. **Testing**: Test with real users

---

## Questions to Answer

1. **Tab Placement**: Option 1, 2, or 3?
2. **Avatar Solution**: Presets only? Upload only? Both? AI?
3. **AI Generation**: Is it a priority? Or can we start without it?
4. **Short Info**: Where should it be displayed? (Widget header? About section?)
5. **Primary Color**: Should it affect more than just avatar? (Buttons, accents?)

---

**Status**: Planning Phase - Awaiting decisions before implementation

