# Reference — AI Gym Feedback Companion

## System Structure

Components below map to folders under `app/` unless noted. The running server is built in **`app/main.py`** (`create_app()`).

### 1. Application shell (`app/main.py`)

- **Flask** hosts HTML pages and JSON APIs.
- **Blueprints** (route groups) mounted at startup:
  - `/auth/*` → `auth_module`
  - `/api/chat/*` → `chat_module`
  - `/api/profile/*` → `profile_module`
  - `/api/cv/*` → `exercises` (computer vision)
- **Sessions:** cookie-based; after Supabase login the server stores tokens and `user_id` for later API calls.
- **CORS:** enabled for Expo dev URLs (`localhost:8081`, `19006`, etc.) on `/auth/*` and `/api/*`, with credentials so the mobile/web client can send cookies.
- **Startup:** loads fitness benchmark data via `app/fitness/benchmark_loader.py` into `app.benchmarks` (fails fast if data is missing).
- **Pages:** `/` → login template, `/chat` → chat template; static JS/CSS under `app/static/`, HTML under `app/templates/`.

### 2. Authentication (`app/auth_module/`)

- **Supabase** (`supabase_client.py`) performs register/login using `SUPABASE_URL` and `SUPABASE_ANON_KEY`.
- **Routes** validate input, call Supabase, then set the Flask session (`access_token`, `refresh_token`, `user_id`, `email`, `username`).
- **Logout** clears Supabase session when possible and always clears the Flask session.
- On register/login, the app tries to ensure a matching **DynamoDB profile row** exists (via the profile service) so downstream APIs have something to attach data to.

### 3. Profile & health data (`app/profile_module/` + `app/dynamodb_module/`)

- **HTTP layer** (`routes.py`): CRUD for `/api/profile/user` and `/api/profile/health`; every call expects an authenticated session and scopes data to `session["user_id"]`.
- **Services** (`service.py`): `ProfileService` and `HealthDataService` read/write DynamoDB through the shared client.
- **Models** (`models.py`): `UserProfile` is minimal (user id only in DynamoDB); `HealthData` holds demographics, goal, and JSON **context** (onboarding state, Q&A).
- **DynamoDB client** (`dynamodb_module/client.py`): table names from env (defaults: `user_profiles`, `health_data`, `fitness_plan`), and `init_tables.py` to create tables once per environment.

### 4. Chat, onboarding & fitness plans (`app/chat_module/`, `app/fitness/`, `app/fitness_plan_module/`)

- **Routes** (`chat_module/routes.py`): `/api/chat/health-onboarding` (guided questions), `/api/chat` and `/api/chat/llm` (Gemini replies), `/api/chat/plan` (returns a structured calendar built from stored plan rows), `GET /api/chat/health` (config probe).
- **Gemini** (`chat_module/gemini_client.py`): extends the shared client in `app/chatbot/gemini_client.py` with helpers for onboarding intros and follow-up questions.
- **Plan shaping** (`app/fitness/plan_transformer.py`): converts raw DynamoDB plan entries into a **calendar** structure the API and LLM summaries use.
- **Plan storage** (`fitness_plan_module/service.py` + `models.py`): one DynamoDB item per user + workout id; generation/writes are triggered from the chat flow (not a separate public blueprint in `main.py`).

### 5. Exercise form & video (`app/exercises/`)

- **Route:** `POST /api/cv/analyze` accepts multipart upload (`video`, `exercise`, `user_id`), saves briefly under `app/exercises/video_in/`, then runs pose comparison logic.
- **Pipeline:** `openpose.py` / `exercise.py` compare the user clip to reference movement; results include numeric scores and short text feedback.
- **AWS:** raw/processed assets use S3 (bucket name is fixed in code: `fitness-form-videos`); same AWS credentials as DynamoDB are typically used.

### 6. Mobile app (`mobile/`)

- **Expo / React Native** screens call the Flask API with `fetch` and **`credentials: "include"`** so session cookies match the browser-style auth flow.
- **Config:** `mobile/src/services/api.js` defines the API base URL (localhost vs emulator IP); optional Supabase env vars on the device help resolve the current user id for video upload.
- **Typical calls:** `authAPI` (register/login), `chatAPI.sendChatbotMessage` → `/api/chat/llm`, `chatAPI.generatePlan` → `/api/chat/plan`, `cvAPI.analyzeVideo` → `/api/cv/analyze`.

---

## Key APIs / Interfaces

**Base URL:** `http://<host>:5001` (adjust for device vs emulator).

| Area | Method | Path | Purpose |
|------|--------|------|---------|
| Auth | POST | `/auth/register` | Create account (`username`, `email`, `password`). |
| Auth | POST | `/auth/login` | Sign in (`username` or email, `password`). |
| Auth | GET | `/auth/check` | See if the session is still valid. |
| Profile | GET/POST/PUT/DELETE | `/api/profile/user` | User profile record (tied to session). |
| Health | GET/POST/PUT/DELETE | `/api/profile/health` | Health entries; optional query `?timestamp=…` for one row. |
| Chat | POST | `/api/chat` | Simple AI message (web). Body: `message`, optional `conversation_history`, `profile`. |
| Chat | POST | `/api/chat/llm` | Main mobile chat: onboarding, then plan-aware replies. Body: `message`, optional `conversation_history`, `profile`. |
| Plan | POST | `/api/chat/plan` | Returns the saved calendar-style plan for the logged-in user. |
| Onboarding | POST | `/api/chat/health-onboarding` | Step-by-step health questions (web flow). |
| Video | POST | `/api/cv/analyze` | Form analysis. `multipart/form-data`: file field `video`, plus `exercise`, `user_id`. |

**Health check:** `GET /api/chat/health` — confirms Gemini is configured.

For a **consumer-by-consumer** breakdown of every route (mobile vs web vs tests vs unused), see [`doc/backend-api-inventory.md`](backend-api-inventory.md).

---

## Configuration

Set in a `.env` file in the project root (see `.env.example`).

| Variable | Needed for |
|----------|------------|
| `SUPABASE_URL`, `SUPABASE_ANON_KEY` | Sign-up / login |
| `GEMINI_API_KEY` | Chat and onboarding |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` | DynamoDB, S3, video pipeline |
| `SECRET_KEY` | Flask sessions (use a strong value in production) |

---

## DB Schemas

| Store | What it holds |
|-------|----------------|
| **Supabase** | User identity (email/password). |
| **DynamoDB `user_profiles`** | One item per user id. |
| **DynamoDB `health_data`** | User id + timestamp; fields like age, height, weight, gender, fitness goal, and extra context JSON. |
| **DynamoDB `fitness_plan`** | User id + workout id; exercise details and dates for generated plans. |

---

## Health Onboarding to Fitness Plan Generation Flow

- New users answer fixed questions (age, height, weight, gender), then a fitness goal, then a few follow-ups.
- That data is stored in **health_data** (DynamoDB).
- After onboarding, the app can **generate and store a multi-day plan** and the chat can refer to it.
- Mobile uses **`POST /api/chat/llm`** for this flow; the web UI can use **`/api/chat/health-onboarding`** and **`/api/chat`**.

---

## CV Form Scoring Pipeline Flow

- **`POST /api/cv/analyze`** accepts a short video and an exercise name; the server scores form and returns text feedback and scores.
- Videos are stored in bucket **`fitness-form-videos`** (AWS).
- The mobile helper **`cvAPI.analyzeVideo`** attaches the current user id automatically when possible.
