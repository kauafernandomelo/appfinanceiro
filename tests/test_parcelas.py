"""Testes unitarios para calculo de parcelas."""

import calendar
from datetime import datetime


def calcular_parcelas(valor_total: float, num_parcelas: int, data_inicio: str) -> list[dict]:
    """Calcula parcelas mensais de uma compra. Retorna lista de dicts com data e valor."""
    if num_parcelas < 1:
        raise ValueError("Numero de parcelas deve ser >= 1")
    if valor_total <= 0:
        raise ValueError("Valor total deve ser positivo")

    valor_base = round(valor_total / num_parcelas, 2)
    valor_total_base = round(valor_base * num_parcelas, 2)
    diff = round(valor_total - valor_total_base, 2)

    data_ref = datetime.strptime(data_inicio, "%Y-%m-%d")
    parcelas = []

    for i in range(num_parcelas):
        # Calcula data da parcela
        mes = data_ref.month + i
        ano = data_ref.year
        while mes > 12:
            mes -= 12
            ano += 1

        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dia = min(data_ref.day, ultimo_dia)
        data_parcela = f"{ano}-{mes:02d}-{dia:02d}"

        # Primeira parcela absorve a diferenca de arredondamento
        valor = valor_base if i > 0 else round(valor_base + diff, 2)

        parcelas.append({"data": data_parcela, "valor": valor})

    return parcelas


def test_parcelas_2x():
    parcelas = calcular_parcelas(100.00, 2, "2025-01-15")
    assert len(parcelas) == 2
    assert parcelas[0]["data"] == "2025-01-15"
    assert parcelas[1]["data"] == "2025-02-15"
    assert parcelas[0]["valor"] + parcelas[1]["valor"] == 100.00


def test_parcelas_3x_valor_impar():
    parcelas = calcular_parcelas(100.00, 3, "2025-01-10")
    assert len(parcelas) == 3
    total = sum(p["valor"] for p in parcelas)
    assert total == 100.00


def test_parcelas_12x():
    parcelas = calcular_parcelas(1200.00, 12, "2025-01-01")
    assert len(parcelas) == 12
    assert parcelas[0]["valor"] == 100.00
    assert parcelas[11]["data"] == "2025-12-01"
    total = sum(p["valor"] for p in parcelas)
    assert total == 1200.00


def test_parcelas_fevereiro_bissexto():
    parcelas = calcular_parcelas(100.00, 2, "2024-01-29")
    assert parcelas[0]["data"] == "2024-01-29"
    assert parcelas[1]["data"] == "2024-02-29"  # 2024 e bissexto


def test_parcelas_fevereiro_nao_bissexto():
    parcelas = calcular_parcelas(100.00, 2, "2025-01-29")
    assert parcelas[0]["data"] == "2025-01-29"
    assert parcelas[1]["data"] == "2025-02-28"  # 2025 nao e bissexto


def test_parcelas_mudanca_ano():
    parcelas = calcular_parcelas(600.00, 6, "2025-10-15")
    assert parcelas[0]["data"] == "2025-10-15"
    assert parcelas[2]["data"] == "2025-12-15"
    assert parcelas[3]["data"] == "2026-01-15"
    assert parcelas[5]["data"] == "2026-03-15"


def test_parcelas_dia_31_em_mes_curto():
    parcelas = calcular_parcelas(100.00, 3, "2025-01-31")
    assert parcelas[0]["data"] == "2025-01-31"
    assert parcelas[1]["data"] == "2025-02-28"  # Fevereiro tem 28 dias
    assert parcelas[2]["data"] == "2025-03-31"


def test_parcelas_arredondamento_centavos():
    parcelas = calcular_parcelas(10.00, 3, "2025-01-01")
    total = sum(p["valor"] for p in parcelas)
    assert total == 10.00


def test_parcelas_60x():
    parcelas = calcular_parcelas(6000.00, 60, "2025-01-01")
    assert len(parcelas) == 60
    assert parcelas[59]["data"] == "2029-12-01"
    total = sum(p["valor"] for p in parcelas)
    assert abs(total - 6000.00) < 0.01


def test_parcelas_valor_minimo():
    parcelas = calcular_parcelas(1.00, 3, "2025-01-01")
    assert len(parcelas) == 3
    total = sum(p["valor"] for p in parcelas)
    assert total == 1.00


def test_parcelas_numero_invalido():
    import pytest
    with pytest.raises(ValueError):
        calcular_parcelas(100.00, 0, "2025-01-01")


def test_parcelas_valor_negativo():
    import pytest
    with pytest.raises(ValueError):
        calcular_parcelas(-100.00, 3, "2025-01-01")
