# PenguWave — Security Operations Portal

A real, secure backend for the PenguWave security-ops portal, built in Python with FastAPI. Connects to a React + TypeScript frontend for a complete end-to-end authentication and role-based access system.

## Quick start

**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate (Windows)
pip install -r requirements.txt
cp .env.example .env
./run.sh
# Server runs on http://localhost:3001
```

**Frontend:**
```bash
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

Then navigate to `http://localhost:5173` in your browser. The login modal will appear. Use:
- **Admin:** admin@penguwave.io / admin123
- **Analyst:** analyst@penguwave.io / pass456
- **Viewer:** viewer@penguwave.io / view789 (account is disabled, login will fail)

## What we built

### Backend (Python + FastAPI)
- **Authentication:** email/password login with opaque session tokens (real logout/revocation)
- **Authorization:** role-based access control (admin, analyst, viewer)
- **API endpoints:**
  - `POST /api/auth/login` — authenticate and get a token
  - `POST /api/auth/logout` — revoke the token (real logout)
  - `GET /api/auth/me` — get current user info
  - `GET /api/events` — list all security events (role-based visibility: all active users see all)
  - `GET /api/events/{id}` — get a single event
  - `GET /api/users` — list users (admin only)
  - `POST /api/users` — create a user (admin only)
  - `PATCH /api/users/{id}` — update user role/status (admin only)
  - `DELETE /api/users/{id}` — delete a user (admin only)
- **Data persistence:** SQLite database with idempotent seed of hashed users and 59 security events
- **Security:**
  - Bcrypt password hashing (never plaintext passwords)
  - HTML-escaped event descriptions to defend against stored XSS (evt-052)
  - Admin self-lockout guards (can't disable/demote yourself)
  - No-enumeration login (same error for unknown user, bad password, disabled account)
  - CORS locked to the frontend origin

### Frontend (React + TypeScript)
- **Fixed security flaws:**
  - Removed committed API secret (`pw_live_sk_...`)
  - Stopped logging passwords to console
  - Fixed login to only store token on success + capture role for RBAC
  - Removed debug auth bypass
- **Real auth flow:**
  - Login modal calls the backend, shows errors on failure
  - Routes guarded by authentication state
  - `/users` page only visible to admins (returns 404 to non-admins)
  - Logout button that revokes the session
- **Real data:**
  - Events load from the backend API (not mock JSON)
  - User management calls the backend CRUD endpoints
  - Severity filter includes CRITICAL (fixed the type mismatch from the starter)

## Key decisions & tradeoffs

### 1. Role-based event visibility (not per-user ownership)
- **Decision:** all authenticated active users see all events. Admin is the only special role (manages users).
- **Why:** in a SOC (Security Operations Center) portal, analysts triage a shared queue of events. Ownership is metadata (evt.userId), not an access boundary.
- **Tradeoff:** simpler code and authorization logic; users can't be isolated to their own events (but the data structure supports it if needed later).

### 2. Opaque session tokens (not stateless JWT)
- **Decision:** random tokens stored in a `sessions` table. Logout deletes the row.
- **Why:** enables *real* logout and instant revocation. If an admin disables a user, their active tokens die immediately.
- **Tradeoff:** requires a DB lookup on every request; slightly more infra (the sessions table). Stateless JWT would scale better but logout would be cosmetic (token expires after 1h or so).

### 3. Backend HTML-escaping the event descriptions
- **Decision:** escape `title` and `description` fields on output so evt-052's stored XSS payload (`<img src=x onerror=...>`) ships inert.
- **Why:** defense-in-depth. Non-browser clients consuming the API won't be vulnerable to that stored payload.
- **Cross-track note:** the real sink is the frontend's `el.innerHTML` + the no-op `sanitizeHtml()`. With more time, we'd wire up DOMPurify or drop `innerHTML` in favor of `.textContent` (see "Bonus" below).

## Security checklist

- ✓ Passwords hashed with bcrypt (never plaintext)
- ✓ Session tokens are random and server-stored (real logout/revocation)
- ✓ Auth required for all event/user endpoints
- ✓ Admin-only routes guarded at the dependency level
- ✓ No-enumeration login (don't leak whether an email exists)
- ✓ Self-lockout guards (admin can't disable/demote themselves)
- ✓ Disabled users can't log in; existing tokens rejected
- ✓ CORS restricted to frontend origin only
- ✓ HTML-escaped event text on output
- ✓ `.gitignore` added (`.env`, `*.db`, `.venv/`, etc.)
- ✓ Committed secret (`X-Api-Key`) removed from frontend

## Testing checklist (manual smoke tests)

1. **Backend boots:**
   ```bash
   curl http://localhost:3001/health
   ```
   Returns `{"status":"ok"}` ✓

2. **Login works:**
   ```bash
   curl -X POST http://localhost:3001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@penguwave.io","password":"admin123"}'
   ```
   Returns `{"token":"...", "user":{...}}` ✓

3. **Events visible to authenticated user:**
   ```bash
   curl -H "Authorization: Bearer <token>" \
     http://localhost:3001/api/events
   ```
   Returns array of 59 events (CRITICAL, HIGH, MEDIUM, LOW) with HTML-escaped descriptions ✓

4. **Users endpoint admin-only:**
   ```bash
   # As analyst (not admin)
   curl -H "Authorization: Bearer <analyst-token>" \
     http://localhost:3001/api/users
   ```
   Returns `{"error": "Admin role required"}` (403) ✓

5. **Logout revokes token:**
   ```bash
   curl -X POST -H "Authorization: Bearer <token>" \
     http://localhost:3001/api/auth/logout
   # Reuse the token:
   curl -H "Authorization: Bearer <token>" \
     http://localhost:3001/api/auth/me
   ```
   Returns `{"error":"..."}` (401) ✓

6. **Frontend:**
   - Login modal appears
   - Can log in with admin / admin123, see events
   - Events load from API, can filter by severity (now includes CRITICAL)
   - Can click to `/users`, see user list
   - Non-admin users see 404 when trying `/users`
   - Logout clears localStorage, shows login modal again

## Bonus features (with more time)

- [ ] **DOMPurify on the frontend** — wire up DOMPurify to sanitize user-provided search text and event descriptions shown via `innerHTML`. The backend now escapes (defense-in-depth), but the frontend sink (`dangerouslySetInnerHTML`, `el.innerHTML`) should also be hardened.
- [ ] **Pagination** — add `?limit=20&offset=0` to `GET /api/events` for large datasets.
- [ ] **Automated tests** — pytest fixtures for the DB, happy/sad path tests for login (401, 403, 404), RBAC guards, etc.
- [ ] **Request logging** — log all POST/PATCH/DELETE for audit trails.
- [ ] **Brute-force defense** — rate-limit login attempts (5 per IP per minute). Relevant given evt-002 is an SSH brute-force event.
- [ ] **Token expiry/refresh** — add an `expires_at` to sessions and a refresh endpoint. Force re-auth every 24h.
- [ ] **Secret rotation (incident response)** — the starter code shipped a fake `X-Api-Key`. In a real incident, we'd:
  1. Delete it from the code (done, commit 7).
  2. Use `git filter-repo` or `BFG` to scrub it from history (risky on shared repos; not done here).
  3. Rotate any real keys that were in the same commit.
  4. Educate the team on `.gitignore` and secret scanning (e.g., `git-secrets`, `TruffleHog`).

## Architecture notes

**Backend structure:**
- `app/main.py` — FastAPI app, CORS, error handlers, router includes, startup seed.
- `app/config.py` — settings from `.env` (database, CORS origin, seed passwords).
- `app/database.py` — SQLAlchemy engine, session management, `get_session()` dependency.
- `app/models.py` — SQLModel tables (User, Event, Session) with proper enum fields.
- `app/schemas.py` — Pydantic request/response models; EventOut applies HTML escaping.
- `app/security.py` — password hashing, token generation.
- `app/deps.py` — `get_current_user()` and `require_admin()` dependencies for RBAC.
- `app/errors.py` — custom exceptions + global error handler for consistent `{"error": "..."}` responses.
- `app/routers/{auth,events,users}.py` — endpoint implementations.
- `app/seed.py` — idempotent seeding of users (hashed) and 59 events from `data/mock_events.json`.
- `app/sanitize.py` — HTML escape function.

**Frontend structure:**
- `src/api.ts` — HTTP client for all backend endpoints (login, logout, events, users).
- `src/components/LoginModal.tsx` — login form; calls `api.login()`, shows errors, only closes on success.
- `src/components/Navbar.tsx` — nav bar; shows login/logout button based on auth state.
- `src/pages/EventsPage.tsx` — events table; loads from API, filters by severity (incl. CRITICAL) and search.
- `src/pages/UsersPage.tsx` — user management; calls `getUsers()`, `createUser()`, `deleteUser()`.
- `src/App.tsx` — router; guards `/users` by admin role, shows login modal if no token.

**Database:**
- SQLite file at `backend/penguwave.db` (auto-created on first run).
- User ids: `usr-001`, `usr-002`, `usr-003` (matches event `userId` namespace).
- Events idempotently seeded from `data/mock_events.json` (includes evt-052 with XSS, now escaped).
- Sessions table stores opaque tokens; deleting a row = logout.

## Deliverables

- ✓ Git branch `feat/backend` with clean commit history (9 commits).
- ✓ Pull request ready to merge to `main`.
- ✓ README (this file) documenting how to run, what we built, and key decisions.
- ✓ Backend: real auth, RBAC, persistent data, secure.
- ✓ Frontend: wired to backend, routes guarded, security flaws fixed.
- ✓ No secrets in the repo (`.gitignore` + removed `X-Api-Key`).
