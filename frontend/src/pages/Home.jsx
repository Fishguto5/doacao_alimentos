import { useState, useEffect } from 'react'
import { api } from '../api'
import DonationCard from '../components/DonationCard'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

export default function Home() {
  const { user } = useUser()
  const [doacoes, setDoacoes] = useState([])
  const [categorias, setCategorias] = useState([])
  const [cidades, setCidades] = useState([])
  const [cidadesSelecionadas, setCidadesSelecionadas] = useState(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [searchDebounced, setSearchDebounced] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => setSearchDebounced(search), 400)
    return () => clearTimeout(timer)
  }, [search])
  const [statusFiltro, setStatusFiltro] = useState('disponivel')
  const [categoriaFiltro, setCategoriaFiltro] = useState('')
  const [pesoMaxFiltro, setPesoMaxFiltro] = useState('')
  const [validadeMinFiltro, setValidadeMinFiltro] = useState('')

  useEffect(() => {
    api.getCategorias()
      .then(data => setCategorias(data))
      .catch(() => setCategorias([]))
  }, [])

  useEffect(() => {
    api.getCidades()
      .then(data => setCidades(data))
      .catch(() => setCidades([]))
  }, [])

  const cidadesFiltroParam = cidadesSelecionadas.size > 0
    ? [...cidadesSelecionadas].sort().join(',')
    : ''

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
        if (validadeMinFiltro) params.validade_min = validadeMinFiltro
        if (cidadesFiltroParam) params.cidades = cidadesFiltroParam
        if (searchDebounced) params.busca = searchDebounced
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
  }, [categoriaFiltro, statusFiltro, pesoMaxFiltro, validadeMinFiltro, cidadesFiltroParam, searchDebounced])

  const toggleCidade = (cidade) => {
    setCidadesSelecionadas(prev => {
      const next = new Set(prev)
      if (next.has(cidade)) {
        next.delete(cidade)
      } else {
        next.add(cidade)
      }
      return next
    })
  }

  const selecionarTodasCidades = () => {
    setCidadesSelecionadas(new Set(cidades))
  }

  const limparSelecaoCidades = () => {
    setCidadesSelecionadas(new Set())
  }

  const filtradas = doacoes

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
          <input
            className="input"
            type="date"
            value={validadeMinFiltro}
            onChange={e => setValidadeMinFiltro(e.target.value)}
            aria-label="Filtro por data de validade mínima"
          />
        </div>

        {cidades.length > 0 && (
          <div className="cidades-filtro" aria-label="Filtro por cidade">
            <div className="cidades-filtro-acoes">
              <button
                className="btn-secondary btn-sm"
                onClick={selecionarTodasCidades}
                aria-label="Selecionar todas as cidades"
              >
                Todas as cidades
              </button>
              <button
                className="btn-secondary btn-sm"
                onClick={limparSelecaoCidades}
                aria-label="Limpar seleção de cidades"
              >
                Limpar seleção
              </button>
            </div>
            <div className="cidades-lista">
              {cidades.map(cidade => (
                <label key={cidade} className="cidade-checkbox-label">
                  <input
                    type="checkbox"
                    checked={cidadesSelecionadas.has(cidade)}
                    onChange={() => toggleCidade(cidade)}
                    aria-label={`Filtrar por ${cidade}`}
                  />
                  {cidade}
                </label>
              ))}
            </div>
          </div>
        )}

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
