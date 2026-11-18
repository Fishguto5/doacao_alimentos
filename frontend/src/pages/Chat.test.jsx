import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import Chat from './Chat'
import { api } from '../api'
import { useUser } from '../context/UserContext'

vi.mock('../api', () => ({
  api: {
    getDoacoes: vi.fn(),
    getSolicitacoes: vi.fn(),
    getAvaliacoes: vi.fn(),
    getUsuario: vi.fn(),
    getMensagens: vi.fn(),
    sendMensagem: vi.fn(),
  },
}))
vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }))

describe('Chat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useUser.mockReturnValue({ user: { id: 1, nome: 'Ana', auth_token: 'token' } })
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
    api.getMensagens.mockResolvedValue([
      { id: 40, doacao: 10, remetente: 2, texto: 'Podemos combinar a retirada?', created_at: '2026-11-09T10:00:00Z' },
    ])
  })

  afterEach(() => cleanup())

  it('shows comments from donations created or reserved by the user without exposing other requests', async () => {
    render(<Chat />)

    await screen.findByRole('region', { name: 'Conversas' })
    fireEvent.click(screen.getByRole('button', { name: /Cesta criada/ }))
    const created = screen.getByRole('region', { name: 'Conversa de Cesta criada' })
    expect(within(created).getByText('Quero retirar esta cesta')).toBeInTheDocument()
    expect(within(created).getByText('Entrega excelente')).toBeInTheDocument()
    expect(within(created).getByText('Podemos combinar a retirada?')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /Cesta reservada/ }))
    const reserved = screen.getByRole('region', { name: 'Conversa de Cesta reservada' })
    expect(within(reserved).getByText('Posso buscar amanhã')).toBeInTheDocument()
    expect(within(reserved).getByText('Retirada tranquila')).toBeInTheDocument()
    expect(screen.queryByText('Mensagem de outro solicitante')).not.toBeInTheDocument()
    expect(screen.queryByText('Comentário externo')).not.toBeInTheDocument()
    expect(screen.queryByText('Outra doação')).not.toBeInTheDocument()
  })

  it('sends a message in the selected donation and displays it', async () => {
    api.sendMensagem.mockResolvedValue({ id: 41, doacao: 10, remetente: 1, texto: 'Sim, amanhã!', created_at: '2026-11-09T11:00:00Z' })
    render(<Chat />)
    await screen.findByRole('region', { name: 'Conversas' })
    fireEvent.click(screen.getByRole('button', { name: /Cesta criada/ }))
    fireEvent.change(screen.getByRole('textbox', { name: 'Sua mensagem' }), { target: { value: 'Sim, amanhã!' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar' }))
    expect(await within(screen.getByRole('log')).findByText('Sim, amanhã!')).toBeInTheDocument()
    expect(api.sendMensagem).toHaveBeenCalledWith({ doacao: 10, texto: 'Sim, amanhã!' })
  })
})
