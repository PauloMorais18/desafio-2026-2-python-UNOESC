"""Header component for the chat application."""

import streamlit as st


def render_header() -> None:
    """Render the product title and version consistently."""
    st.markdown(
        """
        <style>
          #MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
          .stApp { background: #fbfcff !important; color: #132d5b !important; font-family: "Segoe UI", Arial, sans-serif; }
          section[data-testid="stSidebar"] { min-width: 312px !important; max-width: 312px !important;
            background: #ffffff !important; border-right: 1px solid #e4e9f2; }
          [data-testid="stSidebar"] > div:first-child { padding: 1.95rem 1.65rem 1.2rem; background: #ffffff !important; }
          [data-testid="stSidebar"] [data-testid^="stBaseButton-"] { background: transparent !important;
            color: #17315e !important; border: 0 !important; text-align: left !important; border-radius: 10px !important;
            padding: 0.67rem 0.75rem !important; transition: background .16s ease, transform .16s ease !important; }
          [data-testid="stSidebar"] [data-testid^="stBaseButton-"]:hover { background: #f1f8f4 !important;
            color: #178a50 !important; transform: translateX(2px); }
          [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] { background: #34a965 !important;
            color: #ffffff !important; text-align: center !important; box-shadow: 0 6px 14px rgba(33, 149, 83, .16); }
          [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover { background: #288e53 !important; color: #ffffff !important; }
          .brand { display: flex; align-items: center; gap: 0.72rem; padding: 0.05rem 0 2.55rem; }
          .brand-mark { display: grid; place-items: center; width: 43px; height: 43px; border-radius: 50% 50% 6px 50%;
            background: linear-gradient(138deg, #39ad61 0 46%, #0e559d 47% 100%); color: white; font-size: 1.4rem; }
          .brand b { color: #0753a2; font-size: 1.14rem; letter-spacing: -0.04em; }
          .brand span, .sidebar-label { color: #7284a2; font-size: 0.73rem; }
          .sidebar-label { margin: 2.25rem 0 0.65rem; font-weight: 700; }
          .conversation-active { display: flex; align-items: center; gap: 0.75rem; color: #168c50;
            background: #edf8f1; border-radius: 10px; padding: 0.72rem 0.75rem; margin-bottom: 0.1rem; font-size: 0.88rem; }
          .block-container { max-width: 1140px; padding: 2.45rem 1.5rem 1.65rem; }
          .app-header { display: flex; align-items: center; justify-content: space-between; padding: 0 0 2.55rem; }
          .app-header h1 { margin: 0; color: #152d58; font-size: 1.68rem; font-weight: 500; letter-spacing: -0.035em; }
          .app-header h1 strong { color: #0d55a2; font-weight: 700; }
          .app-header p { margin: 0.52rem 0 0; color: #7486a5; font-size: 0.94rem; }
          .header-actions { display: flex; gap: 1.45rem; align-items: center; }
          .app-header span { color: #24925a; background: #eff9f2; border-radius: 999px; padding: 0.55rem 1rem; font-size: 0.78rem; }
          .mock-user { display: flex; align-items: center; gap: 0.65rem; color: #152d58; font-size: 0.87rem;
            padding-left: 1.45rem; border-left: 1px solid #e7ecf3; }
          .mock-avatar { width: 44px; height: 44px; display: grid; place-items: center; background: #edf4fc;
            border: 1px solid #dce7f3; border-radius: 50%; color: #6883aa; font-size: 1.35rem; }
          .info-card { display: flex; gap: 0.95rem; align-items: flex-start; background: #f7fbff; color: #114b96;
            border: 1px solid #cfe0f5; border-radius: 15px; padding: 1.25rem 1.45rem; margin-bottom: 1.1rem; }
          .info-card .info-icon { font-size: 1.65rem; line-height: 1.25; }
          .info-card p { margin: 0; font-size: 0.9rem; line-height: 1.65; }
          [data-testid="stVerticalBlockBorderWrapper"] { background: #ffffff !important; border: 1px solid #e8edf4 !important;
            border-radius: 20px !important; box-shadow: 0 7px 20px rgba(25, 59, 108, .055) !important; }
          .chat-hint { text-align: center; margin: 0.55rem 0 1.45rem; color: #8494af; font-size: 0.72rem; }
          .message-row { display: flex; gap: 0.7rem; align-items: flex-end; margin: 1.45rem 0; }
          .message-row.user { justify-content: flex-end; }
          .message-avatar { display: grid; place-items: center; width: 44px; height: 44px; flex: 0 0 44px;
            background: #eff8f2; border-radius: 50%; color: #209458; font-size: 1.2rem; }
          .message-avatar.user-avatar { background: #e9f2fb; color: #2262a3; }
          .message-bubble { max-width: min(68%, 600px); border-radius: 13px 13px 13px 4px; padding: 1rem 1.25rem 0.65rem;
            background: #eef5fc; color: #142f5c; font-size: 0.95rem; line-height: 1.65; }
          .message-row.user .message-bubble { border-radius: 13px 13px 4px 13px; background: #eef9f2; color: #173d32; }
          .message-time { display: block; margin-top: 0.45rem; color: #7d91b1; font-size: 0.69rem; }
          .attachment-icon { color: #7a8eac; font-size: 1.6rem; padding-top: 0.2rem; }
          [data-testid="stForm"] { background: #ffffff !important; border: 1px solid #d7e3f1 !important; border-radius: 15px !important;
            padding: 0.38rem 0.5rem 0.38rem 1.1rem !important; box-shadow: 0 5px 14px rgba(24, 62, 115, .08) !important; }
          [data-testid="stTextInput"], [data-testid="stTextInput"] > div, [data-baseweb="input"], [data-baseweb="base-input"] { background: transparent !important; }
          [data-testid="stTextInput"] input { border: 0 !important; box-shadow: none !important; background: transparent !important;
            color: #1a315b !important; font-size: 0.95rem !important; }
          [data-testid="stTextInput"] input::placeholder { color: #91a0b8 !important; opacity: 1; }
          [data-testid="stFormSubmitButton"] button { border-radius: 10px !important; min-height: 2.75rem; background: #0c55a4 !important;
            border-color: #0c55a4 !important; color: #ffffff !important; transition: transform .15s ease, background .15s ease; }
          [data-testid="stFormSubmitButton"] button:hover { background: #084583 !important; transform: translateY(-1px); }
          .about-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
            padding: 1.4rem 1.6rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04); }
          .about-card h3 { margin-top: 0; }
          .about-card p { color: #475569; }
        </style>
        <div class="app-header">
          <div>
            <h1>Bem-vindo ao <strong>Assistente Acadêmico</strong></h1>
            <p>Tire dúvidas utilizando a base de conhecimento da instituição.</p>
          </div>
          <div class="header-actions">
            <span>Versão 1.0</span>
            <div class="mock-user"><div class="mock-avatar">♙</div><div><b>Aluno Teste</b><br><small>Aluno</small></div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
