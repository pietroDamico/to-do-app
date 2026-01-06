/**
 * Tests for the ProtectedRoute component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';

// Mock the auth context with different states
let mockAuthState = {
  isAuthenticated: false,
  loading: false,
};

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => mockAuthState,
}));

// Helper to render with router
const renderWithRouter = (initialRoute = '/protected') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route 
          path="/protected" 
          element={
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          } 
        />
      </Routes>
    </MemoryRouter>
  );
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState = {
      isAuthenticated: false,
      loading: false,
    };
  });

  it('redirects to login when not authenticated', () => {
    mockAuthState = { isAuthenticated: false, loading: false };
    renderWithRouter();
    
    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    mockAuthState = { isAuthenticated: true, loading: false };
    renderWithRouter();
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });

  it('shows loading state while checking authentication', () => {
    mockAuthState = { isAuthenticated: false, loading: true };
    renderWithRouter();
    
    expect(screen.getByLabelText('Loading')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });

  it('does not redirect while loading even if not authenticated', () => {
    mockAuthState = { isAuthenticated: false, loading: true };
    renderWithRouter();
    
    // Should show loading, not redirect
    expect(screen.getByLabelText('Loading')).toBeInTheDocument();
    expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
  });
});
