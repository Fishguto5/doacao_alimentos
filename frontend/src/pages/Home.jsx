import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import DonationCard from '../components/DonationCard'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

export default function Home() {
  const { user } = useUser()
  const [doacoes, setDoacoes] = useState([])
  const [categorias, setCategorias] = useState([])
  const [alimentos, setAlimentos] = useState([])
  const [avaliacoes, setAvaliacoes] = useState([])
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
  const [cidades, setCidades] = useState([])
  const [cidadesSelecionadas, setCidadesSelecionadas] = useState(new Set())
  const [comboAberta, setComboAberta] = useState(false)
  const comboRef = useRef(null)
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

  useEffect(() => {
    if (typeof api.getAlimentos !== 'function') return
    api.getAlimentos().then(setAlimentos).catch(() => setAlimentos([]))
  }, [])

  useEffect(() => {
    api.getAvaliacoes().then(setAvaliacoes).catch(() => setAvaliacoes([]))
    const onSearch = event => setSearch(event.detail)
    const onToggleFilters = () => setMobileFiltersOpen(open => !open)
    window.addEventListener('donation-search', onSearch)
    window.addEventListener('toggle-donation-filters', onToggleFilters)
    return () => {
      window.removeEventListener('donation-search', onSearch)
      window.removeEventListener('toggle-donation-filters', onToggleFilters)
    }
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

  useEffect(() => {
    function handleClickFora(e) {
      if (comboRef.current && !comboRef.current.contains(e.target)) {
        setComboAberta(false)
      }
    }
    document.addEventListener('mousedown', handleClickFora)
    return () => document.removeEventListener('mousedown', handleClickFora)
  }, [])

  const filtradas = doacoes

  return (
    <main className="page">
      <section className="hero-banner">
        <img className="hero-leaf" src="/figma/hero-leaf.svg" alt="" />
        <div className="hero-content">
          <span className="hero-eyebrow">UMA REDE QUE ALIMENTA ESPERANÇA</span>
          <h1>Compartilhe alimentos,<br />transforme vidas</h1>
          <p>Conectando quem tem com quem precisa. Anuncie ou solicite doações de alimentos na sua região.</p>
          {!user && (
            <div className="hero-cta">
              <button className="btn-primary btn-lg hero-action" onClick={() => navigate('#/register')}>
                <span className="hero-action-icon">+</span> Começar agora
              </button>
            </div>
          )}
          {user && (
            <div className="hero-cta">
              <button className="btn-primary btn-lg hero-action" onClick={() => navigate('#/create')}>
                <span className="hero-action-icon">+</span> Anunciar doação
              </button>
            </div>
          )}
        </div>
      </section>

      <div className="mobile-list-heading">
        <h1>Doações</h1>
        <button type="button" onClick={() => setMobileFiltersOpen(open => !open)} aria-label="Abrir filtros">
          <img src="/figma/mobile-filter.png" alt="" />
        </button>
      </div>

      <section className={`filters-section${mobileFiltersOpen ? ' mobile-filters-open' : ''}`}>
        <div className="filters-panel">
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
          {cidades.length > 0 && (
            <div className="cidades-combo" ref={comboRef}>
              <button
                className="input cidades-combo-trigger"
                onClick={() => setComboAberta(prev => !prev)}
                aria-haspopup="listbox"
                aria-expanded={comboAberta}
                aria-label="Filtro por cidade"
              >
                {(cidadesSelecionadas.size === 0 || cidadesSelecionadas.size === cidades.length)
                  ? 'Todas as cidades'
                  : `${cidadesSelecionadas.size} cidade${cidadesSelecionadas.size > 1 ? 's' : ''} selecionada${cidadesSelecionadas.size > 1 ? 's' : ''}`}
                <span className="cidades-combo-arrow">{comboAberta ? '▲' : '▼'}</span>
              </button>
              {comboAberta && (
                <div className="cidades-combo-menu" role="listbox">
                  <div className="cidades-combo-acoes">
                    <button
                      className="btn-secondary btn-sm"
                      onClick={selecionarTodasCidades}
                      aria-label="Selecionar todas as cidades"
                    >
                      Todas
                    </button>
                    <button
                      className="btn-secondary btn-sm"
                      onClick={limparSelecaoCidades}
                      aria-label="Limpar seleção de cidades"
                    >
                      Limpar
                    </button>
                  </div>
                  <div className="cidades-opcoes">
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
            </div>
          )}
          </div>
        </div>
      </section>

      <div className="results-heading">
        <div>
          <span className="section-eyebrow">PERTO DE VOCÊ</span>
          <p className="results-count">{filtradas.length} doaç{filtradas.length !== 1 ? 'ões' : 'ão'} encontrada{filtradas.length !== 1 ? 's' : ''}</p>
        </div>
        <span className="sort-hint">Ordenadas pelas mais recentes</span>
      </div>

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
            {filtradas.map(d => (
              <DonationCard
                key={d.id}
                doacao={d}
                alimentos={alimentos.filter(alimento => alimento.doacao === d.id)}
                categorias={categorias}
                rating={(() => {
                  const donorRatings = avaliacoes.filter(avaliacao => avaliacao.avaliado === d.doador)
                  return donorRatings.length ? donorRatings.reduce((sum, avaliacao) => sum + Number(avaliacao.nota), 0) / donorRatings.length : null
                })()}
              />
            ))}
          </div>
        )
      )}
    </main>
  )
}
