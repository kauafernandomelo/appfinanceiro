import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import CATEGORIAS_PADRAO, get_connection, init_db


@pytest.fixture
def db(tmp_path):
    import database
    original = database.DB_PATH
    database.DB_PATH = tmp_path / "test.db"
    init_db()
    yield database.DB_PATH
    database.DB_PATH = original


def test_init_db_cria_tabelas(db):
    with get_connection() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {t["name"] for t in tables}
        assert "categorias" in names
        assert "receitas" in names
        assert "despesas" in names
        assert "investimentos" in names
        assert "orcamento" in names
        assert "metas" in names
        assert "recorrentes" in names


def test_init_db_insere_categorias_padrao(db):
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
        assert count == len(CATEGORIAS_PADRAO)


def test_init_db_nao_duplica(db):
    init_db()
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
        assert count == len(CATEGORIAS_PADRAO)


def test_insert_receita(db):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO receitas (descricao, valor, data) VALUES (?, ?, ?)",
            ("Salario", 5000.0, "2025-03-15"),
        )
        conn.commit()
        r = conn.execute("SELECT * FROM receitas").fetchone()
        assert r["descricao"] == "Salario"
        assert r["valor"] == 5000.0


def test_insert_despesa(db):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO despesas (descricao, valor, data) VALUES (?, ?, ?)",
            ("Aluguel", 1500.0, "2025-03-01"),
        )
        conn.commit()
        r = conn.execute("SELECT * FROM despesas").fetchone()
        assert r["descricao"] == "Aluguel"
        assert r["valor"] == 1500.0


def test_insert_investimento(db):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO investimentos (nome, tipo, valor_investido, valor_atual, data) VALUES (?,?,?,?,?)",
            ("PETR4", "Acoes", 1000.0, 1200.0, "2025-03-15"),
        )
        conn.commit()
        r = conn.execute("SELECT * FROM investimentos").fetchone()
        assert r["nome"] == "PETR4"
        assert r["valor_atual"] == 1200.0


def test_insert_meta(db):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO metas (nome, valor_alvo, valor_atual, prazo) VALUES (?,?,?,?)",
            ("Viagem", 5000.0, 1000.0, "2025-12-31"),
        )
        conn.commit()
        r = conn.execute("SELECT * FROM metas").fetchone()
        assert r["nome"] == "Viagem"
        assert r["valor_alvo"] == 5000.0


def test_delete_receita(db):
    with get_connection() as conn:
        conn.execute("INSERT INTO receitas (descricao, valor, data) VALUES (?,?,?)",
                     ("Teste", 100.0, "2025-03-15"))
        conn.commit()
        conn.execute("DELETE FROM receitas WHERE descricao='Teste'")
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM receitas").fetchone()[0]
        assert count == 0


def test_update_meta(db):
    with get_connection() as conn:
        conn.execute("INSERT INTO metas (nome,valor_alvo,valor_atual,prazo) VALUES (?,?,?,?)",
                     ("Teste", 1000.0, 0, "2025-12-31"))
        conn.commit()
        conn.execute("UPDATE metas SET valor_atual=500 WHERE nome='Teste'")
        conn.commit()
        r = conn.execute("SELECT valor_atual FROM metas WHERE nome='Teste'").fetchone()
        assert r["valor_atual"] == 500.0


def test_foreign_key_categoria(db):
    with get_connection() as conn:
        c = conn.execute("SELECT id FROM categorias WHERE tipo='despesa' LIMIT 1").fetchone()
        conn.execute("INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                     ("Teste FK", 50.0, "2025-03-15", c["id"]))
        conn.commit()
        r = conn.execute("SELECT * FROM despesas WHERE descricao='Teste FK'").fetchone()
        assert r["categoria_id"] == c["id"]
