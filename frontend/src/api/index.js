const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://doacaoalimentos-production.up.railway.app').replace(/\/$/, '')

const request = async (method, path, body, params) => {
  const opts = { method, headers: {} }
  if (body !== undefined) {
    if (body instanceof FormData) {
      opts.body = body
    } else {
      opts.headers['Content-Type'] = 'application/json'
      opts.body = JSON.stringify(body)
    }
  }

  const searchParams = params
    ? new URLSearchParams(
        Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
      ).toString()
    : ''

  // Garante que o path seja apenas a rota relativa limpa (ex: /auth/register/)
  const cleanPath = path.replace(/^https?:\/\/[^\/]+/, '').replace(/^\[+/, '').replace(/\]+/, '')
  const formattedPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`

  // Monta a URL final unindo a base do backend com a rota relativa
  const url = searchParams 
    ? `${API_BASE_URL}${formattedPath}?${searchParams}` 
    : `${API_BASE_URL}${formattedPath}`

  const res = await fetch(url, opts)
  if (res.status === 204) return null

  const json = await res.json()
  if (!res.ok) {
    const msg = json.msg || JSON.stringify(json)
    throw new Error(msg)
  }
  return json.data
}