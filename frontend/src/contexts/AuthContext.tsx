import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { getApiBaseUrl } from '@/services/api'

interface User {
  id: string
  email: string
  name: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  demoLogin: () => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      fetchCurrentUser()
    } else {
      localStorage.removeItem('token')
      setUser(null)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        logout()
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error)
      logout()
    }
  }

  const login = async (email: string, password: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      })

      if (response.ok) {
        const data = await response.json()
        setToken(data.access_token)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const signup = async (email: string, password: string, name: string) => {
    setLoading(true)
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name })
      })

      if (response.ok) {
        await login(email, password)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Signup failed')
      }
    } catch (error) {
      console.error('Signup error:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const demoLogin = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/demo-login`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        setToken(data.access_token)
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Demo login failed')
      }
    } catch (error) {
      console.error('Demo login error:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      signup,
      demoLogin,
      logout,
      loading
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}