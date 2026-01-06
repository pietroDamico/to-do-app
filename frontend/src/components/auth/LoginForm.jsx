/**
 * Login form component.
 * Authenticates users and stores JWT token.
 */
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginUser } from '../../services/authService';
import './LoginForm.css';

export function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!username.trim()) {
      setError('Username is required');
      return;
    }
    if (!password) {
      setError('Password is required');
      return;
    }

    setLoading(true);

    try {
      const data = await loginUser(username, password);
      // Log login attempt (username only, never password)
      console.log('Login successful for user:', username);
      
      // Store token and user info via auth context
      login(data.access_token, data.user);
      
      // Redirect to home/dashboard
      navigate('/');
    } catch (err) {
      // Log API errors for debugging (never log passwords)
      console.error('Login failed for user:', username, '- Error:', err.response?.status);
      
      // Handle different error types
      if (err.response?.status === 401) {
        setError('Invalid username or password');
      } else if (err.response?.status === 422) {
        setError(err.response?.data?.detail || 'Validation error');
      } else {
        setError(err.response?.data?.detail || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit} noValidate>
      <h2>Welcome Back</h2>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={loading}
          autoComplete="username"
          placeholder="Enter your username"
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
          autoComplete="current-password"
          placeholder="Enter your password"
        />
      </div>

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true"></span>
            <span>Signing in...</span>
          </>
        ) : (
          'Sign In'
        )}
      </button>

      <p className="register-link">
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
    </form>
  );
}

export default LoginForm;
