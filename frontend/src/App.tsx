import React from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import { Layout } from "./components/Layout"
import Home from "./pages/Home"
import Register from "./pages/Register"
import Login from "./pages/Login"
import Settings from "./pages/Settings"
import { useAuth } from "./auth"

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { tokens } = useAuth()
  if (!tokens) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
