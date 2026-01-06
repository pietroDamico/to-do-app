/**
 * Logout button component.
 * Clears auth state and redirects to login page.
 */
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './LogoutButton.css';

/**
 * LogoutButton component.
 * @param {Object} props - Component props
 * @param {string} [props.className] - Additional CSS class
 * @returns {React.ReactNode} Logout button
 */
export function LogoutButton({ className = '' }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <button
      onClick={handleLogout}
      className={`logout-button ${className}`.trim()}
      type="button"
    >
      Logout
    </button>
  );
}

export default LogoutButton;
