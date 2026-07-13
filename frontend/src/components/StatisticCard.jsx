export function StatisticCard({ icon, title, value, detail, tone = "blue" }) {
  return <article className={`dashboard-stat-card tone-${tone}`}>
    <div className="stat-icon" aria-hidden="true">{icon}</div>
    <div>
      <span>{title}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  </article>;
}
