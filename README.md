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
