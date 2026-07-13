import React from "react";
import ReactDOM from "react-dom/client";
import { registerSW } from "virtual:pwa-register";

import App from "./App";
import "./styles.css";

// Avoid restoring an outdated Vite page from the browser back/forward cache.
window.addEventListener("pageshow", (event) => {
  if (event.persisted) window.location.reload();
});

// Registra o service worker gerado no build e mantém a versão instalada atualizada.
registerSW({ immediate: true });

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
