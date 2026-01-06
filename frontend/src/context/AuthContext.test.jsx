/**
 * Tests for the AuthContext.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';

// Test component that uses the auth context
function TestComponent() {
  const { user, token, isAuthenticated, loading, login, logout } = useAuth();
  
  return (
    <div>
      <span data-testid="loading">{loading ? 'loading' : 'loaded'}</span>
      <span data-testid="authenticated">{isAuthenticated ? 'yes' : 'no'}</span>
      <span data-testid="username">{user?.username || 'none'}</span>
      <span data-testid="token">{token || 'none'}</span>
      <button onClick={() => login('test-token', { id: 1, username: 'testuser' })}>
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Initial state', () => {
    it('starts with no user and loading false after mount', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for useEffect to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(screen.getByTestId('username')).toHaveTextContent('none');
      expect(screen.getByTestId('token')).toHaveTextContent('none');
    });

    it('restores auth state from localStorage on mount', async () => {
      // Set up localStorage before render
      localStorage.setItem('token', 'stored-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'storeduser' }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for useEffect to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(screen.getByTestId('username')).toHaveTextContent('storeduser');
      expect(screen.getByTestId('token')).toHaveTextContent('stored-token');
    });

    it('clears invalid stored data', async () => {
      // Set up invalid localStorage data
      localStorage.setItem('token', 'valid-token');
      localStorage.setItem('user', 'invalid-json{');

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for useEffect to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });

  describe('login', () => {
    it('stores token and user in state and localStorage', async () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for initial load
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      // Click login button
      await act(async () => {
        screen.getByText('Login').click();
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      expect(screen.getByTestId('username')).toHaveTextContent('testuser');
      expect(screen.getByTestId('token')).toHaveTextContent('test-token');
      expect(localStorage.getItem('token')).toBe('test-token');
      expect(JSON.parse(localStorage.getItem('user'))).toEqual({ id: 1, username: 'testuser' });
    });
  });

  describe('logout', () => {
    it('clears token and user from state and localStorage', async () => {
      // Start with logged in state
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'testuser' }));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      // Wait for initial load
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');

      // Click logout button
      await act(async () => {
        screen.getByText('Logout').click();
      });

      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      expect(screen.getByTestId('username')).toHaveTextContent('none');
      expect(screen.getByTestId('token')).toHaveTextContent('none');
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });

  describe('useAuth hook', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(<TestComponent />);
      }).toThrow('useAuth must be used within an AuthProvider');

      consoleSpy.mockRestore();
    });
  });
});
