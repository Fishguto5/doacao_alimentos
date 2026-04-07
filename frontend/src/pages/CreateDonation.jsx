import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

const UNIDADES = ['kg', 'g', 'l', 'ml', 'unidade']
const UFS_BRASIL = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

export default function CreateDonation() {
  const { user } = useUser()
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showEstadoOptions, setShowEstadoOptions] = useState(false)
  const estadoSelectRef = useRef(null)

  const [form, setForm] = useState({
    titulo: '', descricao: '', imagem_desc_url: '',
    cep: '', cidade: user?.cidade || '', estado: user?.estado || '',
    bairro: '', estimativa_peso: '', expira_em: '',
  })

  const [alimentos, setAlimentos] = useState([
    { nome: '', categoria: '', data_validade: '', quantidade: '', unidade: 'kg' }
  ])

  const [newCategoria, setNewCategoria] = useState('')
  const [showNewCategoria, setShowNewCategoria] = useState(false)

  useEffect(() => {
    if (!user) { navigate('#/register'); return }
    api.getCategorias().then(setCategorias).catch(() => {})
  }, [user])

  useEffect(() => {
    function handleClickOutside(event) {
      if (estadoSelectRef.current && !estadoSelectRef.current.contains(event.target)) {
        setShowEstadoOptions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function updateForm(field, value) {
    setForm(f => ({ ...f, [field]: value }))
  }

  function updateAlimento(i, field, value) {
    setAlimentos(list => list.map((a, idx) => idx === i ? { ...a, [field]: value } : a))
  }

  function addAlimento() {
    setAlimentos(list => [...list, { nome: '', categoria: '', data_validade: '', quantidade: '', unidade: 'kg' }])
  }

  function removeAlimento(i) {
    setAlimentos(list => list.filter((_, idx) => idx !== i))
  }

  async function handleAddCategoria() {
    if (!newCategoria.trim()) return
    try {
      const created = await api.createCategoria({ nome: newCategoria.trim() })
      setCategorias(c => [...c, created])
      setNewCategoria('')
      setShowNewCategoria(false)
    } catch (e) {
      setError('Erro ao criar categoria: ' + e.message)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.estado) {
      setError('Selecione o estado da doação.')
      return
    }
    setLoading(true)
    try {
      const payload = {
        doador: user.id,
        receptor: null,
        status: 'disponivel',
        titulo: form.titulo,
        descricao: form.descricao,
        cep: form.cep,
        cidade: form.cidade,
        estado: form.estado,
        bairro: form.bairro,
        estimativa_peso: form.estimativa_peso || null,
      }
      if (form.imagem_desc_url) payload.imagem_desc_url = form.imagem_desc_url
      if (form.expira_em) payload.expira_em = form.expira_em

      const doacao = await api.createDoacao(payload)

      const validAlimentos = alimentos.filter(a => a.nome.trim() && a.categoria && a.quantidade)
      await Promise.all(
        validAlimentos.map(a =>
          api.createAlimento({
            doacao: doacao.id,
            categoria: Number(a.categoria),
            nome: a.nome,
            data_validade: a.data_validade || null,
            quantidade: a.quantidade,
            unidade: a.unidade,
          })
        )
      )
      navigate(`#/donation/${doacao.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!user) return null

  return (
    <main className="page page-narrow">
      <button className="back-btn" onClick={() => navigate('#/')}>← Voltar</button>
      <h1 className="page-title">Anunciar doação</h1>

      {error && <div className="error-msg">{error}</div>}

      <form onSubmit={handleSubmit} className="create-form">
        <section className="form-section">
          <h2>Informações gerais</h2>

          <div className="form-group">
            <label>Título *</label>
            <input className="input" required value={form.titulo} onChange={e => updateForm('titulo', e.target.value)} placeholder="Ex: Cesta básica, Frutas da época..." />
          </div>

          <div className="form-group">
            <label>Descrição</label>
            <textarea className="input" rows={4} value={form.descricao} onChange={e => updateForm('descricao', e.target.value)} placeholder="Descreva os alimentos, estado de conservação, etc." />
          </div>

          <div className="form-group">
            <label>URL da imagem</label>
            <input className="input" type="url" value={form.imagem_desc_url} onChange={e => updateForm('imagem_desc_url', e.target.value)} placeholder="https://..." />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Peso estimado (kg)</label>
              <input className="input" type="number" min="0" step="0.1" value={form.estimativa_peso} onChange={e => updateForm('estimativa_peso', e.target.value)} placeholder="0.0" />
            </div>
            <div className="form-group">
              <label>Expira em</label>
              <input className="input" type="datetime-local" value={form.expira_em} onChange={e => updateForm('expira_em', e.target.value)} />
            </div>
          </div>
        </section>

        <section className="form-section">
          <h2>Localização</h2>
          <div className="form-row">
            <div className="form-group">
              <label>Cidade *</label>
              <input className="input" required value={form.cidade} onChange={e => updateForm('cidade', e.target.value)} />
            </div>
            <div className="form-group form-group-uf">
              <label>Estado *</label>
              <div className={`estado-select${showEstadoOptions ? ' open' : ''}`} ref={estadoSelectRef}>
                <button
                  type="button"
                  className={`input estado-select-trigger${form.estado ? '' : ' placeholder'}`}
                  onClick={() => setShowEstadoOptions(open => !open)}
                  aria-haspopup="listbox"
                  aria-expanded={showEstadoOptions}
                >
                  <span>{form.estado || 'Selecione a UF'}</span>
                </button>
                {showEstadoOptions && (
                  <div className="estado-select-menu" role="listbox" aria-label="Selecionar estado">
                    {UFS_BRASIL.map(uf => (
                      <button
                        key={uf}
                        type="button"
                        className={`estado-option${form.estado === uf ? ' selected' : ''}`}
                        onClick={() => {
                          updateForm('estado', uf)
                          setShowEstadoOptions(false)
                        }}
                      >
                        {uf}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Bairro *</label>
              <input className="input" required value={form.bairro} onChange={e => updateForm('bairro', e.target.value)} />
            </div>
            <div className="form-group">
              <label>CEP *</label>
              <input className="input" required value={form.cep} onChange={e => updateForm('cep', e.target.value)} maxLength={8} />
            </div>
          </div>
        </section>

        <section className="form-section">
          <div className="section-header-row">
            <h2>Itens da doação</h2>
            <button type="button" className="btn-outline btn-sm" onClick={addAlimento}>+ Adicionar item</button>
          </div>

          {categorias.length === 0 && (
            <div className="info-msg">Crie uma categoria antes de adicionar itens.</div>
          )}

          {alimentos.map((a, i) => (
            <div key={i} className="alimento-form-row">
              <div className="form-row">
                <div className="form-group">
                  <label>Nome *</label>
                  <input className="input" value={a.nome} onChange={e => updateAlimento(i, 'nome', e.target.value)} placeholder="Ex: Arroz" />
                </div>
                <div className="form-group">
                  <label>Categoria</label>
                  <select className="input" value={a.categoria} onChange={e => updateAlimento(i, 'categoria', e.target.value)}>
                    <option value="">-- selecione --</option>
                    {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Quantidade *</label>
                  <input className="input" type="number" min="0" step="0.01" value={a.quantidade} onChange={e => updateAlimento(i, 'quantidade', e.target.value)} />
                </div>
                <div className="form-group form-group-sm">
                  <label>Unidade</label>
                  <select className="input" value={a.unidade} onChange={e => updateAlimento(i, 'unidade', e.target.value)}>
                    {UNIDADES.map(u => <option key={u} value={u}>{u}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Validade</label>
                  <input className="input" type="date" value={a.data_validade} onChange={e => updateAlimento(i, 'data_validade', e.target.value)} />
                </div>
                {alimentos.length > 1 && (
                  <button type="button" className="btn-remove" onClick={() => removeAlimento(i)} title="Remover item">✕</button>
                )}
              </div>
            </div>
          ))}

          <div className="categoria-add">
            {!showNewCategoria ? (
              <button type="button" className="link-btn" onClick={() => setShowNewCategoria(true)}>+ Criar nova categoria</button>
            ) : (
              <div className="form-row">
                <input className="input" value={newCategoria} onChange={e => setNewCategoria(e.target.value)} placeholder="Nome da categoria" />
                <button type="button" className="btn-outline btn-sm" onClick={handleAddCategoria}>Criar</button>
                <button type="button" className="btn-sm" onClick={() => setShowNewCategoria(false)}>✕</button>
              </div>
            )}
          </div>
        </section>

        <button className="btn-primary btn-full" type="submit" disabled={loading}>
          {loading ? 'Publicando...' : 'Publicar doação'}
        </button>
      </form>
    </main>
  )
}
