import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, within } from '@testing-library/react'
import Chat from './Chat'
import { api } from '../api'
import { useUser } from '../context/UserContext'

vi.mock('../api', () => ({
  api: {
    getDoacoes: vi.fn(),
    getSolicitacoes: vi.fn(),
    getAvaliacoes: vi.fn(),
    getUsuario: vi.fn(),
  },
}))
vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }))

describe('Chat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useUser.mockReturnValue({ user: { id: 1, nome: 'Ana' } })
    api.getDoacoes.mockResolvedValue([
      { id: 10, doador: 1, receptor: 2, titulo: 'Cesta criada', data_publicacao: '2026-11-01T10:00:00Z' },
      { id: 11, doador: 2, receptor: 1, titulo: 'Cesta reservada', data_publicacao: '2026-11-02T10:00:00Z' },
      { id: 12, doador: 2, receptor: 3, titulo: 'Outra doação', data_publicacao: '2026-11-03T10:00:00Z' },
    ])
    api.getSolicitacoes.mockResolvedValue([
      { id: 20, doacao: 10, solicitante: 2, status: 'aceita', mensagem: 'Quero retirar esta cesta', data_solicitacao: '2026-11-04T10:00:00Z' },
      { id: 21, doacao: 11, solicitante: 1, status: 'aceita', mensagem: 'Posso buscar amanhã', data_solicitacao: '2026-11-05T10:00:00Z' },
      { id: 22, doacao: 11, solicitante: 3, status: 'recusada', mensagem: 'Mensagem de outro solicitante', data_solicitacao: '2026-11-05T10:00:00Z' },
      { id: 23, doacao: 12, solicitante: 3, status: 'aceita', mensagem: 'Mensagem de outra doação', data_solicitacao: '2026-11-06T10:00:00Z' },
    ])
    api.getAvaliacoes.mockResolvedValue([
      { id: 30, doacao: 10, avaliador: 2, comentario: 'Entrega excelente', created_at: '2026-11-07T10:00:00Z' },
      { id: 31, doacao: 11, avaliador: 2, comentario: 'Retirada tranquila', created_at: '2026-11-08T10:00:00Z' },
      { id: 32, doacao: 12, avaliador: 3, comentario: 'Comentário externo', created_at: '2026-11-08T10:00:00Z' },
    ])
    api.getUsuario.mockResolvedValue({ id: 2, nome: 'Bruno' })
  })

  afterEach(() => cleanup())

  it('shows comments from donations created or reserved by the user without exposing other requests', async () => {
    render(<Chat />)

    const created = await screen.findByRole('region', { name: 'Comentários de Cesta criada' })
    const reserved = screen.getByRole('region', { name: 'Comentários de Cesta reservada' })
    expect(within(created).getByText('Quero retirar esta cesta')).toBeInTheDocument()
    expect(within(created).getByText('Entrega excelente')).toBeInTheDocument()
    expect(within(reserved).getByText('Posso buscar amanhã')).toBeInTheDocument()
    expect(within(reserved).getByText('Retirada tranquila')).toBeInTheDocument()
    expect(screen.queryByText('Mensagem de outro solicitante')).not.toBeInTheDocument()
    expect(screen.queryByText('Comentário externo')).not.toBeInTheDocument()
    expect(screen.queryByText('Outra doação')).not.toBeInTheDocument()
  })
})
