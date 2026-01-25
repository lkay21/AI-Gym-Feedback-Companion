# AI Gym Feedback Companion - React Native Mobile App

## Setup Instructions

### 1. Install Dependencies

```bash
cd mobile
npm install
```

Or with yarn:
```bash
cd mobile
yarn install
```

### 2. Install Expo CLI (if not already installed)

```bash
npm install -g expo-cli
```

### 3. Update API Base URL

Edit `src/services/api.js` and update the `API_BASE_URL`:

- **iOS Simulator**: `http://localhost:5001`
- **Android Emulator**: `http://10.0.2.2:5001`
- **Physical Device**: `http://YOUR_COMPUTER_IP:5001` (e.g., `http://192.168.1.100:5001`)

To find your computer's IP:
- Mac/Linux: `ifconfig | grep "inet "`
- Windows: `ipconfig`

### 4. Start the Flask Backend

In the project root:
```bash
python3 -m app.main
```

### 5. Start the React Native App

```bash
cd mobile
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

## Features

- ✅ Login screen with username/password
- ✅ Signup screen with email, username, password, and confirm password
- ✅ Form validation with error messages
- ✅ Password visibility toggle
- ✅ Loading states
- ✅ Success/error alerts
- ✅ Navigation between screens
- ✅ AsyncStorage for user session
- ✅ Connected to Flask backend API

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

## API Endpoints Used

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/check` - Check session
- `POST /api/chat` - Send chat message

## Troubleshooting

### "Network request failed"
- Make sure Flask backend is running
- Check API_BASE_URL matches your setup
- For physical device, ensure phone and computer are on same WiFi network
- Check firewall settings

### "Module not found"
- Run `npm install` again
- Clear cache: `npm start -- --clear`

### Expo Go app issues
- Make sure you're using the latest Expo Go app
- Clear Expo Go cache and restart

