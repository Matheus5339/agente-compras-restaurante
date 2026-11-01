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

## Deploy atual (31/10/2026)
- Container App `agente-compras-restaurante` no grupo `rg-go-api-lab`, ambiente `env-go-api-lab` (Brazil South, tipo **Express**).
- URL: https://agente-compras-restaurante.calmwave-44962e56.brazilsouth.azurecontainerapps.io
- Chave: segredo `gemini-key` → variável `GEMINI_API_KEY=secretref:gemini-key`
  (cadastrado por `carreira/ferramentas/azure_segredo_gemini.py`, que lê o .env sem exibir).
- Ambiente Express não aceita `--revision-suffix` nem `revision restart`. Para publicar versão nova,
  troque a imagem pela tag do commit: `az containerapp update -n agente-compras-restaurante -g rg-go-api-lab --image ghcr.io/matheus5339/agente-compras-restaurante:<sha>`.
- Apagar só este app: `az containerapp delete -n agente-compras-restaurante -g rg-go-api-lab`.
- 1º push no GHCR falhou com "denied" na tag (pacote novo); "Re-run failed jobs" resolveu.
