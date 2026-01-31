# Debugging Setup for React Native App

## Hermes Engine

Hermes is now enabled in `app.json`. This is the JavaScript engine used by React Native for better performance and debugging.

## Debugging Options

### Option 1: Use React Native Debugger (Recommended)

1. **Install React Native Debugger:**
   ```bash
   brew install --cask react-native-debugger
   ```

2. **Start the debugger:**
   - Open React Native Debugger app
   - Or press `Cmd+D` (iOS) / `Cmd+M` (Android) in the app
   - Select "Debug"

### Option 2: Use Chrome DevTools

1. **In your app:**
   - Shake device or press `Cmd+D` (iOS) / `Cmd+M` (Android)
   - Select "Debug"

2. **Chrome will open automatically** at `http://localhost:8081/debugger-ui/`

3. **Open Chrome DevTools:**
   - Press `Cmd+Option+I` (Mac) or `F12` (Windows/Linux)

### Option 3: Use Flipper (Advanced)

Flipper is Facebook's debugging platform:
```bash
brew install --cask flipper
```

## Common Debugging Issues

### "No compatible apps connected"

**Solution 1:** Make sure Hermes is enabled (already done in app.json)

**Solution 2:** Restart Metro bundler:
```bash
npm start -- --reset-cache
```

**Solution 3:** Rebuild the app:
- Close the app completely
- Restart Expo: `npm start`
- Reload the app

### "JavaScript Debugging can only be used with Hermes"

Hermes is now enabled. If you still see this:
1. Close the app completely
2. Clear cache: `npm start -- --clear`
3. Rebuild and reload

### Debugger not connecting

1. **Check Metro bundler is running:**
   - Should see "Metro waiting on exp://..."

2. **Check network:**
   - Device and computer on same network
   - Firewall not blocking port 8081

3. **Try alternative:**
   - Use React Native Debugger instead of Chrome
   - Or use console.log for simple debugging

## Quick Debugging Tips

### Console Logging
```javascript
console.log('Debug:', variable);
console.warn('Warning:', message);
console.error('Error:', error);
```

### React DevTools
```bash
npm install -g react-devtools
react-devtools
```

### Network Debugging
Check API calls in:
- Chrome DevTools → Network tab
- React Native Debugger → Network tab

## Disable Debugging

If you want to disable debugging warnings:
- The error is just informational
- App will still work without debugger
- You can ignore it if not actively debugging


