# AuthGuard Frontend (Vite + React + TS)

This frontend matches the provided FastAPI backend endpoints:

- `POST /auth/register` (JSON)
- `POST /auth/login` (OAuth2PasswordRequestForm: x-www-form-urlencoded)
- `POST /auth/enable-2fa` (Bearer auth)

## Run

```bash
cd authguard-frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:3000** (same as backend CORS allowlist).

## Configure API base

Optionally set:

```bash
# Windows (PowerShell)
$env:VITE_API_BASE="http://localhost:8000"

# macOS/Linux
export VITE_API_BASE="http://localhost:8000"
```
