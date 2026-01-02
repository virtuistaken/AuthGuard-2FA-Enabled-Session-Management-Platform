import React, { useEffect, useState } from "react"
import { health } from "../api"
import { useAuth } from "../auth"

export default function Home() {
  const { tokens } = useAuth()
  const [h, setH] = useState<any>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    health().then(setH).catch((e) => setErr(e.message))
  }, [])

  return (
    <div className="card">
      <h2>Welcome</h2>
      <p className="muted">
        This UI talks to your FastAPI backend (<code>/auth/register</code>, <code>/auth/login</code>, <code>/auth/enable-2fa</code>).
      </p>

      <div className="row">
        <div className="col">
          <h3 style={{ marginTop: 0 }}>Backend health</h3>
          {err && <div className="bad">Error: {err}</div>}
          {h && (
            <div className="kv">
              <div>Status</div><div><span className="good">{String(h.status)}</span></div>
              <div>Version</div><div>{String(h.version)}</div>
              <div>Security</div><div>{String(h.security)}</div>
            </div>
          )}
          {!h && !err && <div className="muted">Loading...</div>}
        </div>

        <div className="col">
          <h3 style={{ marginTop: 0 }}>Session</h3>
          {tokens ? (
            <>
              <div className="good">Logged in (tokens stored in localStorage).</div>
              <div className="muted" style={{ marginTop: 8 }}>
                Go to <b>Security</b> to enable 2FA and generate a QR code.
              </div>
            </>
          ) : (
            <div className="muted">Not logged in.</div>
          )}
        </div>
      </div>
    </div>
  )
}
