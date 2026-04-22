# AI Gym Feedback Companion - Mobile App

React Native mobile application built with Expo for the AI Gym Feedback Companion project.

## Prerequisites

Before running the mobile app, ensure you have the following installed:

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **npm** or **yarn** - Comes with Node.js
- **Expo CLI** (optional, but recommended) - Install globally with `npm install -g expo-cli`
- **iOS Simulator** (Mac only) - Comes with Xcode
- **Android Emulator** - Install via Android Studio
- **Expo Go app** (for physical devices) - [iOS](https://apps.apple.com/app/expo-go/id982107779) | [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)

## Installation

1. **Navigate to the mobile directory:**
   ```bash
   cd mobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```
   
   Or if you prefer yarn:
   ```bash
   yarn install
   ```

3. **Start the Flask backend** (from project root):
   ```bash
   # From the project root directory
   python3 -m app.main
   ```
   
   The backend should be running on `http://localhost:5001`

## Configuration

### API URL Configuration

The app needs to connect to your Flask backend. Update the API URL in `src/services/api.js` based on your setup:

- **iOS Simulator**: `http://localhost:5001` (default)
- **Android Emulator**: `http://10.0.2.2:5001`
- **Physical Device**: `http://YOUR_COMPUTER_IP:5001`

To find your computer's IP address:
- **Mac/Linux**: Run `ifconfig` or `ipconfig getifaddr en0`
- **Windows**: Run `ipconfig` and look for IPv4 Address

Example for physical device:
```javascript
const API_BASE_URL = 'http://192.168.1.100:5001'; // Replace with your IP
```

## Running the App

### Start the Expo Development Server

```bash
npm start
```

Or:
```bash
expo start
```

This will open the Expo DevTools in your browser and display a QR code.

### Run on Different Platforms

**iOS Simulator (Mac only):**
```bash
npm run ios
# or
expo start --ios
```

**Android Emulator:**
```bash
npm run android
# or
expo start --android
```

**Web Browser:**
```bash
npm run web
# or
expo start --web
```

**Physical Device:**
1. Install the **Expo Go** app on your phone
2. Scan the QR code displayed in the terminal or browser
3. The app will load on your device

## Available Scripts

- `npm start` - Start the Expo development server
- `npm run ios` - Start and open in iOS simulator
- `npm run android` - Start and open in Android emulator
- `npm run web` - Start and open in web browser

## Project Structure

```
mobile/
├── App.js                 # Main app entry point with navigation
├── app.json              # Expo configuration
├── package.json          # Dependencies and scripts
├── babel.config.js       # Babel configuration
├── metro.config.js       # Metro bundler configuration
└── src/
    ├── screens/
    │   ├── LoginScreen.js    # User login screen
    │   ├── SignupScreen.js   # User registration screen
    │   └── ChatScreen.js     # Chat interface screen
    └── services/
        └── api.js            # API service for backend communication
```

## Features

- ✅ **User Authentication**
  - Login with username and password
  - User registration with email, username, and password
  - Session management with AsyncStorage

- ✅ **Navigation**
  - Stack navigation between screens
  - Smooth transitions

- ✅ **Backend Integration**
  - Connected to Flask backend
  - Error handling with user-friendly messages
  - AsyncStorage for session persistence

## Troubleshooting

### "Network request failed" error
- Make sure the Flask backend is running on port 5001
- Check that the API URL in `src/services/api.js` matches your setup
- For physical devices, ensure your phone and computer are on the same network
- Check firewall settings that might be blocking the connection

### "Module not found" errors
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Expo cache: `expo start -c` or `npm start -- --clear`

### Port already in use
- Kill the process using port 8081 (default Expo port):
  ```bash
  # Mac/Linux
  lsof -ti:8081 | xargs kill -9
  
  # Or use a different port
  expo start --port 8082
  ```

### iOS Simulator not opening
- Make sure Xcode is installed
- Open Xcode and accept the license agreement
- Run `xcode-select --install` if needed

### Android Emulator not opening
- Make sure Android Studio is installed
- Create and start an Android Virtual Device (AVD) from Android Studio
- Ensure `ANDROID_HOME` environment variable is set

### Expo Go app not connecting
- Ensure your phone and computer are on the same Wi-Fi network
- Try using the tunnel connection: `expo start --tunnel`
- Check that your firewall isn't blocking the connection

## Development Tips

- Use **React Native Debugger** for better debugging experience
- Enable **Fast Refresh** (enabled by default) for instant code updates
- Use **Expo DevTools** (opens automatically) to view logs and performance
- Check the terminal for any warnings or errors

## Dependencies

Key dependencies:
- `expo` - Expo framework
- `react-native` - React Native core
- `@react-navigation/native` - Navigation library
- `@react-navigation/stack` - Stack navigator
- `@react-native-async-storage/async-storage` - Local storage
- `axios` - HTTP client (via fetch API)

See `package.json` for the complete list of dependencies.

## Building for Production

For production builds, refer to the [Expo documentation](https://docs.expo.dev/build/introduction/):
- **iOS**: `expo build:ios`
- **Android**: `expo build:android`

Or use EAS Build (recommended):
- Install EAS CLI: `npm install -g eas-cli`
- Configure: `eas build:configure`
- Build: `eas build --platform ios` or `eas build --platform android`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the [Expo documentation](https://docs.expo.dev/)
3. Check the main project README in the root directory
