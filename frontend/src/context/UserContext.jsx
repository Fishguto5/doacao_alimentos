import { createContext, useContext, useState } from 'react'

const UserContext = createContext(null)

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('doacaoUser')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })

  function login(userData) {
    localStorage.setItem('doacaoUser', JSON.stringify(userData))
    setUser(userData)
  }

  function logout() {
    localStorage.removeItem('doacaoUser')
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
