# Manual RAG Testing Guide

## ⚡ IMPORTANT: Knowledge Availability

**Answer: IMMEDIATELY (0 seconds delay)**

All three ingestion methods (File Upload, Website Crawling, FAQ) write directly to ChromaDB using `user_vectorstore.add_documents(chunks)`. As soon as the API returns success, the knowledge is available for RAG queries.

---

## Test 1: File Upload & Ingestion

### Step 1: Upload Test Document
1. Go to Dashboard → Knowledge Base tab
2. Select category: "general"
3. Click "Upload Documents"
4. Upload `test_rag_document.txt` (already created in project root)
5. Wait for upload to complete

### Step 2: Review & Ingest
1. Find the uploaded file in the list
2. Click "View" to preview the extracted text
3. Click "Ingest" button
4. Wait for success notification: "File ingested successfully. Added X chunks."

### Step 3: Test Chatbot (IMMEDIATELY - no wait needed)
1. Go to Dashboard → Overview tab (or Widget Preview)
2. Ask chatbot: **"What is the CEO's name?"**
3. **Expected**: Should respond with "John Smith"
4. Check server logs for: `📚 Retrieved X relevant documents from knowledge base`

### Step 4: Additional Test Questions
- "What is the company's phone number?" → Should say "(555) 123-4567"
- "Where is the headquarters located?" → Should mention "123 AI Street, San Francisco"
- "What is the monthly subscription price?" → Should say "$29.99/month"

---

## Test 2: Website Crawling

### Step 1: Crawl a Test Website
1. Go to Dashboard → Knowledge Base tab → "Crawl Websites" section
2. Enter a test URL (e.g., https://example.com or any simple website)
3. Select category: "general"
4. Enable "AI Content Cleaning" (optional)
5. Click "Crawl Website"
6. Wait for crawl to complete

### Step 2: Review & Ingest
1. Find the crawled URL in the list
2. Click "View" to preview the extracted text
3. Click "Ingest" button
4. Wait for success notification: "URL ingested successfully. Added X chunks."

### Step 3: Test Chatbot (IMMEDIATELY)
1. Ask chatbot a question about the crawled website content
2. Example: If you crawled a company website, ask "What services does this company offer?"
3. **Expected**: Chatbot should respond using information from the crawled website
4. Check server logs for retrieval messages

---

## Test 3: FAQ Management

### Step 1: Add Test FAQ
1. Go to Dashboard → Knowledge Base tab → "FAQ Management" section
2. Select category: "general"
3. Enter Question: **"What is the return policy?"**
4. Enter Answer: **"We offer a 30-day money-back guarantee. Returns must be in original packaging. Contact support@cortexai.com for return requests."**
5. Click "Add FAQ"

### Step 2: Ingest FAQ
1. Find the FAQ in the list
2. Click "Ingest" button
3. Wait for success notification: "FAQ ingested successfully. Added X chunk(s)."

### Step 3: Test Chatbot (IMMEDIATELY)
1. Ask chatbot: **"What is your return policy?"**
2. **Expected**: Should respond with the FAQ answer about 30-day guarantee
3. Ask: **"How do I return a product?"**
4. **Expected**: Should mention contacting support@cortexai.com
5. Check server logs for retrieval messages

---

## Verification Checklist

After each ingestion, verify:

- [ ] API returns success message immediately
- [ ] Status changes to "ingested" (for files/URLs) or "active" (for FAQs)
- [ ] Chatbot can answer questions about the ingested content **immediately** (no wait)
- [ ] Server logs show: `📚 Retrieved X relevant documents from knowledge base`
- [ ] Server logs show: `📄 Sources: [filename/url/faq]`
- [ ] Chatbot response contains information from the knowledge base
- [ ] No errors in server logs related to retrieval

---

## Troubleshooting

### If chatbot doesn't retrieve knowledge:

1. **Check server logs** for errors:
   - Look for: `⚠️ Error retrieving documents:`
   - Look for: `⚠️ No retriever available`

2. **Verify ingestion succeeded**:
   - Check file/URL/FAQ status is "ingested" or "active"
   - Check server logs for: `✅ Successfully added chunks to vectorstore`

3. **Check retriever initialization**:
   - Server logs should show: `✅ Chroma vectorstore object created`
   - No errors about `get_relevant_documents` (should be using `invoke()` now)

4. **Test with a very specific question**:
   - Use exact phrases from the ingested content
   - Example: If document says "CEO is John Smith", ask "Who is John Smith?"

5. **Check knowledge stats**:
   - Go to Knowledge Base tab
   - Check "Vector Documents" count increased after ingestion

---

## Expected Server Log Output

When RAG is working correctly, you should see:

```
📚 Retrieved 3 relevant documents from knowledge base
📄 Sources: ['test_rag_document.txt', 'FAQ_1', 'https://example.com']
✅ Using user LLM: openai / gpt-4o-mini
```

If retrieval fails, you might see:

```
⚠️ Error retrieving documents: [error message]
⚠️ No retriever available - using direct LLM response
```

---

## Test Results Template

After completing all tests, document:

1. **File Upload Test**: ✅/❌
   - Uploaded: [filename]
   - Ingested: [timestamp]
   - Tested: [timestamp] (should be same or seconds later)
   - Question: [your question]
   - Response: [chatbot response]
   - Retrieved docs: [yes/no]

2. **Website Crawl Test**: ✅/❌
   - Crawled: [URL]
   - Ingested: [timestamp]
   - Tested: [timestamp]
   - Question: [your question]
   - Response: [chatbot response]
   - Retrieved docs: [yes/no]

3. **FAQ Test**: ✅/❌
   - FAQ ID: [ID]
   - Ingested: [timestamp]
   - Tested: [timestamp]
   - Question: [your question]
   - Response: [chatbot response]
   - Retrieved docs: [yes/no]

---

## Summary

**All three knowledge sources (Files, URLs, FAQs) are available IMMEDIATELY after ingestion completes. There is no indexing delay, no background processing, and no wait time required.**

