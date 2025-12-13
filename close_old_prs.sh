#!/bin/bash

# Script to close old pull requests on GitHub
# Usage: ./close_old_prs.sh
# Requires: GITHUB_TOKEN environment variable or GitHub CLI (gh)

REPO="janisrael/cortex-chatbot-"

echo "🔍 Fetching pull requests for $REPO..."

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ Using GitHub CLI..."
    
    # List all open PRs
    PRS=$(gh pr list --repo $REPO --state open --json number,title --jq '.[] | "\(.number)|\(.title)"')
    
    if [ -z "$PRS" ]; then
        echo "✅ No open pull requests found!"
        exit 0
    fi
    
    echo "📋 Found open pull requests:"
    echo "$PRS" | while IFS='|' read -r number title; do
        echo "  - PR #$number: $title"
    done
    
    echo ""
    read -p "Do you want to close all these PRs? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$PRS" | while IFS='|' read -r number title; do
            echo "🚫 Closing PR #$number: $title"
            gh pr close $number --repo $REPO --comment "Closing old pull request"
        done
        echo "✅ All pull requests closed!"
    else
        echo "❌ Cancelled."
    fi
    
elif [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ Using GitHub API with token..."
    
    # Get all open PRs
    PRS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO/pulls?state=open" | \
        jq -r '.[] | "\(.number)|\(.title)"')
    
    if [ -z "$PRS" ]; then
        echo "✅ No open pull requests found!"
        exit 0
    fi
    
    echo "📋 Found open pull requests:"
    echo "$PRS" | while IFS='|' read -r number title; do
        echo "  - PR #$number: $title"
    done
    
    echo ""
    read -p "Do you want to close all these PRs? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$PRS" | while IFS='|' read -r number title; do
            echo "🚫 Closing PR #$number: $title"
            curl -X PATCH \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Accept: application/vnd.github.v3+json" \
                "https://api.github.com/repos/$REPO/pulls/$number" \
                -d '{"state":"closed"}' > /dev/null 2>&1
        done
        echo "✅ All pull requests closed!"
    else
        echo "❌ Cancelled."
    fi
    
else
    echo "❌ Error: GitHub CLI (gh) or GITHUB_TOKEN required"
    echo ""
    echo "Option 1: Install GitHub CLI and authenticate:"
    echo "  brew install gh  # macOS"
    echo "  gh auth login"
    echo ""
    echo "Option 2: Set GITHUB_TOKEN environment variable:"
    echo "  export GITHUB_TOKEN=your_token_here"
    echo ""
    echo "Option 3: Close PRs manually at:"
    echo "  https://github.com/$REPO/pulls"
    exit 1
fi




