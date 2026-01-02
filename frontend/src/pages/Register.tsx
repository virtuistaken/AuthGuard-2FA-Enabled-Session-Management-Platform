import React, { useState } from "react"
import { register } from "../api"
import { useNavigate } from "react-router-dom"

export default function Register() {
  const nav = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErr(null); setMsg(null); setBusy(true)
    try {
      const u = await register(email.trim(), password)
      setMsg(`User created: ${u.email} (id=${u.id}). You can login now.`)
      setTimeout(() => nav("/login"), 600)
    } catch (e: any) {
      setErr(e.message ?? "Registration failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Create account</h2>
      <p className="muted">Backend enforces minimum 8 characters for password.</p>

      <form onSubmit={submit}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />

        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required minLength={8} />

        <div style={{ height: 12 }} />
        <button disabled={busy}>{busy ? "Creating..." : "Register"}</button>

        {msg && <p className="good">{msg}</p>}
        {err && <p className="bad">{err}</p>}
      </form>
    </div>
  )
}
