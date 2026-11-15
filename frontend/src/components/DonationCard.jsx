import { navigate } from '../router'
import { mediaUrl } from '../api'

const STATUS_LABELS = {
  disponivel: 'Disponível',
  reservada: 'Reservada',
  concluida: 'Concluída',
  expirada: 'Expirada',
  cancelada: 'Cancelada',
}

export default function DonationCard({ doacao, alimentos = [], categorias = [], rating }) {
  const VALID_STATUSES = ['disponivel', 'reservada', 'concluida', 'expirada', 'cancelada']
  const status = VALID_STATUSES.includes(doacao.status) ? doacao.status : 'disponivel'
  const statusClass = `badge badge-${status}`
  const date = new Date(doacao.data_publicacao).toLocaleDateString('pt-BR')
  const categoriaIds = [...new Set(alimentos.map(alimento => alimento.categoria))]
  const categoriaLabel = categoriaIds
    .map(id => categorias.find(categoria => categoria.id === id)?.nome)
    .filter(Boolean)
    .slice(0, 2)
    .join(' · ') || 'DOAÇÃO DE ALIMENTOS'

  return (
    <article
      className="donation-card"
      onClick={() => navigate(`#/donation/${doacao.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && navigate(`#/donation/${doacao.id}`)}
    >
      {doacao.imagem && (
        <div className="card-image">
          <img
            src={mediaUrl(doacao.imagem)}
            alt={`Imagem da doação: ${doacao.titulo}`}
            onError={e => { e.currentTarget.parentElement.style.display = 'none' }}
          />
        </div>
      )}
      <div className="card-body">
        <div className="card-header-row">
          <span className={statusClass}>{STATUS_LABELS[status] || status}</span>
          <span className="card-date">{date}</span>
        </div>
        <span className="card-category">{categoriaLabel}</span>
        <h3 className="card-title">{doacao.titulo}</h3>
        {doacao.descricao && (
          <p className="card-desc">{doacao.descricao.length > 100 ? doacao.descricao.slice(0, 100) + '…' : doacao.descricao}</p>
        )}
        <div className="card-meta">
          {doacao.cidade && (
            <span className="meta-item"><img className="desktop-pin-icon" src="/figma/pin.svg" alt="" /><img className="mobile-location-icon" src="/figma/mobile-location.png" alt="" /> {doacao.cidade}{doacao.estado ? `, ${doacao.estado}` : ''}</span>
          )}
          {rating && <span className="meta-item mobile-rating"><img src="/figma/mobile-person.png" alt="" /> {rating.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} <img className="mobile-star-icon" src="/figma/mobile-star.png" alt="" /></span>}
          {doacao.estimativa_peso && (
            <span className="meta-item"><img src="/figma/scale.svg" alt="" /> {Number(doacao.estimativa_peso).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} kg</span>
          )}
        </div>
      </div>
    </article>
  )
}
