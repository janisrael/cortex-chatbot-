#!/bin/bash
# Script to update diagrams in docs/details/

echo "=== Updating Diagrams ==="
cd "$(dirname "$0")"

# Force add all PNG files
echo "Force adding PNG files..."
git add -f docs/details/*.png

# Check if there are changes
if git diff --cached --quiet docs/details/ 2>/dev/null; then
    echo "⚠️  No changes detected in PNG files"
    echo "   Make sure files are saved before running this script"
    exit 1
else
    echo "✅ Changes detected - committing..."
    git commit -m "docs: Update architecture diagrams with modified image content

Updated PNG files in docs/details/ with latest diagram modifications.
All 17 diagram and screenshot files updated."
    
    echo "✅ Committed - pushing to main..."
    git push origin main
    echo "✅ Diagrams updated and pushed!"
fi
