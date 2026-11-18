import { createContext, useContext, useState } from 'react'

const UserContext = createContext(null)
const STORAGE_KEY = 'doacaoUserAuth'
const LEGACY_STORAGE_KEY = 'doacaoUser'

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      localStorage.removeItem(LEGACY_STORAGE_KEY)
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })

  function login(userData) {
    const nextUser = {
      ...userData,
      auth_token: userData.auth_token || (user?.id === userData.id ? user.auth_token : undefined),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser))
    setUser(nextUser)
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(LEGACY_STORAGE_KEY)
    setUser(null)
    window.location.hash = '#/'
  }

  return (
    <UserContext.Provider value={{ user, login, logout }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  return useContext(UserContext)
}
