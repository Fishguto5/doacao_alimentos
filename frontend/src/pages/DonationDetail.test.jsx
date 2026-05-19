import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import DonationDetail from './DonationDetail'
import { api } from '../api'
import { useUser } from '../context/UserContext'

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

describe('DonationDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the donation image when imagem is returned by the API', async () => {
    useUser.mockReturnValue({ user: { id: 1 } })
    api.getDoacao.mockResolvedValue({
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
    })
    api.getAlimentos.mockResolvedValue([])
    api.getSolicitacoes.mockResolvedValue([])
    api.getAvaliacoes.mockResolvedValue([])
    api.getUsuario.mockResolvedValue({ id: 1, nome: 'Doador Teste' })

    render(<DonationDetail id={1} />)

    const image = await screen.findByRole('img', { name: /Doação de Teste/i })
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', '/media/doacoes/test.jpg')
  })
})
