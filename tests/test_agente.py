"""Testa o loop do agente com um cliente falso (sem chamar a API do Gemini)."""

from types import SimpleNamespace

from google.genai import types

from app import agente


def _resposta_com_chamada(nome, args):
    chamada = types.FunctionCall(name=nome, args=args)
    conteudo = types.Content(role="model", parts=[types.Part(function_call=chamada)])
    return SimpleNamespace(function_calls=[chamada], candidates=[SimpleNamespace(content=conteudo)], text=None)


def _resposta_final(texto):
    return SimpleNamespace(function_calls=None, candidates=[], text=texto)


class ClienteFalso:
    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.conteudos = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.conteudos.append(list(contents))
        return self.respostas.pop(0)


def test_agente_executa_ferramenta_e_devolve_resultado_ao_modelo():
    cliente = ClienteFalso([
        _resposta_com_chamada("calcular_compra", {"produto_id": "tomate"}),
        _resposta_final("Compre 15 kg de tomate."),
    ])
    saida = agente.executar("quanto tomate?", cliente=cliente)

    assert saida["resposta"] == "Compre 15 kg de tomate."
    assert saida["ferramentas"] == [{"ferramenta": "calcular_compra", "argumentos": {"produto_id": "tomate"}}]
    # Na 2ª chamada o modelo recebe o resultado real da ferramenta.
    ultima = cliente.conteudos[1][-1].parts[0].function_response
    assert ultima.name == "calcular_compra"
    assert ultima.response["resultado"]["comprar"] == 15


def test_ferramenta_inexistente_vira_erro_para_o_modelo():
    cliente = ClienteFalso([
        _resposta_com_chamada("apagar_tudo", {}),
        _resposta_final("Não posso."),
    ])
    saida = agente.executar("x", cliente=cliente)
    resposta = cliente.conteudos[1][-1].parts[0].function_response.response
    assert "erro" in resposta["resultado"]
    assert saida["resposta"] == "Não posso."


def test_para_depois_do_maximo_de_passos():
    cliente = ClienteFalso([_resposta_com_chamada("listar_fornecedores", {})] * agente.MAX_PASSOS)
    saida = agente.executar("x", cliente=cliente)
    assert len(saida["ferramentas"]) == agente.MAX_PASSOS
    assert "Não consegui" in saida["resposta"]
