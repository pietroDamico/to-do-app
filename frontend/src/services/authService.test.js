/**
 * Tests for the authentication service.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { register, loginUser } from './authService';
import api from './api';

// Mock the api module
vi.mock('./api', () => ({
  default: {
    post: vi.fn(),
  },
}));

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('register', () => {
    it('calls POST /api/auth/register with username and password', async () => {
      const mockResponse = {
        data: { id: 1, username: 'testuser', created_at: '2026-01-06T12:00:00Z' },
      };
      api.post.mockResolvedValue(mockResponse);

      const result = await register('testuser', 'password123');

      expect(api.post).toHaveBeenCalledWith('/api/auth/register', {
        username: 'testuser',
        password: 'password123',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when registration fails', async () => {
      const error = {
        response: { status: 409, data: { detail: 'Username already exists' } },
      };
      api.post.mockRejectedValue(error);

      await expect(register('existinguser', 'password123')).rejects.toEqual(error);
    });
  });

  describe('loginUser', () => {
    it('calls POST /api/auth/login with username and password', async () => {
      const mockResponse = {
        data: {
          access_token: 'jwt.token.here',
          token_type: 'bearer',
          user: { id: 1, username: 'testuser' },
        },
      };
      api.post.mockResolvedValue(mockResponse);

      const result = await loginUser('testuser', 'password123');

      expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
        username: 'testuser',
        password: 'password123',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when login fails', async () => {
      const error = {
        response: { status: 401, data: { detail: 'Invalid credentials' } },
      };
      api.post.mockRejectedValue(error);

      await expect(loginUser('wronguser', 'wrongpass')).rejects.toEqual(error);
    });
  });
});
