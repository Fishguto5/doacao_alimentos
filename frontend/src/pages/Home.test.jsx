import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import Home from './Home'
import { api } from '../api'

vi.mock('../api', () => ({
  api: {
    getCategorias: vi.fn(),
    getCidades: vi.fn(),
    getDoacoes: vi.fn(),
  },
}))

vi.mock('../context/UserContext', () => ({
  useUser: () => ({ user: null }),
}))

vi.mock('../components/DonationCard', () => ({
  default: ({ doacao }) => <div>{doacao.titulo}</div>,
}))

const DOACAO_FRUTAS = {
  id: 1,
  titulo: 'Doacao Frutas',
  descricao: 'Descricao 1',
  status: 'disponivel',
  data_publicacao: '2026-06-01T10:00:00Z',
  cidade: 'Campinas',
  estado: 'SP',
  bairro: 'Centro',
  estimativa_peso: '2.00',
}

const DOACAO_LEGUMES = {
  id: 2,
  titulo: 'Doacao Legumes',
  descricao: 'Descricao 2',
  status: 'disponivel',
  data_publicacao: '2026-06-02T10:00:00Z',
  cidade: 'São Paulo',
  estado: 'SP',
  bairro: 'Centro',
  estimativa_peso: '3.00',
}

describe('Home', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getCategorias.mockResolvedValue([
      { id: 1, nome: 'Frutas' },
      { id: 2, nome: 'Legumes' },
    ])
    api.getCidades.mockResolvedValue(['Campinas', 'São Paulo'])
    // Mock permanente: sempre retorna a lista completa por padrão.
    // Cada teste redefine com mockResolvedValueOnce quando precisa de um retorno diferente.
    api.getDoacoes.mockResolvedValue([DOACAO_FRUTAS, DOACAO_LEGUMES])
  })

  afterEach(() => {
    cleanup()
  })

  it('recarrega as doações ao filtrar por categoria', async () => {
    render(<Home />)

    expect(api.getCategorias).toHaveBeenCalledTimes(1)
    await screen.findByText('Doacao Frutas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_LEGUMES])

    fireEvent.change(screen.getByLabelText('Filtro por categoria de alimento'), {
      target: { value: '2' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ categoria: '2', status: 'disponivel' })
    })

    expect(await screen.findByText('Doacao Legumes')).toBeInTheDocument()
    expect(screen.queryByText('Doacao Frutas')).not.toBeInTheDocument()
  })

  it('recarrega as doações ao filtrar por status', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')

    api.getDoacoes.mockResolvedValueOnce([])

    fireEvent.change(screen.getByDisplayValue('Disponível'), {
      target: { value: 'reservada' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'reservada' })
    })
  })

  it('envia a requisição sem filtro de status quando "Todos os status" é selecionado', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS, DOACAO_LEGUMES])

    fireEvent.change(screen.getByDisplayValue('Disponível'), {
      target: { value: '' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith(undefined)
    })
  })

  it('recarrega as doações ao filtrar por peso máximo', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_LEGUMES])

    fireEvent.change(screen.getByLabelText('Filtro por peso máximo da doação'), {
      target: { value: '5' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', peso_max: '5' })
    })

    expect(await screen.findByText('Doacao Legumes')).toBeInTheDocument()
  })

  it('recarrega as doações ao filtrar por data de validade mínima', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_LEGUMES])

    fireEvent.change(screen.getByLabelText('Filtro por data de validade mínima'), {
      target: { value: '2027-01-01' },
    })

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', validade_min: '2027-01-01' })
    })

    expect(await screen.findByText('Doacao Legumes')).toBeInTheDocument()
  })

  it('exibe checkboxes de cidades retornadas pelo backend', async () => {
    render(<Home />)

    expect(await screen.findByLabelText('Filtrar por Campinas')).toBeInTheDocument()
    expect(screen.getByLabelText('Filtrar por São Paulo')).toBeInTheDocument()
    expect(api.getCidades).toHaveBeenCalledTimes(1)
  })

  it('filtra por uma cidade ao marcar seu checkbox', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')
    await screen.findByLabelText('Filtrar por Campinas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS])

    fireEvent.click(screen.getByLabelText('Filtrar por Campinas'))

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', cidades: 'Campinas' })
    })
  })

  it('filtra por múltiplas cidades ao marcar mais de um checkbox', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')
    await screen.findByLabelText('Filtrar por Campinas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS])
    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS, DOACAO_LEGUMES])

    fireEvent.click(screen.getByLabelText('Filtrar por Campinas'))
    fireEvent.click(screen.getByLabelText('Filtrar por São Paulo'))

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', cidades: 'Campinas,São Paulo' })
    })
  })

  it('botão "Todas as cidades" marca todos os checkboxes e envia todas as cidades', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')
    await screen.findByLabelText('Filtrar por Campinas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS, DOACAO_LEGUMES])

    fireEvent.click(screen.getByLabelText('Selecionar todas as cidades'))

    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', cidades: 'Campinas,São Paulo' })
    })

    expect(screen.getByLabelText('Filtrar por Campinas')).toBeChecked()
    expect(screen.getByLabelText('Filtrar por São Paulo')).toBeChecked()
  })

  it('botão "Limpar seleção" desmarca todos os checkboxes e remove o filtro de cidades', async () => {
    render(<Home />)

    await screen.findByText('Doacao Frutas')
    await screen.findByLabelText('Filtrar por Campinas')

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS, DOACAO_LEGUMES])
    fireEvent.click(screen.getByLabelText('Selecionar todas as cidades'))
    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel', cidades: 'Campinas,São Paulo' })
    })

    api.getDoacoes.mockResolvedValueOnce([DOACAO_FRUTAS, DOACAO_LEGUMES])
    fireEvent.click(screen.getByLabelText('Limpar seleção de cidades'))
    await waitFor(() => {
      expect(api.getDoacoes).toHaveBeenLastCalledWith({ status: 'disponivel' })
    })

    expect(screen.getByLabelText('Filtrar por Campinas')).not.toBeChecked()
    expect(screen.getByLabelText('Filtrar por São Paulo')).not.toBeChecked()
  })
})