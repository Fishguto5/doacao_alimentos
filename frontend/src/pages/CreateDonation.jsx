import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import { useUser } from '../context/UserContext'
import { navigate } from '../router'

const UNIDADES = ['kg', 'g', 'l', 'ml', 'unidade']
const UFS_BRASIL = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

function isoToDisplay(iso) {
  if (!iso) return ''
  const parts = iso.split('-')
  if (parts.length !== 3) return iso
  const [year, month, day] = parts
  return `${day}/${month}/${year}`
}

function displayToIso(display) {
  if (!display || display.length !== 10) return ''
  const parts = display.split('/')
  if (parts.length !== 3) return ''
  const [day, month, year] = parts
  return `${year}-${month}-${day}`
}

function formatDateInput(raw) {
  const digits = raw.replace(/\D/g, '').slice(0, 8)
  if (digits.length <= 2) return digits
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`
}

export default function CreateDonation() {
  const { user } = useUser()
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showEstadoOptions, setShowEstadoOptions] = useState(false)
  const estadoSelectRef = useRef(null)
  const [imagem, setImagem] = useState(null)
  const [imagemPreview, setImagemPreview] = useState(null)

  const [form, setForm] = useState({
    titulo: '', descricao: '',
    cep: '', cidade: user?.cidade || '', estado: user?.estado || '',
    bairro: '', logradouro: '', numero: '', complemento: '', estimativa_peso: '',
  })

  const [alimentos, setAlimentos] = useState([
    { nome: '', categoria: '', data_validade: '', quantidade: '', unidade: 'kg' }
  ])

  const [newCategoria, setNewCategoria] = useState('')
  const [showNewCategoria, setShowNewCategoria] = useState(false)

  const expiracaoCalculada = alimentos
    .map(a => a.data_validade ? displayToIso(a.data_validade) : '')
    .filter(Boolean)
    .sort()[0] || ''

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

  function handleImagemChange(e) {
    const file = e.target.files?.[0]
    if (file) {
      setImagem(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setImagemPreview(event.target?.result)
      }
      reader.readAsDataURL(file)
    }
  }

  function removeImagem() {
    setImagem(null)
    setImagemPreview(null)
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

    // Validação básica dos campos obrigatórios
    if (!form.titulo.trim()) return setError('O título da doação é obrigatório.')
    if (!form.cidade.trim()) return setError('A cidade é obrigatória.')
    if (!form.estado) return setError('Selecione o estado da doação.')
    if (!form.bairro.trim()) return setError('O bairro é obrigatório.')
    if (!form.cep.trim() || form.cep.trim().length !== 8) return setError('O CEP é obrigatório e deve ter 8 dígitos.')
    if (!form.logradouro.trim()) return setError('O logradouro é obrigatório.')
    if (!form.numero.trim()) return setError('O número é obrigatório.')

    // Validação do tamanho da imagem (máximo 5MB)
    if (imagem && imagem.size > 5 * 1024 * 1024) {
      return setError('A imagem excede o tamanho máximo de 5MB.')
    }

    // Validação dos alimentos
    const validAlimentos = alimentos.filter(a => a.nome.trim() && a.categoria && a.quantidade && Number(a.quantidade) > 0)
    if (validAlimentos.length === 0) {
      return setError('Adicione pelo menos um item (alimento) válido com nome, categoria e quantidade maior que zero.')
    }


    setLoading(true)
    try {
      const payload = new FormData()
      payload.append('doador', user.id)
      payload.append('status', 'disponivel')
      payload.append('titulo', form.titulo)
      payload.append('descricao', form.descricao)
      payload.append('cep', form.cep)
      payload.append('cidade', form.cidade)
      payload.append('estado', form.estado)
      payload.append('bairro', form.bairro)
      payload.append('logradouro', form.logradouro)
      payload.append('numero', form.numero)
      payload.append('complemento', form.complemento)
      payload.append('estimativa_peso', form.estimativa_peso || '')
      if (imagem) {
        payload.append('imagem', imagem)
      }

      const doacao = await api.createDoacao(payload)

      try {
        await Promise.all(
          validAlimentos.map(a =>
            api.createAlimento({
              doacao: doacao.id,
              categoria: Number(a.categoria),
              nome: a.nome,
              data_validade: a.data_validade ? displayToIso(a.data_validade) : null,
              quantidade: a.quantidade,
              unidade: a.unidade,
            })
          )
        )
        navigate(`#/donation/${doacao.id}`)
      } catch (alimentoErr) {
        console.error('Falha ao criar os alimentos:', alimentoErr)
        // Se falhar ao criar os alimentos, tenta deletar a doação criada para não deixar órfã
        try {
           await api.deleteDoacao(doacao.id)
        } catch (delErr) {
           console.error('Falha ao reverter a doação:', delErr)
        }
        throw new Error('Falha ao adicionar os itens à doação. A operação foi cancelada.')
      }
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
            <label>Descrição *</label>
            <textarea className="input" rows={4} required value={form.descricao} onChange={e => updateForm('descricao', e.target.value)} placeholder="Descreva os alimentos, estado de conservação, etc." />
          </div>

          <div className="form-group">
            <label>Imagem da doação</label>
            {imagemPreview ? (
              <div className="imagem-preview">
                <img src={imagemPreview} alt="Preview da imagem" style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }} />
                <button type="button" className="btn-remove" onClick={removeImagem} style={{ marginTop: '8px' }}>Remover imagem</button>
              </div>
            ) : (
              <input
                className="input"
                type="file"
                accept="image/*"
                onChange={handleImagemChange}
                placeholder="Selecione uma imagem"
              />
            )}
            <small>Máximo 5MB. Formatos aceitos: JPG, PNG, GIF, WebP</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Peso estimado (kg)</label>
              <input className="input" type="number" min="0" step="0.1" value={form.estimativa_peso} onChange={e => updateForm('estimativa_peso', e.target.value)} placeholder="0.0" />
            </div>
            <div className="form-group">
              <label>Data de vencimento da doação</label>
              <input className="input" type="text" value={isoToDisplay(expiracaoCalculada)} readOnly />
              <small>Definida automaticamente pela menor validade dos itens.</small>
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
              <input 
                className="input" 
                required 
                minLength={8} 
                maxLength={8} 
                pattern="\d{8}" 
                title="O CEP deve conter exatamente 8 dígitos" 
                value={form.cep} 
                onChange={e => updateForm('cep', e.target.value.replace(/\D/g, ''))} 
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Logradouro *</label>
              <input className="input" required value={form.logradouro} onChange={e => updateForm('logradouro', e.target.value)} />
            </div>
            <div className="form-group form-group-sm">
              <label>Número *</label>
              <input className="input" required value={form.numero} onChange={e => updateForm('numero', e.target.value)} />
            </div>
          </div>
          <div className="form-group">
            <label>Complemento</label>
            <input className="input" value={form.complemento} onChange={e => updateForm('complemento', e.target.value)} />
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
                  <input className="input" required value={a.nome} onChange={e => updateAlimento(i, 'nome', e.target.value)} placeholder="Ex: Arroz" />
                </div>
                <div className="form-group">
                  <label>Categoria *</label>
                  <select className="input" required value={a.categoria} onChange={e => updateAlimento(i, 'categoria', e.target.value)}>
                    <option value="">-- selecione --</option>
                    {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Quantidade *</label>
                  <input className="input" type="number" required min="0" step="0.01" value={a.quantidade} onChange={e => updateAlimento(i, 'quantidade', e.target.value)} />
                </div>
                <div className="form-group form-group-sm">
                  <label>Unidade *</label>
                  <select className="input" required value={a.unidade} onChange={e => updateAlimento(i, 'unidade', e.target.value)}>
                    {UNIDADES.map(u => <option key={u} value={u}>{u}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Validade *</label>
                  <input
                    className="input"
                    type="text"
                    required
                    pattern="^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$"
                    title="Informe uma data válida no formato dd/mm/aaaa"
                    placeholder="dd/mm/aaaa"
                    maxLength={10}
                    value={a.data_validade}
                    onChange={e => {
                      const val = formatDateInput(e.target.value)
                      updateAlimento(i, 'data_validade', val)
                      
                      e.target.setCustomValidity('')
                      if (val.length === 10) {
                        const parts = val.split('/')
                        if (parts.length === 3) {
                          const [day, month, year] = parts.map(Number)
                          const date = new Date(year, month - 1, day)
                          if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
                            e.target.setCustomValidity('Esta data não existe no calendário.')
                          } else {
                            const today = new Date()
                            today.setHours(0, 0, 0, 0)
                            if (date < today) {
                              e.target.setCustomValidity('Esta data já expirou.')
                            }
                          }
                        }
                      }
                    }}
                    onInvalid={e => {
                      if (e.target.validity.valueMissing) {
                        e.target.setCustomValidity('Preencha a data de validade.')
                      } else if (e.target.validity.patternMismatch) {
                        e.target.setCustomValidity('Informe uma data válida no formato dd/mm/aaaa.')
                      }
                    }}
                  />
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
