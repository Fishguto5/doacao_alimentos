import { navigate } from '../router'

const STATUS_LABELS = {
  disponivel: 'Disponível',
  reservada: 'Reservada',
  concluida: 'Concluída',
  expirada: 'Expirada',
  cancelada: 'Cancelada',
}

export default function DonationCard({ doacao }) {
  const statusClass = `badge badge-${doacao.status}`
  const date = new Date(doacao.data_publicacao).toLocaleDateString('pt-BR')

  return (
    <article
      className="donation-card"
      onClick={() => navigate(`#/donation/${doacao.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && navigate(`#/donation/${doacao.id}`)}
    >
      {doacao.imagem_desc_url && (
        <div className="card-image">
          <img
            src={doacao.imagem_desc_url}
            alt={doacao.titulo}
            onError={e => { e.target.style.display = 'none' }}
          />
        </div>
      )}
      <div className="card-body">
        <div className="card-header-row">
          <span className={statusClass}>{STATUS_LABELS[doacao.status] || doacao.status}</span>
          <span className="card-date">{date}</span>
        </div>
        <h3 className="card-title">{doacao.titulo}</h3>
        {doacao.descricao && (
          <p className="card-desc">{doacao.descricao.length > 100 ? doacao.descricao.slice(0, 100) + '…' : doacao.descricao}</p>
        )}
        <div className="card-meta">
          {doacao.cidade && (
            <span className="meta-item">📍 {doacao.cidade}{doacao.estado ? `, ${doacao.estado}` : ''}</span>
          )}
          {doacao.estimativa_peso && (
            <span className="meta-item">⚖️ {doacao.estimativa_peso} kg</span>
          )}
        </div>
      </div>
    </article>
  )
}
