export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

const API_BASE = (import.meta as any).env?.VITE_API_BASE ?? "http://localhost:8000"

export function getApiBase() {
  return API_BASE
}

function jsonHeaders(extra?: Record<string, string>) {
  return { "Content-Type": "application/json", ...(extra ?? {}) }
}

export function saveTokens(tokens: TokenResponse) {
  localStorage.setItem("authguard.tokens", JSON.stringify(tokens))
}

export function loadTokens(): TokenResponse | null {
  const raw = localStorage.getItem("authguard.tokens")
  if (!raw) return null
  try { return JSON.parse(raw) as TokenResponse } catch { return null }
}

export function clearTokens() {
  localStorage.removeItem("authguard.tokens")
}

export function authHeader(): Record<string, string> {
  const t = loadTokens()
  if (!t?.access_token) return {}
  return { Authorization: `Bearer ${t.access_token}` }
}

async function handle(res: Response) {
  const text = await res.text()
  const isJson = (res.headers.get("content-type") ?? "").includes("application/json")
  const data = isJson && text ? JSON.parse(text) : (text ? { detail: text } : {})
  if (!res.ok) {
    const msg = data?.detail ?? `HTTP ${res.status}`
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg))
  }
  return data
}

export async function register(email: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({ email, password }),
  })
  return handle(res) as Promise<{ id: number; email: string; is_active: boolean; is_2fa_enabled: boolean }>
}

/**
 * Backend uses OAuth2PasswordRequestForm:
 * Content-Type: application/x-www-form-urlencoded
 * Field name: username (email), password (password), and optional totp_code.
 */
export async function login(email: string, password: string, totp_code?: string) {
  const body = new URLSearchParams()
  body.set("username", email)
  body.set("password", password)
  if (totp_code) body.set("totp_code", totp_code)

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  })
  return handle(res) as Promise<TokenResponse & { user?: any; is_2fa_required?: boolean }>
}

export async function enable2fa() {
  const res = await fetch(`${API_BASE}/auth/enable-2fa`, {
    method: "POST",
    headers: { ...jsonHeaders(), ...authHeader() },
    body: JSON.stringify({}),
  })
  return handle(res) as Promise<{ secret: string; otpauth_url: string }>
}

export async function health() {
  const res = await fetch(`${API_BASE}/health`)
  return handle(res) as Promise<any>
}
