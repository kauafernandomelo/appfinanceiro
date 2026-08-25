"""Testes unitarios para logica de recorrentes."""

import calendar


def calcular_dias_no_mes(ano: int, mes: int) -> int:
    """Retorna o numero de dias no mes, incluindo anos bissextos."""
    return calendar.monthrange(ano, mes)[1]


def calcular_data_recorrente(dia_mes: int, mes: int, ano: int) -> str:
    """Calcula a data correta para um lancamento recorrente."""
    dias_no_mes = calcular_dias_no_mes(ano, mes)
    dia = min(dia_mes, dias_no_mes)
    return f"{ano}-{mes:02d}-{dia:02d}"


def verificar_recorrentes_geradas(recorrentes: list, mes: str) -> dict:
    """Verifica quais recorrentes ja foram geradas no mes.

    Args:
        recorrentes: Lista de dicts com 'descricao' e 'tipo'
        mes: String no formato "YYYY-MM"

    Returns:
        Dict com 'total', 'geradas', 'pendentes'
    """
    from database import get_connection

    total = len(recorrentes)
    geradas = 0

    with get_connection() as conn:
        for rec in recorrentes:
            if rec["tipo"] == "receita":
                existe = conn.execute(
                    "SELECT COUNT(*) FROM receitas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                    (rec["descricao"], mes),
                ).fetchone()[0]
            else:
                existe = conn.execute(
                    "SELECT COUNT(*) FROM despesas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                    (rec["descricao"], mes),
                ).fetchone()[0]
            if existe > 0:
                geradas += 1

    return {"total": total, "geradas": geradas, "pendentes": total - geradas}


def test_dias_janeiro():
    assert calcular_dias_no_mes(2025, 1) == 31


def test_dias_fevereiro_bissexto():
    assert calcular_dias_no_mes(2024, 2) == 29


def test_dias_fevereiro_nao_bissexto():
    assert calcular_dias_no_mes(2025, 2) == 28


def test_dias_abril():
    assert calcular_dias_no_mes(2025, 4) == 30


def test_dias_dezembro():
    assert calcular_dias_no_mes(2025, 12) == 31


def test_data_recorrente_dia_valido():
    assert calcular_data_recorrente(15, 1, 2025) == "2025-01-15"


def test_data_recorrente_dia_31_em_fevereiro():
    assert calcular_data_recorrente(31, 2, 2025) == "2025-02-28"


def test_data_recorrente_dia_31_em_fevereiro_bissexto():
    assert calcular_data_recorrente(31, 2, 2024) == "2024-02-29"


def test_data_recorrente_dia_30_em_abril():
    assert calcular_data_recorrente(30, 4, 2025) == "2025-04-30"


def test_data_recorrente_dia_31_em_abril():
    assert calcular_data_recorrente(31, 4, 2025) == "2025-04-30"


def test_data_recorrente_dia_29_em_fevereiro_nao_bissexto():
    assert calcular_data_recorrente(29, 2, 2025) == "2025-02-28"


def test_data_recorrente_dia_29_em_fevereiro_bissexto():
    assert calcular_data_recorrente(29, 2, 2024) == "2024-02-29"


def test_todos_meses_tem_dias_validos():
    """Verifica que todos os meses de 2025 tem dias validos."""
    for mes in range(1, 13):
        dias = calcular_dias_no_mes(2025, mes)
        assert 28 <= dias <= 31
        data = calcular_data_recorrente(31, mes, 2025)
        ano, m, d = data.split("-")
        assert int(m) == mes
        assert 1 <= int(d) <= dias
