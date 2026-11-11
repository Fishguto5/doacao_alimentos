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

  const contentType = res.headers.get('content-type') || ''
  const responseText = await res.text()
  let json = null

  if (responseText && contentType.includes('application/json')) {
    try {
      json = JSON.parse(responseText)
    } catch {
      json = null
    }
  }

  if (!res.ok) {
    const msg = json?.msg || responseText || `Erro HTTP ${res.status}`
    throw new Error(msg)
  }

  if (!json) {
    throw new Error(`Resposta inválida do servidor (HTTP ${res.status})`)
  }

  return json.data
}

export const api = {
  // Autenticação
  register: (data) => request('POST', '/auth/register/', data),
  login: (data) => request('POST', '/auth/login/', data),

  // Usuários
  getUsuarios: () => request('GET', '/usuario/'),
  getUsuario: (id) => request('GET', `/usuario/${id}/`),
  createUsuario: (data) => request('POST', '/usuario/', data),
  updateUsuario: (data) => request('PATCH', '/usuario/', data),

  // Doações
  getDoacoes: (params) => request('GET', '/doacao/', undefined, params),
  getDoacao: (id) => request('GET', `/doacao/${id}/`),
  getCidades: () => request('GET', '/doacao/cidades/'),
  createDoacao: (data) => request('POST', '/doacao/', data),
  updateDoacao: (data) => request('PATCH', '/doacao/', data),
  deleteDoacao: (id) => request('DELETE', `/doacao/${id}/`),

  // Categorias
  getCategorias: () => request('GET', '/categoria/'),
  createCategoria: (data) => request('POST', '/categoria/', data),

  // Alimentos
  getAlimentos: () => request('GET', '/alimento/'),
  createAlimento: (data) => request('POST', '/alimento/', data),
  deleteAlimento: (id) => request('DELETE', `/alimento/${id}/`),

  // Solicitações de doação
  getSolicitacoes: () => request('GET', '/solicitacao-doacao/'),
  createSolicitacao: (data) => request('POST', '/solicitacao-doacao/', data),
  updateSolicitacao: (data) => request('PATCH', '/solicitacao-doacao/', data),
  aceitarSolicitacao: (id) => request('POST', `/solicitacao-doacao/${id}/aceitar/`),

  // Notificações
  getNotificacoes: () => request('GET', '/notificacao/'),
  updateNotificacao: (data) => request('PATCH', '/notificacao/', data),

  // Avaliações
  getAvaliacoes: (params) => request('GET', '/avaliacao/', undefined, params),
  createAvaliacao: (data) => request('POST', '/avaliacao/', data),
}
