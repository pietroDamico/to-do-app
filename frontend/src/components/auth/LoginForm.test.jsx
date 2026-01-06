/**
 * Tests for the LoginForm component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginForm } from './LoginForm';

// Mock the auth service
vi.mock('../../services/authService', () => ({
  loginUser: vi.fn(),
}));

// Mock the auth context
const mockLogin = vi.fn();
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
  }),
}));

// Mock react-router-dom navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import { loginUser } from '../../services/authService';

// Helper to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the login form with all fields', () => {
      renderWithRouter(<LoginForm />);
      
      expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('has password field with type password (masked)', () => {
      renderWithRouter(<LoginForm />);
      
      const passwordInput = screen.getByLabelText(/password/i);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('has link to register page', () => {
      renderWithRouter(<LoginForm />);
      
      const registerLink = screen.getByRole('link', { name: /register here/i });
      expect(registerLink).toHaveAttribute('href', '/register');
    });

    it('has placeholder text for inputs', () => {
      renderWithRouter(<LoginForm />);
      
      expect(screen.getByPlaceholderText(/enter your username/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('shows error for empty username', async () => {
      const user = userEvent.setup();
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(loginUser).not.toHaveBeenCalled();
    });

    it('shows error for empty password', async () => {
      const user = userEvent.setup();
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      expect(loginUser).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    it('calls loginUser API with correct credentials', async () => {
      const user = userEvent.setup();
      loginUser.mockResolvedValue({
        access_token: 'jwt.token.here',
        token_type: 'bearer',
        user: { id: 1, username: 'testuser' },
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      expect(loginUser).toHaveBeenCalledWith('testuser', 'password123');
    });

    it('shows loading state during submission', async () => {
      const user = userEvent.setup();
      loginUser.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeDisabled();
      expect(screen.getByLabelText(/password/i)).toBeDisabled();
    });

    it('disables submit button during loading', async () => {
      const user = userEvent.setup();
      loginUser.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('calls login and navigates on successful login', async () => {
      const user = userEvent.setup();
      const mockUserData = { id: 1, username: 'testuser' };
      loginUser.mockResolvedValue({
        access_token: 'jwt.token.here',
        token_type: 'bearer',
        user: mockUserData,
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('jwt.token.here', mockUserData);
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message for invalid credentials (401)', async () => {
      const user = userEvent.setup();
      loginUser.mockRejectedValue({
        response: { status: 401, data: { detail: 'Invalid credentials' } }
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'wronguser');
      await user.type(screen.getByLabelText(/password/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
      });
    });

    it('displays error message for validation errors (422)', async () => {
      const user = userEvent.setup();
      loginUser.mockRejectedValue({
        response: { status: 422, data: { detail: 'Validation error' } }
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/validation error/i)).toBeInTheDocument();
      });
    });

    it('displays generic error message for unknown errors', async () => {
      const user = userEvent.setup();
      loginUser.mockRejectedValue({
        response: { status: 500 }
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/login failed/i)).toBeInTheDocument();
      });
    });

    it('re-enables form after error', async () => {
      const user = userEvent.setup();
      loginUser.mockRejectedValue({
        response: { status: 401, data: { detail: 'Invalid credentials' } }
      });
      
      renderWithRouter(<LoginForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'wronguser');
      await user.type(screen.getByLabelText(/password/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      await waitFor(() => {
        expect(screen.getByLabelText(/username/i)).not.toBeDisabled();
        expect(screen.getByLabelText(/password/i)).not.toBeDisabled();
        expect(screen.getByRole('button', { name: /sign in/i })).not.toBeDisabled();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper labels for all form fields', () => {
      renderWithRouter(<LoginForm />);
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      
      expect(usernameInput).toHaveAttribute('id');
      expect(passwordInput).toHaveAttribute('id');
    });

    it('has autocomplete attributes for form fields', () => {
      renderWithRouter(<LoginForm />);
      
      expect(screen.getByLabelText(/username/i)).toHaveAttribute('autocomplete', 'username');
      expect(screen.getByLabelText(/password/i)).toHaveAttribute('autocomplete', 'current-password');
    });

    it('error messages have role="alert"', async () => {
      const user = userEvent.setup();
      renderWithRouter(<LoginForm />);
      
      await user.click(screen.getByRole('button', { name: /sign in/i }));
      
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });
  });
});
