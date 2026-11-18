import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

const sameId = (a, b) => Number(a) === Number(b)

export default function Chat() {
  const { user } = useUser()
  const [donations, setDonations] = useState([])
  const [requests, setRequests] = useState([])
  const [ratings, setRatings] = useState([])
  const [messages, setMessages] = useState([])
  const [names, setNames] = useState({})
  const [selectedId, setSelectedId] = useState(null)
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState('')
  const [chatAuthError, setChatAuthError] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('#/register?tab=login')
      return
    }
    let active = true
    async function load() {
      setLoading(true)
      setError('')
      setChatAuthError('')
      try {
        const [allDonations, allRequests, allRatings, allMessages] = await Promise.all([
          api.getDoacoes(), api.getSolicitacoes(), api.getAvaliacoes(),
          user.auth_token ? api.getMensagens().catch(err => {
            if (active) setChatAuthError(err.message || 'Não foi possível abrir as mensagens.')
            return []
          }) : Promise.resolve([]),
        ])
        const acceptedIds = new Set(allRequests
          .filter(request => sameId(request.solicitante, user.id) && request.status === 'aceita')
          .map(request => Number(request.doacao)))
        const related = allDonations.filter(donation =>
          sameId(donation.doador, user.id) || sameId(donation.receptor, user.id) || acceptedIds.has(Number(donation.id)))
        const ids = new Set([
          ...related.flatMap(donation => [donation.doador, donation.receptor]),
          ...allRequests.filter(request => related.some(donation => sameId(donation.id, request.doacao))).map(request => request.solicitante),
          ...allRatings.filter(rating => related.some(donation => sameId(donation.id, rating.doacao))).map(rating => rating.avaliador),
        ].filter(Boolean).map(Number))
        const authors = await Promise.all([...ids].map(async id => {
          if (sameId(id, user.id)) return [id, user.nome]
          try { return [id, (await api.getUsuario(id)).nome] } catch { return [id, 'Usuário'] }
        }))
        if (active) {
          setDonations(related)
          setRequests(allRequests)
          setRatings(allRatings)
          setMessages(allMessages)
          setNames(Object.fromEntries(authors))
        }
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => { active = false }
  }, [user])

  useEffect(() => {
    if (!user?.auth_token) return undefined
    let active = true
    const timer = window.setInterval(async () => {
      try {
        const latest = await api.getMensagens()
        if (active) setMessages(latest)
      } catch (err) {
        if (active && err.message?.includes('Entre novamente')) setChatAuthError(err.message)
      }
    }, 10000)
    return () => { active = false; window.clearInterval(timer) }
  }, [user?.auth_token])

  const conversations = useMemo(() => donations.map(donation => {
    const isDonor = sameId(donation.doador, user?.id)
    const ownRequests = requests.filter(request => sameId(request.doacao, donation.id) &&
      (isDonor || sameId(request.solicitante, user?.id)) && request.mensagem?.trim())
    const donationRatings = ratings.filter(rating => sameId(rating.doacao, donation.id) && rating.comentario?.trim())
    const timeline = [
      ...ownRequests.map(request => ({ id: `request-${request.id}`, authorId: request.solicitante, text: request.mensagem, kind: 'Solicitação', date: request.data_solicitacao })),
      ...donationRatings.map(rating => ({ id: `rating-${rating.id}`, authorId: rating.avaliador, text: rating.comentario, kind: 'Avaliação', date: rating.created_at })),
      ...messages.filter(message => sameId(message.doacao, donation.id)).map(message => ({ id: `message-${message.id}`, authorId: message.remetente, text: message.texto, kind: '', date: message.created_at })),
    ].sort((a, b) => new Date(a.date || 0) - new Date(b.date || 0))
    return { donation, isDonor, timeline }
  }).sort((a, b) => new Date(b.timeline.at(-1)?.date || b.donation.data_publicacao || 0) -
    new Date(a.timeline.at(-1)?.date || a.donation.data_publicacao || 0)), [donations, requests, ratings, messages, user?.id])

  const selected = conversations.find(conversation => sameId(conversation.donation.id, selectedId))
  const canSend = selected && selected.donation.doador && selected.donation.receptor && user?.auth_token && !chatAuthError

  async function send(event) {
    event.preventDefault()
    const texto = draft.trim()
    if (!canSend || !texto || sending) return
    setSending(true)
    setSendError('')
    try {
      const sent = await api.sendMensagem({ doacao: selected.donation.id, texto })
      setMessages(current => current.some(message => sameId(message.id, sent.id)) ? current : [...current, sent])
      setDraft('')
    } catch (err) {
      setSendError(err.message || 'Não foi possível enviar a mensagem.')
    } finally {
      setSending(false)
    }
  }

  if (!user) return null
  return (
    <main className="page chat-page">
      <div className="mobile-detail-header">
        <button type="button" onClick={() => selected ? setSelectedId(null) : navigate('#/')} aria-label="Voltar"><img src="/figma/mobile-back.png" alt="" /></button>
        <span>{selected?.donation.titulo || 'Mensagens'}</span>
      </div>
      <h1 className="chat-title">Mensagens das suas doações</h1>
      <p className="chat-intro">Converse sobre as doações que você criou ou reservou.</p>
      {loading && <div className="loading">Carregando mensagens...</div>}
      {!loading && error && <div className="error-msg">Erro ao carregar mensagens: {error}</div>}
      {!loading && !error && conversations.length === 0 && <div className="empty-state"><p>Você ainda não tem doações ou reservas com mensagens.</p></div>}
      {!loading && !error && conversations.length > 0 && (
        <div className={`chat-layout${selected ? ' chat-has-selection' : ''}`}>
          <section className="chat-list" aria-label="Conversas">
            <div className="chat-list-heading">Suas conversas <span>{conversations.length}</span></div>
            {conversations.map(({ donation, isDonor, timeline }) => (
              <button type="button" className={`chat-list-item${sameId(selectedId, donation.id) ? ' active' : ''}`} key={donation.id}
                onClick={() => { setSelectedId(donation.id); setDraft(''); setSendError('') }}>
                <span className="chat-list-avatar" aria-hidden="true">{donation.titulo?.charAt(0).toUpperCase() || 'D'}</span>
                <span className="chat-list-copy"><strong>{donation.titulo}</strong><small>{isDonor ? 'Você doou' : 'Você reservou'}</small><span>{timeline.at(-1)?.text || 'Inicie uma conversa'}</span></span>
              </button>
            ))}
          </section>
          <section className="chat-thread" aria-label={selected ? `Conversa de ${selected.donation.titulo}` : 'Selecione uma conversa'}>
            {selected ? <>
              <header className="chat-thread-header"><div><span className="chat-role">{selected.isDonor ? 'Doação criada por você' : 'Doação reservada por você'}</span><h2>{selected.donation.titulo}</h2></div><button type="button" className="link-btn" onClick={() => navigate(`#/donation/${selected.donation.id}`)}>Ver doação</button></header>
              <div className="chat-thread-messages" role="log" aria-live="polite">
                {selected.timeline.length === 0 && <p className="chat-empty">Ainda não há mensagens nesta doação.</p>}
                {selected.timeline.map(item => <article className={`chat-comment${sameId(item.authorId, user.id) ? ' own' : ''}`} key={item.id}>
                  <div className="chat-comment-meta"><strong>{names[Number(item.authorId)] || 'Usuário'}</strong>{item.kind && <span>{item.kind}</span>}{item.date && <time dateTime={item.date}>{new Date(item.date).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}</time>}</div>
                  <p>{item.text}</p>
                </article>)}
              </div>
              {canSend ? <form className="chat-composer" onSubmit={send}>
                {sendError && <p className="chat-send-error" role="alert">{sendError}</p>}
                <label className="sr-only" htmlFor="chat-message">Sua mensagem</label>
                <input id="chat-message" value={draft} onChange={event => setDraft(event.target.value)} placeholder="Escreva uma mensagem..." maxLength={2000} />
                <button type="submit" disabled={!draft.trim() || sending}>{sending ? 'Enviando...' : 'Enviar'}</button>
              </form> : <div className="chat-composer-notice">{!user.auth_token || chatAuthError ? <><span>{chatAuthError || 'Entre novamente para enviar mensagens.'}</span> <button type="button" onClick={() => navigate('#/register?tab=login')}>Entrar</button></> : 'A conversa ficará disponível quando a doação for reservada.'}</div>}
            </> : <div className="chat-select-hint">Selecione uma doação para ler e enviar mensagens.</div>}
          </section>
        </div>
      )}
    </main>
  )
}
