import React, { createContext, useContext, useMemo, useState } from "react"
import { TokenResponse, clearTokens, loadTokens, saveTokens } from "./api"

type AuthState = {
  tokens: TokenResponse | null
  setTokens: (t: TokenResponse | null) => void
  logout: () => void
}

const Ctx = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [tokens, setTokensState] = useState<TokenResponse | null>(() => loadTokens())

  const setTokens = (t: TokenResponse | null) => {
    setTokensState(t)
    if (t) saveTokens(t)
    else clearTokens()
  }

  const logout = () => setTokens(null)

  const value = useMemo(() => ({ tokens, setTokens, logout }), [tokens])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useAuth() {
  const v = useContext(Ctx)
  if (!v) throw new Error("useAuth must be used inside AuthProvider")
  return v
}
