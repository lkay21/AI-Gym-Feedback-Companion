# Supabase Authentication Setup

This application uses Supabase for user authentication. Follow these steps to set it up:

## 1. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Your project name
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region
5. Click "Create new project" and wait for it to initialize

## 2. Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. You'll find:
   - **Project URL** (SUPABASE_URL): `https://xxxxx.supabase.co`
   - **anon/public key** (SUPABASE_ANON_KEY): A long string starting with `eyJ...`

## 3. Configure Environment Variables

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

## 4. Install Dependencies

```bash
pip3 install -r app/requirements.txt
```

Or install Supabase separately:
```bash
pip3 install supabase==2.3.4
```

## 5. Configure Supabase Auth Settings (Optional)

In your Supabase dashboard:
1. Go to **Authentication** → **Settings**
2. Configure:
   - **Site URL**: `http://localhost:5001` (for development)
   - **Redirect URLs**: Add `http://localhost:5001/**`
   - **Email Auth**: Enable email/password authentication

## 6. Test the Setup

1. Start the server:
   ```bash
   python3 -m app.main
   ```

2. Go to `http://localhost:5001/`
3. Try signing up with a new account
4. Check your Supabase dashboard → **Authentication** → **Users** to see the new user

## Features

- ✅ Email/Password authentication
- ✅ Username stored in user metadata
- ✅ Session management with access/refresh tokens
- ✅ Secure password hashing (handled by Supabase)
- ✅ User registration and login
- ✅ Logout functionality
- ✅ Session checking

## Notes

- Users are stored in Supabase's `auth.users` table
- Username is stored in `user_metadata.username`
- Passwords are securely hashed by Supabase
- Access tokens are stored in Flask sessions


