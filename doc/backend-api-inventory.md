# Backend API inventory (by consumer)

This document freezes the HTTP surface of the Flask app as of the inventory pass. Use it before deleting or gating routes.

**Canonical sources**

| Role | Path |
|------|------|
| App factory & inline routes | [`app/main.py`](../app/main.py) |
| Blueprints | [`app/auth_module/routes.py`](../app/auth_module/routes.py), [`app/chat_module/routes.py`](../app/chat_module/routes.py), [`app/profile_module/routes.py`](../app/profile_module/routes.py), [`app/exercises/routes.py`](../app/exercises/routes.py) |
| React Native client | [`mobile/src/services/api.js`](../mobile/src/services/api.js) |
| Web static client | [`app/static/js/auth.js`](../app/static/js/auth.js), [`app/static/js/chat.js`](../app/static/js/chat.js) |

---

## A. Used by the React Native app (current screens)

| Method | Path | Source |
|--------|------|--------|
| POST | `/auth/register` | `api.js` + signup screen |
| POST | `/auth/login` | `api.js` + login screen |
| POST | `/api/chat/llm` | `ChatBotScreen.jsx` via `chatAPI.sendChatbotMessage` |
| POST | `/api/chat/plan` | `PlanScreen.js`, `SnapshotScreen.jsx` via `chatAPI.generatePlan` |
| POST | `/api/cv/analyze` | `RecordVideoScreen.jsx` via `cvAPI.analyzeVideo` |

### Upload endpoint limits

`POST /api/cv/analyze` is rate-limited with Flask-Limiter using both identities:

- Authenticated user key: `X-User-Id` / resolved session identity (default `10 per minute`)
- IP address key: client remote IP (default `30 per minute`)

Environment variables:

- `CV_UPLOAD_USER_RATE_LIMIT` (for example: `10 per minute`)
- `CV_UPLOAD_IP_RATE_LIMIT` (for example: `30 per minute`)

When a request exceeds either limit, the API returns HTTP `429` with:

```json
{
	"error": "Rate limit exceeded",
	"detail": "<limit description>"
}
```

Violations are logged with request path, method, user identity, IP, and exceeded limit.

`chatAPI.sendMessage` in `api.js` maps to `POST /api/chat` but **no screen imports it**; only `sendChatbotMessage` is used. That is unused client surface, not proof the backend route is unused globally (web uses `POST /api/chat`).

---

## B. Used by the Flask web UI (not mobile)

| Method | Path | Source |
|--------|------|--------|
| POST | `/auth/register`, `/auth/login` | `app/static/js/auth.js` |
| GET | `/api/profile/health?timestamp=health_profile` | `app/static/js/chat.js` |
| POST | `/api/chat/health-onboarding` | `app/static/js/chat.js` |
| POST | `/api/chat` | `app/static/js/chat.js` |

**Pages:** `GET /`, `GET /chat` — [`app/main.py`](../app/main.py) (templates).

---

## C. Used by automated tests / tooling

| Surface | References |
|---------|------------|
| `app.scaffolding_chat.scaffold_chat_post` (same logic as the former `POST /api/scaffolding/chat`) | `tests/test_backend_scaffolding.py`, `tests/test_main_integration.py` |
| `POST /api/chat`, `POST /api/chat/health-onboarding`, `GET /api/chat/health`, `POST /api/chat/llm`, `POST /api/chat/plan` | `tests/test_integration_chat_auth.py`, `tests/test_llm_conversation_health_onboarding.py`, `tests/test_chat_plan_endpoint.py`, and related |
| Auth | `tests/test_auth.py` (register, login, **logout**, **check**, **user**), `tests/test_auth_utils.py` |
| Profile (HTTP) | No dedicated grep hit in `tests/` for `/api/profile` paths in this pass; profile behavior may be covered indirectly — confirm before removing profile routes. |

**Scripts**

| Script | Endpoint |
|--------|----------|
| `scripts/test_health_onboarding_interactive.py` | `POST /api/chat/health-onboarding` |
| `scripts/test_fitness_plan_generate.py` | Calls [`app/fitness/plan_generation.py`](../app/fitness/plan_generation.py) `generate_two_week_plan_and_save` (no REST route). |

---

## D. No mobile / web static reference (verify before delete)

Present in [`app/auth_module/routes.py`](../app/auth_module/routes.py) and covered by **tests**, but **not** in `mobile/src` or `app/static`:

- `POST /auth/logout`, `GET /auth/check`, `GET /auth/user`

Present in [`app/profile_module/routes.py`](../app/profile_module/routes.py); **web** only calls `GET /api/profile/health` (see B). Other profile/health HTTP verbs are not referenced from static JS.

**Important:** `HealthDataService` and related services must remain for `/api/chat/plan` and LLM flows even if HTTP profile routes are trimmed.

---

## E. Removed duplicate / extra HTTP surface (cleanup applied)

The following were removed or replaced (no longer exposed as routes):

| Item | Replacement |
|------|----------------|
| Duplicate `app/chatbot/routes.py` (removed) | Active HTTP remains only in [`app/chat_module/routes.py`](../app/chat_module/routes.py). |
| Unregistered `app/fitness_plan_module/routes.py` blueprint (removed) | Plan generation lives in [`app/fitness/plan_generation.py`](../app/fitness/plan_generation.py) (`generate_two_week_plan_and_save`). |
| CV stub routes | Removed from [`app/exercises/routes.py`](../app/exercises/routes.py). |
| `POST /api/scaffolding/chat` in [`app/main.py`](../app/main.py) | Logic in [`app/scaffolding_chat.py`](../app/scaffolding_chat.py) for tests; not mounted on the app. |

---

## Grep verification (pre-deletion)

Commands run from the repository root (April 2026 inventory pass):

```bash
rg '/auth/' --glob '*.{py,js,jsx,md}'
rg '/api/profile' --glob '*.{py,js,jsx,md}'
rg '/api/fitness-plan|fitness_plan_bp|fitness-plan' --glob '*.{py,js,jsx,md}'
rg 'chatbot\.routes|from app\.chatbot import routes|app\.chatbot\.routes' --glob '*.py'
rg '/api/' scripts --glob '*.py'
```

**Summary**

- **`/auth/`:** Mobile uses register/login; web static uses register/login; `tests/test_auth.py` exercises logout, check, user; README and `doc/reference.md` document the full set.
- **`/api/profile`:** Web `chat.js` uses `GET .../health?timestamp=health_profile`; README lists full CRUD; no `mobile/src` hits.
- **`/api/fitness-plan`:** Removed; use `plan_generation.generate_two_week_plan_and_save` from Python or `/api/chat/plan` for calendar retrieval.
- **`chatbot.routes`:** File removed; `app.chatbot` non-route modules unchanged.
- **`scripts/`:** Health onboarding script hits `/api/chat/health-onboarding`; fitness plan script calls `generate_two_week_plan_and_save` directly.

---

## Follow-up PRs (scheduled work)

1. **Optional unused auth/profile HTTP:** After confirming no external clients, consider trimming endpoints only hit by tests — with test and doc updates (`README.md`, `doc/reference.md`).
2. **Mobile-only product:** If the team drops the Flask web chat, remove web-only routes, templates, and static JS in one coherent change with test updates.

Optional client cleanup: remove unused `chatAPI.sendMessage` from [`mobile/src/services/api.js`](../mobile/src/services/api.js) when tightening the mobile API surface.
