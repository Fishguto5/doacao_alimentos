// Obtém a URL do Backend da variável de ambiente com fallback para a URL de produção do Railway
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
  
  // Concatena a URL base do backend ao caminho (path) da requisição
  const fullPath = path.startsWith('/') ? path : `/${path}`
  const url = searchParams ? `${API_BASE_URL}${fullPath}?${searchParams}` : `${API_BASE_URL}${fullPath}`

  const res = await fetch(url, opts)
  if (res.status === 204) return null
  const json = await res.json()
  if (!res.ok) {
    const msg = json.msg || JSON.stringify(json)
    throw new Error(msg)
  }
  return json.data
}

export const api = {
  // Auth
  register: (data) => request('POST', '/auth/register/', data),
  login: (data) => request('POST', '/auth/login/', data),

  // Usuario
  getUsuarios: () => request('GET', '/usuario/'),
  getUsuario: (id) => request('GET', `/usuario/${id}/`),
  createUsuario: (data) => request('POST', '/usuario/', data),
  updateUsuario: (data) => request('PATCH', '/usuario/', data),

  // Doacao
  getDoacoes: (params) => request('GET', '/doacao/', undefined, params),
  getDoacao: (id) => request('GET', `/doacao/${id}/`),
  getCidades: () => request('GET', '/doacao/cidades/'),
  createDoacao: (data) => request('POST', '/doacao/', data),
  updateDoacao: (data) => request('PATCH', '/doacao/', data),
  deleteDoacao: (id) => request('DELETE', `/doacao/${id}/`),

  // Categoria
  getCategorias: () => request('GET', '/categoria/'),
  createCategoria: (data) => request('POST', '/categoria/', data),

  // Alimento
  getAlimentos: () => request('GET', '/alimento/'),
  createAlimento: (data) => request('POST', '/alimento/', data),
  deleteAlimento: (id) => request('DELETE', `/alimento/${id}/`),

  // SolicitacaoDoacao
  getSolicitacoes: () => request('GET', '/solicitacao-doacao/'),
  createSolicitacao: (data) => request('POST', '/solicitacao-doacao/', data),
  updateSolicitacao: (data) => request('PATCH', '/solicitacao-doacao/', data),
  aceitarSolicitacao: (id) => request('POST', `/solicitacao-doacao/${id}/aceitar/`),

  // Notificacao
  getNotificacoes: () => request('GET', '/notificacao/'),
  updateNotificacao: (data) => request('PATCH', '/notificacao/', data),

  // Avaliacao
  getAvaliacoes: (params) => request('GET', '/avaliacao/', undefined, params),
  createAvaliacao: (data) => request('POST', '/avaliacao/', data),
}