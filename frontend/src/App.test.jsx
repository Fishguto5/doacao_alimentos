import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

beforeEach(() => {
  window.location.hash = '#/'
  localStorage.clear()

  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: [] }),
    }),
  )
})

describe('App', () => {
  it('renderiza a tela inicial', async () => {
    render(<App />)

    expect(screen.getByRole('button', { name: /DoacaoAlimentos/i })).toBeInTheDocument()
    expect(
      await screen.findByRole('heading', { name: /transforme vidas/i }),
    ).toBeInTheDocument()
  })
})
