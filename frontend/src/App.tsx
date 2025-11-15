import { useState } from 'react'
import { LoginForm } from '@/components/LoginForm'
import { SignupForm } from '@/components/SignupForm'
import { Dashboard } from '@/components/Dashboard'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'

function AuthenticatedApp() {
  const { user, login, signup, demoLogin, loading } = useAuth()
  const [authView, setAuthView] = useState<'login' | 'signup'>('login')

  if (!user) {
    if (authView === 'login') {
      return (
        <LoginForm
          onLogin={login}
          onSignupClick={() => setAuthView('signup')}
          onDemoLogin={demoLogin}
          loading={loading}
        />
      )
    } else {
      return (
        <SignupForm
          onSignup={signup}
          onLoginClick={() => setAuthView('login')}
          loading={loading}
        />
      )
    }
  }

  return <Dashboard />
}

function App() {
  return (
    <AuthProvider>
      <AuthenticatedApp />
    </AuthProvider>
  )
}

export default App