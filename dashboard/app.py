"""Mocked Streamlit dashboard prototype for the academic assistant."""

import streamlit as st

from components.header import render_header
from components.stat_card import render_stat_card

HOUR_DATA: dict[str, list[int]] = {
    "Perguntas": [4, 7, 10, 13, 9, 15, 11, 6],
}
STUDENT_DATA: list[dict[str, str | int]] = [
    {"aluno": "Ana Souza", "perguntas": 12},
    {"aluno": "Bruno Lima", "perguntas": 9},
    {"aluno": "Carla Mendes", "perguntas": 7},
    {"aluno": "Diego Alves", "perguntas": 5},
]
LATEST_QUESTIONS: list[dict[str, str]] = [
    {"Aluno": "Ana Souza", "Pergunta": "Como acesso o calendário acadêmico?", "Data": "Hoje, 14:25", "Tempo": "1,2 s"},
    {"Aluno": "Bruno Lima", "Pergunta": "Onde encontro os horários das aulas?", "Data": "Hoje, 13:48", "Tempo": "0,9 s"},
    {"Aluno": "Carla Mendes", "Pergunta": "Como solicito segunda chamada?", "Data": "Hoje, 11:10", "Tempo": "1,4 s"},
    {"Aluno": "Diego Alves", "Pergunta": "Qual o prazo para rematrícula?", "Data": "Hoje, 09:32", "Tempo": "1,1 s"},
]


def render_student_chart() -> None:
    """Render a horizontal mocked chart using Streamlit's Vega-Lite support."""
    st.vega_lite_chart(
        data=STUDENT_DATA,
        spec={
            "mark": {"type": "bar", "cornerRadiusEnd": 5},
            "encoding": {
                "x": {"field": "perguntas", "type": "quantitative", "title": "Perguntas"},
                "y": {"field": "aluno", "type": "nominal", "sort": "-x", "title": None},
                "color": {"value": "#2563eb"},
                "tooltip": [
                    {"field": "aluno", "type": "nominal", "title": "Aluno"},
                    {"field": "perguntas", "type": "quantitative", "title": "Perguntas"},
                ],
            },
        },
        use_container_width=True,
    )


def main() -> None:
    """Render a visual-only administrative dashboard with mock data."""
    st.set_page_config(page_title="Dashboard | Assistente Acadêmico", page_icon="📊", layout="wide")
    render_header()

    cards = st.columns(4)
    with cards[0]:
        render_stat_card("Perguntas hoje", "75", "↑ 12% em relação a ontem")
    with cards[1]:
        render_stat_card("Alunos atendidos", "42", "Hoje")
    with cards[2]:
        render_stat_card("Tempo médio", "1,2 s", "Resposta simulada")
    with cards[3]:
        render_stat_card("Sem resposta", "6", "8% das perguntas")

    st.markdown("### Perguntas por hora")
    st.bar_chart(HOUR_DATA, color="#2563eb", use_container_width=True)

    st.markdown("### Perguntas por aluno")
    render_student_chart()

    st.markdown("### Últimas perguntas")
    st.dataframe(LATEST_QUESTIONS, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
