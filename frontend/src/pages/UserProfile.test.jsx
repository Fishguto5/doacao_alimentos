import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import UserProfile from './UserProfile'
import MobileNav from '../components/MobileNav'
import { api } from '../api'
import { useUser } from '../context/UserContext'

vi.mock('../api', () => ({
  api: {
    getDoacoes: vi.fn(),
    getSolicitacoes: vi.fn(),
    getNotificacoes: vi.fn(),
    deleteDoacao: vi.fn(),
  },
}))

vi.mock('../context/UserContext', () => ({ useUser: vi.fn() }))
vi.mock('../components/DonationCard', () => ({
  default: ({ doacao }) => <article>{doacao.titulo}</article>,
}))

describe('UserProfile mobile navigation and donations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.location.hash = '#/profile?tab=solicitacoes'
    useUser.mockReturnValue({ user: { id: 1, nome: 'Ana', email: 'ana@example.com' }, login: vi.fn(), logout: vi.fn() })
    api.getDoacoes.mockResolvedValue([
      { id: 10, doador: 1, titulo: 'Cesta de alimentos' },
      { id: 11, doador: 2, titulo: 'Hortifruti reservado' },
    ])
    api.getSolicitacoes.mockResolvedValue([{ id: 20, doacao: 11, solicitante: 1, status: 'aceita', data_solicitacao: '2026-11-15T10:00:00Z' }])
    api.getNotificacoes.mockResolvedValue([])
    api.deleteDoacao.mockResolvedValue(null)
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('opens personal data from the bottom navigation and switches between reservations and donations', async () => {
    render(<><UserProfile /><MobileNav /></>)

    expect(await screen.findByText('Ver doacao ->')).toBeInTheDocument()
    expect(screen.getByText('Hortifruti reservado')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Perfil' }))
    expect(await screen.findByText('ana@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Meus dados' })).toHaveClass('active')

    fireEvent.click(screen.getByRole('button', { name: /Minhas doações/ }))
    expect(await screen.findByText('Cesta de alimentos')).toBeInTheDocument()
  })

  it('removes a confirmed donation from the profile list', async () => {
    window.location.hash = '#/profile?tab=doacoes'
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    render(<UserProfile />)

    const button = await screen.findByRole('button', { name: 'Excluir doação Cesta de alimentos' })
    fireEvent.click(button)

    await waitFor(() => expect(api.deleteDoacao).toHaveBeenCalledWith(10))
    expect(screen.queryByText('Cesta de alimentos')).not.toBeInTheDocument()
    expect(screen.getByText('Doação excluída com sucesso.')).toBeInTheDocument()
  })
})
