import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import PublicUserProfile from './PublicUserProfile'
import { api } from '../api'

vi.mock('../api', () => ({
  api: {
    getUsuario: vi.fn(),
    getDoacoes: vi.fn(),
    getAvaliacoes: vi.fn(),
  },
}))

vi.mock('../router', () => ({
  navigate: vi.fn(),
}))

vi.mock('../components/DonationCard', () => ({
  default: ({ doacao }) => <article>{doacao.titulo}</article>,
}))

describe('PublicUserProfile', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getUsuario.mockImplementation(id => {
      if (Number(id) === 1) {
        return Promise.resolve({
          id: 1,
          nome: 'Doador Teste',
          cidade: 'Campinas',
          estado: 'SP',
          foto_perfil_url: '',
        })
      }
      return Promise.resolve({
        id: 2,
        nome: 'Receptor Teste',
        cidade: 'Valinhos',
        estado: 'SP',
        foto_perfil_url: '',
      })
    })
    api.getDoacoes.mockResolvedValue([
      {
        id: 10,
        titulo: 'Doação publicada',
        doador: 1,
        status: 'concluida',
        data_publicacao: '2026-06-01T10:00:00Z',
      },
      {
        id: 11,
        titulo: 'Doação de outro usuário',
        doador: 3,
        status: 'disponivel',
        data_publicacao: '2026-06-02T10:00:00Z',
      },
    ])
    api.getAvaliacoes.mockResolvedValue([
      {
        id: 20,
        doacao: 10,
        avaliador: 2,
        avaliado: 1,
        nota: 5,
        comentario: 'Retirada combinada e alimentos em ótimo estado.',
        created_at: '2026-06-03T10:00:00Z',
      },
    ])
  })

  afterEach(() => {
    cleanup()
  })

  it('renders public profile ratings and donations', async () => {
    render(<PublicUserProfile id="1" />)

    expect(await screen.findByRole('heading', { name: /Doador Teste/i })).toBeInTheDocument()
    expect(api.getAvaliacoes).toHaveBeenCalledWith({ avaliado: '1' })
    expect(screen.getByText(/Receptor Teste/)).toBeInTheDocument()
    expect(screen.getByText('Retirada combinada e alimentos em ótimo estado.')).toBeInTheDocument()
    expect(screen.getByText('Doação publicada')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByText('Doação de outro usuário')).not.toBeInTheDocument()
    })
  })
})
