# Production Environment Variables Update

## SMTP Configuration for Feedback Emails

Add the following to your production `.env` file:

```bash
# SMTP Configuration for Feedback Emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=janfrancisisrael@gmail.com
SMTP_PASSWORD=goyz tpmm dtxm mjib
```

## Steps to Update Production .env

### Option 1: SSH into Production Server

```bash
# SSH into your production server
ssh -i /home/swordfish/.ssh/swordfishproject.pem ubuntu@16.52.149.96

# Navigate to project directory
cd /path/to/chatbot

# Edit .env file
nano .env

# Add the SMTP configuration lines above
# Save and exit (Ctrl+X, then Y, then Enter)

# Restart Flask application
sudo systemctl restart chatbot
# OR if using screen/tmux:
# pkill -f "python3 app.py"
# python3 app.py
```

### Option 2: Using SCP to Copy .env

```bash
# From local machine, copy .env to production
scp -i /home/swordfish/.ssh/swordfishproject.pem .env ubuntu@16.52.149.96:/path/to/chatbot/.env

# Then SSH and restart Flask
ssh -i /home/swordfish/.ssh/swordfishproject.pem ubuntu@16.52.149.96
cd /path/to/chatbot
sudo systemctl restart chatbot
```

### Option 3: Direct Edit via SSH

```bash
ssh -i /home/swordfish/.ssh/swordfishproject.pem ubuntu@16.52.149.96 << 'EOF'
cd /path/to/chatbot
cat >> .env << 'ENVEOF'

# SMTP Configuration for Feedback Emails
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=janfrancisisrael@gmail.com
SMTP_PASSWORD=goyz tpmm dtxm mjib
ENVEOF
sudo systemctl restart chatbot
EOF
```

## Verify SMTP Configuration

After updating, test the email sending:

```bash
# On production server
cd /path/to/chatbot
python3 test_email_sending.py
```

## Important Notes

- **Never commit .env to Git** - It's already in .gitignore
- **Restart Flask app** after updating .env for changes to take effect
- **Gmail App Password**: If using Gmail, make sure you're using an App Password, not your regular password
- **Firewall**: Ensure port 587 (SMTP) is not blocked on production server

## Troubleshooting

If email sending fails:

1. Check SMTP credentials are correct
2. Verify Gmail App Password is used (not regular password)
3. Check server logs for SMTP errors
4. Test with: `python3 test_email_sending.py`
5. Check firewall allows outbound connections on port 587

