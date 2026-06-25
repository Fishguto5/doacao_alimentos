import { UserProvider } from './context/UserContext'
import { useRouter } from './router'
import Header from './components/Header'
import Home from './pages/Home'
import DonationDetail from './pages/DonationDetail'
import CreateDonation from './pages/CreateDonation'
import UserProfile from './pages/UserProfile'
import PublicUserProfile from './pages/PublicUserProfile'
import Register from './pages/Register'

function Router() {
  const hash = useRouter()

  const path = hash.replace('#', '').split('?')[0]

  if (path === '/register') return <Register />
  if (path === '/create') return <CreateDonation />
  if (path === '/profile') return <UserProfile />
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
          <p>DoacaoAlimentos — Compartilhe alimentos, transforme vidas. 🌱</p>
        </footer>
      </div>
    </UserProvider>
  )
}
