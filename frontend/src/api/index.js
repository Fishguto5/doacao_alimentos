const request = async (method, path, body) => {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(path, opts)
  if (res.status === 204) return null
  const json = await res.json()
  if (!res.ok) {
    const msg = json.msg || JSON.stringify(json)
    throw new Error(msg)
  }
  return json.data
}

export const api = {
  // Usuario
  getUsuarios: () => request('GET', '/usuario/'),
  getUsuario: (id) => request('GET', `/usuario/${id}/`),
  createUsuario: (data) => request('POST', '/usuario/', data),
  updateUsuario: (data) => request('PATCH', '/usuario/', data),

  // Doacao
  getDoacoes: () => request('GET', '/doacao/'),
  getDoacao: (id) => request('GET', `/doacao/${id}/`),
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

  // Notificacao
  getNotificacoes: () => request('GET', '/notificacao/'),
  updateNotificacao: (data) => request('PATCH', '/notificacao/', data),

  // Avaliacao
  getAvaliacoes: () => request('GET', '/avaliacao/'),
  createAvaliacao: (data) => request('POST', '/avaliacao/', data),
}
