# AI Gym Feedback Companion - React Native Mobile App

## Setup Instructions

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Update API Base URL

Edit `src/services/api.js` and update the `API_BASE_URL`:

- **iOS Simulator**: `http://localhost:5001`
- **Android Emulator**: `http://10.0.2.2:5001`
- **Physical Device**: `http://YOUR_COMPUTER_IP:5001`

To find your computer's IP:
```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

### 3. Start the Flask Backend

In the project root:
```bash
python3 -m app.main
```

### 4. Start the React Native App

```bash
cd mobile
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

## Features

✅ **Login Screen**
- Username and password inputs
- Form validation
- Password visibility toggle
- Loading states
- Error handling
- Navigation to signup
- Google login button (placeholder)

✅ **Signup Screen**
- Email, username, password, and confirm password inputs
- Comprehensive form validation
- Password visibility toggles
- Loading states
- Error handling
- Navigation to login
- Google signup button (placeholder)

✅ **API Integration**
- Connected to Flask backend (`/auth/register`, `/auth/login`)
- AsyncStorage for session management
- Error handling with user-friendly messages

✅ **Design**
- Matches Figma design exactly
- Purple gradient background (#7c3aed to #4c1d95)
- Clean, modern mobile UI
- Smooth animations

## Project Structure

```
mobile/
├── App.js                 # Main app entry point with navigation
├── package.json          # Dependencies
├── app.json             # Expo configuration
├── babel.config.js      # Babel configuration
└── src/
    ├── screens/
    │   ├── LoginScreen.js    # Login screen component
    │   ├── SignupScreen.js   # Signup screen component
    │   └── ChatScreen.js     # Chat screen (placeholder)
    └── services/
        └── api.js            # API service for backend communication
```

## Troubleshooting

### "Network request failed"
- Make sure Flask backend is running on port 5001
- Check API_BASE_URL matches your setup
- For physical device, ensure phone and computer are on same WiFi network
- Check firewall settings

### "Module not found"
- Run `npm install` again
- Clear cache: `npm start -- --clear`

### Expo Go app issues
- Make sure you're using the latest Expo Go app
- Clear Expo Go cache and restart
