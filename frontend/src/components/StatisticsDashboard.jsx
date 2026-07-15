import { useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartCard } from "./ChartCard";
import { DashboardHeader } from "./DashboardHeader";
import { StatisticCard } from "./StatisticCard";

const COLORS = ["#0d55a2", "#32a966"];

export function StatisticsDashboard({ statistics, loading, error, onBack, onRefresh }) {
  const [activeShortcut, setActiveShortcut] = useState("geral");
  const summary = statistics?.summary || {};
  const daily = statistics?.daily || {};
  const unresolved = statistics?.unresolved || {};
  const students = (statistics?.byStudent?.alunos || []).slice(0, 10);
  const totalToday = daily.totalPerguntas || 0;
  const unansweredToday = unresolved.totalSemRespostaOuErro || 0;
  const answeredToday = Math.max(0, totalToday - unansweredToday);
  const successRate = totalToday ? Math.round((answeredToday / totalToday) * 100) : 0;
  const responseTime = Math.round(statistics?.average?.tempoMedioRespostaMs ?? 0);
  const dailySeries = daily.data ? [{ data: daily.data, perguntas: totalToday }] : [];
  const successData = [
    { name: "Respondidas", value: answeredToday },
    { name: "Sem resposta/erro", value: unansweredToday },
  ];
  const shortcuts = [
    ["geral", "Visão geral"],
    ["perguntas", "Perguntas"],
    ["qualidade", "Qualidade"],
    ["desempenho", "Desempenho"],
  ];

  return <section className="utility-screen dashboard-screen" aria-label="Dashboard de estatísticas">
    <DashboardHeader onRefresh={onRefresh} onBack={onBack} />
    <nav className="dashboard-quick-menu" aria-label="Menu rápido do dashboard">
      {shortcuts.map(([id, label]) => <button className={activeShortcut === id ? "active" : ""} key={id} type="button" onClick={() => setActiveShortcut(id)}>{label}</button>)}
    </nav>
    {loading ? <div className="utility-empty">Atualizando os indicadores...</div> : error ? <div className="utility-empty utility-error">{error}</div> : <div className="dashboard-scroll">
      {activeShortcut === "geral" && <>
        <div className="dashboard-metric-grid">
          <StatisticCard icon="◫" title="Total de perguntas" value={summary.total_questions ?? 0} detail="Todos os registros armazenados" tone="blue" />
          <StatisticCard icon="✓" title="Perguntas respondidas" value={summary.answered_questions ?? 0} detail="Respostas registradas no banco" tone="green" />
          <StatisticCard icon="!" title="Sem resposta ou erro" value={unansweredToday} detail="Ocorrências registradas hoje" tone="orange" />
          <StatisticCard icon="◷" title="Tempo médio" value={`${responseTime} ms`} detail="Processamento das respostas" tone="teal" />
        </div>
        <div className="dashboard-chart-grid dashboard-chart-grid-two">
          <ChartCard title="Perguntas realizadas hoje" description="Volume de perguntas recebido no dia atual.">
            <ResponsiveContainer width="100%" height={240}><LineChart data={dailySeries}><XAxis dataKey="data" tick={{ fontSize: 11 }} /><YAxis allowDecimals={false} tick={{ fontSize: 11 }} /><Tooltip /><Legend /><Line type="monotone" dataKey="perguntas" name="Perguntas" stroke="#0d55a2" strokeWidth={3} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Taxa de sucesso hoje" description="Relação entre perguntas respondidas e registros sem resposta ou com erro.">
            <div className="success-chart"><ResponsiveContainer width="100%" height={200}><PieChart><Pie data={successData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={82} paddingAngle={3}>{successData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer><strong>{successRate}%</strong><span>sucesso hoje</span></div>
          </ChartCard>
        </div>
      </>}

      {activeShortcut === "perguntas" && <>
        <div className="dashboard-metric-grid dashboard-metric-grid-full"><StatisticCard icon="◫" title="Perguntas hoje" value={totalToday} detail={daily.data || "Data atual"} tone="blue" /></div>
        <div className="dashboard-chart-grid dashboard-chart-grid-two">
          <ChartCard title="Perguntas por dia" description="Registros do período armazenados no banco."><ResponsiveContainer width="100%" height={270}><LineChart data={dailySeries}><XAxis dataKey="data" tick={{ fontSize: 11 }} /><YAxis allowDecimals={false} tick={{ fontSize: 11 }} /><Tooltip /><Legend /><Line type="monotone" dataKey="perguntas" name="Perguntas" stroke="#0d55a2" strokeWidth={3} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer></ChartCard>
          <ChartCard title="Perguntas por aluno" description="Top 10 alunos por quantidade de perguntas."><ResponsiveContainer width="100%" height={270}><BarChart data={students} layout="vertical" margin={{ left: 8 }}><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="codigoAluno" width={68} tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="totalPerguntas" name="Perguntas" fill="#0d55a2" radius={[0, 6, 6, 0]} /></BarChart></ResponsiveContainer></ChartCard>
        </div>
      </>}

      {activeShortcut === "qualidade" && <>
        <div className="dashboard-metric-grid dashboard-metric-grid-compact"><StatisticCard icon="!" title="Sem resposta ou erro hoje" value={unansweredToday} detail="Registros que requerem acompanhamento" tone="orange" /><StatisticCard icon="✓" title="Respondidas hoje" value={answeredToday} detail="Perguntas concluídas no período" tone="green" /></div>
        <div className="dashboard-chart-grid dashboard-chart-grid-single"><ChartCard title="Taxa de sucesso" description="Indicador calculado com as informações do dia atual."><div className="success-chart success-chart-large"><ResponsiveContainer width="100%" height={260}><PieChart><Pie data={successData} dataKey="value" nameKey="name" innerRadius={80} outerRadius={108} paddingAngle={3}>{successData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer><strong>{successRate}%</strong><span>sucesso hoje</span></div></ChartCard></div>
      </>}

      {activeShortcut === "desempenho" && <>
        <div className="dashboard-metric-grid dashboard-metric-grid-full"><StatisticCard icon="◷" title="Tempo médio de resposta" value={`${responseTime} ms`} detail="Todas as respostas armazenadas" tone="teal" /></div>
        <div className="dashboard-chart-grid dashboard-chart-grid-single"><ChartCard title="Tempo médio de resposta" description="Média calculada a partir dos registros do banco."><div className="response-time-chart"><span>0 ms</span><div><i style={{ width: `${Math.min(100, Math.max(2, responseTime / 10))}%` }} /></div><span>1.000 ms</span><strong>{responseTime} ms</strong><small>Referência visual: até 1 segundo.</small></div></ChartCard></div>
      </>}
    </div>}
  </section>;
}
