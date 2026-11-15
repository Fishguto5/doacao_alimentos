import { useEffect, useState } from 'react'
import { api } from '../api'
import { navigate } from '../router'

export default function ReservationSuccess({ id }) {
  const [title, setTitle] = useState('Reserva')

  useEffect(() => {
    api.getDoacao(id).then(doacao => setTitle(doacao.titulo)).catch(() => {})
  }, [id])

  return (
    <main className="page reservation-success-page">
      <header className="mobile-detail-header">
        <button type="button" onClick={() => navigate(`#/donation/${id}`)} aria-label="Voltar à doação">
          <img src="/figma/mobile-back-reservation.png" alt="" />
        </button>
        <span>{title}</span>
      </header>
      <section className="reservation-success-card" aria-live="polite">
        <img className="reservation-checkmark" src="/figma/mobile-checkmark.png" alt="" />
        <h1>Reserva efetuada!</h1>
        <p>Aguarde confirmação do doador.</p>
        <button type="button" onClick={() => navigate('#/profile?tab=solicitacoes')}>Ver reservas</button>
      </section>
    </main>
  )
}
