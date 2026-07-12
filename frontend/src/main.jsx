import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles.css";

// Avoid restoring an outdated Vite page from the browser back/forward cache.
window.addEventListener("pageshow", (event) => {
  if (event.persisted) window.location.reload();
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
