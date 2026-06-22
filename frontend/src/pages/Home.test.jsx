import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import Home from './Home'
import { api } from '../api'

vi.mock('../api', () => ({
  api: {
    getCategorias: vi.fn(),
    getDoacoes: vi.fn(),
  },
}))

vi.mock('../context/UserContext', () => ({
  useUser: () => ({ user: null }),
}))

vi.mock('../components/DonationCard', () => ({
  default: ({ doacao }) => <div>{doacao.titulo}</div>,
}))

describe('Home', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getCategorias.mockResolvedValue([
      { id: 1, nome: 'Frutas' },
      { id: 2, nome: 'Legumes' },
    ])
    api.getDoacoes.mockResolvedValueOnce([
      {
        id: 1,
        titulo: 'Doacao Frutas',
        descricao: 'Descricao 1',
        status: 'disponivel',
        data_publicacao: '2026-06-01T10:00:00Z',
        cidade: 'Campinas',
        estado: 'SP',
        bairro: 'Centro',
        estimativa_peso: '2.00',
      },
      {
        id: 2,
        titulo: 'Doacao Legumes',
        descricao: 'Descricao 2',
        status: 'disponivel',
        data_publicacao: '2026-06-02T10:00:00Z',
        cidade: 'Campinas',
        estado: 'SP',
        bairro: 'Centro',
        estimativa_peso: '3.00',
      },
    ])
    api.getDoacoes.mockResolvedValueOnce([
      {
        id: 2,
        titulo: 'Doacao Legumes',
        descricao: 'Descricao 2',
        status: 'disponivel',
        data_publicacao: '2026-06-02T10:00:00Z',
        cidade: 'Campinas',
        estado: 'SP',
        bairro: 'Centro',
        estimativa_peso: '3.00',
      },
    ])
  })

  afterEach(() => {
    cleanup()
  })

  it('recarrega as doações ao filtrar por categoria', async () => {
    render(<Home />)

    expect(api.getCategorias).toHaveBeenCalledTimes(1)
    await screen.findByText('Doacao Frutas')
    expect(api.getDoacoes).toHaveBeenNthCalledWith(1, { status: 'disponivel' })

    fireEvent.change(screen.getByLabelText('Filtro por categoria de alimento'), {
      target: { value: '2' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenNthCalledWith(2, { categoria: '2', status: 'disponivel' })
    })

    expect(await screen.findByText('Doacao Legumes')).toBeInTheDocument()
    expect(screen.queryByText('Doacao Frutas')).not.toBeInTheDocument()
  })

  it('recarrega as doações ao filtrar por status', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')
    expect(api.getDoacoes).toHaveBeenNthCalledWith(1, { status: 'disponivel' })

    fireEvent.change(screen.getByDisplayValue('Disponível'), {
      target: { value: 'reservada' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenNthCalledWith(2, { status: 'reservada' })
    })
  })

  it('envia a requisição sem filtro de status quando "Todos os status" é selecionado', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')

    fireEvent.change(screen.getByDisplayValue('Disponível'), {
      target: { value: '' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenNthCalledWith(2, undefined)
    })
  })
})