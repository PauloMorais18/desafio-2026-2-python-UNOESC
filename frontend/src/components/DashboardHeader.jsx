export function DashboardHeader({ onRefresh, onBack }) {
  return <header className="dashboard-header">
    <div>
      <span className="utility-eyebrow">RF06 · ACOMPANHAMENTO</span>
      <h2>Dashboard de Estatísticas</h2>
      <p>Acompanhe o uso do assistente a partir dos registros disponíveis na API.</p>
    </div>
    <div className="dashboard-header-actions">
      <label className="period-selector">Período<select value="hoje" disabled aria-label="Período disponível"><option value="hoje">Hoje</option></select></label>
      <button type="button" onClick={onRefresh}>Atualizar</button>
      <button type="button" onClick={onBack}>Voltar ao chat</button>
    </div>
  </header>;
}
