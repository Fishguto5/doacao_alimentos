import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import CreateDonation from './CreateDonation'
import { useUser } from '../context/UserContext'
import { api } from '../api'

// Mockando dependências
vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}))

vi.mock('../api', () => ({
  api: {
    getCategorias: vi.fn(),
    createDoacao: vi.fn(),
    createAlimento: vi.fn(),
    deleteDoacao: vi.fn(),
  },
}))

vi.mock('../router', () => ({
  navigate: vi.fn(),
}))

describe('CreateDonation Component Validations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useUser.mockReturnValue({
      user: {
        id: 1,
        nome: 'Doador Teste',
        cidade: 'Campinas',
        estado: 'SP'
      }
    })
    api.getCategorias.mockResolvedValue([
      { id: 1, nome: 'Categoria 1' }
    ])
  })

  afterEach(() => {
    cleanup()
  })

  it('renders correctly', async () => {
    render(<CreateDonation />)
    expect(screen.getByText('Anunciar doação')).toBeInTheDocument()
    await waitFor(() => {
      expect(api.getCategorias).toHaveBeenCalled()
    })
  })

  it('shows error if submitting without required fields', async () => {
    render(<CreateDonation />)
    
    // Tentando enviar sem preencher os campos obrigatórios
    const submitBtn = screen.getByRole('button', { name: 'Publicar doação' })
    fireEvent.submit(submitBtn.closest('form'))
    
    // A validação começa pelo título
    await waitFor(() => {
      expect(screen.getByText('O título da doação é obrigatório.')).toBeInTheDocument()
    })
  })

  it('shows error if no valid items are added', async () => {
    render(<CreateDonation />)
    
    // Preenchendo campos obrigatórios
    const inputs = screen.getAllByRole('textbox')
    // Encontrando input pelo placeholder
    const tituloInput = screen.getByPlaceholderText('Ex: Cesta básica, Frutas da época...')
    fireEvent.change(tituloInput, { target: { value: 'Doação de Teste' } })
    
    // Colocando texto aleatório em todos os campos obrigatórios para passar na validação básica
    inputs.forEach(input => {
        if (!input.readOnly && !input.value) {
            fireEvent.change(input, { target: { value: 'Teste' } })
        }
    })
    
    const cepInput = document.querySelector('input[maxLength="8"]')
    if (cepInput) fireEvent.change(cepInput, { target: { value: '13000000' } })

    const submitBtn = screen.getByRole('button', { name: 'Publicar doação' })
    fireEvent.submit(submitBtn.closest('form'))
    
    await waitFor(() => {
      expect(screen.getByText('Adicione pelo menos um item (alimento) válido com nome, categoria e quantidade maior que zero.')).toBeInTheDocument()
    })
  })

  it('validates expired and non-existent dates', async () => {
    render(<CreateDonation />)
    const validadeInput = screen.getByPlaceholderText('dd/mm/aaaa')
    
    // Data inexistente
    fireEvent.change(validadeInput, { target: { value: '31/02/2030' } })
    expect(validadeInput.validationMessage).toBe('Esta data não existe no calendário.')
    
    // Data expirada
    fireEvent.change(validadeInput, { target: { value: '01/01/2000' } })
    expect(validadeInput.validationMessage).toBe('Esta data já expirou.')
    
    // Data válida
    fireEvent.change(validadeInput, { target: { value: '01/01/2030' } })
    expect(validadeInput.validationMessage).toBe('')
  })

  it('formats CEP to allow only digits', async () => {
    render(<CreateDonation />)
    
    // Usando query do container já que os labels não estão diretamente vinculados via htmlFor
    const cepInput = document.querySelector('input[maxLength="8"]')
    expect(cepInput).not.toBeNull()
    
    fireEvent.change(cepInput, { target: { value: '13a00b00-c' } })
    expect(cepInput.value).toBe('130000')
  })

  it('calculates estimated weight from donation items', async () => {
    render(<CreateDonation />)

    expect(screen.getByDisplayValue('0.00')).toBeInTheDocument()

    const quantidadeInput = document.querySelector('input[type="number"]')
    const unidadeSelect = screen.getByDisplayValue('kg')

    fireEvent.change(quantidadeInput, { target: { value: '500' } })
    fireEvent.change(unidadeSelect, { target: { value: 'g' } })

    expect(screen.getByDisplayValue('0.50')).toBeInTheDocument()
  })

  it('validates quantity input based on unit rules', async () => {
    render(<CreateDonation />)
    const quantidadeInput = document.querySelector('input[type="number"]')
    const unidadeSelect = screen.getByDisplayValue('kg')

    // Test kg - invalid (exceeds 100)
    fireEvent.change(quantidadeInput, { target: { value: '101' } })
    expect(quantidadeInput.validationMessage).toBe("A quantidade máxima para 'kg' é 100.")

    // Test kg - valid (100)
    fireEvent.change(quantidadeInput, { target: { value: '100' } })
    expect(quantidadeInput.validationMessage).toBe("")

    // Test g - invalid decimal (250.50)
    fireEvent.change(unidadeSelect, { target: { value: 'g' } })
    fireEvent.change(quantidadeInput, { target: { value: '250.5' } })
    expect(quantidadeInput.validationMessage).toBe("A quantidade para 'g' deve ser um número inteiro.")

    // Test g - invalid min (49)
    fireEvent.change(quantidadeInput, { target: { value: '49' } })
    expect(quantidadeInput.validationMessage).toBe("A quantidade mínima para 'g' é 50.")

    // Test g - invalid max (1000)
    fireEvent.change(quantidadeInput, { target: { value: '1000' } })
    expect(quantidadeInput.validationMessage).toBe("A quantidade máxima para 'g' é 999. Para 1000 ou mais, use a unidade superior correspondente.")

    // Test unidade - invalid decimal (1.5)
    fireEvent.change(unidadeSelect, { target: { value: 'unidade' } })
    fireEvent.change(quantidadeInput, { target: { value: '1.5' } })
    expect(quantidadeInput.validationMessage).toBe("A quantidade para a unidade 'unidade' deve ser um número inteiro.")
  })
})
