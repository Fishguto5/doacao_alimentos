import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import DonationDetail from './DonationDetail'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

vi.mock('../api', () => ({
  api: {
    getDoacao: vi.fn(),
    getAlimentos: vi.fn(),
    getSolicitacoes: vi.fn(),
    getAvaliacoes: vi.fn(),
    getUsuario: vi.fn(),
  },
}))

vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}))

vi.mock('../router', () => ({
  navigate: vi.fn(),
}))

describe('DonationDetail', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const donation = {
    id: 1,
    titulo: 'Doação de Teste',
    descricao: 'Descrição de teste',
    imagem: '/media/doacoes/test.jpg',
    status: 'disponivel',
    data_publicacao: '2026-05-12T12:00:00Z',
    cep: '13000000',
    cidade: 'Campinas',
    estado: 'SP',
    bairro: 'Centro',
    logradouro: 'Rua Teste',
    numero: '100',
    complemento: '',
    estimativa_peso: '5.00',
    expira_em: null,
    doador: 1,
    receptor: null,
  }

  function mockDonationDetail(overrides = {}) {
    api.getDoacao.mockResolvedValue({ ...donation, ...overrides })
    api.getAlimentos.mockResolvedValue([])
    api.getSolicitacoes.mockResolvedValue([])
    api.getAvaliacoes.mockResolvedValue([])
    api.getUsuario.mockResolvedValue({ id: 1, nome: 'Doador Teste' })
  }

  it('renders the donation image when imagem is returned by the API', async () => {
    useUser.mockReturnValue({ user: { id: 1 } })
    mockDonationDetail()

    render(<DonationDetail id={1} />)

    const image = await screen.findByRole('img', { name: /Doação de Teste/i })
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', '/media/doacoes/test.jpg')
    expect(api.getAvaliacoes).toHaveBeenCalledWith({ doacao: 1 })
  })

  it('opens the public donor profile from the donation detail', async () => {
    useUser.mockReturnValue({ user: { id: 2 } })
    mockDonationDetail({ receptor: 2 })

    render(<DonationDetail id={1} />)

    const donorButton = await screen.findByRole('button', { name: /Doador Teste/i })
    fireEvent.click(donorButton)

    expect(navigate).toHaveBeenCalledWith('#/users/1')
  })

  it('shows rating action only to the receiver of a completed donation', async () => {
    useUser.mockReturnValue({ user: { id: 2 } })
    mockDonationDetail({ status: 'concluida', receptor: 2 })

    render(<DonationDetail id={1} />)

    expect(await screen.findByRole('button', { name: /deixar avaliação/i })).toBeInTheDocument()
  })

  it('does not show rating action to the donor of a completed donation', async () => {
    useUser.mockReturnValue({ user: { id: 1 } })
    mockDonationDetail({ status: 'concluida', receptor: 2 })

    render(<DonationDetail id={1} />)

    await screen.findByRole('heading', { name: /Doação de Teste/i })
    expect(screen.queryByRole('button', { name: /deixar avaliação/i })).not.toBeInTheDocument()
  })
})
