/**
 * Tests for the main App component.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'

// Mock the API service
vi.mock('./services/api', () => ({
  healthCheck: vi.fn(),
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import { healthCheck } from './services/api'

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('Unauthenticated state', () => {
    it('renders the app title on home page', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)
      expect(screen.getByText('To-Do App')).toBeInTheDocument()
    })

    it('displays API status from health check', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        const healthyElements = screen.getAllByText('healthy')
        expect(healthyElements).toHaveLength(2)
      })
    })

    it('displays error status when health check fails', async () => {
      healthCheck.mockRejectedValue(new Error('Connection failed'))

      render(<App />)

      await waitFor(() => {
        const errorElements = screen.getAllByText('error')
        expect(errorElements).toHaveLength(2)
      })
    })

    it('shows register and login links when not authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      expect(screen.getByRole('link', { name: /register/i })).toHaveAttribute('href', '/register')
      expect(screen.getByRole('link', { name: /login/i })).toHaveAttribute('href', '/login')
    })

    it('does not show logout button when not authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument()
    })

    it('displays unhealthy database status correctly', async () => {
      healthCheck.mockResolvedValue({
        status: 'degraded',
        components: {
          api: 'healthy',
          database: 'unhealthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        expect(screen.getByText('healthy')).toBeInTheDocument()
        expect(screen.getByText('unhealthy')).toBeInTheDocument()
      })
    })
  })

  describe('Authenticated state', () => {
    beforeEach(() => {
      // Set up authenticated state in localStorage
      localStorage.setItem('token', 'test-token')
      localStorage.setItem('user', JSON.stringify({ id: 1, username: 'testuser' }))
    })

    it('shows welcome message with username when authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        expect(screen.getByText(/welcome, testuser/i)).toBeInTheDocument()
      })
    })

    it('shows logout button when authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
      })
    })

    it('does not show register/login links when authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        expect(screen.queryByRole('link', { name: /^register$/i })).not.toBeInTheDocument()
        expect(screen.queryByRole('link', { name: /^login$/i })).not.toBeInTheDocument()
      })
    })

    it('shows link to todo list when authenticated', async () => {
      healthCheck.mockResolvedValue({
        status: 'healthy',
        components: {
          api: 'healthy',
          database: 'healthy',
        },
      })

      render(<App />)

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /view my to-do list/i })).toBeInTheDocument()
        expect(screen.getByRole('link', { name: /view my to-do list/i })).toHaveAttribute('href', '/todos')
      })
    })
  })
})
