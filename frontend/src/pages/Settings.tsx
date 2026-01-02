import React, { useState } from "react"
import { enable2fa, loadTokens } from "../api"
import QRCode from "qrcode.react"

export default function Settings() {
  const tokens = loadTokens()
  const [secret, setSecret] = useState<string | null>(null)
  const [uri, setUri] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const doEnable = async () => {
    setErr(null); setBusy(true)
    try {
      const r = await enable2fa()
      setSecret(r.secret)
      setUri(r.otpauth_url)
    } catch (e: any) {
      setErr(e.message ?? "Failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card">
      <h2>Security</h2>
      <p className="muted">
        Use this page to generate a TOTP secret and QR code for Google Authenticator/Authy.
      </p>

      <div className="row">
        <div className="col">
          <h3 style={{ marginTop: 0 }}>Tokens (local)</h3>
          {!tokens && <div className="bad">Not logged in.</div>}
          {tokens && (
            <>
              <div className="muted">Access token is used as <code>Authorization: Bearer ...</code> on protected calls.</div>
              <div style={{ height: 10 }} />
              <div className="kv">
                <div>token_type</div><div>{tokens.token_type}</div>
                <div>access_token</div><div style={{ wordBreak: "break-all" }}><code>{tokens.access_token}</code></div>
                <div>refresh_token</div><div style={{ wordBreak: "break-all" }}><code>{tokens.refresh_token}</code></div>
              </div>
            </>
          )}
        </div>

        <div className="col">
          <h3 style={{ marginTop: 0 }}>Enable 2FA</h3>
          <button onClick={doEnable} disabled={busy || !tokens}>{busy ? "Working..." : "Generate secret & QR"}</button>
          {err && <p className="bad">{err}</p>}

          {secret && uri && (
            <>
              <hr />
              <div className="muted">Scan the QR code with your authenticator app, or copy the secret manually.</div>
              <div style={{ height: 10 }} />
              <div className="row" style={{ alignItems: "center" }}>
                <div className="card" style={{ padding: 14 }}>
                  <QRCode value={uri} />
                </div>
                <div style={{ minWidth: 220 }}>
                  <div className="muted">Secret</div>
                  <div style={{ wordBreak: "break-all" }}><code>{secret}</code></div>
                  <div style={{ height: 8 }} />
                  <div className="muted">otpauth_url</div>
                  <div style={{ wordBreak: "break-all" }}><code>{uri}</code></div>
                </div>
              </div>
              <p className="muted" style={{ marginTop: 10 }}>
                After enabling 2FA, logout and login again with the 6-digit code.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
