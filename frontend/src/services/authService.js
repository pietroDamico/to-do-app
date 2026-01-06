/**
 * Authentication service for user registration and login operations.
 */
import api from './api';

/**
 * Register a new user.
 * 
 * @param {string} username - The username (3-50 chars, alphanumeric + underscore)
 * @param {string} password - The password (minimum 8 characters)
 * @returns {Promise<Object>} The created user object (id, username, created_at)
 * @throws {Error} If registration fails (409 for duplicate username, 422 for validation errors)
 */
export const register = async (username, password) => {
  const response = await api.post('/api/auth/register', {
    username,
    password,
  });
  return response.data;
};

/**
 * Login an existing user.
 * 
 * @param {string} username - The username
 * @param {string} password - The password
 * @returns {Promise<Object>} The login response with access_token and user info
 * @throws {Error} If login fails (401 for invalid credentials)
 */
export const loginUser = async (username, password) => {
  const response = await api.post('/api/auth/login', {
    username,
    password,
  });
  return response.data;
};
