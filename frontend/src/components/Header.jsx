import { useUser } from '../context/UserContext'
import { navigate } from '../router'
import { useState, useEffect } from 'react'
import { api } from '../api'

export default function Header() {
  const { user, logout } = useUser()
  const [notifCount, setNotifCount] = useState(0)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    if (!user) return
    api.getNotificacoes()
      .then(list => {
        const unread = list.filter(n => n.usuario === user.id && n.status === 'pendente')
        setNotifCount(unread.length)
      })
      .catch(() => {})
  }, [user])

  function go(path) {
    navigate(path)
    setMenuOpen(false)
  }

  return (
    <header className="header">
      <div className="header-inner">
        <button className="logo" onClick={() => go('#/')}>
          <span className="logo-icon">🌱</span>
          <span className="logo-text">DoacaoAlimentos</span>
        </button>

        <nav className="nav-links">
          <button className="nav-link" onClick={() => go('#/')}>Doações</button>
          {user && (
            <button className="nav-link" onClick={() => go('#/create')}>
              + Nova Doação
            </button>
          )}
        </nav>

        <div className="header-actions">
          {user ? (
            <div className="user-menu">
              {notifCount > 0 && (
                <button className="notif-btn" onClick={() => go('#/profile?tab=notificacoes')} title="Notificações">
                  🔔 <span className="badge">{notifCount}</span>
                </button>
              )}
              <button className="user-btn" onClick={() => setMenuOpen(o => !o)}>
                <span className="user-avatar">{user.nome.charAt(0).toUpperCase()}</span>
                <span className="user-name">{user.nome.split(' ')[0]}</span>
                <span>▾</span>
              </button>
              {menuOpen && (
                <div className="dropdown">
                  <button onClick={() => go('#/profile')}>Meu Perfil</button>
                  <button onClick={() => go('#/profile?tab=doacoes')}>Minhas Doações</button>
                  <button onClick={() => go('#/profile?tab=solicitacoes')}>Minhas Solicitações</button>
                  <button onClick={() => go('#/profile?tab=notificacoes')}>Notificações {notifCount > 0 && `(${notifCount})`}</button>
                  <hr />
                  <button onClick={logout} className="logout-btn">Sair</button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <button className="btn-outline" onClick={() => go('#/register?tab=login')}>Entrar</button>
              <button className="btn-primary" onClick={() => go('#/register')}>Cadastrar</button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
