/**
 * Tests for the LogoutButton component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LogoutButton } from './LogoutButton';

// Mock the auth context
const mockLogout = vi.fn();
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    logout: mockLogout,
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

// Helper to render component with router
const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('LogoutButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the logout button', () => {
    renderWithRouter(<LogoutButton />);
    
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('calls logout and navigates to login on click', async () => {
    const user = userEvent.setup();
    renderWithRouter(<LogoutButton />);
    
    await user.click(screen.getByRole('button', { name: /logout/i }));
    
    expect(mockLogout).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('accepts additional className', () => {
    renderWithRouter(<LogoutButton className="custom-class" />);
    
    const button = screen.getByRole('button', { name: /logout/i });
    expect(button).toHaveClass('logout-button');
    expect(button).toHaveClass('custom-class');
  });

  it('has type="button" to prevent form submission', () => {
    renderWithRouter(<LogoutButton />);
    
    const button = screen.getByRole('button', { name: /logout/i });
    expect(button).toHaveAttribute('type', 'button');
  });
});
