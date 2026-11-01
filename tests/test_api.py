from fastapi.testclient import TestClient

from app import main

cliente = TestClient(main.app)


def test_pagina_e_health():
    assert cliente.get("/").status_code == 200
    assert cliente.get("/health").json()["status"] == "ok"


def test_lista_sem_ia():
    d = cliente.get("/api/lista").json()
    assert "pedidos" in d and d["total_geral"] > 0


def test_sem_chave_responde_503(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert cliente.post("/api/sugerir", json={}).status_code == 503


def test_limite_de_uso(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "teste")
    monkeypatch.setattr(main, "LIMITE_POR_HORA", 1)
    monkeypatch.setattr(main, "_chamadas", main.deque())
    monkeypatch.setattr(main.agente, "executar", lambda p: {"resposta": "ok", "ferramentas": []})
    assert cliente.post("/api/sugerir", json={}).status_code == 200
    assert cliente.post("/api/sugerir", json={}).status_code == 429


def test_pergunta_longa_rejeitada(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "teste")
    assert cliente.post("/api/sugerir", json={"pergunta": "x" * 501}).status_code == 422


def test_cota_do_provedor_vira_429_amigavel(monkeypatch):
    class ErroCota(Exception):
        code = 429

    def estoura(p):
        raise ErroCota("quota")

    monkeypatch.setenv("GEMINI_API_KEY", "teste")
    monkeypatch.setattr(main, "_chamadas", main.deque())
    monkeypatch.setattr(main.agente, "executar", estoura)
    r = cliente.post("/api/sugerir", json={})
    assert r.status_code == 429
    assert "Aguarde 1 minuto" in r.json()["detail"]
