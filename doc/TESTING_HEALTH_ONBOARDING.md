# Testing Health Onboarding Flow

The health onboarding flow: **fixed health stats from HealthData → ask fitness goal → store in HealthData → 2–3 AI follow-up questions → store Q&A in HealthData context**.

---

## Prerequisites

- **.env** with `GEMINI_API_KEY` (and AWS/DynamoDB if using real DB)
- **DynamoDB** tables exist: `python -m app.dynamodb_module.init_tables` (if using AWS)
- Or use **LocalStack** / local DynamoDB if you use it

---

## 1. Browser test (recommended)

1. **Start the app**
   ```bash
   cd /Users/aryansrivastava/AI-Gym-Feedback-Companion
   python -m app.main
   ```
   App runs at **http://127.0.0.1:5001**.

2. **Log in**
   - Open http://127.0.0.1:5001
   - Sign in (Supabase auth sets `session['user_id']`)

3. **Open Chat**
   - Go to http://127.0.0.1:5001/chat

4. **Walk through the flow**
   - **First message:** AI shows “Here’s what I have on file…” (from HealthData) and asks for your fitness goal.
   - **You:** e.g. “Lose weight” or “Build muscle”.
   - **AI:** Saves goal to HealthData and asks the first follow-up question.
   - **You:** Answer; AI asks the next (2–3 questions total).
   - **After last answer:** AI says something like “I’ve saved your answers…” and `phase` is `complete`; next messages go to normal chat.

5. **Optional: add fixed stats first**
   - Create a health profile record with age/height/weight so the intro shows real stats:
   - After login, call `POST /api/profile/health` with body:
     ```json
     {
       "timestamp": "health_profile",
       "age": 30,
       "height": 175,
       "weight": 70,
       "gender": "male"
     }
     ```
   - Reload /chat; the first AI message should include these stats.

---

## 2. API test with curl (with session cookie)

1. Start the app and **log in in the browser** (same origin).
2. In DevTools → Application → Cookies, copy the **session** cookie value for `127.0.0.1:5001`.
3. Or use a browser extension to copy the full `Cookie` header.

Then:

```bash
# Replace YOUR_SESSION_COOKIE with the actual value
COOKIE="session=YOUR_SESSION_COOKIE"
BASE="http://127.0.0.1:5001"

# 1) Get intro (fixed stats + ask goal)
curl -s -X POST "$BASE/api/chat/health-onboarding" \
  -H "Content-Type: application/json" \
  -d '{"message":""}' \
  -b "$COOKIE" | jq .

# 2) Send fitness goal
curl -s -X POST "$BASE/api/chat/health-onboarding" \
  -H "Content-Type: application/json" \
  -d '{"message":"lose weight"}' \
  -b "$COOKIE" | jq .

# 3) Answer follow-up questions (repeat for each question)
curl -s -X POST "$BASE/api/chat/health-onboarding" \
  -H "Content-Type: application/json" \
  -d '{"message":"3 days per week"}' \
  -b "$COOKIE" | jq .
```

Each response should include `response`, `phase` (`ask_goal` → `follow_up` → `complete`), and `success: true`.

---

## 3. Verify data in DynamoDB

After completing the flow:

```bash
python scripts/check_database.py
```

Or in code: get the health profile item for your user:

- **Table:** `health_data` (or `DYNAMODB_HEALTH_DATA_TABLE`)
- **Key:** `user_id` = your user id, `timestamp` = `"health_profile"`
- **Fields:** `age`, `height`, `weight`, `gender`, `fitness_goal`, `context` (with `qa_pairs` and `pending_questions`)

---

## 4. Run the automated test script (no real login)

The script `scripts/test_health_onboarding.py` uses a Flask test client and a fake session so you can test the endpoint without logging in (and optionally without DynamoDB if you mock it). Run:

```bash
python scripts/test_health_onboarding.py
```

See the script for requirements (e.g. DynamoDB available or mocked).
