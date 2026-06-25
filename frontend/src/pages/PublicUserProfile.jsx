import { useEffect, useState } from 'react'
import { api } from '../api'
import { navigate } from '../router'
import DonationCard from '../components/DonationCard'

function formatRating(value) {
  return value.toFixed(1).replace('.', ',')
}

export default function PublicUserProfile({ id }) {
  const [profile, setProfile] = useState(null)
  const [doacoes, setDoacoes] = useState([])
  const [avaliacoes, setAvaliacoes] = useState([])
  const [avaliadores, setAvaliadores] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadProfile() {
      setLoading(true)
      setError('')
      try {
        const [usuario, todasDoacoes, avaliacoesRecebidas] = await Promise.all([
          api.getUsuario(id),
          api.getDoacoes(),
          api.getAvaliacoes({ avaliado: id }),
        ])

        const avaliadorIds = [...new Set(avaliacoesRecebidas.map(a => a.avaliador))]
        const usuariosAvaliadores = await Promise.all(
          avaliadorIds.map(avaliadorId =>
            api.getUsuario(avaliadorId)
              .then(usuarioAvaliador => [avaliadorId, usuarioAvaliador])
              .catch(() => [avaliadorId, null])
          )
        )

        if (!active) return
        setProfile(usuario)
        setDoacoes(todasDoacoes.filter(doacao => doacao.doador === usuario.id))
        setAvaliacoes(avaliacoesRecebidas)
        setAvaliadores(Object.fromEntries(usuariosAvaliadores.filter(([, usuario]) => usuario)))
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadProfile()

    return () => {
      active = false
    }
  }, [id])

  if (loading) return <main className="page"><div className="loading">Carregando...</div></main>
  if (error) return <main className="page"><div className="error-msg">Erro: {error}</div></main>
  if (!profile) return null

  const totalAvaliacoes = avaliacoes.length
  const media = totalAvaliacoes
    ? avaliacoes.reduce((total, avaliacao) => total + avaliacao.nota, 0) / totalAvaliacoes
    : 0

  return (
    <main className="page">
      <button className="back-btn" onClick={() => navigate('#/')}>← Voltar</button>

      <div className="profile-layout public-profile-layout">
        <aside className="profile-sidebar">
          {profile.foto_perfil_url ? (
            <img className="profile-photo" src={profile.foto_perfil_url} alt={profile.nome} onError={e => { e.target.style.display = 'none' }} />
          ) : (
            <div className="profile-avatar-lg">{profile.nome.charAt(0).toUpperCase()}</div>
          )}
          <h1 className="profile-name">{profile.nome}</h1>
          {profile.cidade && <p className="profile-location">Local: {profile.cidade}{profile.estado ? `, ${profile.estado}` : ''}</p>}

          <div className="public-profile-stats">
            <div>
              <span className="public-profile-stat-value">{doacoes.length}</span>
              <span className="meta-label">Doações</span>
            </div>
            <div>
              <span className="public-profile-stat-value">{totalAvaliacoes ? formatRating(media) : '-'}</span>
              <span className="meta-label">Nota média</span>
            </div>
          </div>
        </aside>

        <div className="profile-content">
          <section className="section">
            <h2>Avaliações recebidas</h2>
            {avaliacoes.length === 0 ? (
              <div className="empty-state public-empty-state">
                <p>Este usuário ainda não recebeu avaliações.</p>
              </div>
            ) : (
              <div className="ratings-list">
                {avaliacoes
                  .slice()
                  .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                  .map(avaliacao => (
                    <article key={avaliacao.id} className="rating-card">
                      <div className="rating-header">
                        <div className="stars">{'★'.repeat(avaliacao.nota)}{'☆'.repeat(5 - avaliacao.nota)}</div>
                        <span className="card-date">{new Date(avaliacao.created_at).toLocaleDateString('pt-BR')}</span>
                      </div>
                      {avaliadores[avaliacao.avaliador] && (
                        <p className="rating-author">Por {avaliadores[avaliacao.avaliador].nome}</p>
                      )}
                      {avaliacao.comentario && <p>{avaliacao.comentario}</p>}
                    </article>
                  ))}
              </div>
            )}
          </section>

          <section className="section">
            <h2>Doações publicadas</h2>
            {doacoes.length === 0 ? (
              <div className="empty-state public-empty-state">
                <p>Este usuário ainda não publicou doações.</p>
              </div>
            ) : (
              <div className="donations-grid">
                {doacoes.map(doacao => <DonationCard key={doacao.id} doacao={doacao} />)}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  )
}
