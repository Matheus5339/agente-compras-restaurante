"""Ferramentas (tools) que o agente pode chamar.

Decisão principal: toda a conta fica aqui, em Python, e é testada. O modelo de
linguagem só decide QUAIS ferramentas chamar e EXPLICA o resultado; ele não
faz aritmética, porque LLM erra conta e não é auditável.
"""

import math

from app.dados import FORNECEDORES, PRODUTOS

# Estoque de segurança para itens não perecíveis: 20% da previsão da semana.
MARGEM_SEGURANCA = 0.20


def _produto(produto_id: str) -> dict:
    for p in PRODUTOS:
        if p["id"] == produto_id:
            return p
    raise ValueError(f"produto desconhecido: {produto_id}")


def listar_fornecedores() -> list[dict]:
    """Fornecedores com pedido mínimo e dias de entrega."""
    return [{"id": fid, **f} for fid, f in FORNECEDORES.items()]


def consultar_estoque(fornecedor: str | None = None) -> list[dict]:
    """Estoque atual de cada produto (opcionalmente de um fornecedor só)."""
    if fornecedor and fornecedor not in FORNECEDORES:
        raise ValueError(f"fornecedor desconhecido: {fornecedor}")
    return [
        {k: p[k] for k in ("id", "nome", "unidade", "fornecedor", "estoque", "perecivel")}
        for p in PRODUTOS
        if fornecedor is None or p["fornecedor"] == fornecedor
    ]


def prever_consumo(produto_id: str) -> dict:
    """Previsão da próxima semana: média ponderada das 4 últimas semanas.

    Pesos 1, 2, 3, 4 (a semana mais recente pesa mais), para captar tendência
    de alta ou baixa sem precisar de modelo estatístico.
    """
    p = _produto(produto_id)
    historico = p["consumo_4_semanas"]
    pesos = [1, 2, 3, 4]
    previsao = sum(h * w for h, w in zip(historico, pesos)) / sum(pesos)
    variacao = (historico[-1] - historico[0]) / historico[0] * 100
    return {
        "produto_id": produto_id,
        "historico": historico,
        "previsao_semana": round(previsao, 1),
        "variacao_4_semanas_pct": round(variacao, 1),
    }


def calcular_compra(produto_id: str) -> dict:
    """Quanto comprar de um produto para a próxima semana.

    necessidade = previsão + segurança - estoque (perecível não tem segurança),
    arredondada para cima no múltiplo da embalagem do fornecedor.
    """
    p = _produto(produto_id)
    consumo = prever_consumo(produto_id)
    previsao = consumo["previsao_semana"]
    seguranca = 0.0 if p["perecivel"] else previsao * MARGEM_SEGURANCA
    necessidade = previsao + seguranca - p["estoque"]
    if necessidade <= 0:
        quantidade = 0
    else:
        quantidade = math.ceil(necessidade / p["embalagem"]) * p["embalagem"]
    return {
        "produto_id": produto_id,
        "nome": p["nome"],
        "unidade": p["unidade"],
        "fornecedor": p["fornecedor"],
        "estoque": p["estoque"],
        "previsao_semana": previsao,
        "variacao_4_semanas_pct": consumo["variacao_4_semanas_pct"],
        "perecivel": p["perecivel"],
        "estoque_seguranca": round(seguranca, 1),
        "embalagem": p["embalagem"],
        "comprar": quantidade,
        "custo": round(quantidade * p["preco"], 2),
    }


def montar_lista_compras() -> dict:
    """Lista da semana agrupada por fornecedor, com aviso de pedido mínimo."""
    pedidos = {}
    for fid, f in FORNECEDORES.items():
        itens = [calcular_compra(p["id"]) for p in PRODUTOS if p["fornecedor"] == fid]
        itens = [i for i in itens if i["comprar"] > 0]
        total = round(sum(i["custo"] for i in itens), 2)
        pedidos[fid] = {
            "fornecedor": f["nome"],
            "entrega": f["entrega"],
            "itens": itens,
            "total": total,
            "pedido_minimo": f["pedido_minimo"],
            "abaixo_do_minimo": 0 < total < f["pedido_minimo"],
        }
    return {
        "pedidos": pedidos,
        "total_geral": round(sum(p["total"] for p in pedidos.values()), 2),
    }


# Registro usado pelo agente: nome da ferramenta -> função Python.
FERRAMENTAS = {
    "listar_fornecedores": listar_fornecedores,
    "consultar_estoque": consultar_estoque,
    "prever_consumo": prever_consumo,
    "calcular_compra": calcular_compra,
    "montar_lista_compras": montar_lista_compras,
}

# Descrição das ferramentas no formato JSON Schema que o Gemini entende.
DECLARACOES = [
    {
        "name": "listar_fornecedores",
        "description": "Lista os fornecedores com pedido mínimo (R$) e dias de entrega.",
        "parameters_json_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_estoque",
        "description": "Estoque atual dos produtos. Filtra por fornecedor se informado.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "fornecedor": {"type": "string", "enum": list(FORNECEDORES)},
            },
        },
    },
    {
        "name": "prever_consumo",
        "description": "Histórico de 4 semanas e previsão de consumo da próxima semana de um produto.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {"produto_id": {"type": "string", "enum": [p["id"] for p in PRODUTOS]}},
            "required": ["produto_id"],
        },
    },
    {
        "name": "calcular_compra",
        "description": "Quantidade e custo a comprar de um produto, já arredondado na embalagem.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {"produto_id": {"type": "string", "enum": [p["id"] for p in PRODUTOS]}},
            "required": ["produto_id"],
        },
    },
    {
        "name": "montar_lista_compras",
        "description": "Lista de compras completa da semana, agrupada por fornecedor, com totais e aviso de pedido mínimo.",
        "parameters_json_schema": {"type": "object", "properties": {}},
    },
]
