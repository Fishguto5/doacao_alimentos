import { useState, useEffect } from 'react'
import { api } from '../api'
import DonationCard from '../components/DonationCard'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

export default function Home() {
  const { user } = useUser()
  const [doacoes, setDoacoes] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [cidadeFiltro, setCidadeFiltro] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('disponivel')
  const [categoriaFiltro, setCategoriaFiltro] = useState('')
  const [pesoMaxFiltro, setPesoMaxFiltro] = useState('')

  useEffect(() => {
    api.getCategorias()
      .then(data => setCategorias(data))
      .catch(() => setCategorias([]))
  }, [])

  useEffect(() => {
    let active = true

    async function loadDoacoes() {
      setLoading(true)
      setError('')

      try {
        const params = {}
        if (categoriaFiltro) params.categoria = categoriaFiltro
        if (statusFiltro) params.status = statusFiltro
        if (pesoMaxFiltro) params.peso_max = pesoMaxFiltro
        const data = await api.getDoacoes(Object.keys(params).length ? params : undefined)
        if (!active) return
        setDoacoes(data)
      } catch (e) {
        if (!active) return
        setError(e.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadDoacoes()

    return () => {
      active = false
    }
  }, [categoriaFiltro, statusFiltro, pesoMaxFiltro])

  const cidades = [...new Set(doacoes.map(d => d.cidade).filter(Boolean))].sort()

  const filtradas = doacoes.filter(d => {
    if (cidadeFiltro && d.cidade !== cidadeFiltro) return false
    if (search) {
      const q = search.toLowerCase()
      return (
        d.titulo?.toLowerCase().includes(q) ||
        d.descricao?.toLowerCase().includes(q) ||
        d.bairro?.toLowerCase().includes(q)
      )
    }
    return true
  })

  return (
    <main className="page">
      <section className="hero-banner">
        <div className="hero-content">
          <h1>Compartilhe alimentos,<br />transforme vidas</h1>
          <p>Conectando quem tem com quem precisa. Anuncie ou solicite doações de alimentos na sua região.</p>
          {!user && (
            <div className="hero-cta">
              <button className="btn-primary btn-lg" onClick={() => navigate('#/register')}>
                Começar agora
              </button>
            </div>
          )}
          {user && (
            <div className="hero-cta">
              <button className="btn-primary btn-lg" onClick={() => navigate('#/create')}>
                + Anunciar doação
              </button>
            </div>
          )}
        </div>
      </section>

      <section className="filters-section">
        <div className="filters-row">
          <input
            className="input search-input"
            type="text"
            placeholder="Buscar doações..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <select className="input" value={statusFiltro} onChange={e => setStatusFiltro(e.target.value)}>
            <option value="">Todos os status</option>
            <option value="disponivel">Disponível</option>
            <option value="reservada">Reservada</option>
            <option value="concluida">Concluída</option>
            <option value="expirada">Expirada</option>
            <option value="cancelada">Cancelada</option>
          </select>
          <select
            className="input"
            value={categoriaFiltro}
            onChange={e => setCategoriaFiltro(e.target.value)}
            aria-label="Filtro por categoria de alimento"
          >
            <option value="">Todas as categorias</option>
            {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
          </select>
          <select className="input" value={cidadeFiltro} onChange={e => setCidadeFiltro(e.target.value)}>
            <option value="">Todas as cidades</option>
            {cidades.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <input
            className="input"
            type="number"
            min="0"
            step="0.1"
            value={pesoMaxFiltro}
            onChange={e => setPesoMaxFiltro(e.target.value)}
            placeholder="Peso máximo (kg)"
            aria-label="Filtro por peso máximo da doação"
          />
        </div>
        <p className="results-count">{filtradas.length} doaç{filtradas.length !== 1 ? 'ões' : 'ão'} encontrada{filtradas.length !== 1 ? 's' : ''}</p>
      </section>

      {loading && <div className="loading">Carregando doações...</div>}
      {error && <div className="error-msg">Erro ao carregar: {error}</div>}

      {!loading && !error && (
        filtradas.length === 0 ? (
          <div className="empty-state">
            <p>🍃 Nenhuma doação encontrada com esses filtros.</p>
            {user && (
              <button className="btn-primary" onClick={() => navigate('#/create')}>
                Seja o primeiro a doar!
              </button>
            )}
          </div>
        ) : (
          <div className="donations-grid">
            {filtradas.map(d => <DonationCard key={d.id} doacao={d} />)}
          </div>
        )
      )}
    </main>
  )
}
