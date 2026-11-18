import { navigate } from '../router'

const items = [
  { id: 'home', label: 'Tela inicial', path: '#/', icon: '/figma/mobile-home.png', className: 'mobile-nav-home' },
  { id: 'reservations', label: 'Reservas', path: '#/profile?tab=solicitacoes', icon: '/figma/mobile-reservations.png', className: '' },
  { id: 'create', label: 'Nova doação', path: '#/create', icon: '/figma/mobile-add.png', className: 'mobile-nav-add' },
  { id: 'messages', label: 'Mensagens', path: '#/chat', icon: '/figma/mobile-messages.png', className: '' },
  { id: 'notifications', label: 'Notificações', path: '#/profile?tab=notificacoes', icon: '/figma/mobile-notifications.png', className: '' },
]

export default function MobileNav() {
  return (
    <nav className="mobile-bottom-nav" aria-label="Navegação principal">
      {items.map(item => (
        <button type="button" key={item.id} className={item.className} onClick={() => navigate(item.path)}>
          <img src={item.icon} alt="" />
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  )
}
