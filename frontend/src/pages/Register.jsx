/**
 * Registration page component.
 * Renders the registration form centered on the page.
 */
import { RegisterForm } from '../components/auth/RegisterForm';
import './Register.css';

export function Register() {
  return (
    <div className="register-page">
      <RegisterForm />
    </div>
  );
}

export default Register;
