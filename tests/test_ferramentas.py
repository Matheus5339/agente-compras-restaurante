import pytest

from app.ferramentas import (
    DECLARACOES,
    FERRAMENTAS,
    calcular_compra,
    consultar_estoque,
    montar_lista_compras,
    prever_consumo,
)


def test_previsao_e_media_ponderada():
    # tomate: (18*1 + 20*2 + 19*3 + 23*4) / 10 = 20.7
    assert prever_consumo("tomate")["previsao_semana"] == 20.7


def test_perecivel_nao_tem_estoque_de_seguranca():
    c = calcular_compra("tomate")
    assert c["estoque_seguranca"] == 0
    # 20.7 - 6 = 14.7 -> embalagem de 5 -> 15
    assert c["comprar"] == 15


def test_nao_perecivel_tem_seguranca_e_arredonda_na_embalagem():
    c = calcular_compra("batata")
    # previsão (25+54+90+128)/10 = 29.7; segurança 5.94; 29.7+5.94-8 = 27.64 -> 30
    assert c["estoque_seguranca"] == 5.9
    assert c["comprar"] == 30
    assert c["comprar"] % c["embalagem"] == 0


def test_estoque_suficiente_nao_compra():
    # linguiça: previsão 6.1 + 1.22 = 7.32 < estoque 9
    assert calcular_compra("linguica")["comprar"] == 0


def test_lista_agrupa_por_fornecedor_e_soma_total():
    lista = montar_lista_compras()
    assert set(lista["pedidos"]) == {"hortifruti", "acougue", "secos", "bebidas"}
    soma = round(sum(p["total"] for p in lista["pedidos"].values()), 2)
    assert lista["total_geral"] == soma
    for p in lista["pedidos"].values():
        assert p["abaixo_do_minimo"] == (0 < p["total"] < p["pedido_minimo"])


def test_produto_ou_fornecedor_invalido():
    with pytest.raises(ValueError):
        calcular_compra("caviar")
    with pytest.raises(ValueError):
        consultar_estoque("padaria")


def test_toda_declaracao_tem_funcao():
    assert {d["name"] for d in DECLARACOES} == set(FERRAMENTAS)
