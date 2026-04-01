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
| `POST /api/scaffolding/chat` | `tests/test_backend_scaffolding.py`, `tests/test_main_integration.py` |
| `POST /api/chat`, `POST /api/chat/health-onboarding`, `GET /api/chat/health`, `POST /api/chat/llm`, `POST /api/chat/plan` | `tests/test_integration_chat_auth.py`, `tests/test_llm_conversation_health_onboarding.py`, `tests/test_chat_plan_endpoint.py`, and related |
| Auth | `tests/test_auth.py` (register, login, **logout**, **check**, **user**), `tests/test_auth_utils.py` |
| Profile (HTTP) | No dedicated grep hit in `tests/` for `/api/profile` paths in this pass; profile behavior may be covered indirectly — confirm before removing profile routes. |

**Scripts**

| Script | Endpoint |
|--------|----------|
| `scripts/test_health_onboarding_interactive.py` | `POST /api/chat/health-onboarding` |
| `scripts/test_fitness_plan_generate.py` | `POST /api/fitness-plan/generate` — see section E (blueprint not mounted in `main.py`; script may require a test harness or local registration to work). |

---

## D. No mobile / web static reference (verify before delete)

Present in [`app/auth_module/routes.py`](../app/auth_module/routes.py) and covered by **tests**, but **not** in `mobile/src` or `app/static`:

- `POST /auth/logout`, `GET /auth/check`, `GET /auth/user`

Present in [`app/profile_module/routes.py`](../app/profile_module/routes.py); **web** only calls `GET /api/profile/health` (see B). Other profile/health HTTP verbs are not referenced from static JS.

**Important:** `HealthDataService` and related services must remain for `/api/chat/plan` and LLM flows even if HTTP profile routes are trimmed.

---

## E. Dead, duplicate, or stub HTTP surface

| Item | Notes |
|------|--------|
| [`app/chatbot/routes.py`](../app/chatbot/routes.py) | Defines a `chat_bp` that is **not** registered in [`app/main.py`](../app/main.py). Active chat HTTP is [`app/chat_module/routes.py`](../app/chat_module/routes.py). Other `app/chatbot/*` modules (e.g. `gemini_client`, `ai_recommendations`) are still imported elsewhere. |
| [`app/fitness_plan_module/routes.py`](../app/fitness_plan_module/routes.py) | `fitness_plan_bp` (`/api/fitness-plan`) is **not** registered in `main.py`. Plan logic is used via **imports** from `chat_module` (e.g. `generate_plan`), not via this blueprint. |
| `POST /api/cv/update_standard_data`, `GET /api/cv/get_user_pose_estimation` | Stubs in [`app/exercises/routes.py`](../app/exercises/routes.py). |

**Inline:** `POST /api/scaffolding/chat` in `main.py` — tests only (see C).

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
- **`/api/fitness-plan`:** Blueprint definition and `scripts/test_fitness_plan_generate.py` only; not registered in `main.py`.
- **`chatbot.routes`:** No Python import registers the blueprint; `app.chatbot` is used for non-route modules.
- **`scripts/`:** Health onboarding script hits `/api/chat/health-onboarding`; fitness plan script targets `/api/fitness-plan/generate` (see E).

---

## Follow-up PRs (scheduled work)

Execute in separate PRs to keep review small:

1. **Dead / stub routes:** Resolve duplicate `chatbot/routes` blueprint vs `chat_module`; either remove dead file(s) or consolidate. Remove or implement CV stub routes. Decide whether to keep `POST /api/scaffolding/chat` and its tests or fold that logic elsewhere.
2. **Optional unused auth/profile HTTP:** After confirming no external clients, consider removing endpoints only hit by tests — **only** with test updates and documentation updates (`README.md`, `doc/reference.md`).
3. **Mobile-only product:** If the team drops the Flask web chat, remove web-only routes, templates, and static JS in one coherent change with test updates.

Optional client cleanup: remove unused `chatAPI.sendMessage` from [`mobile/src/services/api.js`](../mobile/src/services/api.js) when tightening the mobile API surface.
