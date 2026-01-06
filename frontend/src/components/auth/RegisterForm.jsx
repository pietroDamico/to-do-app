/**
 * Registration form component.
 * Validates input client-side and submits to the registration API.
 */
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../../services/authService';
import './RegisterForm.css';

/**
 * Validate username according to backend rules.
 * @param {string} username - The username to validate
 * @returns {string|null} Error message or null if valid
 */
const validateUsername = (username) => {
  if (!username) {
    return 'Username is required';
  }
  if (username.length < 3) {
    return 'Username must be at least 3 characters';
  }
  if (username.length > 50) {
    return 'Username must be at most 50 characters';
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return 'Username can only contain letters, numbers, and underscores';
  }
  return null;
};

/**
 * Validate password according to backend rules.
 * @param {string} password - The password to validate
 * @returns {string|null} Error message or null if valid
 */
const validatePassword = (password) => {
  if (!password) {
    return 'Password is required';
  }
  if (password.length < 8) {
    return 'Password must be at least 8 characters';
  }
  return null;
};

export function RegisterForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    const errors = {};
    const usernameError = validateUsername(username);
    const passwordError = validatePassword(password);

    if (usernameError) errors.username = usernameError;
    if (passwordError) errors.password = passwordError;

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await register(username, password);
      // Log registration attempt (username only, never password)
      console.log('Registration successful for user:', username);
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err) {
      // Log API errors for debugging (never log passwords)
      console.error('Registration failed for user:', username, '- Error:', err.response?.status);
      
      // Handle different error types
      if (err.response?.status === 409) {
        setError('Username already exists');
      } else if (err.response?.status === 422) {
        // Validation errors from backend
        const detail = err.response?.data?.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation errors
          const backendErrors = {};
          detail.forEach((item) => {
            const field = item.loc?.[1];
            if (field) {
              backendErrors[field] = item.msg;
            }
          });
          setFieldErrors(backendErrors);
        } else {
          setError(detail || 'Validation error');
        }
      } else {
        setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
    // Clear field error when user starts typing
    if (fieldErrors.username) {
      setFieldErrors((prev) => ({ ...prev, username: null }));
    }
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
    // Clear field error when user starts typing
    if (fieldErrors.password) {
      setFieldErrors((prev) => ({ ...prev, password: null }));
    }
  };

  return (
    <form className="register-form" onSubmit={handleSubmit} noValidate>
      <h2>Create Account</h2>

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
          onChange={handleUsernameChange}
          disabled={loading}
          aria-describedby={fieldErrors.username ? 'username-error' : undefined}
          aria-invalid={!!fieldErrors.username}
          autoComplete="username"
          placeholder="Enter username (3-50 characters)"
        />
        {fieldErrors.username && (
          <span id="username-error" className="field-error" role="alert">
            {fieldErrors.username}
          </span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={password}
          onChange={handlePasswordChange}
          disabled={loading}
          aria-describedby={fieldErrors.password ? 'password-error' : undefined}
          aria-invalid={!!fieldErrors.password}
          autoComplete="new-password"
          placeholder="Enter password (8+ characters)"
        />
        {fieldErrors.password && (
          <span id="password-error" className="field-error" role="alert">
            {fieldErrors.password}
          </span>
        )}
      </div>

      <button type="submit" disabled={loading} className="submit-button">
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true"></span>
            <span>Creating account...</span>
          </>
        ) : (
          'Create Account'
        )}
      </button>

      <p className="login-link">
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </form>
  );
}

export default RegisterForm;
