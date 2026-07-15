export function DashboardHeader({ period, onPeriodChange, onRefresh, onBack }) {
  return <header className="dashboard-header">
    <div>
      <span className="utility-eyebrow">RF06 · ACOMPANHAMENTO</span>
      <h2>Dashboard de Estatísticas</h2>
      <p>Acompanhe o uso do assistente a partir dos registros armazenados no banco de dados.</p>
    </div>
    <div className="dashboard-header-actions">
      <label className="period-selector">Período<select value={period} onChange={(event) => onPeriodChange(event.target.value)} aria-label="Período das estatísticas"><option value="hoje">Hoje</option><option value="7dias">Últimos 7 dias</option><option value="30dias">Últimos 30 dias</option><option value="tudo">Todo o período</option></select></label>
      <button type="button" onClick={onRefresh}>Atualizar</button>
      <button type="button" onClick={onBack}>Voltar ao chat</button>
    </div>
  </header>;
}
