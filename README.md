<<<<<<< HEAD
# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.
=======
# AI Gym Feedback Companion

A fitness-focused personal trainer AI application with user profiles and health data tracking.

## Team
- Ava Lyall
- Aryan Srivastava
- Logan Kay
- Mythrai Kapidi

## Quick Start

### Prerequisites
- Python 3.8+
- AWS Account (for DynamoDB)
- Supabase Account (for authentication)
- Google Gemini API Key

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see `.env.example` or `AWS_SETUP.md`)

4. Initialize DynamoDB tables:
```bash
python -m app.dynamodb_module.init_tables
```

5. Run the application:
```bash
python -m app.main
```

## Documentation

- **[AWS Quick Start](AWS_QUICK_START.md)** - 5-minute AWS setup guide
- **[AWS Setup Guide](AWS_SETUP.md)** - Complete guide for setting up AWS DynamoDB
- **[Check Tables Guide](CHECK_TABLES.md)** - How to verify DynamoDB tables
- **[Design Document](doc/Design%20Document.pdf)** - Project design documentation
- **[Development Plan](doc/Final%20Software%20Development%20Plan.pdf)** - Software development plan

## Project Structure

```
app/
  auth_module/          # Supabase authentication
  profile_module/       # User profiles and health data API
  dynamodb_module/      # AWS DynamoDB client and utilities
  static/              # CSS and JavaScript files
  templates/           # HTML templates
```

## Features

- User authentication via Supabase
- User profile management (age, height, weight, fitness goals)
- Health data tracking (workouts, activity metrics)
- AI-powered fitness advice via Google Gemini
- RESTful API for profile and health data

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/check` - Check session status

### User Profile
- `GET /api/profile/user` - Get user profile
- `POST /api/profile/user` - Create/update profile
- `PUT /api/profile/user` - Update profile
- `DELETE /api/profile/user` - Delete profile

### Health Data
- `POST /api/profile/health` - Create health data entry
- `GET /api/profile/health` - Get health data (with filters)
- `PUT /api/profile/health/<timestamp>` - Update entry
- `DELETE /api/profile/health/<timestamp>` - Delete entry
>>>>>>> origin/develop
