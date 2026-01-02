import React, { useState } from "react"
import { login } from "../api"
import { useAuth } from "../auth"
import { useNavigate } from "react-router-dom"

export default function Login() {
  const { setTokens } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [totp, setTotp] = useState("")
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErr(null); setBusy(true)
    try {
      const res = await login(email.trim(), password, totp.trim() || undefined)
      if ((res as any).is_2fa_required) {
        setErr("2FA code required. Enter the 6-digit code from your authenticator app and try again.")
      } else if (res.access_token) {
        setTokens({ access_token: res.access_token, refresh_token: res.refresh_token, token_type: res.token_type })
        nav("/settings")
      } else {
        setErr("Unexpected response from backend.")
      }
    } catch (e: any) {
      setErr(e.message ?? "Login failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Login</h2>
      <p className="muted">
        If you enabled 2FA, you must provide <code>totp_code</code> along with username/password.
      </p>

      <form onSubmit={submit}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />

        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />

        <label>2FA code (optional)</label>
        <input value={totp} onChange={(e) => setTotp(e.target.value)} placeholder="123456" inputMode="numeric" />

        <div style={{ height: 12 }} />
        <button disabled={busy}>{busy ? "Logging in..." : "Login"}</button>

        {err && <p className="bad">{err}</p>}
      </form>
    </div>
  )
}
