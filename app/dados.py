"""Dados FICTÍCIOS de um restaurante pequeno.

Nenhum número aqui vem de um restaurante real. Os nomes de fornecedores são
inventados. A estrutura (4 fornecedores, pedido mínimo, perecíveis com compra
mais frequente) imita a rotina de compras de um restaurante de bairro.
"""

FORNECEDORES = {
    "hortifruti": {
        "nome": "Hortifruti Vale Verde (fictício)",
        "pedido_minimo": 150.0,
        "entrega": "terça e sexta",
    },
    "acougue": {
        "nome": "Açougue Boi Bom (fictício)",
        "pedido_minimo": 300.0,
        "entrega": "segunda",
    },
    "secos": {
        "nome": "Distribuidora Grão Forte (fictício)",
        "pedido_minimo": 400.0,
        "entrega": "quarta",
    },
    "bebidas": {
        "nome": "Bebidas Gelada Já (fictício)",
        "pedido_minimo": 250.0,
        "entrega": "quinta",
    },
}

# consumo_4_semanas: da mais antiga para a mais recente (unidade do produto).
# embalagem: o fornecedor só vende em múltiplos desse valor.
# perecivel: validade curta; não vale a pena manter estoque de segurança.
PRODUTOS = [
    {"id": "tomate", "nome": "Tomate", "unidade": "kg", "fornecedor": "hortifruti",
     "estoque": 6, "consumo_4_semanas": [18, 20, 19, 23], "embalagem": 5,
     "preco": 7.50, "perecivel": True},
    {"id": "alface", "nome": "Alface crespa", "unidade": "maço", "fornecedor": "hortifruti",
     "estoque": 4, "consumo_4_semanas": [30, 28, 32, 30], "embalagem": 10,
     "preco": 2.80, "perecivel": True},
    {"id": "cebola", "nome": "Cebola", "unidade": "kg", "fornecedor": "hortifruti",
     "estoque": 12, "consumo_4_semanas": [10, 11, 9, 10], "embalagem": 5,
     "preco": 5.20, "perecivel": False},
    {"id": "batata", "nome": "Batata", "unidade": "kg", "fornecedor": "hortifruti",
     "estoque": 8, "consumo_4_semanas": [25, 27, 30, 32], "embalagem": 10,
     "preco": 4.90, "perecivel": False},
    {"id": "alcatra", "nome": "Alcatra", "unidade": "kg", "fornecedor": "acougue",
     "estoque": 5, "consumo_4_semanas": [14, 15, 13, 16], "embalagem": 1,
     "preco": 44.90, "perecivel": True},
    {"id": "frango", "nome": "Peito de frango", "unidade": "kg", "fornecedor": "acougue",
     "estoque": 10, "consumo_4_semanas": [20, 22, 21, 25], "embalagem": 2,
     "preco": 19.90, "perecivel": True},
    {"id": "linguica", "nome": "Linguiça toscana", "unidade": "kg", "fornecedor": "acougue",
     "estoque": 9, "consumo_4_semanas": [6, 5, 7, 6], "embalagem": 1,
     "preco": 24.50, "perecivel": False},
    {"id": "arroz", "nome": "Arroz tipo 1", "unidade": "pacote 5 kg", "fornecedor": "secos",
     "estoque": 3, "consumo_4_semanas": [8, 8, 9, 9], "embalagem": 6,
     "preco": 27.90, "perecivel": False},
    {"id": "feijao", "nome": "Feijão carioca", "unidade": "pacote 1 kg", "fornecedor": "secos",
     "estoque": 20, "consumo_4_semanas": [14, 15, 15, 14], "embalagem": 10,
     "preco": 8.40, "perecivel": False},
    {"id": "oleo", "nome": "Óleo de soja", "unidade": "frasco 900 ml", "fornecedor": "secos",
     "estoque": 18, "consumo_4_semanas": [10, 9, 11, 10], "embalagem": 20,
     "preco": 7.90, "perecivel": False},
    {"id": "refrigerante", "nome": "Refrigerante lata", "unidade": "lata", "fornecedor": "bebidas",
     "estoque": 40, "consumo_4_semanas": [90, 95, 100, 120], "embalagem": 12,
     "preco": 3.10, "perecivel": False},
    {"id": "suco", "nome": "Polpa de suco", "unidade": "pacote 1 kg", "fornecedor": "bebidas",
     "estoque": 15, "consumo_4_semanas": [12, 12, 13, 12], "embalagem": 10,
     "preco": 11.00, "perecivel": False},
]
