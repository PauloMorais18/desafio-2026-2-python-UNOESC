import { useState } from "react";
import { StatisticsDashboard } from "./components/StatisticsDashboard";

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
  const [showProfile, setShowProfile] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileError, setProfileError] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [searchMode, setSearchMode] = useState(() => window.localStorage.getItem("unoia_search_mode") || "like");
  const [showDocuments, setShowDocuments] = useState(false);
  const [documents, setDocuments] = useState(null);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [showStatistics, setShowStatistics] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [statisticsError, setStatisticsError] = useState("");
  const [statisticsLoading, setStatisticsLoading] = useState(false);
  const [showDocumentation, setShowDocumentation] = useState(false);
  const [apiDocumentation, setApiDocumentation] = useState(null);
  const [documentationLoading, setDocumentationLoading] = useState(false);
  const [documentationError, setDocumentationError] = useState("");

  function startNewChat() {
    setActiveConversation("");
    setCurrentChatId(null);
    setMessages([]);
    setShowAbout(false);
    setShowHistory(false);
    setShowStatistics(false);
    setShowDocumentation(false);
  }

  async function selectConversation(conversation) {
    setActiveConversation(conversation.id);
    setCurrentChatId(conversation.id);
    setShowAbout(false);
    setShowHistory(false);
    if (conversation.messages?.length) {
      setMessages(conversation.messages);
      return;
    }
    try {
      const response = await fetch(`${API_URL}/conversas/${encodeURIComponent(conversation.id)}/historico`, { headers: { Authorization: `Bearer ${accessToken}` } });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível carregar a conversa."));
      const loadedMessages = body.map((message) => ({ id: message.chave, author: message.tipo === 1 ? "user" : "assistant", content: message.conteudo, time: new Date(message.data).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) }));
      setMessages(loadedMessages);
      setChatHistory((current) => current.map((chat) => chat.id === conversation.id ? { ...chat, messages: loadedMessages } : chat));
    } catch (error) {
      setMessages([]);
      setLoginError(error.message || "Não foi possível carregar a conversa.");
    }
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

  function changeSearchMode(mode) {
    setSearchMode(mode);
    window.localStorage.setItem("unoia_search_mode", mode);
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
      setDocumentsError("");
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_URL}/contexto/upload`, { method: "POST", headers: { Authorization: `Bearer ${accessToken}` }, body: formData });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível enviar o contexto."));
      await loadDocuments(true);
    } catch (error) {
      setDocumentsError(error.message || "Não foi possível enviar o contexto.");
    } finally {
      event.target.value = "";
    }
    setShowUserMenu(false);
  }

  async function loadDocuments(force = false) {
    if (!accessToken) {
      openAuth("login");
      return;
    }
    if (documents && !force) return;
    setDocumentsLoading(true);
    setDocumentsError("");
    try {
      const response = await fetch(`${API_URL}/contexto/documentos`, { headers: { Authorization: `Bearer ${accessToken}` } });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível listar os documentos."));
      setDocuments(body.documentos);
    } catch (error) {
      setDocumentsError(error.message || "Não foi possível listar os documentos.");
    } finally {
      setDocumentsLoading(false);
    }
  }

  function openDocuments() {
    setShowUserMenu(false);
    setShowStatistics(false);
    setShowDocumentation(false);
    setShowDocuments(true);
    loadDocuments();
  }

  async function openStatistics() {
    setShowUserMenu(false);
    setShowDocuments(false);
    setShowHistory(false);
    setShowAbout(false);
    setShowDocumentation(false);
    setShowStatistics(true);
    setStatisticsLoading(true);
    setStatisticsError("");
    try {
      const responses = await Promise.all([
        fetch(`${API_URL}/estatisticas`),
        fetch(`${API_URL}/estatisticas/perguntas-do-dia`),
        fetch(`${API_URL}/estatisticas/perguntas-por-aluno`),
        fetch(`${API_URL}/estatisticas/sem-resposta-ou-erro-do-dia`),
        fetch(`${API_URL}/estatisticas/tempo-medio-resposta`),
      ]);
      const bodies = await Promise.all(responses.map((response) => response.json()));
      const failedIndex = responses.findIndex((response) => !response.ok);
      if (failedIndex >= 0) throw new Error(getApiErrorMessage(bodies[failedIndex].detail, "Não foi possível carregar as estatísticas."));
      setStatistics({ summary: bodies[0], daily: bodies[1], byStudent: bodies[2], unresolved: bodies[3], average: bodies[4] });
    } catch (error) {
      setStatisticsError(error.message || "Não foi possível carregar as estatísticas.");
    } finally {
      setStatisticsLoading(false);
    }
  }

  async function openDocumentation() {
    setShowUserMenu(false);
    setShowDocuments(false);
    setShowHistory(false);
    setShowAbout(false);
    setShowStatistics(false);
    setShowDocumentation(true);
    setDocumentationLoading(true);
    setDocumentationError("");
    try {
      const response = await fetch(`${API_URL}/openapi.json`);
      const body = await response.json();
      if (!response.ok) throw new Error("Não foi possível carregar a documentação da API.");
      setApiDocumentation(body);
    } catch (error) {
      setDocumentationError(error.message || "Não foi possível carregar a documentação da API.");
    } finally {
      setDocumentationLoading(false);
    }
  }

  async function openHistory() {
    if (!accessToken) {
      openAuth("login");
      setShowUserMenu(false);
      return;
    }
    try {
      const response = await fetch(`${API_URL}/conversas`, { headers: { Authorization: `Bearer ${accessToken}` } });
      const body = await response.json();
      if (!response.ok) throw new Error(getApiErrorMessage(body.detail, "Não foi possível carregar o histórico."));
      setChatHistory((current) => body.map((conversation) => {
        const existing = current.find((chat) => chat.id === conversation.chaveConversa);
        return { id: conversation.chaveConversa, title: conversation.title, messages: existing?.messages || [] };
      }));
      setShowHistory(true);
    } catch (error) {
      setLoginError(error.message || "Não foi possível carregar o histórico.");
    } finally {
      setShowUserMenu(false);
    }
  }

  async function viewDocument(contextDocument) {
    try {
      const response = await fetch(`${API_URL}/contexto/documentos/${encodeURIComponent(contextDocument.id)}`, { headers: { Authorization: `Bearer ${accessToken}` } });
      if (!response.ok) throw new Error("Não foi possível abrir o documento.");
      const url = URL.createObjectURL(await response.blob());
      const link = window.document.createElement("a");
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener";
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch (error) {
      setDocumentsError(error.message || "Não foi possível abrir o documento.");
    }
  }

  async function deleteDocument(documentToDelete) {
    if (!window.confirm(`Excluir o documento "${documentToDelete.nome}"?`)) return;
    try {
      const response = await fetch(`${API_URL}/contexto/documentos/${encodeURIComponent(documentToDelete.id)}`, { method: "DELETE", headers: { Authorization: `Bearer ${accessToken}` } });
      if (!response.ok) throw new Error("Não foi possível excluir o documento.");
      setDocuments((current) => current?.filter((document) => document.id !== documentToDelete.id) || []);
    } catch (error) {
      setDocumentsError(error.message || "Não foi possível excluir o documento.");
    }
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
      const receivedPayload = { codigoAluno: Number.isNaN(Number(studentCode)) ? studentCode : Number(studentCode), pergunta: question, modoBusca: searchMode, ...(typeof currentChatId === "string" ? { chaveConversa: currentChatId } : {}) };
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
      if (body.chaveConversa && body.chaveConversa !== chatId) {
        setCurrentChatId(body.chaveConversa);
        setActiveConversation(body.chaveConversa);
        setChatHistory((current) => current.map((chat) => chat.id === chatId ? { ...chat, id: body.chaveConversa } : chat));
      }
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
            {chatHistory.length ? chatHistory.map((conversation) => <button className={`conversation-item ${activeConversation === conversation.id ? "active" : ""}`} key={conversation.id} type="button" onClick={() => selectConversation(conversation)}><span className="chat-icon" aria-hidden="true" />{conversation.title}</button>) : <p className="empty-history">Nenhuma conversa iniciada.</p>}
          </nav>
        </div>
        <div className="sidebar-footer"><div className="footer-divider" />{accessToken ? <button className="sidebar-link exit" type="button" onClick={logout}><span aria-hidden="true">⇥</span>Sair</button> : <><button className="sidebar-link exit" type="button" onClick={() => openAuth("login")}><span aria-hidden="true">⇥</span>Entrar</button><button className="sidebar-link" type="button" onClick={() => openAuth("register")}><span aria-hidden="true">＋</span>Criar conta</button></>}</div>
      </aside>

      <section className="content">
        <header className="topbar"><div><h1>Bem-vindo ao <strong>Assistente Acadêmico</strong></h1><p>Tire dúvidas utilizando a base de conhecimento da instituição.</p></div><div className="account-actions"><span className="version">Versão 1.0</span>{accessToken ? <button className="account" type="button" onClick={logout}><div className="profile-avatar" aria-hidden="true">♙</div><div className="profile-copy"><strong>Aluno {studentCode}</strong><span>Clique para sair</span></div></button> : <><button className="auth-action" type="button" onClick={() => openAuth("login")}>Entrar</button><button className="auth-action primary" type="button" onClick={() => openAuth("register")}>Criar conta</button></>}<button className="hamburger-button" type="button" aria-label="Abrir menu" aria-expanded={showUserMenu} onClick={() => setShowUserMenu(!showUserMenu)}><span /><span /><span /></button></div></header>

        {showUserMenu && <aside className="cascade-menu" aria-label="Menu do usuário"><button className="cascade-item" type="button" onClick={openProfile}><span>◉</span>Perfil</button><button className="cascade-item" type="button" onClick={openHistory}><span>◷</span>Histórico de chats</button><button className="cascade-item" type="button" onClick={openDocuments}><span>⇧</span>Upload contexto</button><button className="cascade-item" type="button" onClick={() => { setShowSettings(true); setShowUserMenu(false); }}><span>⚙</span>Configurações</button><button className="cascade-item" type="button" onClick={openStatistics}><span>▥</span>Estatísticas</button><button className="cascade-item" type="button" onClick={openDocumentation}><span>▤</span>Documentação</button><button className="cascade-item" type="button" onClick={() => { setShowAbout(true); setShowUserMenu(false); }}><span>ⓘ</span>Sobre o Assistente</button></aside>}

        {showStatistics && <StatisticsDashboard statistics={statistics} loading={statisticsLoading} error={statisticsError} onBack={() => setShowStatistics(false)} onRefresh={openStatistics} />}
        {showDocumentation && <DocumentationScreen documentation={apiDocumentation} loading={documentationLoading} error={documentationError} onBack={() => setShowDocumentation(false)} onRefresh={openDocumentation} />}

        {showProfile && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowProfile(false)}><section className="modal-card" role="dialog" aria-modal="true" aria-label="Perfil do usuário" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setShowProfile(false)}>×</button><h2>Perfil</h2>{profile ? <dl className="profile-details"><div><dt>Código do aluno</dt><dd>{profile.codigoAluno}</dd></div><div><dt>Nome</dt><dd>{profile.nome}</dd></div><div><dt>E-mail</dt><dd>{profile.email || "Não informado"}</dd></div><div><dt>Status</dt><dd>{profile.ativo ? "Ativo" : "Inativo"}</dd></div><div><dt>Cadastro</dt><dd>{new Date(profile.datahoracad).toLocaleDateString("pt-BR")}</dd></div></dl> : <p>{profileError || "Carregando perfil..."}</p>}</section></div>}
        {showSettings && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowSettings(false)}><section className="modal-card settings-modal" role="dialog" aria-modal="true" aria-label="Configurações" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setShowSettings(false)}>×</button><h2>Configurações gerais</h2><label className="setting-option"><span>Notificações do assistente</span><input type="checkbox" checked={notificationsEnabled} onChange={(event) => setNotificationsEnabled(event.target.checked)} /></label><fieldset className="search-mode"><legend>Modo de busca</legend><label><input type="radio" name="search-mode" checked={searchMode === "like"} onChange={() => changeSearchMode("like")} /> Like <small>padrão</small></label><label><input type="radio" name="search-mode" checked={searchMode === "full_text"} onChange={() => changeSearchMode("full_text")} /> Full Text</label><label><input type="radio" name="search-mode" checked={searchMode === "embeddings"} onChange={() => changeSearchMode("embeddings")} /> Embeddings <small>usa Full Text até a camada vetorial ser adicionada</small></label></fieldset><p>O modo escolhido fica salvo neste navegador e é usado na próxima pergunta.</p></section></div>}

        {showDocuments ? <section className="documents-screen"><div className="history-screen-header"><div><h2>Documentos de contexto</h2><p>Arquivos armazenados em <code>contexto/documentos</code>.</p></div><div className="documents-actions"><button type="button" onClick={() => loadDocuments(true)}>Atualizar</button><label className="upload-button">Enviar documento<input type="file" accept=".pdf,.txt,.doc,.docx,.md" onChange={handleContextFile} /></label><button type="button" onClick={() => setShowDocuments(false)}>Voltar ao chat</button></div></div>{documentsLoading ? <div className="history-empty"><p>Buscando documentos...</p></div> : documentsError ? <div className="history-empty"><p>{documentsError}</p></div> : documents?.length ? <div className="documents-list">{documents.map((document) => <article className="document-row" key={document.id}><div><strong>{document.nome}</strong><span>{Math.max(1, Math.ceil(document.tamanho / 1024))} KB</span></div><div className="document-actions"><button type="button" onClick={() => viewDocument(document)}>Visualizar</button><button type="button" className="danger" onClick={() => deleteDocument(document)}>Excluir</button></div></article>)}</div> : <div className="history-empty"><h3>Nenhum documento enviado</h3><p>Envie um PDF, TXT, MD, DOC ou DOCX para preparar a base de conhecimento.</p></div>}</section> : showHistory ? <section className="history-screen"><div className="history-screen-header"><div><h2>Histórico de chats</h2><p>Cada card é identificado pela primeira mensagem enviada.</p></div><button type="button" onClick={() => setShowHistory(false)}>Voltar ao chat</button></div>{chatHistory.length ? <div className="history-cards">{chatHistory.map((chat) => <button type="button" className="history-card" key={chat.id} onClick={() => selectConversation(chat)}><span>Chat</span><strong>{chat.title}</strong><small>{chat.messages.length} mensagem(ns)</small></button>)}</div> : <div className="history-empty"><h3>Nenhuma conversa ainda</h3><p>Envie sua primeira pergunta para criar um chat.</p></div>}</section> : showAbout ? <section className="about-card"><span className="about-icon">ⓘ</span><div><h2>Sobre o UNOIA</h2><p>Protótipo de assistente acadêmico para orientar alunos usando a base de conhecimento institucional.</p><p><strong>Versão:</strong> 1.0 · <strong>Tecnologias:</strong> React, FastAPI e PostgreSQL.</p></div></section> : <>
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

function StatisticsScreen({ statistics, loading, error, onBack, onRefresh }) {
  const [activeSection, setActiveSection] = useState("visao-geral");
  const students = statistics?.byStudent?.alunos || [];
  const maximumQuestions = Math.max(...students.map((student) => student.totalPerguntas), 1);
  const dailyQuestions = statistics?.daily?.totalPerguntas ?? 0;
  const unresolvedQuestions = statistics?.unresolved?.totalSemRespostaOuErro ?? 0;
  const resolvedQuestions = Math.max(0, dailyQuestions - unresolvedQuestions);
  const unresolvedPercentage = dailyQuestions ? Math.round((unresolvedQuestions / dailyQuestions) * 100) : 0;
  const responseTime = Math.round(statistics?.average?.tempoMedioRespostaMs ?? 0);
  const performancePercentage = Math.min(100, Math.round((responseTime / 1000) * 100));

  const quickMenu = [
    ["visao-geral", "Visão geral"],
    ["perguntas", "Perguntas"],
    ["qualidade", "Qualidade"],
    ["desempenho", "Desempenho"],
  ];

  return <section className="utility-screen" aria-label="Estatísticas"><div className="utility-header"><div><span className="utility-eyebrow">RF06 · ACOMPANHAMENTO</span><h2>Estatísticas</h2><p>Indicadores calculados a partir das perguntas registradas pelo assistente.</p></div><div><button type="button" onClick={onRefresh}>Atualizar</button><button type="button" onClick={onBack}>Voltar ao chat</button></div></div><nav className="statistics-quick-menu" aria-label="Menu rápido de estatísticas">{quickMenu.map(([id, label]) => <button key={id} className={activeSection === id ? "active" : ""} type="button" onClick={() => setActiveSection(id)}>{label}</button>)}</nav>{loading ? <div className="utility-empty">Atualizando indicadores...</div> : error ? <div className="utility-empty utility-error">{error}</div> : <div className="statistics-content">{activeSection === "visao-geral" && <><div className="statistics-grid"><article><span>Perguntas realizadas hoje</span><strong>{dailyQuestions}</strong><small>{statistics?.daily?.data || "Data atual"}</small></article><article><span>Sem resposta ou com erro hoje</span><strong>{unresolvedQuestions}</strong><small>Requer acompanhamento</small></article><article><span>Tempo médio de resposta</span><strong>{responseTime} ms</strong><small>Todas as respostas armazenadas</small></article></div><div className="overview-chart-grid"><section className="chart-panel"><h3>Resumo diário</h3><p>Volume de perguntas recebidas hoje.</p><div className="single-bar-chart"><div><i style={{ height: `${Math.max(8, Math.min(100, dailyQuestions * 10))}%` }} /><strong>{dailyQuestions}</strong></div><span>Hoje</span></div></section><section className="chart-panel"><h3>Qualidade das respostas</h3><p>Proporção de registros com erro ou sem resposta.</p><div className="mini-donut" style={{ background: `conic-gradient(#dc4a4a 0 ${unresolvedPercentage}%, #31a965 ${unresolvedPercentage}% 100%)` }}><span>{unresolvedPercentage}%<small>pendente</small></span></div></section></div></>}{activeSection === "perguntas" && <div className="chart-layout"><section className="chart-panel daily-chart-panel"><div><h3>Perguntas realizadas hoje</h3><p>Total de mensagens registradas na data atual.</p></div><div className="daily-column-chart"><div className="column-scale"><span>{dailyQuestions}</span><i style={{ height: `${Math.max(8, Math.min(100, dailyQuestions * 10))}%` }} /></div><strong>{statistics?.daily?.data || "Hoje"}</strong></div></section><section className="student-chart"><div><h3>Perguntas por aluno</h3><p>Distribuição de todas as perguntas registradas.</p></div>{students.length ? <div className="bar-chart">{students.map((student) => <div className="bar-row" key={student.codigoAluno}><span>Aluno {student.codigoAluno}</span><div className="bar-track"><i style={{ width: `${(student.totalPerguntas / maximumQuestions) * 100}%` }} /></div><strong>{student.totalPerguntas}</strong></div>)}</div> : <p className="chart-empty">Ainda não há perguntas registradas.</p>}</section></div>}{activeSection === "qualidade" && <section className="quality-chart-panel"><div><h3>Perguntas sem resposta ou com erro</h3><p>Indicador calculado para os registros do dia atual.</p><div className="quality-legend"><span><i className="resolved" />Respondidas: {resolvedQuestions}</span><span><i className="unresolved" />Sem resposta/erro: {unresolvedQuestions}</span></div></div><div className="quality-donut" style={{ background: `conic-gradient(#dc4a4a 0 ${unresolvedPercentage}%, #31a965 ${unresolvedPercentage}% 100%)` }}><div><strong>{unresolvedPercentage}%</strong><span>pendente</span></div></div></section>}{activeSection === "desempenho" && <section className="performance-chart-panel"><div><h3>Tempo médio de resposta</h3><p>Tempo médio de processamento de todas as respostas armazenadas.</p><div className="performance-scale"><span>0 ms</span><div><i style={{ width: `${performancePercentage}%` }} /></div><span>1.000 ms</span></div><small>Referência visual: até 1 segundo.</small></div><div className="performance-gauge" style={{ background: `conic-gradient(#0d55a2 0 ${performancePercentage}%, #e8eef6 ${performancePercentage}% 100%)` }}><span><strong>{responseTime}</strong>ms</span></div></section>}<div className="statistics-note"><strong>Fonte dos dados:</strong> os indicadores são calculados a partir de <code>logs_perguntas</code> e atualizados ao selecionar “Atualizar”.</div></div>}</section>;
}

function DocumentationScreen({ documentation, loading, error, onBack, onRefresh }) {
  const endpoints = Object.entries(documentation?.paths || {}).flatMap(([path, methods]) => Object.entries(methods).filter(([method]) => ["get", "post", "put", "patch", "delete"].includes(method)).map(([method, operation]) => ({ path, method: method.toUpperCase(), operation })));

  return <section className="utility-screen documentation-screen" aria-label="Documentação da API"><div className="utility-header"><div><span className="utility-eyebrow">API UNOIA</span><h2>Documentação da API</h2><p>Endpoints disponíveis nesta instância do Assistente Acadêmico.</p></div><div><button type="button" onClick={onRefresh}>Atualizar</button><a className="utility-link-button" href={`${API_URL}/docs`} target="_blank" rel="noreferrer">Abrir Swagger</a><button type="button" onClick={onBack}>Voltar ao chat</button></div></div>{loading ? <div className="utility-empty">Carregando endpoints...</div> : error ? <div className="utility-empty utility-error">{error}</div> : <><div className="api-summary"><span>{endpoints.length} endpoints disponíveis</span><code>{API_URL}</code></div><div className="api-endpoints-list">{endpoints.map(({ path, method, operation }) => <article className="api-endpoint" key={`${method}-${path}`}><div className="endpoint-main"><span className={`http-method method-${method.toLowerCase()}`}>{method}</span><code>{path}</code></div><div className="endpoint-details"><strong>{operation.summary || operation.operationId || "Operação da API"}</strong><p>{operation.description || "Endpoint disponível na API UNOIA."}</p><small>{operation.tags?.join(" · ") || "API"}{operation.requestBody ? " · recebe dados" : ""}</small></div></article>)}</div><div className="documentation-footer">Esta lista é obtida diretamente do contrato OpenAPI. Para exemplos de requisição e resposta, use o botão <strong>Abrir Swagger</strong>.</div></>}</section>;
}

export default App;
