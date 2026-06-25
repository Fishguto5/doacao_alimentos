import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import Register from './Register'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

vi.mock('../api', () => ({
  api: {
    register: vi.fn(),
    login: vi.fn(),
  },
}))

vi.mock('../context/UserContext', () => ({
  useUser: vi.fn(),
}))

vi.mock('../router', () => ({
  navigate: vi.fn(),
}))

describe('Register', () => {
  const login = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    window.location.hash = '#/register'
    useUser.mockReturnValue({ login })
  })

  afterEach(() => {
    cleanup()
  })

  it('registers a new user with password through auth endpoint', async () => {
    api.register.mockResolvedValue({
      id: 1,
      nome: 'Maria Silva',
      email: 'maria@example.com',
      cidade: 'Campinas',
      estado: 'SP',
      bairro: 'Centro',
      cep: '13000000',
      logradouro: 'Rua A',
      numero: '10',
      complemento: '',
      foto_perfil_url: '',
    })

    render(<Register />)

    fireEvent.change(screen.getByPlaceholderText('Seu nome'), {
      target: { value: 'Maria Silva' },
    })
    fireEvent.change(screen.getByPlaceholderText('seu@email.com'), {
      target: { value: 'maria@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Mínimo 6 caracteres'), {
      target: { value: 'senha12345' },
    })
    fireEvent.change(screen.getByPlaceholderText('Sua cidade'), {
      target: { value: 'Campinas' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Selecione a UF' }))
    fireEvent.click(screen.getByRole('button', { name: 'SP' }))
    fireEvent.change(screen.getByPlaceholderText('Rua, avenida, etc.'), {
      target: { value: 'Rua A' },
    })
    fireEvent.change(screen.getByPlaceholderText('123'), {
      target: { value: '10' },
    })
    fireEvent.change(screen.getByPlaceholderText('Seu bairro'), {
      target: { value: 'Centro' },
    })
    fireEvent.change(screen.getByPlaceholderText('00000000'), {
      target: { value: '13000000' },
    })

    fireEvent.submit(screen.getByRole('button', { name: 'Criar conta' }).closest('form'))

    await waitFor(() => {
      expect(api.register).toHaveBeenCalledWith(
        expect.objectContaining({
          email: 'maria@example.com',
          password: 'senha12345',
          estado: 'SP',
        })
      )
    })
    expect(login).toHaveBeenCalledWith(expect.objectContaining({ email: 'maria@example.com' }))
    expect(navigate).toHaveBeenCalledWith('#/')
  })

  it('logs in with email and password through auth endpoint', async () => {
    window.location.hash = '#/register?tab=login'
    api.login.mockResolvedValue({
      id: 2,
      nome: 'Joao Silva',
      email: 'joao@example.com',
      cidade: 'Campinas',
      estado: 'SP',
      bairro: 'Centro',
      cep: '13000000',
      logradouro: 'Rua B',
      numero: '20',
      complemento: '',
      foto_perfil_url: '',
    })

    render(<Register />)

    fireEvent.change(screen.getByPlaceholderText('seu@email.com'), {
      target: { value: 'joao@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Sua senha'), {
      target: { value: 'senha12345' },
    })
    fireEvent.submit(screen.getAllByRole('button', { name: 'Entrar' }).at(-1).closest('form'))

    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith({
        email: 'joao@example.com',
        password: 'senha12345',
      })
    })
    expect(login).toHaveBeenCalledWith(expect.objectContaining({ email: 'joao@example.com' }))
    expect(navigate).toHaveBeenCalledWith('#/')
  })
})
