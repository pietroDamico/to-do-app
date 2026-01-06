/**
 * Tests for the RegisterForm component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { RegisterForm } from './RegisterForm';

// Mock the auth service
vi.mock('../../services/authService', () => ({
  register: vi.fn(),
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

import { register } from '../../services/authService';

// Helper to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the registration form with all fields', () => {
      renderWithRouter(<RegisterForm />);
      
      expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });

    it('has password field with type password (masked)', () => {
      renderWithRouter(<RegisterForm />);
      
      const passwordInput = screen.getByLabelText(/password/i);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('has link to login page', () => {
      renderWithRouter(<RegisterForm />);
      
      const loginLink = screen.getByRole('link', { name: /login here/i });
      expect(loginLink).toHaveAttribute('href', '/login');
    });

    it('has placeholder text for inputs', () => {
      renderWithRouter(<RegisterForm />);
      
      expect(screen.getByPlaceholderText(/enter username/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter password/i)).toBeInTheDocument();
    });
  });

  describe('Client-side Validation', () => {
    it('shows error for username less than 3 characters', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'ab');
      await user.type(screen.getByLabelText(/password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('shows error for password less than 8 characters', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'validuser');
      await user.type(screen.getByLabelText(/password/i), 'short');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('shows error for empty username', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('shows error for empty password', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'validuser');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('shows error for username with invalid characters', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'user@name');
      await user.type(screen.getByLabelText(/password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/username can only contain letters, numbers, and underscores/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('shows error for username longer than 50 characters', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      const longUsername = 'a'.repeat(51);
      await user.type(screen.getByLabelText(/username/i), longUsername);
      await user.type(screen.getByLabelText(/password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/username must be at most 50 characters/i)).toBeInTheDocument();
      expect(register).not.toHaveBeenCalled();
    });

    it('clears field error when user starts typing', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      // Trigger validation error
      await user.type(screen.getByLabelText(/username/i), 'ab');
      await user.type(screen.getByLabelText(/password/i), 'validpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
      
      // Type more to clear error
      await user.type(screen.getByLabelText(/username/i), 'c');
      
      expect(screen.queryByText(/username must be at least 3 characters/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('calls register API with correct credentials on valid submission', async () => {
      const user = userEvent.setup();
      register.mockResolvedValue({ id: 1, username: 'testuser', created_at: '2026-01-06T12:00:00Z' });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(register).toHaveBeenCalledWith('testuser', 'testpass123');
    });

    it('shows loading state during submission', async () => {
      const user = userEvent.setup();
      // Make the registration take some time
      register.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      // Check loading state
      expect(screen.getByText(/creating account/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeDisabled();
      expect(screen.getByLabelText(/password/i)).toBeDisabled();
    });

    it('disables submit button during loading', async () => {
      const user = userEvent.setup();
      register.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('redirects to login page on successful registration', async () => {
      const user = userEvent.setup();
      register.mockResolvedValue({ id: 1, username: 'testuser', created_at: '2026-01-06T12:00:00Z' });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login', {
          state: { message: 'Registration successful! Please login.' }
        });
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message for duplicate username (409)', async () => {
      const user = userEvent.setup();
      register.mockRejectedValue({
        response: { status: 409, data: { detail: 'Username already exists' } }
      });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'existinguser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/username already exists/i)).toBeInTheDocument();
      });
    });

    it('displays error message for validation errors (422)', async () => {
      const user = userEvent.setup();
      register.mockRejectedValue({
        response: { status: 422, data: { detail: 'Validation error' } }
      });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/validation error/i)).toBeInTheDocument();
      });
    });

    it('displays generic error message for unknown errors', async () => {
      const user = userEvent.setup();
      register.mockRejectedValue({
        response: { status: 500 }
      });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'testuser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      await waitFor(() => {
        expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
      });
    });

    it('re-enables form after error', async () => {
      const user = userEvent.setup();
      register.mockRejectedValue({
        response: { status: 409, data: { detail: 'Username already exists' } }
      });
      
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'existinguser');
      await user.type(screen.getByLabelText(/password/i), 'testpass123');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      await waitFor(() => {
        expect(screen.getByLabelText(/username/i)).not.toBeDisabled();
        expect(screen.getByLabelText(/password/i)).not.toBeDisabled();
        expect(screen.getByRole('button', { name: /create account/i })).not.toBeDisabled();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper labels for all form fields', () => {
      renderWithRouter(<RegisterForm />);
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      
      expect(usernameInput).toHaveAttribute('id');
      expect(passwordInput).toHaveAttribute('id');
    });

    it('sets aria-invalid on fields with errors', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'ab');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      expect(screen.getByLabelText(/username/i)).toHaveAttribute('aria-invalid', 'true');
    });

    it('has autocomplete attributes for form fields', () => {
      renderWithRouter(<RegisterForm />);
      
      expect(screen.getByLabelText(/username/i)).toHaveAttribute('autocomplete', 'username');
      expect(screen.getByLabelText(/password/i)).toHaveAttribute('autocomplete', 'new-password');
    });

    it('error messages have role="alert"', async () => {
      const user = userEvent.setup();
      renderWithRouter(<RegisterForm />);
      
      await user.type(screen.getByLabelText(/username/i), 'ab');
      await user.click(screen.getByRole('button', { name: /create account/i }));
      
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBeGreaterThan(0);
    });
  });
});
