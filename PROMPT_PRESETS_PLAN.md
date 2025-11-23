# 📋 Prompt Presets Implementation Plan

**Feature:** Pre-defined chatbot personality templates  
**Status:** Planning  
**Date:** 2025-11-23

---

## 🎯 Feature Overview

Allow users to quickly start with pre-configured chatbot personalities (presets) that automatically populate the prompt editor. Users can then customize and save as their own.

---

## 📐 Design Approach

### UI Layout
```
┌─────────────────────────────────────────┐
│ Chatbot Configuration                   │
├─────────────────────────────────────────┤
│ Chatbot Name: [input]                   │
│                                         │
│ Prompt Presets:                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│ │ Virtual  │ │   Tech   │ │  Sales   ││
│ │Assistant │ │ Support  │ │  Agent   ││
│ └──────────┘ └──────────┘ └──────────┘│
│                                         │
│ System Prompt Template:                 │
│ ┌─────────────────────────────────────┐│
│ │ [textarea - auto-populated]         ││
│ └─────────────────────────────────────┘│
│                                         │
│ [Save] [Reset] [Test]                  │
└─────────────────────────────────────────┘
```

---

## 🏗️ Implementation Plan

### Phase 1: Define Presets (Backend)

**File:** `config/constants.py`

Add `PROMPT_PRESETS` dictionary:

```python
PROMPT_PRESETS = {
    'virtual_assistant': {
        'id': 'virtual_assistant',
        'name': 'Virtual Assistant',
        'icon': 'support_agent',
        'description': 'General-purpose helpful assistant',
        'prompt': '''You are {bot_name}, an intelligent AI assistant.

Your job is to help users with their questions. Always be polite, helpful, and conversational.

INSTRUCTIONS:
- Vary your greetings and responses to avoid sounding repetitive or robotic.
- Reference the user's specific question in your answer.
- Use ONLY the information provided in the "Relevant Info" section below.
- If you don't know the answer or the information isn't available, respond with a polite fallback.
- Only ask follow-up questions if they make sense and feel natural.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Keep your tone friendly and concise.
- Always finish with a relevant follow-up or offer to help further.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
    },
    'tech_support': {
        'id': 'tech_support',
        'name': 'Tech Support',
        'icon': 'computer',
        'description': 'Technical support and troubleshooting',
        'prompt': '''You are {bot_name}, a technical support specialist.

Your role is to help users resolve technical issues, answer questions about products or services, and provide clear, step-by-step guidance.

INSTRUCTIONS:
- Be patient and understanding, especially with technical difficulties.
- Break down complex solutions into simple, numbered steps.
- Use technical terms when appropriate, but explain them clearly.
- If you don't have the answer, guide users to the right resources.
- Always confirm understanding before moving to the next step.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with a clear next step or follow-up question.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
    },
    'sales_agent': {
        'id': 'sales_agent',
        'name': 'Sales Agent',
        'icon': 'shopping_cart',
        'description': 'Sales and product recommendations',
        'prompt': '''You are {bot_name}, a knowledgeable sales representative.

Your goal is to help customers find the right products or services, answer questions about offerings, and guide them through the purchase process.

INSTRUCTIONS:
- Be enthusiastic but not pushy.
- Focus on benefits and value, not just features.
- Ask qualifying questions to understand customer needs.
- Provide clear pricing and availability information.
- Address objections professionally and helpfully.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- Always include a clear call-to-action.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
    },
    'customer_service': {
        'id': 'customer_service',
        'name': 'Customer Service',
        'icon': 'headset_mic',
        'description': 'Customer support and inquiries',
        'prompt': '''You are {bot_name}, a friendly customer service representative.

Your mission is to provide excellent customer service, resolve issues, answer questions, and ensure customer satisfaction.

INSTRUCTIONS:
- Always greet customers warmly and professionally.
- Listen carefully to customer concerns and acknowledge them.
- Provide accurate information from the knowledge base.
- If you cannot resolve an issue, escalate appropriately.
- Maintain a positive, solution-oriented attitude.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with an offer to help further or confirm resolution.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
    },
    'educator': {
        'id': 'educator',
        'name': 'Educator',
        'icon': 'school',
        'description': 'Educational content and tutoring',
        'prompt': '''You are {bot_name}, an educational assistant.

Your purpose is to help students learn, explain concepts clearly, and provide educational support.

INSTRUCTIONS:
- Break down complex topics into understandable parts.
- Use examples and analogies to clarify concepts.
- Encourage questions and active learning.
- Provide accurate information from educational materials.
- Adapt explanations to the student's level of understanding.
- Respond in HTML format (use <br> for line breaks, <ul><li> for lists, <strong> for emphasis).
- End with a question to check understanding or suggest next steps.

Relevant Info:
{context}

User Question: {question}

{bot_name}'s Response:'''
    }
}
```

---

### Phase 2: API Endpoint (Backend)

**File:** `blueprints/api.py`

Add endpoint to get presets:

```python
@api_bp.route("/api/prompt-presets", methods=["GET"])
@login_required
def get_prompt_presets():
    """Get available prompt presets"""
    from config.constants import PROMPT_PRESETS
    return jsonify({
        "presets": PROMPT_PRESETS
    })
```

---

### Phase 3: UI Component (Frontend)

**File:** `templates/components/dashboard_prompt_tab.html`

Add preset selector section before prompt editor:

```html
<!-- Prompt Presets -->
<div class="preset-selector-section">
    <label class="section-label">Choose a Preset (Optional)</label>
    <p class="section-description">Start with a pre-configured personality template, then customize as needed.</p>
    <div class="preset-grid" id="presetGrid">
        <!-- Dynamically populated -->
    </div>
</div>
```

---

### Phase 4: JavaScript Logic (Frontend)

**File:** `static/v2/js/dashboard-prompt.js`

Add functions:
- `loadPresets()` - Fetch presets from API
- `renderPresets()` - Display preset cards
- `applyPreset(presetId)` - Load preset into editor
- `replaceBotNameInPrompt(prompt, botName)` - Replace {bot_name} placeholder

---

### Phase 5: CSS Styling

**File:** `static/v2/css/dashboard.css`

Add styles for:
- `.preset-selector-section` - Container
- `.preset-grid` - Grid layout for preset cards
- `.preset-card` - Individual preset card
- `.preset-card:hover` - Hover effects
- `.preset-card.active` - Selected state

---

## 🎨 Design Specifications

### Preset Cards
- **Layout:** Grid (3-4 columns on desktop, 2 on tablet, 1 on mobile)
- **Card Style:** Neumorphism or clean card with icon
- **Elements:**
  - Icon (Material Icons)
  - Preset name
  - Short description
  - "Use This" button or clickable card

### Visual States
- **Default:** Clean card with border
- **Hover:** Slight elevation/shadow
- **Active/Selected:** Highlighted border or background
- **After Applied:** Show checkmark or "Applied" badge

---

## 🔄 User Flow

1. User opens Prompt Editor tab
2. Presets load and display as cards
3. User clicks a preset card
4. Prompt editor auto-populates with preset template
5. `{bot_name}` placeholder replaced with current chatbot name
6. User can edit the prompt
7. User clicks "Save Prompt" to save custom version
8. Preset remains unchanged (read-only template)

---

## ✅ Benefits

1. **Quick Start:** Users can begin with proven templates
2. **Best Practices:** Presets include best practices
3. **Customizable:** Users can modify after applying
4. **No Lock-in:** Presets are templates, not restrictions
5. **Professional:** Makes the platform more user-friendly

---

## 🚀 Implementation Steps

1. ✅ Hide website selector (DONE)
2. ⏳ Add PROMPT_PRESETS to constants.py
3. ⏳ Create /api/prompt-presets endpoint
4. ⏳ Add preset selector UI to prompt tab
5. ⏳ Add JavaScript functions
6. ⏳ Add CSS styling
7. ⏳ Test preset loading and application
8. ⏳ Test save functionality with preset

---

## 📝 Notes

- Presets are **read-only templates** - users can't modify them
- Users can save **custom versions** after applying a preset
- `{bot_name}` placeholder is replaced with actual chatbot name
- `{context}` and `{question}` placeholders remain for RAG system
- Presets can be expanded in the future

---

**Next Steps:** Ready to implement when approved!

