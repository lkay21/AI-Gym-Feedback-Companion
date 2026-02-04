# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip3 install -r app/requirements.txt
```

Or install Supabase separately:
```bash
pip3 install supabase==2.3.4
```

## Step 2: Set Up Supabase (If Not Done Already)

1. **Create a Supabase Project:**
   - Go to [https://supabase.com](https://supabase.com)
   - Sign up/Login
   - Click "New Project"
   - Fill in project details and create

2. **Get Your Credentials:**
   - In Supabase Dashboard → **Settings** → **API**
   - Copy your **Project URL** and **anon/public key**

3. **Configure Environment Variables:**
   - Make sure you have a `.env` file in the project root
   - Add your Supabase credentials:
     ```env
     SUPABASE_URL=https://your-project-id.supabase.co
     SUPABASE_ANON_KEY=your-anon-key-here
     SECRET_KEY=your-secret-key-here
     GEMINI_API_KEY=your-gemini-api-key-here
     ```

4. **Optional - Disable Email Confirmation (for testing):**
   - In Supabase Dashboard → **Authentication** → **Settings**
   - Disable "Enable email confirmations"

## Step 3: Run the Application

```bash
python3 -m app.main
```

The server will start on **http://localhost:5001**

## Step 4: Test It

1. Open your browser and go to: **http://localhost:5001/**
2. Click "Sign up" to create a new account
3. Fill in:
   - Email
   - Username
   - Password (min 6 characters)
4. Click "Sign Up"
5. You'll be redirected to the chat page on success

## Troubleshooting

### "Supabase credentials not found" error
- Make sure your `.env` file exists in the project root
- Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly

### "ModuleNotFoundError: No module named 'supabase'"
- Run: `pip3 install supabase==2.3.4`

### Port 5001 already in use
- The app is configured to use port 5001
- If it's in use, you can change it in `app/main.py` line 175: `app.run(debug=True, port=5001)`

### Email confirmation required
- If you see a message about email confirmation, either:
  - Check your email and click the confirmation link, OR
  - Disable email confirmation in Supabase settings (for testing)


