# FAQ Knowledge Base - Implementation Plan

## Overview
Add a user-isolated FAQ (Frequently Asked Questions) management system that integrates with the chatbot's knowledge base, similar to crawled URLs and uploaded files.

---

## Architecture

### 1. Database Model (`models/faq.py`)
**Similar to `CrawledUrl` model structure:**

```python
class FAQ:
    - id (PRIMARY KEY)
    - user_id (FOREIGN KEY → users.id, ON DELETE CASCADE)
    - question (TEXT, NOT NULL)
    - answer (TEXT, NOT NULL)
    - category (VARCHAR(50), DEFAULT 'company_details')
    - status (ENUM: 'draft', 'active', 'deleted')
    - ingested_at (DATETIME, NULL)
    - created_at (DATETIME)
    - updated_at (DATETIME)
    
    Methods:
    - init_db() - Create table
    - create(user_id, question, answer, category, status='draft')
    - get_by_id(user_id, faq_id)
    - get_all_by_user(user_id, status='active')
    - update(user_id, faq_id, question, answer, category)
    - update_status(faq_id, status)
    - delete(faq_id) - Soft delete (status='deleted')
    - to_dict(row) - Convert to dict format
```

**Table Schema:**
- SQLite: `faqs` table with INTEGER PRIMARY KEY
- MySQL: `faqs` table with INT AUTO_INCREMENT
- Indexes: `idx_user_id`, `idx_status`

---

### 2. API Endpoints (`blueprints/api.py`)

#### 2.1 List FAQs
```
GET /api/faqs
- Returns: { "faqs": [...], "total": N }
- User-isolated (current_user.id)
- Filter by status (default: 'active')
```

#### 2.2 Get Single FAQ
```
GET /api/faqs/<int:faq_id>
- Returns: { "id": 1, "question": "...", "answer": "...", ... }
- User-isolated check
```

#### 2.3 Create FAQ
```
POST /api/faqs
Body: {
    "question": "What is your return policy?",
    "answer": "We offer 30-day returns...",
    "category": "company_details"
}
- Returns: { "id": 1, "message": "FAQ created successfully" }
- Status: 'draft' by default
```

#### 2.4 Update FAQ
```
PUT /api/faqs/<int:faq_id>
Body: {
    "question": "...",
    "answer": "...",
    "category": "..."
}
- Returns: { "message": "FAQ updated successfully" }
- User-isolated check
```

#### 2.5 Delete FAQ
```
DELETE /api/faqs/<int:faq_id>
- Soft delete (status='deleted')
- If ingested, remove from vectorstore
- Returns: { "message": "FAQ deleted successfully" }
```

#### 2.6 Ingest FAQ to Knowledge Base
```
POST /api/faqs/<int:faq_id>/ingest
- Convert FAQ to Document format
- Split into chunks (if needed, or use as single chunk)
- Add to user's vectorstore
- Update status to 'active' and set ingested_at
- Metadata: {
    'source_file': f"FAQ_{faq_id}",
    'source_type': 'faq',
    'category': faq.category,
    'faq_id': faq_id,
    'question': faq.question
}
```

#### 2.7 Bulk Ingest FAQs
```
POST /api/faqs/bulk-ingest
Body: { "faq_ids": [1, 2, 3] }
- Ingest multiple FAQs at once
- Useful for batch operations
```

---

### 3. Frontend UI (`templates/components/dashboard_knowledge_tab.html`)

#### 3.1 New FAQ Card Section
Add a new card in the Knowledge Base tab (after Crawled Websites):

```html
<div class="card">
    <h2>
        <span class="material-icons-round">help_center</span>
        FAQ Management
    </h2>
    
    <!-- Add FAQ Form -->
    <div class="faq-form">
        <input type="text" id="faqQuestion" placeholder="Question...">
        <textarea id="faqAnswer" placeholder="Answer..."></textarea>
        <select id="faqCategory">...</select>
        <button onclick="createFAQ()">Add FAQ</button>
    </div>
    
    <!-- FAQ List -->
    <div id="faqList">
        Loading FAQs...
    </div>
</div>
```

#### 3.2 FAQ List Display
- Show question, answer preview, category, status
- Actions: Edit, Ingest, Delete
- Status badges: Draft, Active (ingested), Deleted
- Bulk actions: Select multiple → Bulk ingest/delete

#### 3.3 FAQ Editor Modal
- Edit question/answer inline
- Category selector
- Ingest button (if not ingested)
- Delete button

---

### 4. JavaScript (`static/js/dashboard/faq_management.js`)

**Functions:**
```javascript
- loadFAQs() - Fetch and display FAQs
- createFAQ() - POST new FAQ
- updateFAQ(faqId) - PUT update FAQ
- deleteFAQ(faqId) - DELETE FAQ
- ingestFAQ(faqId) - POST ingest to vectorstore
- bulkIngestFAQs(faqIds) - Bulk ingest
- refreshFAQList() - Reload FAQ list
- renderFAQList(faqs) - Display FAQs in UI
```

**Integration:**
- Add to `dashboard_knowledge_tab.html` script section
- Or create separate `faq_management.js` file
- Call `loadFAQs()` when Knowledge tab is opened

---

### 5. Vectorstore Integration

#### 5.1 Document Format
When ingesting FAQ, create Document:
```python
Document(
    page_content=f"Q: {faq.question}\nA: {faq.answer}",
    metadata={
        'source_file': f"FAQ_{faq.id}",
        'source_type': 'faq',
        'category': faq.category,
        'user_id': str(user_id),
        'faq_id': faq_id,
        'question': faq.question,
        'upload_time': datetime.now().isoformat()
    }
)
```

#### 5.2 Chunking Strategy
- **Option A**: Single chunk per FAQ (Q&A together)
  - Pros: Preserves context, better for retrieval
  - Cons: Larger chunks
- **Option B**: Split if answer is long (>500 chars)
  - Pros: Better for very long answers
  - Cons: May lose Q&A connection

**Recommendation**: Option A (single chunk) - FAQs are typically concise

#### 5.3 Removal from Vectorstore
When FAQ is deleted:
- Use `remove_file_from_vectorstore(user_id, f"FAQ_{faq_id}")`
- Similar to how crawled URLs are removed

---

### 6. Statistics Integration

#### 6.1 Update `get_knowledge_stats()` (`services/knowledge_service.py`)
```python
def get_knowledge_stats(user_id):
    # ... existing code ...
    
    # Get FAQ count
    from models.faq import FAQ
    faqs = FAQ.get_all_by_user(user_id, status='active')
    ingested_faqs = [f for f in faqs if f.get('ingested_at')]
    
    return {
        "total_documents": doc_count,
        "vector_store_status": db_status,
        "uploaded_files": files,
        "faq_count": len(faqs),
        "ingested_faq_count": len(ingested_faqs)
    }
```

#### 6.2 Update Overview Tab
- Already shows "FAQ Entries" metric
- Update `updateOverviewMetrics()` to use real FAQ count from API

---

### 7. File Structure

```
chatbot/
├── models/
│   └── faq.py                    # NEW: FAQ model
├── blueprints/
│   └── api.py                    # ADD: FAQ endpoints
├── templates/components/
│   └── dashboard_knowledge_tab.html  # ADD: FAQ card section
├── static/js/dashboard/
│   └── faq_management.js         # NEW: FAQ JS functions
└── services/
    └── knowledge_service.py      # UPDATE: Add FAQ stats
```

---

## Implementation Phases

### Phase 1: Database & Model ✅
1. Create `models/faq.py`
2. Implement `FAQ` class with all CRUD methods
3. Add `init_db()` call in `migrations.py`
4. Test model operations

### Phase 2: API Endpoints ✅
1. Add FAQ endpoints to `blueprints/api.py`
2. Implement user-isolation checks
3. Add ingest endpoint (vectorstore integration)
4. Test all endpoints

### Phase 3: Frontend UI ✅
1. Add FAQ card to Knowledge Base tab
2. Create FAQ form (question, answer, category)
3. Create FAQ list display
4. Add edit/delete/ingest buttons
5. Create FAQ editor modal

### Phase 4: JavaScript Integration ✅
1. Create `faq_management.js`
2. Implement all CRUD functions
3. Add event listeners
4. Integrate with Knowledge tab loading

### Phase 5: Vectorstore Integration ✅
1. Implement FAQ → Document conversion
2. Add to vectorstore on ingest
3. Remove from vectorstore on delete
4. Test retrieval in chatbot

### Phase 6: Statistics & Overview ✅
1. Update `get_knowledge_stats()` to include FAQ count
2. Update Overview tab to show real FAQ count
3. Test stats display

### Phase 7: Testing & Polish ✅
1. Test all CRUD operations
2. Test ingest/delete from vectorstore
3. Test chatbot retrieval of FAQs
4. Mobile responsive design
5. Error handling

---

## Data Flow

### Creating FAQ:
```
User Input → POST /api/faqs → FAQ.create() → Database → Return FAQ ID
```

### Ingesting FAQ:
```
User Clicks "Ingest" → POST /api/faqs/<id>/ingest → 
  → Get FAQ from DB → Convert to Document → 
  → Split into chunks → Add to vectorstore → 
  → Update status='active' → Return success
```

### Chatbot Retrieval:
```
User asks question → get_chatbot_response() → 
  → Vectorstore search → Retrieve relevant chunks → 
  → If source_type='faq', format as Q&A → Return to user
```

### Deleting FAQ:
```
User Clicks "Delete" → DELETE /api/faqs/<id> → 
  → If ingested, remove from vectorstore → 
  → Update status='deleted' → Return success
```

---

## UI/UX Design

### FAQ Card Layout:
```
┌─────────────────────────────────────────┐
│ 📋 FAQ Management                      │
├─────────────────────────────────────────┤
│                                         │
│  [Question Input Field]                │
│  [Answer Textarea]                      │
│  [Category Dropdown]                    │
│  [➕ Add FAQ Button]                    │
│                                         │
│  ───────────────────────────────────    │
│                                         │
│  FAQ List:                              │
│  ┌─────────────────────────────────┐   │
│  │ Q: What is your return policy? │   │
│  │ A: We offer 30-day returns...   │   │
│  │ [Category] [Draft]              │   │
│  │ [Edit] [Ingest] [Delete]        │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Status Badges:
- **Draft** (gray) - Created but not ingested
- **Active** (green) - Ingested to knowledge base
- **Deleted** (red) - Soft deleted

---

## Security Considerations

1. **User Isolation**: All queries filter by `user_id = current_user.id`
2. **Input Validation**: Sanitize question/answer inputs
3. **SQL Injection**: Use parameterized queries (already in model pattern)
4. **XSS Prevention**: Escape HTML in question/answer display
5. **Rate Limiting**: Consider rate limits for bulk operations

---

## Testing Checklist

- [ ] Create FAQ (draft status)
- [ ] Update FAQ question/answer
- [ ] Ingest single FAQ to vectorstore
- [ ] Bulk ingest multiple FAQs
- [ ] Delete FAQ (soft delete)
- [ ] Delete ingested FAQ (removes from vectorstore)
- [ ] FAQ appears in chatbot responses
- [ ] FAQ count shows in Overview stats
- [ ] User isolation (user 1 can't see user 2's FAQs)
- [ ] Mobile responsive design
- [ ] Error handling (invalid FAQ ID, network errors)

---

## Future Enhancements (Optional)

1. **FAQ Categories**: Group FAQs by category in UI
2. **FAQ Search**: Search/filter FAQs by question/answer
3. **FAQ Import/Export**: CSV/JSON import/export
4. **FAQ Analytics**: Track which FAQs are most retrieved
5. **FAQ Templates**: Pre-defined FAQ templates
6. **FAQ Versioning**: Track FAQ edit history
7. **FAQ Tags**: Add tags for better organization

---

## Estimated Implementation Time

- **Phase 1-2** (Model + API): 2-3 hours
- **Phase 3-4** (Frontend + JS): 2-3 hours
- **Phase 5** (Vectorstore): 1 hour
- **Phase 6** (Stats): 30 minutes
- **Phase 7** (Testing): 1-2 hours

**Total**: ~7-10 hours

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Database Model)
3. Implement incrementally, testing each phase
4. Deploy to production after full testing

---

**Created by**: Agimat (Super Debugger AI)  
**Date**: 2025-11-25  
**Version**: 1.0

