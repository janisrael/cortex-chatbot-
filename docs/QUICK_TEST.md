# Quick Knowledge Base Test

## Simple Test Commands (Run One at a Time)

### 1. Start Server (Terminal 1)
```bash
cd /run/media/swordfish/Projects/development/chatbot
python3 app.py
```

### 2. Test Upload & Chat (Terminal 2)

**Step 1: Create test file**
```bash
echo "TechSolutions Inc. offers AI chatbot development. Contact: contact@techsolutions.com. Pricing: $99/month for Basic plan." > /tmp/test.txt
```

**Step 2: Register/Login (use browser or curl)**
- Go to: http://localhost:6001/register
- Create account: test@test.com / test123

**Step 3: Upload file (use browser)**
- Go to dashboard
- Upload /tmp/test.txt

**Step 4: Test chat**
- Ask: "What services does TechSolutions offer?"
- Should mention: "AI chatbot development"
- Ask: "What is the contact email?"
- Should mention: "contact@techsolutions.com"

## Or Use Python Test Script

```bash
python3 test_knowledge_base.py
```

This does everything automatically.

