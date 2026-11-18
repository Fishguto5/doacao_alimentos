import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import UserProfile from './UserProfile'
import MobileNav from '../components/MobileNav'
import Header from '../components/Header'
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

  it('opens personal data from the side menu and switches between reservations and donations', async () => {
    window.location.hash = '#/'
    render(<><Header /><UserProfile /><MobileNav /></>)

    fireEvent.click(screen.getByRole('button', { name: 'Abrir menu' }))
    fireEvent.click(screen.getByRole('button', { name: 'Meu perfil' }))
    expect(await screen.findByText('ana@example.com')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Meus dados' })).toHaveClass('active'))

    fireEvent.click(screen.getByRole('button', { name: 'Reservas' }))
    expect(await screen.findByText('Hortifruti reservado')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Minhas doações/ }))
    expect(await screen.findByText('Cesta de alimentos')).toBeInTheDocument()
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Navegação principal' })).getByRole('button', { name: 'Mensagens' }))
    expect(window.location.hash).toBe('#/chat')
  })

  it('opens the same chat from the desktop header', () => {
    window.location.hash = '#/'
    render(<Header />)

    const desktopNav = screen.getByRole('navigation', { name: 'Navegação desktop' })
    fireEvent.click(within(desktopNav).getByRole('button', { name: 'Mensagens' }))

    expect(window.location.hash).toBe('#/chat')
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

  it('updates the bell and mobile badge when a notification arrives', async () => {
    window.location.hash = '#/'
    render(<><Header /><MobileNav /></>)
    await waitFor(() => expect(api.getNotificacoes).toHaveBeenCalledTimes(2))

    api.getNotificacoes.mockResolvedValue([
      { id: 99, usuario: 1, doacao: 10, mensagem: 'Sua doação foi reservada.', status: 'pendente', created_at: '2026-11-17T10:00:00Z' },
      { id: 100, usuario: 2, doacao: 10, mensagem: 'Outra pessoa', status: 'pendente', created_at: '2026-11-17T10:00:00Z' },
    ])
    window.dispatchEvent(new Event('notifications-updated'))

    expect(await screen.findByRole('button', { name: 'Notificações, 1 não lidas' })).toBeInTheDocument()
    expect(screen.getByLabelText('1 notificações não lidas')).toBeInTheDocument()
  })
})
