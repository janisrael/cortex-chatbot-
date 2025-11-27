#!/bin/bash
# Script to update nginx configuration to disable ALL caching for Cortex AI

NGINX_CONFIG="/etc/nginx/sites-available/cortex.janisrael.com"
BACKUP_FILE="/etc/nginx/sites-available/cortex.janisrael.com.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Updating Nginx Configuration - Disable ALL Caching"
echo "=========================================="

# Backup current config
echo "Creating backup: $BACKUP_FILE"
sudo cp "$NGINX_CONFIG" "$BACKUP_FILE"

# Create new config with no caching
sudo tee "$NGINX_CONFIG" > /dev/null << 'EOF'
server {
    listen 80;
    listen 443 ssl http2;
    server_name cortex.janisrael.com;
    
    # Use existing SSL certificate
    ssl_certificate /etc/letsencrypt/live/airepubliq.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/airepubliq.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:6002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Disable ALL caching
        proxy_cache_bypass 1;
        proxy_no_cache 1;
        proxy_set_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0";
        proxy_set_header Pragma "no-cache";
        proxy_set_header Expires "0";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /var/www/portfolio/cortex/static;
        
        # Disable ALL caching for static files
        expires -1;
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0, private";
        add_header Pragma "no-cache";
        add_header Expires "0";
        add_header X-Accel-Expires "0";
        
        # Disable nginx caching
        proxy_cache_bypass 1;
        proxy_no_cache 1;
        
        access_log off;
    }

    client_max_body_size 20M;
    access_log /var/log/nginx/cortex-access.log;
    error_log /var/log/nginx/cortex-error.log;
}
EOF

echo ""
echo "✅ Nginx configuration updated"
echo ""
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Nginx configuration is valid"
    echo ""
    echo "Reloading nginx..."
    sudo systemctl reload nginx
    echo ""
    echo "=========================================="
    echo "✅ Nginx updated - ALL caching disabled"
    echo "=========================================="
else
    echo ""
    echo "❌ Nginx configuration test failed!"
    echo "Restoring backup..."
    sudo cp "$BACKUP_FILE" "$NGINX_CONFIG"
    echo "Backup restored. Please check the configuration manually."
    exit 1
fi

