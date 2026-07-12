import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const MOCK_RESPONSE = "Esta conversa é apenas um item ilustrativo do histórico.";

function formatTime() {
  return new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

function getApiErrorMessage(detail, fallback) {
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(" ");
  return typeof detail === "string" ? detail : fallback;
}

function App() {
  const [messages, setMessages] = useState([]);
  const [activeConversation, setActiveConversation] = useState("");
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [input, setInput] = useState("");
  const [isAnswering, setIsAnswering] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showNotice, setShowNotice] = useState(true);
  const [accessToken, setAccessToken] = useState("");
  const [studentCode, setStudentCode] = useState("");
  const [showLogin, setShowLogin] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [loginCode, setLoginCode] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [menuNotice, setMenuNotice] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileError, setProfileError] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  function startNewChat() {
    setActiveConversation("");
    setCurrentChatId(null);
    setMessages([]);
    setShowAbout(false);
    setShowHistory(false);
  }

  function selectConversation(conversation) {
    setActiveConversation(conversation.id);
    setCurrentChatId(conversation.id);
    setShowAbout(false);
    setShowHistory(false);
    setMessages(conversation.messages);
  }

  function openAuth(mode) {
    setAuthMode(mode);
    setLoginError("");
    setShowLogin(true);
  }

  async function login(event) {
    event.preventDefault();
    if (!loginCode.trim() || !loginPassword || isLoggingIn) return;
    setIsLoggingIn(true);
    setLoginError("");
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigoAluno: loginCode.trim(), senha: loginPassword }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível realizar o login."));
      setAccessToken(body.access_token);
      setStudentCode(loginCode.trim());
      setLoginPassword("");
      setShowLogin(false);
    } catch (error) {
      setLoginError(error.message || "Não foi possível realizar o login.");
    } finally {
      setIsLoggingIn(false);
    }
  }

  async function register(event) {
    event.preventDefault();
    if (!loginCode.trim() || !loginPassword || !passwordConfirmation || isLoggingIn) return;
    if (loginPassword !== passwordConfirmation) {
      setLoginError("A confirmação de senha não confere.");
      return;
    }
    setIsLoggingIn(true);
    setLoginError("");
    try {
      const response = await fetch(`${API_URL}/cadastro`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigoAluno: loginCode.trim(), senha: loginPassword, confirmacaoSenha: passwordConfirmation }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível criar sua conta."));
      setAccessToken(body.access_token);
      setStudentCode(loginCode.trim());
      setLoginPassword("");
      setPasswordConfirmation("");
      setShowLogin(false);
    } catch (error) {
      setLoginError(error.message || "Não foi possível criar sua conta.");
    } finally {
      setIsLoggingIn(false);
    }
  }

  function logout() {
    setAccessToken("");
    setStudentCode("");
    setMessages([]);
    setShowUserMenu(false);
  }

  function handleMenuAction(message) {
    setMenuNotice(message);
    setShowUserMenu(false);
  }

  async function openProfile() {
    if (!accessToken) {
      openAuth("login");
      setShowUserMenu(false);
      return;
    }
    setProfileError("");
    try {
      const response = await fetch(`${API_URL}/perfil`, { headers: { Authorization: `Bearer ${accessToken}` } });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível carregar o perfil."));
      setProfile(body);
      setShowProfile(true);
    } catch (error) {
      setProfileError(error.message || "Não foi possível carregar o perfil.");
      setShowProfile(true);
    } finally {
      setShowUserMenu(false);
    }
  }

  async function handleContextFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!accessToken) {
      openAuth("login");
      setShowUserMenu(false);
      return;
    }
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_URL}/contexto/upload`, { method: "POST", headers: { Authorization: `Bearer ${accessToken}` }, body: formData });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível enviar o contexto."));
      setMenuNotice(`Contexto enviado: ${body.arquivo}.`);
    } catch (error) {
      setMenuNotice(error.message || "Não foi possível enviar o contexto.");
    }
    setShowUserMenu(false);
  }

  async function sendMessage(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || isAnswering) return;
    if (!accessToken) {
      setLoginError("Entre com seu código e senha para enviar uma pergunta.");
      openAuth("login");
      return;
    }

    const chatId = currentChatId || Date.now();
    const userMessage = { id: Date.now(), author: "user", content: question, time: formatTime() };
    if (!currentChatId) {
      setCurrentChatId(chatId);
      setActiveConversation(chatId);
      setChatHistory((current) => [{ id: chatId, title: question, messages: [userMessage] }, ...current]);
    } else {
      setChatHistory((current) => current.map((chat) => chat.id === chatId ? { ...chat, messages: [...chat.messages, userMessage] } : chat));
    }
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsAnswering(true);
    try {
      const receivedPayload = { codigoAluno: Number.isNaN(Number(studentCode)) ? studentCode : Number(studentCode), pergunta: question };
      console.info("RF01 - JSON enviado:", receivedPayload);
      const response = await fetch(`${API_URL}/perguntar`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify(receivedPayload),
      });
      const body = await response.json();
      if (!response.ok) {
        if (response.status === 401) logout();
        throw new Error(getApiErrorMessage(body.detail, "Não foi possível enviar sua pergunta."));
      }
      console.info("RF01 - Resposta recebida:", body);
      const assistantMessage = { id: Date.now(), author: "assistant", content: body.answer, time: formatTime() };
      setMessages((current) => [...current, assistantMessage]);
      setChatHistory((current) => current.map((chat) => chat.id === chatId ? { ...chat, messages: [...chat.messages, assistantMessage] } : chat));
    } catch (error) {
      const assistantMessage = { id: Date.now(), author: "assistant", content: error.message || "Não foi possível enviar sua pergunta.", time: formatTime() };
      setMessages((current) => [...current, assistantMessage]);
      setChatHistory((current) => current.map((chat) => chat.id === chatId ? { ...chat, messages: [...chat.messages, assistantMessage] } : chat));
    } finally {
      setIsAnswering(false);
    }
  }

  return (
    <main className="application-shell">
      <aside className="sidebar">
        <div>
          <div className="brand"><div className="brand-symbol" aria-hidden="true"><span /></div><div><strong>UNOIA</strong><small>Assistente Acadêmico</small></div></div>
          <button className="new-chat-button" type="button" onClick={startNewChat}><span>＋</span> Novo Chat</button>
          <nav aria-label="Histórico de conversas">
            <p className="navigation-label">HISTÓRICO</p>
            {chatHistory.length ? chatHistory.map((conversation) => <button className={`conversation-item ${activeConversation === conversation.id ? "active" : ""}`} key={conversation.id} type="button" onClick={() => selectConversation(conversation)}><span className="chat-icon" aria-hidden="true">◯</span>{conversation.title}</button>) : <p className="empty-history">Nenhuma conversa iniciada.</p>}
          </nav>
        </div>
        <div className="sidebar-footer"><div className="footer-divider" /><p className="navigation-label">OUTRAS OPÇÕES</p><button className="sidebar-link" type="button" onClick={() => setShowAbout(true)}><span aria-hidden="true">ⓘ</span> Sobre o Assistente</button><div className="footer-divider lower" />{accessToken ? <button className="sidebar-link exit" type="button" onClick={logout}><span aria-hidden="true">⇥</span>Sair</button> : <><button className="sidebar-link exit" type="button" onClick={() => openAuth("login")}><span aria-hidden="true">⇥</span>Entrar</button><button className="sidebar-link" type="button" onClick={() => openAuth("register")}><span aria-hidden="true">＋</span>Criar conta</button></>}</div>
      </aside>

      <section className="content">
        <header className="topbar"><div><h1>Bem-vindo ao <strong>Assistente Acadêmico</strong></h1><p>Tire dúvidas utilizando a base de conhecimento da instituição.</p></div><div className="account-actions"><span className="version">Versão 1.0</span>{accessToken ? <button className="account" type="button" onClick={logout}><div className="profile-avatar" aria-hidden="true">♙</div><div className="profile-copy"><strong>Aluno {studentCode}</strong><span>Clique para sair</span></div></button> : <><button className="auth-action" type="button" onClick={() => openAuth("login")}>Entrar</button><button className="auth-action primary" type="button" onClick={() => openAuth("register")}>Criar conta</button></>}<button className="hamburger-button" type="button" aria-label="Abrir menu" aria-expanded={showUserMenu} onClick={() => setShowUserMenu(!showUserMenu)}><span /><span /><span /></button></div></header>

        {showUserMenu && <aside className="cascade-menu" aria-label="Menu do usuário"><button className="cascade-item" type="button" onClick={openProfile}><span>◉</span>Perfil</button><button className="cascade-item" type="button" onClick={() => { setShowHistory(true); setShowUserMenu(false); }}><span>◷</span>Histórico de chats</button><label className="cascade-item upload-context"><span>⇧</span>Upload contexto<input type="file" accept=".pdf,.txt,.doc,.docx,.md" onChange={handleContextFile} /></label><button className="cascade-item" type="button" onClick={() => { setShowSettings(true); setShowUserMenu(false); }}><span>⚙</span>Configurações</button></aside>}
        {menuNotice && <p className="menu-notice" role="status">{menuNotice}</p>}

        {showProfile && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowProfile(false)}><section className="modal-card" role="dialog" aria-modal="true" aria-label="Perfil do usuário" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setShowProfile(false)}>×</button><h2>Perfil</h2>{profile ? <dl className="profile-details"><div><dt>Código do aluno</dt><dd>{profile.codigoAluno}</dd></div><div><dt>Nome</dt><dd>{profile.nome}</dd></div><div><dt>E-mail</dt><dd>{profile.email || "Não informado"}</dd></div><div><dt>Status</dt><dd>{profile.ativo ? "Ativo" : "Inativo"}</dd></div><div><dt>Cadastro</dt><dd>{new Date(profile.datahoracad).toLocaleDateString("pt-BR")}</dd></div></dl> : <p>{profileError || "Carregando perfil..."}</p>}</section></div>}
        {showSettings && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowSettings(false)}><section className="modal-card settings-modal" role="dialog" aria-modal="true" aria-label="Configurações" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setShowSettings(false)}>×</button><h2>Configurações gerais</h2><label className="setting-option"><span>Notificações do assistente</span><input type="checkbox" checked={notificationsEnabled} onChange={(event) => setNotificationsEnabled(event.target.checked)} /></label><p>As configurações desta tela são aplicadas apenas durante a sessão atual.</p></section></div>}

        {showHistory ? <section className="history-screen"><div className="history-screen-header"><div><h2>Histórico de chats</h2><p>Cada card é identificado pela primeira mensagem enviada.</p></div><button type="button" onClick={() => setShowHistory(false)}>Voltar ao chat</button></div>{chatHistory.length ? <div className="history-cards">{chatHistory.map((chat) => <button type="button" className="history-card" key={chat.id} onClick={() => selectConversation(chat)}><span>Chat</span><strong>{chat.title}</strong><small>{chat.messages.length} mensagem(ns)</small></button>)}</div> : <div className="history-empty"><h3>Nenhuma conversa ainda</h3><p>Envie sua primeira pergunta para criar um chat.</p></div>}</section> : showAbout ? <section className="about-card"><span className="about-icon">ⓘ</span><div><h2>Sobre o UNOIA</h2><p>Protótipo de assistente acadêmico para orientar alunos usando a base de conhecimento institucional.</p><p><strong>Versão:</strong> 1.0 · <strong>Tecnologias:</strong> React, FastAPI e PostgreSQL.</p></div></section> : <>
          {showNotice && <section className="information-card"><span className="information-icon" aria-hidden="true">ⓘ</span><div><p>O assistente responde apenas perguntas presentes na base de conhecimento cadastrada pela instituição.</p><p>Caso não encontre informações suficientes, ele informará isso ao usuário.</p></div><button type="button" aria-label="Fechar aviso" className="close-notice" onClick={() => setShowNotice(false)}>×</button></section>}
          {showLogin && <section className="login-card" aria-label={authMode === "login" ? "Login do aluno" : "Cadastro do aluno"}><div><h2>{authMode === "login" ? "Acesse sua conta" : "Crie sua conta"}</h2><p>{authMode === "login" ? "Entre com seu código de aluno e senha para enviar perguntas." : "Use seu código de aluno e defina uma senha com pelo menos 8 caracteres."}</p><button className="auth-switch" type="button" onClick={() => { setAuthMode(authMode === "login" ? "register" : "login"); setLoginError(""); }}>{authMode === "login" ? "Ainda não possui conta? Criar agora" : "Já possui conta? Entrar"}</button></div><form onSubmit={authMode === "login" ? login : register}><input value={loginCode} onChange={(event) => setLoginCode(event.target.value)} placeholder="Código do aluno" aria-label="Código do aluno" /><div className="password-field"><input value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} type={showPassword ? "text" : "password"} minLength="8" placeholder="Senha" aria-label="Senha" /><button type="button" className="toggle-password" onClick={() => setShowPassword(!showPassword)}>{showPassword ? "Ocultar" : "Ver"}</button></div>{authMode === "register" && <input value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} type={showPassword ? "text" : "password"} minLength="8" placeholder="Confirme sua senha" aria-label="Confirme sua senha" />}<button type="submit" disabled={isLoggingIn}>{isLoggingIn ? "Aguarde..." : authMode === "login" ? "Entrar" : "Criar conta"}</button></form>{loginError && <p className="login-error" role="alert">{loginError}</p>}</section>}
          <section className={`chat-experience ${messages.length ? "has-messages" : "is-empty"}`} aria-label="Conversa atual">
            {messages.length ? <div className="chat-card"><div className="messages">{messages.map((message) => <MessageBubble key={message.id} message={message} />)}{isAnswering && <div className="typing-indicator">O assistente está preparando uma resposta...</div>}</div></div> : <div className="empty-chat-intro"><span className="intro-symbol" aria-hidden="true">◢</span><h2>Como posso ajudar?</h2><p>{accessToken ? "Envie uma dúvida para iniciar a conversa." : "Faça login para enviar uma dúvida acadêmica."}</p></div>}
            <div className="composer-wrapper">{messages.length > 0 && <p className="response-note">As respostas podem levar alguns segundos para serem geradas.</p>}<form className="message-composer" onSubmit={sendMessage}><span className="attachment" aria-hidden="true">⌇</span><input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Digite sua dúvida acadêmica..." aria-label="Digite sua dúvida acadêmica" /><button type="submit" disabled={isAnswering}><span aria-hidden="true">⌁</span> Enviar</button></form></div>
          </section>
        </>}
      </section>
    </main>
  );
}

function MessageBubble({ message }) {
  const isUser = message.author === "user";
  return <article className={`message-row ${isUser ? "user-message" : "assistant-message"}`}>{!isUser && <div className="message-avatar assistant-avatar" aria-hidden="true">◢</div>}<div className="bubble">{message.content.split("\n").map((line) => <p key={line}>{line}</p>)}<time>{message.time}{isUser && "  ✓✓"}</time></div>{isUser && <div className="message-avatar user-avatar" aria-hidden="true">◉</div>}</article>;
}

export default App;
