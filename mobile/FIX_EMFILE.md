# Fix "EMFILE: too many open files" Error

This error occurs when macOS hits the file watcher limit. Here are solutions:

## Solution 1: Increase File Limit (Recommended)

Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
# Increase file watcher limit for React Native/Expo
ulimit -n 4096
```

Then restart your terminal or run:
```bash
source ~/.zshrc
```

## Solution 2: Install Watchman (Best for Development)

Watchman is Facebook's file watching service that's more efficient:

```bash
# Install via Homebrew
brew install watchman

# Or if you don't have Homebrew, install it first:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Solution 3: Use Watchman Config

The `.watchmanconfig` file has been created. After installing watchman, restart Metro:

```bash
npm start -- --reset-cache
```

## Solution 4: Temporary Fix (Quick)

Run this before starting Expo:

```bash
ulimit -n 4096
npm start
```

## Solution 5: Clean and Restart

Sometimes clearing caches helps:

```bash
# Clear Metro cache
npm start -- --clear

# Or clear all caches
rm -rf node_modules
rm -rf .expo
npm install
npm start
```

## After Fixing

1. Update React Native version:
   ```bash
   npm install react-native@0.73.6
   ```

2. Restart Metro bundler:
   ```bash
   npm start -- --reset-cache
   ```

## Verify Fix

Check your file limit:
```bash
ulimit -n
```

Should show 4096 or higher.

