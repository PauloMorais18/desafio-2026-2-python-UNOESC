"""Teste simples de integração entre LangChain e o Ollama local."""

from __future__ import annotations

from langchain_ollama import ChatOllama


OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "qwen2.5:3b"
PROMPT = "Responda apenas 'OK' se estiver funcionando."


def main() -> None:
    """Envia uma mensagem ao Ollama e imprime a resposta recebida."""
    print("=== TESTE OLLAMA ===")
    print(f"\nModelo:\n{MODEL_NAME}")

    try:
        chat = ChatOllama(model=MODEL_NAME, base_url=OLLAMA_URL)
        response = chat.invoke(PROMPT)
        print(f"\nResposta:\n{response.content}")
    except Exception:
        print("\nNão foi possível conectar ao Ollama.")


if __name__ == "__main__":
    main()
