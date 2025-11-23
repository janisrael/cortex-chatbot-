# 🧪 CORTEX AI DASHBOARD - TESTING CHECKLIST

## 📱 **TEST 1: OVERVIEW TAB**
**URL:** http://localhost:6001/dashboard

### Desktop View:
- [ ] Tab loads by default
- [ ] Stats cards display correctly (4 cards visible)
- [ ] Numbers are visible in stats (Total Documents, Files, LLM Model, Website)
- [ ] Recent Files section shows sample files
- [ ] File sizes are formatted correctly (e.g., "2.38 MB")
- [ ] No console errors

### Mobile View (< 768px):
- [ ] Stats cards stack properly (2 columns)
- [ ] Text is readable
- [ ] No horizontal scroll
- [ ] Cards resize appropriately

**Status:** ⏳ Pending

---

## ⚙️ **TEST 2: LLM CONFIGURATION TAB**

### Desktop View:
- [ ] Tab switches correctly when clicked
- [ ] Website selector tabs visible (Default, SourceSelect, Example Business)
- [ ] Can click and switch between websites
- [ ] Active website tab is highlighted (teal background)
- [ ] Global Settings section visible
- [ ] Provider tabs (OpenAI / Ollama) visible
- [ ] Can switch between OpenAI and Ollama tabs
- [ ] Active provider tab is highlighted
- [ ] Form fields populate correctly
- [ ] OpenAI shows: API Key field, Model dropdown
- [ ] Ollama shows: Base URL field, Model dropdown
- [ ] "Save Global Configuration" button visible
- [ ] Button shows loading state when clicked
- [ ] Success message appears after save
- [ ] LLM status indicator shows correct state

### Mobile View:
- [ ] Website tabs wrap properly
- [ ] Provider tabs stack if needed
- [ ] Form fields are full width
- [ ] Buttons are touch-friendly
- [ ] No layout breaks

**Status:** ⏳ Pending

---

## 📝 **TEST 3: PROMPT EDITOR TAB**

### Desktop View:
- [ ] Tab switches correctly
- [ ] Textarea loads with default prompt
- [ ] Textarea is editable
- [ ] Textarea has adequate height (420px)
- [ ] "Save Prompt" button visible
- [ ] "Reset to Default" button visible
- [ ] Save button shows loading state
- [ ] Success message appears after save
- [ ] Keyboard shortcut (Ctrl+S) works
- [ ] Ctrl+S prevents browser save dialog

### Mobile View:
- [ ] Textarea is full width
- [ ] Textarea height is appropriate
- [ ] Buttons stack properly
- [ ] Text is readable in textarea

**Status:** ⏳ Pending

---

## 📁 **TEST 4: KNOWLEDGE BASE TAB**

### Desktop View:
- [ ] Tab switches correctly
- [ ] Category tabs visible (Company Details, Sales Training, Product Info, Policies)
- [ ] Can switch between categories
- [ ] Active category is highlighted
- [ ] File upload area visible
- [ ] Upload area shows icon and text
- [ ] Click to upload works
- [ ] Drag and drop area changes on dragover
- [ ] File upload shows loading state
- [ ] Success message after upload
- [ ] Stats refresh after upload

### Mobile View:
- [ ] Category tabs wrap properly
- [ ] Upload area is touch-friendly
- [ ] Text is readable
- [ ] No layout issues

**Status:** ⏳ Pending

---

## 🔧 **TEST 5: SYSTEM MANAGEMENT TAB**

### Desktop View:
- [ ] Tab switches correctly
- [ ] Management cards visible (4 cards in grid)
- [ ] Each card shows title, description, and button
- [ ] "Reset Knowledge Base" button works
- [ ] Confirmation dialogs appear (2 confirms + text input)
- [ ] Must type "RESET KNOWLEDGE" to confirm
- [ ] Button shows loading state during operation
- [ ] Success message after operation
- [ ] "Clear Chat History" works with confirmation
- [ ] "Rebuild Vector Store" works with confirmation
- [ ] "Create Backup" works
- [ ] "Refresh Session" works
- [ ] "Full System Reset" has triple confirmation
- [ ] Must type "RESET EVERYTHING" to confirm

### Mobile View:
- [ ] Cards stack to single column
- [ ] Buttons are full width
- [ ] Text is readable
- [ ] Confirmation dialogs work on mobile

**Status:** ⏳ Pending

---

## 🔗 **TEST 6: INTEGRATION TAB**

### Desktop View:
- [ ] Tab switches correctly
- [ ] Integration steps visible (numbered steps)
- [ ] Code snippet displays correctly
- [ ] Website ID is shown in snippet
- [ ] "Copy Code" button works
- [ ] Button shows "✅ Copied!" feedback
- [ ] Preview section visible
- [ ] "Refresh Preview" button works
- [ ] "Open in New Tab" button works

### Mobile View:
- [ ] Steps stack vertically
- [ ] Code snippet is scrollable
- [ ] Copy button works on mobile
- [ ] No horizontal overflow

**Status:** ⏳ Pending

---

## 🎨 **TEST 7: DESIGN & UI**

### Colors:
- [ ] Header gradient is teal (not purple)
- [ ] Active tabs are teal
- [ ] Buttons are teal
- [ ] Hover states are darker teal
- [ ] Stat values are teal
- [ ] Footer links are teal
- [ ] No purple colors remaining

### Animations:
- [ ] Tab switching is smooth
- [ ] Button hover effects work
- [ ] Loading states animate
- [ ] Success messages fade in/out

### Responsiveness:
- [ ] Desktop (> 1200px) - full layout
- [ ] Laptop (1024px) - adjusted layout
- [ ] Tablet (768px) - stacked elements
- [ ] Mobile (< 768px) - single column
- [ ] Small mobile (< 480px) - optimized

**Status:** ⏳ Pending

---

## 🐛 **TEST 8: ERROR HANDLING**

### Browser Console:
- [ ] No red errors on page load
- [ ] No 404 errors for JS/CSS files
- [ ] All 6 JS files load (200 status)
- [ ] CSS file loads (200 status)
- [ ] No undefined function errors
- [ ] Console shows: "✅ Dashboard initialized successfully"
- [ ] Console shows: "✅ Utils initialized"

### Network Tab:
- [ ] dashboard.css - 200 OK
- [ ] dashboard-core.js - 200 OK
- [ ] dashboard-utils.js - 200 OK
- [ ] dashboard-overview.js - 200 OK
- [ ] dashboard-llm.js - 200 OK
- [ ] dashboard-prompt.js - 200 OK
- [ ] dashboard-system.js - 200 OK

**Status:** ⏳ Pending

---

## 📊 **TEST 9: FUNCTIONALITY**

### Tab Switching:
- [ ] All tabs switch without page reload
- [ ] URL doesn't change
- [ ] Previous tab content is hidden
- [ ] New tab content is shown
- [ ] Active tab button is highlighted

### Auto-Refresh:
- [ ] Stats auto-refresh every 30 seconds
- [ ] No page reload during refresh
- [ ] Console shows refresh activity

### Keyboard Shortcuts:
- [ ] Ctrl+S works in Prompt Editor tab
- [ ] Ctrl+S is prevented in other tabs
- [ ] No browser save dialog appears

**Status:** ⏳ Pending

---

## 🚀 **TEST 10: PERFORMANCE**

### Load Times:
- [ ] Dashboard loads in < 2 seconds
- [ ] No lag when switching tabs
- [ ] Buttons respond immediately
- [ ] No memory leaks (check DevTools)

### File Sizes:
- [ ] CSS file < 20KB
- [ ] Total JS files < 50KB
- [ ] Page size < 100KB

**Status:** ⏳ Pending

---

## ✅ **FINAL CHECKLIST**

- [ ] All 10 tests completed
- [ ] All critical issues fixed
- [ ] All bugs documented
- [ ] Mobile view works perfectly
- [ ] No console errors
- [ ] Ready for deployment

---

**Testing Started:** [DATE]
**Testing Completed:** [DATE]
**Tested By:** Swordfish + Agimat
**Status:** 🟡 In Progress
