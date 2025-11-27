#!/bin/bash
# Script to update production .env file with SMTP configuration

PROD_HOST="16.52.149.96"
PROD_USER="ubuntu"
SSH_KEY="/home/swordfish/.ssh/swordfishproject.pem"
PROD_PATH="/home/ubuntu/chatbot"  # Adjust this to your actual production path

echo "=========================================="
echo "Updating Production .env File"
echo "=========================================="

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    exit 1
fi

echo "📡 Connecting to production server..."
echo "   Host: $PROD_USER@$PROD_HOST"
echo "   Path: $PROD_PATH"

# SSH into production and update .env
ssh -i "$SSH_KEY" "$PROD_USER@$PROD_HOST" << 'ENDSSH'
cd /home/ubuntu/chatbot || cd /var/www/chatbot || cd ~/chatbot

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating new .env file..."
    touch .env
fi

# Check if SMTP config already exists
if grep -q "SMTP_SERVER" .env; then
    echo "⚠️ SMTP configuration already exists in .env"
    echo "   Removing old SMTP config..."
    sed -i '/^SMTP_SERVER=/d' .env
    sed -i '/^SMTP_PORT=/d' .env
    sed -i '/^SMTP_USER=/d' .env
    sed -i '/^SMTP_PASSWORD=/d' .env
    sed -i '/^# SMTP Configuration/d' .env
fi

# Add SMTP configuration
echo "" >> .env
echo "# SMTP Configuration for Feedback Emails" >> .env
echo "SMTP_SERVER=smtp.gmail.com" >> .env
echo "SMTP_PORT=587" >> .env
echo "SMTP_USER=janfrancisisrael@gmail.com" >> .env
echo "SMTP_PASSWORD=goyz tpmm dtxm mjib" >> .env

echo "✅ SMTP configuration added to .env"

# Verify the configuration
echo ""
echo "📋 Current SMTP configuration in .env:"
grep "^SMTP_" .env || echo "   (No SMTP config found - this shouldn't happen)"

echo ""
echo "🔄 Restarting Flask application..."
# Try different restart methods
if systemctl is-active --quiet chatbot; then
    sudo systemctl restart chatbot
    echo "✅ Flask app restarted via systemctl"
elif pgrep -f "python3 app.py" > /dev/null; then
    pkill -f "python3 app.py"
    sleep 2
    cd /home/ubuntu/chatbot || cd /var/www/chatbot || cd ~/chatbot
    nohup python3 app.py > app.log 2>&1 &
    echo "✅ Flask app restarted manually"
else
    echo "⚠️ Flask app not running. Please start it manually."
fi

echo ""
echo "✅ Production .env update complete!"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully updated production .env"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Test email sending on production:"
    echo "   ssh -i $SSH_KEY $PROD_USER@$PROD_HOST 'cd $PROD_PATH && python3 test_email_sending.py'"
    echo ""
    echo "2. Test feedback form on production website"
else
    echo ""
    echo "=========================================="
    echo "❌ Failed to update production .env"
    echo "=========================================="
    exit 1
fi

