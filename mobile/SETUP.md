# React Native Mobile App Setup

## Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Expo CLI
- iOS Simulator (Mac) or Android Emulator, or Expo Go app on your phone

### Installation Steps

1. **Navigate to mobile directory:**
   ```bash
   cd mobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Update API URL in `src/services/api.js`:**
   - For iOS Simulator: `http://localhost:5001`
   - For Android Emulator: `http://10.0.2.2:5001`
   - For Physical Device: `http://YOUR_COMPUTER_IP:5001`

4. **Start Flask backend** (in project root):
   ```bash
   python3 -m app.main
   ```

5. **Start React Native app:**
   ```bash
   npm start
   ```

6. **Run on device:**
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on your phone

## Features Implemented

✅ **Login Screen**
- Username and password inputs
- Form validation
- Password visibility toggle
- Loading states
- Error handling
- Navigation to signup

✅ **Signup Screen**
- Email, username, password, and confirm password inputs
- Comprehensive form validation
- Password visibility toggles
- Loading states
- Error handling
- Navigation to login

✅ **API Integration**
- Connected to Flask backend
- AsyncStorage for session management
- Error handling with user-friendly messages

✅ **Navigation**
- Stack navigation between screens
- Smooth transitions

## Project Structure

```
mobile/
├── App.js                    # Main app with navigation
├── package.json             # Dependencies
├── app.json                # Expo config
├── babel.config.js         # Babel config
└── src/
    ├── screens/
    │   ├── LoginScreen.js
    │   ├── SignupScreen.js
    │   └── ChatScreen.js
    └── services/
        └── api.js          # API service
```

## Testing

1. **Test Signup:**
   - Fill in email, username, password, confirm password
   - Submit and verify success message
   - Check that user is redirected to Chat screen

2. **Test Login:**
   - Use credentials from signup
   - Submit and verify success
   - Check session persistence

3. **Test Validation:**
   - Try submitting empty fields
   - Try invalid email format
   - Try mismatched passwords
   - Verify error messages appear

## Troubleshooting

**"Network request failed"**
- Ensure Flask backend is running
- Check API_BASE_URL in `src/services/api.js`
- For physical device, ensure same WiFi network

**"Module not found"**
- Run `npm install` again
- Clear cache: `npm start -- --clear`

**Expo issues**
- Update Expo Go app to latest version
- Clear Expo cache

