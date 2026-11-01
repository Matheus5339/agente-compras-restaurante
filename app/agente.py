"""Loop do agente: o Gemini escolhe ferramentas, o Python executa, repete.

O loop é manual (sem "automatic function calling" do SDK) para registrar cada
chamada de ferramenta e mostrar esse rastro na tela: quem usa o agente vê de
onde veio cada número.
"""

import os

from google import genai
from google.genai import types

from app.ferramentas import DECLARACOES, FERRAMENTAS

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MAX_PASSOS = 8
# Tempo limite de 60 s por chamada: sem isso, uma chamada presa travava a requisição para sempre.
# Sem novas tentativas automáticas: a cota grátis é pequena e o erro 429 já vira aviso na tela.
OPCOES_HTTP = types.HttpOptions(timeout=60_000, retry_options=types.HttpRetryOptions(attempts=1))

INSTRUCOES = """Você é o assistente de compras de um restaurante pequeno (dados fictícios).
Objetivo: sugerir a lista de compras da semana POR FORNECEDOR e explicar o porquê.

Regras:
- Use SEMPRE as ferramentas para obter números. Nunca invente quantidade, preço ou estoque.
- Use o MÍNIMO de chamadas (a cota é limitada). Para a lista da semana, chame só
  montar_lista_compras: ela já traz estoque, previsão, tendência (variacao_4_semanas_pct),
  perecível e custo de cada item. Use as outras ferramentas só para perguntas específicas.
- Não refaça contas: repita os valores que as ferramentas devolverem.
- Para cada item comprado, explique em uma frase curta (ex.: consumo subindo, estoque abaixo
  da previsão, perecível sem estoque de segurança).
- Se um fornecedor ficar abaixo do pedido mínimo, avise e sugira uma saída prática
  (juntar com a próxima semana ou completar com item de giro).
- Responda em português do Brasil, em texto simples com listas, sem tabelas.
- Se a pergunta não for sobre compras, estoque ou fornecedores do restaurante, diga que só
  ajuda com isso."""


def _cliente() -> genai.Client:
    # A chave vem da variável de ambiente GEMINI_API_KEY (nunca do código).
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=OPCOES_HTTP)


def executar(pergunta: str, cliente=None) -> dict:
    """Roda o agente e devolve a resposta final e o rastro das ferramentas."""
    cliente = cliente or _cliente()
    config = types.GenerateContentConfig(
        system_instruction=INSTRUCOES,
        tools=[types.Tool(function_declarations=[types.FunctionDeclaration(**d) for d in DECLARACOES])],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        temperature=0.2,
    )
    conteudo = [types.Content(role="user", parts=[types.Part.from_text(text=pergunta)])]
    rastro = []

    for _ in range(MAX_PASSOS):
        resposta = cliente.models.generate_content(model=MODELO, contents=conteudo, config=config)
        chamadas = resposta.function_calls or []
        if not chamadas:
            return {"resposta": resposta.text or "", "ferramentas": rastro}

        # Devolve ao modelo a própria mensagem dele (mantém o contexto) e,
        # em seguida, o resultado de cada ferramenta pedida.
        conteudo.append(resposta.candidates[0].content)
        partes = []
        for chamada in chamadas:
            args = dict(chamada.args or {})
            try:
                resultado = FERRAMENTAS[chamada.name](**args)
            except (KeyError, TypeError, ValueError) as erro:
                resultado = {"erro": str(erro)}
            rastro.append({"ferramenta": chamada.name, "argumentos": args})
            partes.append(types.Part.from_function_response(name=chamada.name, response={"resultado": resultado}))
        conteudo.append(types.Content(role="user", parts=partes))

    return {"resposta": "Não consegui concluir em poucos passos. Tente reformular.", "ferramentas": rastro}
