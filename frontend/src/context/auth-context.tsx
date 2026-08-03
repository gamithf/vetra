import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { authApi, type User, type LoginPayload, type RegisterPayload } from '@/lib/api'

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (data: LoginPayload) => Promise<void>
  register: (data: RegisterPayload) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('vetra_user')
    return stored ? JSON.parse(stored) : null
  })
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('vetra_token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (token) {
      authApi.me()
        .then((u) => {
          setUser(u)
          localStorage.setItem('vetra_user', JSON.stringify(u))
        })
        .catch(() => {
          localStorage.removeItem('vetra_token')
          localStorage.removeItem('vetra_user')
          setUser(null)
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [token])

  const login = useCallback(async (data: LoginPayload) => {
    const res = await authApi.login(data)
    localStorage.setItem('vetra_token', res.access_token)
    localStorage.setItem('vetra_user', JSON.stringify(res.user))
    setToken(res.access_token)
    setUser(res.user)
  }, [])

  const register = useCallback(async (data: RegisterPayload) => {
    const res = await authApi.register(data)
    localStorage.setItem('vetra_token', res.access_token)
    localStorage.setItem('vetra_user', JSON.stringify(res.user))
    setToken(res.access_token)
    setUser(res.user)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('vetra_token')
    localStorage.removeItem('vetra_user')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
