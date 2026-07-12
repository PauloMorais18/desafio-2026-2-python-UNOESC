import { useState } from "react";

const WELCOME_MESSAGE = {
  id: 1,
  author: "assistant",
  content: "Olá! 👋\nComo posso ajudá-lo hoje?",
  time: "10:30",
};

const MOCK_RESPONSE =
  "Esta é uma resposta simulada. Futuramente esta resposta será gerada pelo Assistente Acadêmico através da API.";

const history = ["Conversa 1", "Conversa 2", "Conversa 3", "Conversa 4", "Conversa 5"];

function formatTime() {
  return new Intl.DateTimeFormat("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

function App() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [activeConversation, setActiveConversation] = useState("Conversa 1");
  const [input, setInput] = useState("");
  const [isAnswering, setIsAnswering] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showNotice, setShowNotice] = useState(true);

  function startNewChat() {
    setActiveConversation("");
    setMessages([{ ...WELCOME_MESSAGE, id: Date.now(), time: formatTime() }]);
    setShowAbout(false);
  }

  function selectConversation(conversation) {
    setActiveConversation(conversation);
    setShowAbout(false);
    setMessages([
      { id: Date.now(), author: "user", content: "Mensagem fictícia de " + conversation + ".", time: "10:31" },
      { id: Date.now() + 1, author: "assistant", content: MOCK_RESPONSE, time: "10:32" },
    ]);
  }

  function sendMessage(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || isAnswering) return;

    setMessages((current) => [
      ...current,
      { id: Date.now(), author: "user", content: question, time: formatTime() },
    ]);
    setInput("");
    setIsAnswering(true);

    window.setTimeout(() => {
      setMessages((current) => [
        ...current,
        { id: Date.now(), author: "assistant", content: MOCK_RESPONSE, time: formatTime() },
      ]);
      setIsAnswering(false);
    }, 900);
  }

  return (
    <main className="application-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-symbol" aria-hidden="true"><span /></div>
            <div><strong>UNOIA</strong><small>Assistente Acadêmico</small></div>
          </div>

          <button className="new-chat-button" type="button" onClick={startNewChat}>
            <span>＋</span> Novo Chat
          </button>

          <nav aria-label="Histórico de conversas">
            <p className="navigation-label">HISTÓRICO</p>
            {history.map((conversation) => (
              <button
                className={"conversation-item " + (activeConversation === conversation ? "active" : "")}
                key={conversation}
                type="button"
                onClick={() => selectConversation(conversation)}
              >
                <span className="chat-icon" aria-hidden="true">◯</span>
                {conversation}
              </button>
            ))}
          </nav>
        </div>

        <div className="sidebar-footer">
          <div className="footer-divider" />
          <p className="navigation-label">OUTRAS OPÇÕES</p>
          <button className="sidebar-link" type="button" onClick={() => setShowAbout(true)}>
            <span aria-hidden="true">ⓘ</span> Sobre o Assistente
          </button>
          <button className="sidebar-link" type="button" disabled>
            <span aria-hidden="true">⚙</span> Configurações
          </button>
          <div className="footer-divider lower" />
          <button className="sidebar-link exit" type="button" disabled>
            <span aria-hidden="true">⇥</span> Sair
          </button>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h1>Bem-vindo ao <strong>Assistente Acadêmico</strong></h1>
            <p>Tire dúvidas utilizando a base de conhecimento da instituição.</p>
          </div>
          <div className="account">
            <span className="version">Versão 1.0</span>
            <div className="account-divider" />
            <div className="profile-avatar" aria-hidden="true">♙</div>
            <div className="profile-copy"><strong>Aluno Teste</strong><span>Aluno</span></div>
            <span className="chevron" aria-hidden="true">⌄</span>
          </div>
        </header>

        {showAbout ? (
          <section className="about-card">
            <span className="about-icon">ⓘ</span>
            <div>
              <h2>Sobre o UNOIA</h2>
              <p>Protótipo de assistente acadêmico para orientar alunos usando a base de conhecimento institucional.</p>
              <p><strong>Versão:</strong> 1.0 · <strong>Tecnologias:</strong> React, FastAPI e PostgreSQL.</p>
            </div>
          </section>
        ) : (
          <>
            {showNotice && (
              <section className="information-card">
                <span className="information-icon" aria-hidden="true">ⓘ</span>
                <div>
                  <p>O assistente responde apenas perguntas presentes na base de conhecimento cadastrada pela instituição.</p>
                  <p>Caso não encontre informações suficientes, ele informará isso ao usuário.</p>
                </div>
                <button type="button" aria-label="Fechar aviso" className="close-notice" onClick={() => setShowNotice(false)}>×</button>
              </section>
            )}

            <section className="chat-card" aria-label="Conversa atual">
              <div className="messages">
                {messages.map((message) => <MessageBubble key={message.id} message={message} />)}
                {isAnswering && <div className="typing-indicator">O assistente está preparando uma resposta...</div>}
              </div>
            </section>

            <p className="response-note">As respostas podem levar alguns segundos para serem geradas.</p>

            <form className="message-composer" onSubmit={sendMessage}>
              <span className="attachment" aria-hidden="true">⌇</span>
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Digite sua dúvida acadêmica..."
                aria-label="Digite sua dúvida acadêmica"
              />
              <button type="submit" disabled={isAnswering}><span aria-hidden="true">⌁</span> Enviar</button>
            </form>
          </>
        )}
      </section>
    </main>
  );
}

function MessageBubble({ message }) {
  const isUser = message.author === "user";
  return (
    <article className={"message-row " + (isUser ? "user-message" : "assistant-message")}>
      {!isUser && <div className="message-avatar assistant-avatar" aria-hidden="true">◢</div>}
      <div className="bubble">
        {message.content.split("\n").map((line) => <p key={line}>{line}</p>)}
        <time>{message.time}{isUser && "  ✓✓"}</time>
      </div>
      {isUser && <div className="message-avatar user-avatar" aria-hidden="true">◉</div>}
    </article>
  );
}

export default App;
