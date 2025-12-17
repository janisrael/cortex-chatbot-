#!/bin/bash

# Script to close pull requests using GitHub API
# Usage: GITHUB_TOKEN=your_token ./close_prs_api.sh

REPO="janisrael/cortex-chatbot-"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is required"
    echo ""
    echo "To create a GitHub token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token' -> 'Generate new token (classic)'"
    echo "3. Give it a name (e.g., 'Close PRs')"
    echo "4. Select scope: 'public_repo' (or 'repo' for private repos)"
    echo "5. Click 'Generate token'"
    echo "6. Copy the token and run:"
    echo "   export GITHUB_TOKEN=your_token_here"
    echo "   ./close_prs_api.sh"
    exit 1
fi

echo "🔍 Fetching open pull requests for $REPO..."

# Get all open PRs
PRS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/pulls?state=open")

# Check if we got valid JSON
if echo "$PRS" | jq empty 2>/dev/null; then
    PR_COUNT=$(echo "$PRS" | jq '. | length')
    
    if [ "$PR_COUNT" -eq 0 ]; then
        echo "✅ No open pull requests found!"
        exit 0
    fi
    
    echo "📋 Found $PR_COUNT open pull request(s):"
    echo ""
    echo "$PRS" | jq -r '.[] | "  PR #\(.number): \(.title)"'
    echo ""
    
    read -p "Do you want to close all these PRs? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$PRS" | jq -r '.[] | "\(.number)|\(.title)"' | while IFS='|' read -r number title; do
            echo "🚫 Closing PR #$number: $title"
            
            # Close the PR
            RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Accept: application/vnd.github.v3+json" \
                -H "Content-Type: application/json" \
                "https://api.github.com/repos/$REPO/pulls/$number" \
                -d '{"state":"closed"}')
            
            HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
            BODY=$(echo "$RESPONSE" | head -n-1)
            
            if [ "$HTTP_CODE" -eq 200 ]; then
                echo "   ✅ Successfully closed PR #$number"
            else
                echo "   ❌ Failed to close PR #$number (HTTP $HTTP_CODE)"
                echo "$BODY" | jq -r '.message' 2>/dev/null || echo "$BODY"
            fi
        done
        echo ""
        echo "✅ Done!"
    else
        echo "❌ Cancelled."
    fi
else
    echo "❌ Error: Failed to fetch pull requests"
    echo "Response: $PRS"
    echo ""
    echo "Check your GITHUB_TOKEN and try again."
    exit 1
fi



