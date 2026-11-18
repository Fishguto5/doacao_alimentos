import { UserProvider } from './context/UserContext'
import { useRouter } from './router'
import Header from './components/Header'
import Home from './pages/Home'
import DonationDetail from './pages/DonationDetail'
import CreateDonation from './pages/CreateDonation'
import UserProfile from './pages/UserProfile'
import PublicUserProfile from './pages/PublicUserProfile'
import Register from './pages/Register'
import ReservationSuccess from './pages/ReservationSuccess'
import MobileNav from './components/MobileNav'
import Chat from './pages/Chat'

function Router() {
  const hash = useRouter()

  const path = hash.replace('#', '').split('?')[0]

  if (path === '/register') return <Register />
  if (path === '/create') return <CreateDonation />
  if (path.startsWith('/reservation-success/')) {
    const id = path.replace('/reservation-success/', '')
    return <ReservationSuccess id={id} />
  }
  if (path === '/profile') return <UserProfile />
  if (path === '/chat') return <Chat />
  if (path.startsWith('/users/')) {
    const id = path.replace('/users/', '')
    return <PublicUserProfile id={id} />
  }
  if (path.startsWith('/donation/')) {
    const id = path.replace('/donation/', '')
    return <DonationDetail id={id} />
  }
  return <Home />
}

export default function App() {
  return (
    <UserProvider>
      <div className="app">
        <Header />
        <Router />
        <footer className="footer">
          <div className="footer-inner">
            <a className="footer-brand" href="#/" aria-label="DoacaoAlimentos, página inicial">
              <img src="/figma/brand-leaf-alt.svg" alt="" /> DoacaoAlimentos
            </a>
            <p>Compartilhe alimentos, transforme vidas.</p>
          </div>
        </footer>
        <MobileNav />
      </div>
    </UserProvider>
  )
}
