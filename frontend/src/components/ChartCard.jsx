export function ChartCard({ title, description, children, className = "" }) {
  return <section className={`dashboard-chart-card ${className}`}>
    <header><h3>{title}</h3><p>{description}</p></header>
    <div className="dashboard-chart-content">{children}</div>
  </section>;
}
