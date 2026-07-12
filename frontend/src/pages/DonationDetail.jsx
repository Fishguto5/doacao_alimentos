import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

const STATUS_LABELS = {
  disponivel: 'Disponível', reservada: 'Reservada',
  concluida: 'Concluída', expirada: 'Expirada', cancelada: 'Cancelada',
}
const UNIDADE_LABELS = { unidade: 'un', kg: 'kg', g: 'g', l: 'L', ml: 'mL' }

export default function DonationDetail({ id }) {
  const { user } = useUser()
  const [doacao, setDoacao] = useState(null)
  const [alimentos, setAlimentos] = useState([])
  const [solicitacoes, setSolicitacoes] = useState([])
  const [avaliacoes, setAvaliacoes] = useState([])
  const [doador, setDoador] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [requestMsg, setRequestMsg] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [ratingForm, setRatingForm] = useState({ nota: 5, comentario: '' })
  const [showRating, setShowRating] = useState(false)
  const [isImageModalOpen, setIsImageModalOpen] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [d, allAlimentos, allSols, allAvals] = await Promise.all([
        api.getDoacao(id),
        api.getAlimentos(),
        api.getSolicitacoes(),
        api.getAvaliacoes({ doacao: id }),
      ])
      setDoacao(d)
      setAlimentos(allAlimentos.filter(a => a.doacao === d.id))
      setSolicitacoes(allSols.filter(s => s.doacao === d.id))
      setAvaliacoes(allAvals)
      if (d.doador) {
        api.getUsuario(d.doador).then(setDoador).catch(() => {})
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { loadData() }, [loadData])

  const isDonor = user && doacao && doacao.doador === user.id
  const isReceptor = user && doacao && doacao.receptor === user.id
  const mySolicitation = user && solicitacoes.find(s => s.solicitante === user.id)
  const canRequest = user && doacao?.status === 'disponivel' && !isDonor && !mySolicitation
  const myRating = user && avaliacoes.find(a => a.avaliador === user.id)
  const canRate = user && doacao?.status === 'concluida' && !myRating && isReceptor && doacao?.doador

  async function handleRequest(e) {
    e.preventDefault()
    setSubmitting(true)
    setFeedback('')
    try {
      await api.createSolicitacao({ doacao: doacao.id, solicitante: user.id, status: 'pendente', mensagem: requestMsg })
      setFeedback('Solicitação enviada com sucesso!')
      setRequestMsg('')
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleAccept(solId) {
    setSubmitting(true)
    setFeedback('')
    try {
      await api.aceitarSolicitacao(solId)
      setFeedback('Solicitação aceita!')
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleReject(solId) {
    setSubmitting(true)
    try {
      await api.updateSolicitacao({ id: solId, status: 'recusada', data_resposta: new Date().toISOString() })
      setFeedback('Solicitação recusada.')
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleCancel() {
    if (!confirm('Tem certeza que quer cancelar esta doação?')) return
    setSubmitting(true)
    try {
      await api.updateDoacao({ id: doacao.id, status: 'cancelada' })
      setFeedback('Doação cancelada.')
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleConclude() {
    setSubmitting(true)
    try {
      await api.updateDoacao({ id: doacao.id, status: 'concluida', confirmacao_usuario_id: user.id })
      setFeedback('Doação marcada como concluída!')
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleRating(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      const avaliado = doacao.doador
      await api.createAvaliacao({ doacao: doacao.id, avaliador: user.id, avaliado, nota: ratingForm.nota, comentario: ratingForm.comentario })
      setFeedback('Avaliação enviada!')
      setShowRating(false)
      loadData()
    } catch (err) {
      setFeedback('Erro: ' + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  function openImageModal() {
    setIsImageModalOpen(true)
  }

  function closeImageModal() {
    setIsImageModalOpen(false)
  }

  if (loading) return <main className="page"><div className="loading">Carregando...</div></main>
  if (error) return <main className="page"><div className="error-msg">Erro: {error}</div></main>
  if (!doacao) return null

  const VALID_STATUSES = ['disponivel', 'reservada', 'concluida', 'expirada', 'cancelada']
  const safeStatus = VALID_STATUSES.includes(doacao.status) ? doacao.status : 'disponivel'
  const date = new Date(doacao.data_publicacao).toLocaleDateString('pt-BR')

  return (
    <main className="page">
      <button className="back-btn" onClick={() => navigate('#/')}>← Voltar</button>

      {feedback && <div className={feedback.startsWith('Erro') ? 'error-msg' : 'success-msg'}>{feedback}</div>}

      <div className="detail-layout">
        <div className="detail-main">
          <div className="detail-image-wrapper">
            {doacao.imagem ? (
              <button
                type="button"
                className="detail-image detail-image-button"
                onClick={openImageModal}
              >
                <img
                  src={doacao.imagem}
                  alt={`Imagem ilustrativa da doação: ${doacao.titulo}`}
                  onError={e => { e.target.style.display = 'none' }}
                />
                <div className="detail-image-overlay">Clique para ampliar</div>
              </button>
            ) : (
              <div className="detail-image detail-image-placeholder">
                <span>Imagem indisponível</span>
              </div>
            )}
          </div>

          <div className="detail-header">
              <div className="detail-header-row">
              <span className={`badge badge-${safeStatus}`}>{STATUS_LABELS[safeStatus] || safeStatus}</span>
              <span className="card-date">Publicado em {date}</span>
            </div>
            <h1 className="detail-title">{doacao.titulo}</h1>
            {doacao.descricao && <p className="detail-desc">{doacao.descricao}</p>}
          </div>

          <div className="detail-meta-grid">
            {doacao.cidade && <div className="meta-card"><span className="meta-label">Local</span><span>📍 {doacao.bairro ? `${doacao.bairro}, ` : ''}{doacao.cidade} – {doacao.estado}</span></div>}
            {doacao.estimativa_peso && <div className="meta-card"><span className="meta-label">Peso estimado</span><span>⚖️ {doacao.estimativa_peso} kg</span></div>}
            {doacao.expira_em && <div className="meta-card"><span className="meta-label">Expira em</span><span>📅 {new Date(doacao.expira_em).toLocaleDateString('pt-BR')}</span></div>}
            {doador && (
              <div className="meta-card">
                <span className="meta-label">Doador</span>
                <button className="profile-link" onClick={() => navigate(`#/users/${doador.id}`)}>👤 {doador.nome}</button>
              </div>
            )}
          </div>

          {alimentos.length > 0 && (
            <div className="section">
              <h2>Itens da doação</h2>
              <div className="alimentos-list">
                {alimentos.map(a => (
                  <div key={a.id} className="alimento-item">
                    <span className="alimento-nome">{a.nome}</span>
                    <span className="alimento-qty">{a.quantidade} {UNIDADE_LABELS[a.unidade] || a.unidade}</span>
                    {a.data_validade && <span className="alimento-val">Val: {a.data_validade.split('-').reverse().join('-')}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {avaliacoes.length > 0 && (
            <div className="section">
              <h2>Avaliações</h2>
              {avaliacoes.map(av => (
                <div key={av.id} className="rating-card">
                  <div className="stars">{'★'.repeat(av.nota)}{'☆'.repeat(5 - av.nota)}</div>
                  {av.comentario && <p>{av.comentario}</p>}
                </div>
              ))}
            </div>
          )}

          {isImageModalOpen && (
            <div className="image-modal-overlay" onClick={closeImageModal} role="dialog" aria-modal="true">
              <div className="image-modal-content" onClick={e => e.stopPropagation()}>
                <button
                  type="button"
                  className="image-modal-close"
                  onClick={closeImageModal}
                  aria-label="Fechar imagem"
                >
                  ×
                </button>
                <img
                  src={doacao.imagem}
                  alt={`Imagem em tela cheia da doação: ${doacao.titulo}`}
                />
              </div>
            </div>
          )}
        </div>

        <aside className="detail-sidebar">
          {/* Actions for donor */}
          {isDonor && (
            <div className="sidebar-card">
              <h3>Gerenciar doação</h3>
              {doacao.status === 'disponivel' && (
                <button className="btn-danger btn-full" onClick={handleCancel} disabled={submitting}>Cancelar doação</button>
              )}
              {doacao.status === 'reservada' && (
                doacao.concluida_por_doador ? (
                  <p className="status-waiting-msg">Você confirmou a entrega. Aguardando confirmação do receptor...</p>
                ) : (
                  <button className="btn-primary btn-full" onClick={handleConclude} disabled={submitting}>Marcar como concluída</button>
                )
              )}

              {solicitacoes.length > 0 && (
                <div className="requests-list">
                  <h4>Solicitações ({solicitacoes.length})</h4>
                  {solicitacoes.map(s => (
                    <div key={s.id} className={`request-item request-${s.status}`}>
                      <div className="request-info">
                        <span className={`badge badge-sol-${s.status}`}>{s.status}</span>
                        <span className="request-msg">{s.mensagem}</span>
                        <span className="request-date">{new Date(s.data_solicitacao).toLocaleDateString('pt-BR')}</span>
                      </div>
                      {s.status === 'pendente' && doacao.status === 'disponivel' && (
                        <div className="request-actions">
                          <button className="btn-sm btn-primary" onClick={() => handleAccept(s.id)} disabled={submitting}>Aceitar</button>
                          <button className="btn-sm btn-outline" onClick={() => handleReject(s.id)} disabled={submitting}>Recusar</button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Request for non-donor */}
          {canRequest && (
            <div className="sidebar-card">
              <h3>Solicitar esta doação</h3>
              <form onSubmit={handleRequest}>
                <div className="form-group">
                  <label>Mensagem (opcional)</label>
                  <textarea
                    className="input"
                    rows={3}
                    value={requestMsg}
                    onChange={e => setRequestMsg(e.target.value)}
                    placeholder="Apresente-se ao doador..."
                  />
                </div>
                <button className="btn-primary btn-full" type="submit" disabled={submitting}>
                  {submitting ? 'Enviando...' : 'Solicitar doação'}
                </button>
              </form>
            </div>
          )}

          {mySolicitation && !isDonor && (
            <div className="sidebar-card">
              <h3>Sua solicitação</h3>
              <div className={`badge badge-sol-${mySolicitation.status}`} style={{ display: 'inline-block', marginBottom: '8px' }}>
                {mySolicitation.status}
              </div>
              {mySolicitation.mensagem && <p className="request-msg">"{mySolicitation.mensagem}"</p>}
              <p className="request-date">Enviada em {new Date(mySolicitation.data_solicitacao).toLocaleDateString('pt-BR')}</p>
              {mySolicitation.status === 'aceita' && doacao.status === 'reservada' && (
                doacao.concluida_por_receptor ? (
                  <p className="status-waiting-msg" style={{ marginTop: '12px' }}>Você confirmou a retirada. Aguardando confirmação do doador...</p>
                ) : (
                  <button className="btn-primary btn-full" style={{ marginTop: '12px' }} onClick={handleConclude} disabled={submitting}>
                    Marcar como concluída
                  </button>
                )
              )}
            </div>
          )}

          {!user && doacao.status === 'disponivel' && (
            <div className="sidebar-card">
              <h3>Quer esta doação?</h3>
              <p>Cadastre-se ou entre para solicitar.</p>
              <button className="btn-primary btn-full" onClick={() => navigate('#/register')}>Entrar / Cadastrar</button>
            </div>
          )}

          {canRate && !showRating && (
            <div className="sidebar-card">
              <h3>Avaliar experiência</h3>
              <button className="btn-primary btn-full" onClick={() => setShowRating(true)}>Deixar avaliação</button>
            </div>
          )}

          {showRating && (
            <div className="sidebar-card">
              <h3>Avaliar</h3>
              <form onSubmit={handleRating}>
                <div className="form-group">
                  <label>Nota (1–5)</label>
                  <select className="input" value={ratingForm.nota} onChange={e => setRatingForm(f => ({ ...f, nota: Number(e.target.value) }))}>
                    {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} ★</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Comentário</label>
                  <textarea className="input" rows={3} value={ratingForm.comentario} onChange={e => setRatingForm(f => ({ ...f, comentario: e.target.value }))} />
                </div>
                <button className="btn-primary btn-full" type="submit" disabled={submitting}>Enviar avaliação</button>
              </form>
            </div>
          )}
        </aside>
      </div>
    </main>
  )
}
