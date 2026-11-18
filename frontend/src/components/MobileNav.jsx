import { useEffect, useState } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

const items = [
  { id: 'home', label: 'Tela inicial', path: '#/', icon: '/figma/mobile-home.png', className: 'mobile-nav-home' },
  { id: 'reservations', label: 'Reservas', path: '#/profile?tab=solicitacoes', icon: '/figma/mobile-reservations.png', className: '' },
  { id: 'create', label: 'Nova doação', path: '#/create', icon: '/figma/mobile-add.png', className: 'mobile-nav-add' },
  { id: 'messages', label: 'Mensagens', path: '#/chat', icon: '/figma/mobile-messages.png', className: '' },
  { id: 'notifications', label: 'Notificações', path: '#/profile?tab=notificacoes', icon: '/figma/mobile-notifications.png', className: '' },
]

export default function MobileNav() {
  const { user } = useUser()
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (!user?.id) return undefined
    let active = true
    const refresh = () => api.getNotificacoes()
      .then(list => {
        if (active) setUnread(list.filter(n => Number(n.usuario) === Number(user.id) && n.status === 'pendente').length)
      })
      .catch(() => {})
    refresh()
    const timer = window.setInterval(refresh, 15000)
    window.addEventListener('focus', refresh)
    window.addEventListener('notifications-updated', refresh)
    return () => {
      active = false
      window.clearInterval(timer)
      window.removeEventListener('focus', refresh)
      window.removeEventListener('notifications-updated', refresh)
    }
  }, [user?.id])

  return (
    <nav className="mobile-bottom-nav" aria-label="Navegação principal">
      {items.map(item => (
        <button type="button" key={item.id} className={item.className} onClick={() => navigate(item.path)}>
          <img src={item.icon} alt="" />
          {item.id === 'notifications' && unread > 0 && <span className="mobile-notification-count" aria-label={`${unread} notificações não lidas`}>{unread > 9 ? '9+' : unread}</span>}
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  )
}
