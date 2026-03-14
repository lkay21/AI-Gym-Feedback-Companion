#!/bin/bash
# Quick fix script for EMFILE error

echo "Fixing EMFILE error..."

# Install Watchman if Homebrew is available
if command -v brew &> /dev/null; then
    echo "Installing Watchman (this may take a few minutes)..."
    brew install watchman
else
    echo "Homebrew not found. Install it first:"
    echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "Then run: brew install watchman"
fi

# Update React Native version
echo "Updating React Native version..."
npm install react-native@0.73.6

# Clear caches
echo "Clearing caches..."
rm -rf .expo
rm -rf node_modules/.cache

echo "Done! Now try: npm start -- --reset-cache"


