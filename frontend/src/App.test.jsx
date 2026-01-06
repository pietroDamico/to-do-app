/**
 * Tests for the main App component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'

// Mock the API service
vi.mock('./services/api', () => ({
  healthCheck: vi.fn(),
  default: {
    post: vi.fn(),
  },
}))

import { healthCheck } from './services/api'

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the app title on home page', async () => {
    healthCheck.mockResolvedValue({
      status: 'healthy',
      components: {
        api: { status: 'healthy' },
        database: { status: 'healthy' },
      },
    })

    render(<App />)
    expect(screen.getByText('To-Do App')).toBeInTheDocument()
  })

  it('displays API status from health check', async () => {
    healthCheck.mockResolvedValue({
      status: 'healthy',
      components: {
        api: { status: 'healthy' },
        database: { status: 'healthy' },
      },
    })

    render(<App />)

    await waitFor(() => {
      // Check that both status elements exist
      const healthyElements = screen.getAllByText('healthy')
      expect(healthyElements).toHaveLength(2)
    })
  })

  it('displays error status when health check fails', async () => {
    healthCheck.mockRejectedValue(new Error('Connection failed'))

    render(<App />)

    await waitFor(() => {
      // Check that both status elements show error
      const errorElements = screen.getAllByText('error')
      expect(errorElements).toHaveLength(2)
    })
  })

  it('has links to register and login pages', async () => {
    healthCheck.mockResolvedValue({
      status: 'healthy',
      components: {
        api: { status: 'healthy' },
        database: { status: 'healthy' },
      },
    })

    render(<App />)

    expect(screen.getByRole('link', { name: /register/i })).toHaveAttribute('href', '/register')
    expect(screen.getByRole('link', { name: /login/i })).toHaveAttribute('href', '/login')
  })
})
