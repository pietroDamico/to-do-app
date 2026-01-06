import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { healthCheck } from './services/api'
import { Register } from './pages/Register'
import { Login } from './pages/Login'
import { LogoutButton } from './components/auth/LogoutButton'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import './App.css'

function Home() {
  const [apiStatus, setApiStatus] = useState('checking...')
  const [dbStatus, setDbStatus] = useState('checking...')
  const { user, isAuthenticated } = useAuth()

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await healthCheck()
        setApiStatus(health.components?.api?.status || health.status || 'unknown')
        setDbStatus(health.components?.database?.status || 'unknown')
      } catch (error) {
        console.error('Health check failed:', error)
        setApiStatus('error')
        setDbStatus('error')
      }
    }
    
    checkHealth()
  }, [])

  return (
    <div className="App">
      <header className="app-header">
        <h1>To-Do App</h1>
        {isAuthenticated && (
          <div className="user-info">
            <span className="welcome-message">Welcome, {user?.username}!</span>
            <LogoutButton />
          </div>
        )}
      </header>
      
      <div className="status-container">
        <p>API Status: <span className={`status-${apiStatus}`}>{apiStatus}</span></p>
        <p>Database Status: <span className={`status-${dbStatus}`}>{dbStatus}</span></p>
      </div>
      
      {isAuthenticated ? (
        <div className="authenticated-content">
          <p>You are logged in! Your to-do functionality will appear here.</p>
        </div>
      ) : (
        <div className="auth-links">
          <Link to="/register" className="auth-link">Register</Link>
          <Link to="/login" className="auth-link">Login</Link>
        </div>
      )}
    </div>
  )
}

function Dashboard() {
  const { user } = useAuth()
  
  return (
    <div className="App">
      <header className="app-header">
        <h1>Dashboard</h1>
        <div className="user-info">
          <span className="welcome-message">Welcome, {user?.username}!</span>
          <LogoutButton />
        </div>
      </header>
      <div className="dashboard-content">
        <p>This is a protected dashboard page.</p>
        <p>Your to-do items will appear here in future updates.</p>
        <Link to="/" className="back-link">← Back to Home</Link>
      </div>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
