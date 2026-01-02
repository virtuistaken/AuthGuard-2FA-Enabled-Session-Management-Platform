import React from "react"
import { Link, NavLink } from "react-router-dom"
import { useAuth } from "../auth"
import { getApiBase } from "../api"

const navLinkStyle = ({ isActive }: { isActive: boolean }) => ({
  padding: "8px 10px",
  borderRadius: 12,
  border: "1px solid #2a3657",
  background: isActive ? "#1b2a4a" : "transparent",
})

export function Layout({ children }: { children: React.ReactNode }) {
  const { tokens, logout } = useAuth()
  return (
    <div className="container">
      <div className="row" style={{ alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <Link to="/" style={{ fontSize: 18, fontWeight: 700 }}>AuthGuard</Link>
          <div className="muted">API: <code>{getApiBase()}</code></div>
        </div>
        <div className="row">
          <NavLink to="/" style={navLinkStyle}>Home</NavLink>
          {!tokens && <NavLink to="/register" style={navLinkStyle}>Register</NavLink>}
          {!tokens && <NavLink to="/login" style={navLinkStyle}>Login</NavLink>}
          {tokens && <NavLink to="/settings" style={navLinkStyle}>Security</NavLink>}
          {tokens && (
            <button onClick={logout} title="Clear tokens and logout">Logout</button>
          )}
        </div>
      </div>

      <div style={{ height: 14 }} />
      {children}

      <div style={{ height: 18 }} />
      <div className="muted">
        Tip: Backend CORS currently allows <code>http://localhost:3000</code>. Frontend runs on port 3000 by default in this template.
      </div>
    </div>
  )
}
