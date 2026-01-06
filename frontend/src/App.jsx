import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { healthCheck } from './services/api'
import { Register } from './pages/Register'
import { Login } from './pages/Login'
import './App.css'

function Home() {
  const [apiStatus, setApiStatus] = useState('checking...')
  const [dbStatus, setDbStatus] = useState('checking...')

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
      <h1>To-Do App</h1>
      <div className="status-container">
        <p>API Status: <span className={`status-${apiStatus}`}>{apiStatus}</span></p>
        <p>Database Status: <span className={`status-${dbStatus}`}>{dbStatus}</span></p>
      </div>
      <div className="auth-links">
        <Link to="/register" className="auth-link">Register</Link>
        <Link to="/login" className="auth-link">Login</Link>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
