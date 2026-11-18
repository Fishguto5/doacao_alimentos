import { useUser } from '../context/UserContext'
import { navigate } from '../router'
import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../api'
import { useRouter } from '../router'

export default function Header() {
  const { user, logout } = useUser()
  const userId = user?.id
  const hash = useRouter()
  const pathname = hash.replace('#', '').split('?')[0]
  const isMobileDetailRoute = pathname.startsWith('/donation/') || pathname.startsWith('/reservation-success/') || pathname === '/profile' || pathname === '/chat'
  const [notifCount, setNotifCount] = useState(0)
  const [menuOpen, setMenuOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [notificationNow, setNotificationNow] = useState(null)
  const notificationRef = useRef(null)

  const refreshNotifications = useCallback(() => {
    if (!userId) return
    api.getNotificacoes()
      .then(list => {
        setNotificationNow(Date.now())
        const own = list
          .filter(n => Number(n.usuario) === Number(userId))
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        setNotifications(own)
        setNotifCount(own.filter(n => n.status === 'pendente').length)
      })
      .catch(() => {})
  }, [userId])

  useEffect(() => {
    if (!userId) {
      return undefined
    }
    refreshNotifications()
    const timer = window.setInterval(refreshNotifications, 15000)
    window.addEventListener('focus', refreshNotifications)
    window.addEventListener('notifications-updated', refreshNotifications)
    return () => {
      window.clearInterval(timer)
      window.removeEventListener('focus', refreshNotifications)
      window.removeEventListener('notifications-updated', refreshNotifications)
    }
  }, [userId, refreshNotifications])

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setNotificationsOpen(false)
      }
    }
    document.addEventListener('mousedown', closeOnOutsideClick)
    return () => document.removeEventListener('mousedown', closeOnOutsideClick)
  }, [])

  useEffect(() => {
    const close = () => setMobileMenuOpen(false)
    const closeOnEscape = event => { if (event.key === 'Escape') close() }
    window.addEventListener('hashchange', close)
    window.addEventListener('keydown', closeOnEscape)
    return () => {
      window.removeEventListener('hashchange', close)
      window.removeEventListener('keydown', closeOnEscape)
    }
  }, [])

  async function markAllNotificationsRead() {
    const unread = notifications.filter(n => n.status === 'pendente')
    const results = await Promise.allSettled(
      unread.map(n => api.updateNotificacao({ id: n.id, status: 'lida' })),
    )
    const readIds = new Set(unread.filter((_, index) => results[index].status === 'fulfilled').map(n => n.id))
    setNotifications(current => current.map(n => readIds.has(n.id) ? { ...n, status: 'lida' } : n))
    setNotifCount(count => Math.max(0, count - readIds.size))
    window.dispatchEvent(new Event('notifications-updated'))
  }

  function notificationTime(value) {
    if (!value || notificationNow === null) return ''
    const hours = Math.max(0, Math.floor((notificationNow - new Date(value).getTime()) / 3600000))
    if (hours < 1) return 'agora'
    if (hours < 24) return `há ${hours} h`
    const days = Math.floor(hours / 24)
    return days === 1 ? 'ontem' : `há ${days} dias`
  }

  function go(path) {
    navigate(path)
    setMenuOpen(false)
    setMobileMenuOpen(false)
    setNotificationsOpen(false)
  }

  return (
    <header className={`header${isMobileDetailRoute ? ' header-detail-route' : ''}${mobileMenuOpen ? ' header-menu-open' : ''}`}>
      {!isMobileDetailRoute && (
        <div className="mobile-home-toolbar">
          <button type="button" className="mobile-menu-button" aria-label="Abrir menu" aria-expanded={mobileMenuOpen} aria-controls="mobile-side-menu" onClick={() => setMobileMenuOpen(open => !open)}>
            <span /><span /><span />
          </button>
          <label className="mobile-search-field">
            <input type="search" placeholder="Buscar doações..." aria-label="Buscar doações" onChange={event => window.dispatchEvent(new CustomEvent('donation-search', { detail: event.target.value }))} />
            <img src="/figma/mobile-search.png" alt="" />
          </label>
        </div>
      )}
      {mobileMenuOpen && !isMobileDetailRoute && (
        <div className="mobile-drawer-backdrop" onClick={() => setMobileMenuOpen(false)}>
          <aside id="mobile-side-menu" className="mobile-drawer" aria-label="Menu lateral" onClick={event => event.stopPropagation()}>
            <div className="mobile-drawer-heading">
              <strong><img src="/figma/brand-leaf.svg" alt="" /> DoacaoAlimentos</strong>
              <button type="button" aria-label="Fechar menu" onClick={() => setMobileMenuOpen(false)}>×</button>
            </div>
            <p className="mobile-drawer-eyebrow">Sua comunidade</p>
            {user ? (
              <>
                <button type="button" onClick={() => go('#/profile?tab=perfil')}>Meu perfil</button>
                <button type="button" onClick={() => go('#/profile?tab=doacoes')}>Minhas doações</button>
                <button type="button" onClick={() => go('#/profile?tab=solicitacoes')}>Reservas</button>
                <button type="button" onClick={() => go('#/chat')}>Mensagens</button>
              </>
            ) : (
              <button type="button" onClick={() => go('#/register?tab=login')}>Entrar / Cadastrar</button>
            )}
            {pathname === '/' && (
              <button type="button" onClick={() => {
                setMobileMenuOpen(false)
                window.dispatchEvent(new Event('toggle-donation-filters'))
              }}>Filtros de doações</button>
            )}
            <div className="mobile-drawer-footer"><span aria-hidden="true">✦</span> Compartilhe alimentos, transforme vidas.</div>
          </aside>
        </div>
      )}
      <div className="header-inner">
        <button className="logo" onClick={() => go('#/')}>
          <img className="logo-icon" src="/figma/brand-leaf.svg" alt="" />
          <span className="logo-text">DoacaoAlimentos</span>
        </button>

        <nav className="nav-links" aria-label="Navegação desktop">
          <button className={`nav-link${pathname === '/' ? ' active' : ''}`} onClick={() => go('#/')}>Doações</button>
          {user && (
            <>
              <button className={`nav-link${pathname === '/chat' ? ' active' : ''}`} onClick={() => go('#/chat')}>Mensagens</button>
              <button className="nav-link new-donation-link" onClick={() => go('#/create')}>
                <span className="nav-donation-plus" aria-hidden="true">+</span> Nova Doação
              </button>
            </>
          )}
        </nav>

        <div className="header-actions">
          {user ? (
            <div className="user-menu">
              <div className="notification-menu" ref={notificationRef}>
                <button
                  className="notif-btn"
                  onClick={() => { refreshNotifications(); setNotificationsOpen(open => !open); setMenuOpen(false) }}
                  title="Notificações"
                  aria-label={`Notificações${notifCount ? `, ${notifCount} não lidas` : ''}`}
                  aria-expanded={notificationsOpen}
                >
                  <img className="bell-icon" src="/figma/bell.svg" alt="" />
                  {notifCount > 0 && <span className="notif-count">{notifCount > 9 ? '9+' : notifCount}</span>}
                </button>
                {notificationsOpen && (
                  <section className="notification-popover" aria-label="Últimas notificações">
                    <header className="notification-popover-header">
                      <div>
                        <h2>Notificações</h2>
                        <p>{notifCount ? `Você tem ${notifCount} novas atualizações` : 'Você está em dia'}</p>
                      </div>
                      {notifCount > 0 && (
                        <button className="mark-notifications-read" onClick={markAllNotificationsRead}>
                          Marcar como lidas
                        </button>
                      )}
                    </header>
                    <div className="notification-popover-list">
                      {notifications.length ? notifications.slice(0, 3).map(notification => (
                        <button
                          className={`notification-popover-item${notification.status === 'pendente' ? ' unread' : ''}`}
                          key={notification.id}
                          onClick={() => go('#/profile?tab=notificacoes')}
                        >
                          <span className="notification-type-icon" aria-hidden="true">
                            <img
                              src={notification.mensagem?.toLowerCase().includes('aceita')
                                ? '/figma/check.svg'
                                : '/figma/message.svg'}
                              alt=""
                            />
                          </span>
                          <span className="notification-copy">
                            <span>{notification.mensagem}</span>
                            <small>{notificationTime(notification.created_at)}</small>
                          </span>
                          {notification.status === 'pendente' && <i className="notification-unread-dot" />}
                        </button>
                      )) : (
                        <p className="notification-empty">Nenhuma notificação por enquanto.</p>
                      )}
                    </div>
                    <button className="all-notifications-link" onClick={() => go('#/profile?tab=notificacoes')}>
                      Ver todas as notificações
                    </button>
                  </section>
                )}
              </div>
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
                  <button onClick={() => go('#/chat')}>Mensagens</button>
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
