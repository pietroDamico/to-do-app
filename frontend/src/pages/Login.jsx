/**
 * Login page component (placeholder).
 * Will be fully implemented in Issue #9.
 */
import { useLocation, Link } from 'react-router-dom';
import './Login.css';

export function Login() {
  const location = useLocation();
  const message = location.state?.message;

  return (
    <div className="login-page">
      <div className="login-placeholder">
        <h2>Login</h2>
        {message && (
          <div className="success-message" role="status">
            {message}
          </div>
        )}
        <p>Login functionality will be implemented in Issue #9.</p>
        <p>
          <Link to="/register">Back to Register</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
