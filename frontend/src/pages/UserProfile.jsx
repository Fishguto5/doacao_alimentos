import { useState, useEffect } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'
import DonationCard from '../components/DonationCard'

const STATUS_LABELS = {
  disponivel: 'Disponivel',
  reservada: 'Reservada',
  concluida: 'Concluida',
  expirada: 'Expirada',
  cancelada: 'Cancelada',
}

const SOL_STATUS_LABELS = {
  pendente: 'Pendente',
  aceita: 'Aceita',
  recusada: 'Recusada',
  cancelada: 'Cancelada',
}

export default function UserProfile() {
  const { user, login, logout } = useUser()
  const hash = window.location.hash
  const initialTab = hash.includes('tab=') ? hash.split('tab=')[1] : 'doacoes'
  const [tab, setTab] = useState(initialTab)
  const [doacoes, setDoacoes] = useState([])
  const [solicitacoes, setSolicitacoes] = useState([])
  const [notificacoes, setNotificacoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('#/register')
      return
    }

    Promise.all([
      api.getDoacoes(),
      api.getSolicitacoes(),
      api.getNotificacoes(),
    ]).then(([d, s, n]) => {
      setDoacoes(d.filter(x => x.doador === user.id))
      setSolicitacoes(s.filter(x => x.solicitante === user.id))
      setNotificacoes(n.filter(x => x.usuario === user.id))
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [user])

  useEffect(() => {
    if (user) {
      setEditForm({
        nome: user.nome,
        email: user.email,
        cidade: user.cidade || '',
        estado: user.estado || '',
        bairro: user.bairro || '',
        cep: user.cep || '',
        logradouro: user.logradouro || '',
        numero: user.numero || '',
        complemento: user.complemento || '',
        foto_perfil_url: user.foto_perfil_url || '',
      })
    }
  }, [user])

  async function handleSaveProfile(e) {
    e.preventDefault()
    setSaving(true)
    setFeedback('')

    try {
      const updated = await api.updateUsuario({ id: user.id, ...editForm })
      login({
        id: updated.id,
        nome: updated.nome,
        email: updated.email,
        cidade: updated.cidade,
        estado: updated.estado,
        bairro: updated.bairro,
        cep: updated.cep,
        logradouro: updated.logradouro,
        numero: updated.numero,
        complemento: updated.complemento,
        foto_perfil_url: updated.foto_perfil_url,
      })
      setEditMode(false)
      setFeedback('Perfil atualizado!')
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  async function markRead(notifId) {
    try {
      await api.updateNotificacao({ id: notifId, status: 'lida' })
      setNotificacoes(list => list.map(n => n.id === notifId ? { ...n, status: 'lida' } : n))
    } catch {
      // Ignora falhas de atualização para não bloquear a navegação do usuário.
    }
  }

  if (!user) return null

  const unread = notificacoes.filter(n => n.status === 'pendente').length

  return (
    <main className="page">
      <div className="profile-layout">
        <aside className="profile-sidebar">
          {user.foto_perfil_url ? (
            <img className="profile-photo" src={user.foto_perfil_url} alt={user.nome} onError={e => { e.target.style.display = 'none' }} />
          ) : (
            <div className="profile-avatar-lg">{user.nome.charAt(0).toUpperCase()}</div>
          )}
          <h2 className="profile-name">{user.nome}</h2>
          <p className="profile-email">{user.email}</p>
          {user.cidade && <p className="profile-location">Local: {user.cidade}{user.estado ? `, ${user.estado}` : ''}</p>}
          <button className="btn-danger btn-full" style={{ marginTop: '16px' }} onClick={logout}>Sair</button>
        </aside>

        <div className="profile-content">
          {feedback && <div className={feedback.startsWith('Erro') ? 'error-msg' : 'success-msg'}>{feedback}</div>}

          <div className="profile-tabs">
            <button className={`profile-tab${tab === 'doacoes' ? ' active' : ''}`} onClick={() => setTab('doacoes')}>
              Minhas Doacoes ({doacoes.length})
            </button>
            <button className={`profile-tab${tab === 'solicitacoes' ? ' active' : ''}`} onClick={() => setTab('solicitacoes')}>
              Solicitacoes ({solicitacoes.length})
            </button>
            <button className={`profile-tab${tab === 'notificacoes' ? ' active' : ''}`} onClick={() => setTab('notificacoes')}>
              Notificacoes {unread > 0 && <span className="badge">{unread}</span>}
            </button>
            <button className={`profile-tab${tab === 'perfil' ? ' active' : ''}`} onClick={() => setTab('perfil')}>
              Perfil
            </button>
          </div>

          {loading && <div className="loading">Carregando...</div>}

          {!loading && tab === 'doacoes' && (
            <div>
              <div className="tab-header">
                <button className="btn-primary" onClick={() => navigate('#/create')}>+ Nova doacao</button>
              </div>
              {doacoes.length === 0 ? (
                <div className="empty-state">
                  <p>Voce ainda nao fez nenhuma doacao.</p>
                  <button className="btn-primary" onClick={() => navigate('#/create')}>Fazer primeira doacao</button>
                </div>
              ) : (
                <div className="donations-grid">
                  {doacoes.map(d => <DonationCard key={d.id} doacao={d} />)}
                </div>
              )}
            </div>
          )}

          {!loading && tab === 'solicitacoes' && (
            <div>
              {solicitacoes.length === 0 ? (
                <div className="empty-state">
                  <p>Voce ainda nao fez nenhuma solicitacao.</p>
                  <button className="btn-primary" onClick={() => navigate('#/')}>Buscar doacoes</button>
                </div>
              ) : (
                <div className="solicitacoes-list">
                  {solicitacoes.map(s => (
                    <div key={s.id} className={`solicitation-item solicitation-${s.status}`}>
                      <div className="solicitation-header">
                        <span className={`badge badge-sol-${s.status}`}>{SOL_STATUS_LABELS[s.status]}</span>
                        <span className="card-date">{new Date(s.data_solicitacao).toLocaleDateString('pt-BR')}</span>
                      </div>
                      {s.mensagem && <p className="solicitation-msg">"{s.mensagem}"</p>}
                      <button className="link-btn" onClick={() => navigate(`#/donation/${s.doacao}`)}>Ver doacao -&gt;</button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!loading && tab === 'notificacoes' && (
            <div>
              {notificacoes.length === 0 ? (
                <div className="empty-state"><p>Nenhuma notificacao.</p></div>
              ) : (
                <div className="notificacoes-list">
                  {notificacoes.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map(n => (
                    <div key={n.id} className={`notification-item${n.status === 'pendente' ? ' unread' : ''}`}>
                      <div className="notification-body">
                        <p>{n.mensagem}</p>
                        <span className="card-date">{new Date(n.created_at).toLocaleDateString('pt-BR')}</span>
                      </div>
                      <div className="notification-actions">
                        {n.doacao && <button className="link-btn" onClick={() => navigate(`#/donation/${n.doacao}`)}>Ver doacao -&gt;</button>}
                        {n.status === 'pendente' && <button className="btn-outline btn-sm" onClick={() => markRead(n.id)}>Marcar como lida</button>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {tab === 'perfil' && (
            <div className="profile-edit">
              {!editMode ? (
                <div>
                  <div className="profile-info-grid">
                    <div><span className="meta-label">Nome</span><span>{user.nome}</span></div>
                    <div><span className="meta-label">E-mail</span><span>{user.email}</span></div>
                    <div><span className="meta-label">Cidade</span><span>{user.cidade || '-'}</span></div>
                    <div><span className="meta-label">Estado</span><span>{user.estado || '-'}</span></div>
                    <div><span className="meta-label">Logradouro</span><span>{user.logradouro || '-'}</span></div>
                    <div><span className="meta-label">Numero</span><span>{user.numero || '-'}</span></div>
                    <div><span className="meta-label">Complemento</span><span>{user.complemento || '-'}</span></div>
                    <div><span className="meta-label">Bairro</span><span>{user.bairro || '-'}</span></div>
                    <div><span className="meta-label">CEP</span><span>{user.cep || '-'}</span></div>
                  </div>
                  <button className="btn-outline" onClick={() => setEditMode(true)}>Editar perfil</button>
                </div>
              ) : (
                <form onSubmit={handleSaveProfile}>
                  <div className="form-row">
                    <div className="form-group"><label>Nome</label><input className="input" value={editForm.nome} onChange={e => setEditForm(f => ({ ...f, nome: e.target.value }))} /></div>
                    <div className="form-group"><label>E-mail</label><input className="input" type="email" value={editForm.email} onChange={e => setEditForm(f => ({ ...f, email: e.target.value }))} /></div>
                  </div>
                  <div className="form-row">
                    <div className="form-group"><label>Cidade</label><input className="input" value={editForm.cidade} onChange={e => setEditForm(f => ({ ...f, cidade: e.target.value }))} /></div>
                    <div className="form-group form-group-sm"><label>Estado</label><input className="input" maxLength={2} value={editForm.estado} onChange={e => setEditForm(f => ({ ...f, estado: e.target.value.toUpperCase() }))} /></div>
                  </div>
                  <div className="form-row">
                    <div className="form-group"><label>Logradouro</label><input className="input" value={editForm.logradouro} onChange={e => setEditForm(f => ({ ...f, logradouro: e.target.value }))} /></div>
                    <div className="form-group form-group-sm"><label>Numero</label><input className="input" value={editForm.numero} onChange={e => setEditForm(f => ({ ...f, numero: e.target.value }))} /></div>
                  </div>
                  <div className="form-group"><label>Complemento</label><input className="input" value={editForm.complemento} onChange={e => setEditForm(f => ({ ...f, complemento: e.target.value }))} /></div>
                  <div className="form-row">
                    <div className="form-group"><label>Bairro</label><input className="input" value={editForm.bairro} onChange={e => setEditForm(f => ({ ...f, bairro: e.target.value }))} /></div>
                    <div className="form-group"><label>CEP</label><input className="input" value={editForm.cep} onChange={e => setEditForm(f => ({ ...f, cep: e.target.value }))} /></div>
                  </div>
                  <div className="form-group"><label>URL da foto</label><input className="input" type="url" value={editForm.foto_perfil_url} onChange={e => setEditForm(f => ({ ...f, foto_perfil_url: e.target.value }))} /></div>
                  <div className="form-row">
                    <button className="btn-primary" type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</button>
                    <button type="button" className="btn-outline" onClick={() => setEditMode(false)}>Cancelar</button>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
