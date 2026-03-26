import { useState, useEffect } from 'react'

export function useRouter() {
  const [hash, setHash] = useState(window.location.hash || '#/')

  useEffect(() => {
    const handler = () => setHash(window.location.hash || '#/')
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  return hash
}

export function navigate(path) {
  window.location.hash = path
}
