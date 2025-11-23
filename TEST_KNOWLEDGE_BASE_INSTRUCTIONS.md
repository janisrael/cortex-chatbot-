# Knowledge Base Test Instructions

## Quick Test Steps

### 1. Start the Server
```bash
cd /run/media/swordfish/Projects/development/chatbot
python3 app.py
```

### 2. In Another Terminal, Run the Test
```bash
cd /run/media/swordfish/Projects/development/chatbot
python3 test_knowledge_base.py
```

## Manual Test Steps

### Step 1: Login/Register
```bash
# Register (if needed)
curl -X POST http://localhost:6001/register \
  -H "X-Requested-With: XMLHttpRequest" \
  -d "username=testuser&email=test@test.com&password=test123&confirm_password=test123"

# Login
curl -X POST http://localhost:6001/login \
  -H "X-Requested-With: XMLHttpRequest" \
  -c cookies.txt \
  -d "email=test@test.com&password=test123"
```

### Step 2: Create Test Document
```bash
cat > /tmp/test_doc.txt << 'EOF'
Company Information

TechSolutions Inc. was founded in 2020.
We offer AI chatbot development services.
Contact: contact@techsolutions.com
Phone: +1-555-0123
Pricing: Basic Plan $99/month, Professional $299/month
Special offer: 20% off first month for new customers
EOF
```

### Step 3: Upload Document
```bash
curl -X POST http://localhost:6001/api/upload \
  -b cookies.txt \
  -F "file=@/tmp/test_doc.txt" \
  -F "category=company_details"
```

### Step 4: Wait for Processing
```bash
sleep 5
```

### Step 5: Test Chat with Knowledge Base
```bash
# Ask about company info
curl -X POST http://localhost:6001/chat \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"message": "What services does TechSolutions offer?"}'

# Ask about contact
curl -X POST http://localhost:6001/chat \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the contact email?"}'

# Ask about pricing
curl -X POST http://localhost:6001/chat \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the pricing plans?"}'
```

### Step 6: Verify Response Contains Knowledge Base Info

The responses should include:
- "AI chatbot development" (from document)
- "contact@techsolutions.com" (from document)
- "$99" or "$299" (from document)
- "20% off" (from document)

## Expected Results

✅ **Success Indicators:**
- Upload returns success message
- Chat responses contain information from uploaded document
- Responses mention specific details like email, pricing, services

❌ **Failure Indicators:**
- Generic responses that don't mention document content
- "I don't know" type responses
- No specific details from the document

## Troubleshooting

1. **Server not running?**
   ```bash
   python3 app.py
   ```

2. **Upload fails?**
   - Check you're logged in (cookies.txt exists)
   - Check file path is correct
   - Check server logs for errors

3. **Chat doesn't use knowledge base?**
   - Check server logs for "📚 Retrieved X relevant documents"
   - Verify file was uploaded successfully
   - Check vectorstore directory: `chroma_db/user_{id}/`

4. **No documents retrieved?**
   - Wait longer after upload (processing takes time)
   - Check embeddings are loaded
   - Check vectorstore was created

## Automated Test

Run the full automated test:
```bash
python3 test_knowledge_base.py
```

This will:
1. Login/Register
2. Create test document
3. Upload document
4. Test 5 different questions
5. Verify responses contain knowledge base info
6. Clean up test file

