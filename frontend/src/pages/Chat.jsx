import { useEffect, useState } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

export default function Chat() {
  const { user } = useUser()
  const [conversations, setConversations] = useState([])
  const [names, setNames] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('#/register?tab=login')
      return
    }

    let active = true
    async function loadComments() {
      setLoading(true)
      setError('')
      try {
        const [donations, requests, ratings] = await Promise.all([
          api.getDoacoes(),
          api.getSolicitacoes(),
          api.getAvaliacoes(),
        ])
        const userId = Number(user.id)
        const acceptedIds = new Set(requests
          .filter(request => Number(request.solicitante) === userId && request.status === 'aceita')
          .map(request => Number(request.doacao)))
        const related = donations
          .filter(donation => Number(donation.doador) === userId || Number(donation.receptor) === userId || acceptedIds.has(Number(donation.id)))
          .map(donation => {
            const isDonor = Number(donation.doador) === userId
            const ownRequests = requests.filter(request =>
              Number(request.doacao) === Number(donation.id) &&
              (isDonor || Number(request.solicitante) === userId) &&
              request.mensagem?.trim(),
            )
            const donationRatings = ratings.filter(rating =>
              Number(rating.doacao) === Number(donation.id) && rating.comentario?.trim(),
            )
            const comments = [
              ...ownRequests.map(request => ({
                id: `request-${request.id}`,
                authorId: request.solicitante,
                text: request.mensagem,
                kind: 'Solicitação',
                date: request.data_solicitacao,
              })),
              ...donationRatings.map(rating => ({
                id: `rating-${rating.id}`,
                authorId: rating.avaliador,
                text: rating.comentario,
                kind: 'Avaliação',
                date: rating.created_at,
              })),
            ].sort((a, b) => new Date(a.date) - new Date(b.date))
            return { donation, isDonor, comments }
          })
          .sort((a, b) => new Date(b.comments.at(-1)?.date || b.donation.data_publicacao) - new Date(a.comments.at(-1)?.date || a.donation.data_publicacao))

        const authorIds = [...new Set(related.flatMap(conversation => conversation.comments.map(comment => Number(comment.authorId))))]
        const authors = await Promise.all(authorIds.map(async id => {
          if (id === userId) return [id, user.nome]
          try {
            const author = await api.getUsuario(id)
            return [id, author.nome]
          } catch {
            return [id, 'Usuário']
          }
        }))

        if (active) {
          setConversations(related)
          setNames(Object.fromEntries(authors))
        }
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadComments()
    return () => { active = false }
  }, [user])

  if (!user) return null

  return (
    <main className="page chat-page">
      <div className="mobile-detail-header">
        <button type="button" onClick={() => navigate('#/')} aria-label="Voltar">
          <img src="/figma/mobile-back.png" alt="" />
        </button>
        <span>Mensagens</span>
      </div>
      <h1 className="chat-title">Mensagens das suas doações</h1>
      <p className="chat-intro">Comentários de solicitações e avaliações das doações que você criou ou reservou.</p>

      {loading && <div className="loading">Carregando mensagens...</div>}
      {!loading && error && <div className="error-msg">Erro ao carregar mensagens: {error}</div>}
      {!loading && !error && conversations.length === 0 && (
        <div className="empty-state"><p>Você ainda não tem doações ou reservas com mensagens.</p></div>
      )}
      {!loading && !error && conversations.length > 0 && (
        <div className="chat-conversations">
          {conversations.map(({ donation, isDonor, comments }) => (
            <section className="chat-conversation" key={donation.id} aria-label={`Comentários de ${donation.titulo}`}>
              <div className="chat-conversation-header">
                <div>
                  <span className="chat-role">{isDonor ? 'Doação criada por você' : 'Doação reservada por você'}</span>
                  <h2>{donation.titulo}</h2>
                </div>
                <button type="button" className="link-btn" onClick={() => navigate(`#/donation/${donation.id}`)}>Ver doação</button>
              </div>
              {comments.length === 0 ? (
                <p className="chat-empty">Ainda não há comentários nesta doação.</p>
              ) : (
                <div className="chat-comments">
                  {comments.map(comment => (
                    <article className={`chat-comment${Number(comment.authorId) === Number(user.id) ? ' own' : ''}`} key={comment.id}>
                      <div className="chat-comment-meta">
                        <strong>{names[Number(comment.authorId)] || 'Usuário'}</strong>
                        <span>{comment.kind}</span>
                        {comment.date && <time dateTime={comment.date}>{new Date(comment.date).toLocaleDateString('pt-BR')}</time>}
                      </div>
                      <p>{comment.text}</p>
                    </article>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </main>
  )
}
