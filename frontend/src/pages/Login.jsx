/**
 * Login page component.
 * Renders the login form centered on the page.
 */
import { useLocation } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';
import './Login.css';

export function Login() {
  const location = useLocation();
  const message = location.state?.message;

  return (
    <div className="login-page">
      <div className="login-container">
        {message && (
          <div className="success-message" role="status">
            {message}
          </div>
        )}
        <LoginForm />
      </div>
    </div>
  );
}

export default Login;
