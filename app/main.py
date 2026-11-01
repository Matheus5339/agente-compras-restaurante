"""API e página web do agente de compras."""

import os
import time
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

load_dotenv()  # lê o .env local, se existir (no Azure, a chave vem dos segredos)

from app import agente  # noqa: E402  (depois do load_dotenv)
from app.ferramentas import consultar_estoque, montar_lista_compras  # noqa: E402

PERGUNTA_PADRAO = "Monte a lista de compras desta semana por fornecedor e explique o porquê de cada item."
# Limite global simples para não esgotar a cota gratuita do Gemini se alguém
# abusar da URL pública. Fica em memória: zera quando o contêiner reinicia.
LIMITE_POR_HORA = int(os.getenv("LIMITE_POR_HORA", "30"))
_chamadas: deque[float] = deque()

app = FastAPI(title="Agente de compras de restaurante (dados fictícios)")
STATIC = Path(__file__).parent / "static"


class Pedido(BaseModel):
    pergunta: str = Field(default=PERGUNTA_PADRAO, max_length=500)


def _dentro_do_limite() -> bool:
    agora = time.time()
    while _chamadas and agora - _chamadas[0] > 3600:
        _chamadas.popleft()
    if len(_chamadas) >= LIMITE_POR_HORA:
        return False
    _chamadas.append(agora)
    return True


@app.get("/")
def pagina():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "ia_configurada": bool(os.getenv("GEMINI_API_KEY"))}


@app.get("/api/estoque")
def estoque():
    return consultar_estoque()


@app.get("/api/lista")
def lista():
    """Lista calculada só pelas ferramentas, sem IA (útil para conferir o agente)."""
    return montar_lista_compras()


@app.post("/api/sugerir")
def sugerir(pedido: Pedido, request: Request):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(503, "IA não configurada (falta GEMINI_API_KEY).")
    if not _dentro_do_limite():
        raise HTTPException(429, "Limite de uso da demo atingido. Tente mais tarde.")
    try:
        return agente.executar(pedido.pergunta)
    except Exception as erro:  # erro do provedor (cota, rede): não vaza detalhes
        if getattr(erro, "code", None) == 429:
            raise HTTPException(429, "A cota gratuita da IA por minuto acabou. Aguarde 1 minuto e tente de novo.")
        print(f"erro no agente: {type(erro).__name__}: {erro}")
        raise HTTPException(502, "Falha ao consultar o modelo de IA. Tente de novo em instantes.")
