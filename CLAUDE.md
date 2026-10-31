# agente-compras-restaurante

Projeto de portfólio do Matheus para a vaga iFood GenAI (trilha AI Builder), 31/10/2026.
Repositório: `github.com/Matheus5339/agente-compras-restaurante` (público).

## Decisões
- Python 3.13 + FastAPI; Gemini (`google-genai`) com function calling em loop manual.
- Contas só em Python (`app/ferramentas.py`), testadas; o LLM só escolhe ferramenta e explica.
- Dados FICTÍCIOS (`app/dados.py`). O README diz isso.
- Chave `GEMINI_API_KEY` só por variável de ambiente / segredo do Azure. `.env` no `.gitignore`.
- **Regra do Matheus: nada que custe dinheiro.** Gemini free tier; Azure for Students
  (Container Apps, min 0 / max 1 réplica, mesmo ambiente do go-api-lab); imagem no GHCR.
- Testes sem chamar a API (cliente falso). CI: pytest + docker build + push GHCR.

## Pendências
- Código escrito pelo Claude a pedido dele; ele vai estudar para defender em entrevista.
