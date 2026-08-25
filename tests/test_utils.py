from utils import (
    formatar_data,
    formatar_moeda,
    formatar_percentual,
    obter_data_atual,
    obter_mes_atual,
    parse_data_br,
    parse_valor,
    validar_data,
    validar_valor,
)


def test_formatar_moeda_inteiro():
    assert formatar_moeda(1000) == "R$ 1.000,00"


def test_formatar_moeda_zero():
    assert formatar_moeda(0) == "R$ 0,00"


def test_formatar_moeda_negativo():
    assert formatar_moeda(-50.5) == "R$ -50,50"


def test_formatar_moeda_grande():
    assert formatar_moeda(1234567.89) == "R$ 1.234.567,89"


def test_formatar_data_valida():
    assert formatar_data("2025-03-15") == "15/03/2025"


def test_formatar_data_invalida():
    assert formatar_data("invalido") == "invalido"


def test_obter_mes_atual():
    result = obter_mes_atual()
    assert len(result) == 7
    assert result[4] == "-"


def test_obter_data_atual():
    result = obter_data_atual()
    assert len(result) == 10
    assert result[4] == "-" and result[7] == "-"


def test_parse_data_br():
    assert parse_data_br("15/03/2025") == "2025-03-15"


def test_parse_data_br_invalida():
    assert parse_data_br("invalido") == "invalido"


def test_validar_data_valida():
    assert validar_data("2025-03-15") is True


def test_validar_data_invalida():
    assert validar_data("2025-13-45") is False
    assert validar_data("abc") is False


def test_validar_valor_valido():
    assert validar_valor("100,50") is True
    assert validar_valor("100.50") is True
    assert validar_valor("0") is True


def test_validar_valor_invalido():
    assert validar_valor("abc") is False
    assert validar_valor("") is False


def test_parse_valor():
    assert parse_valor("100,50") == 100.5
    assert parse_valor("100.50") == 100.5
    assert parse_valor("0") == 0.0


def test_formatar_percentual():
    assert formatar_percentual(85.5) == "85,5%"
    assert formatar_percentual(0) == "0,0%"
    assert formatar_percentual(100) == "100,0%"
    assert formatar_percentual(33.333) == "33,3%"
