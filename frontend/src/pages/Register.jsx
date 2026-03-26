import { useState } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

export default function Register() {
  const { login } = useUser()
  const hash = window.location.hash
  const initialTab = hash.includes('tab=login') ? 'login' : 'register'
  const [tab, setTab] = useState(initialTab)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    nome: '', email: '', password: '', cep: '',
    cidade: '', estado: '', bairro: '', foto_perfil_url: '',
  })

  const [loginEmail, setLoginEmail] = useState('')

  function updateForm(field, value) {
    setForm(f => ({ ...f, [field]: value }))
  }

  async function handleRegister(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = { ...form }
      if (!payload.foto_perfil_url) delete payload.foto_perfil_url
      const created = await api.createUsuario(payload)
      login({ id: created.id, nome: created.nome, email: created.email, cidade: created.cidade, estado: created.estado })
      navigate('#/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleLogin(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const usuarios = await api.getUsuarios()
      const found = usuarios.find(u => u.email.toLowerCase() === loginEmail.toLowerCase())
      if (!found) {
        setError('Nenhum usuário encontrado com esse e-mail.')
        return
      }
      login({ id: found.id, nome: found.nome, email: found.email, cidade: found.cidade, estado: found.estado })
      navigate('#/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page page-centered">
      <div className="auth-card">
        <div className="auth-tabs">
          <button
            className={`auth-tab${tab === 'register' ? ' active' : ''}`}
            onClick={() => { setTab('register'); setError('') }}
          >
            Cadastrar
          </button>
          <button
            className={`auth-tab${tab === 'login' ? ' active' : ''}`}
            onClick={() => { setTab('login'); setError('') }}
          >
            Entrar
          </button>
        </div>

        {error && <div className="error-msg">{error}</div>}

        {tab === 'register' ? (
          <form className="auth-form" onSubmit={handleRegister}>
            <h2>Crie sua conta</h2>

            <div className="form-group">
              <label>Nome completo *</label>
              <input className="input" required value={form.nome} onChange={e => updateForm('nome', e.target.value)} placeholder="Seu nome" />
            </div>
            <div className="form-group">
              <label>E-mail *</label>
              <input className="input" type="email" required value={form.email} onChange={e => updateForm('email', e.target.value)} placeholder="seu@email.com" />
            </div>
            <div className="form-group">
              <label>Senha *</label>
              <input className="input" type="password" required minLength={6} value={form.password} onChange={e => updateForm('password', e.target.value)} placeholder="Mínimo 6 caracteres" />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Cidade *</label>
                <input className="input" required value={form.cidade} onChange={e => updateForm('cidade', e.target.value)} placeholder="Sua cidade" />
              </div>
              <div className="form-group form-group-sm">
                <label>Estado *</label>
                <input className="input" required maxLength={2} value={form.estado} onChange={e => updateForm('estado', e.target.value.toUpperCase())} placeholder="SP" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Bairro *</label>
                <input className="input" required value={form.bairro} onChange={e => updateForm('bairro', e.target.value)} placeholder="Seu bairro" />
              </div>
              <div className="form-group">
                <label>CEP *</label>
                <input className="input" required value={form.cep} onChange={e => updateForm('cep', e.target.value)} placeholder="00000000" maxLength={8} />
              </div>
            </div>
            <div className="form-group">
              <label>URL da foto de perfil</label>
              <input className="input" type="url" value={form.foto_perfil_url} onChange={e => updateForm('foto_perfil_url', e.target.value)} placeholder="https://..." />
            </div>

            <button className="btn-primary btn-full" type="submit" disabled={loading}>
              {loading ? 'Criando conta...' : 'Criar conta'}
            </button>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleLogin}>
            <h2>Bem-vindo de volta</h2>
            <div className="form-group">
              <label>E-mail *</label>
              <input
                className="input"
                type="email"
                required
                value={loginEmail}
                onChange={e => setLoginEmail(e.target.value)}
                placeholder="seu@email.com"
              />
            </div>
            <button className="btn-primary btn-full" type="submit" disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
            <p className="auth-hint">
              Não possui conta?{' '}
              <button type="button" className="link-btn" onClick={() => setTab('register')}>Cadastre-se</button>
            </p>
          </form>
        )}
      </div>
    </main>
  )
}
