"""Testes de integracao para verificar que dados persistem corretamente."""

import sqlite3

import pytest

import database
from database import get_connection, init_db


@pytest.fixture
def temp_db(tmp_path):
    """Cria um banco temporario para testes."""
    original = database.DB_PATH
    database.DB_PATH = tmp_path / "test.db"
    init_db()
    yield tmp_path / "test.db"
    database.DB_PATH = original


def test_insert_receita_persiste(temp_db):
    """Verifica que uma receita inserida persiste apos fechar a conexao."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Salario", 5000.00, "2025-01-15", None),
        )
        conn.commit()

    # Abre uma nova conexao e verifica se o dado persistiu
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM receitas WHERE descricao='Salario'").fetchone()
        assert result is not None
        assert result["valor"] == 5000.00
        assert result["data"] == "2025-01-15"


def test_insert_despesa_persiste(temp_db):
    """Verifica que uma despesa inserida persiste."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO despesas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Aluguel", 1500.00, "2025-01-01", None),
        )
        conn.commit()

    with get_connection() as conn:
        result = conn.execute("SELECT * FROM despesas WHERE descricao='Aluguel'").fetchone()
        assert result is not None
        assert result["valor"] == 1500.00


def test_update_receita_persiste(temp_db):
    """Verifica que uma atualizacao de receita persiste."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Freelance", 1000.00, "2025-01-10", None),
        )
        conn.commit()

    with get_connection() as conn:
        conn.execute(
            "UPDATE receitas SET valor=? WHERE descricao='Freelance'",
            (2000.00,),
        )
        conn.commit()

    with get_connection() as conn:
        result = conn.execute("SELECT * FROM receitas WHERE descricao='Freelance'").fetchone()
        assert result["valor"] == 2000.00


def test_delete_receita_persiste(temp_db):
    """Verifica que uma exclusao de receita persiste."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Temp", 100.00, "2025-01-01", None),
        )
        conn.commit()

    with get_connection() as conn:
        conn.execute("DELETE FROM receitas WHERE descricao='Temp'")
        conn.commit()

    with get_connection() as conn:
        result = conn.execute("SELECT * FROM receitas WHERE descricao='Temp'").fetchone()
        assert result is None


def test_commit_multiplos_inserts(temp_db):
    """Verifica que multiplos inserts em uma transacao persistem."""
    with get_connection() as conn:
        for i in range(5):
            conn.execute(
                "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
                (f"Item {i}", float(i * 100), "2025-01-01", None),
            )
        conn.commit()

    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM receitas").fetchone()[0]
        assert count == 5


def test_rollback_sem_commit(temp_db):
    """Verifica que sem commit, dados nao persistem."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Nao Persiste", 100.00, "2025-01-01", None),
        )
        # Nao faz commit - o context manager faz rollback

    with get_connection() as conn:
        result = conn.execute("SELECT * FROM receitas WHERE descricao='Nao Persiste'").fetchone()
        assert result is None


def test_categoria_cascade_delete(temp_db):
    """Verifica que deletar categoria com SET NULL funciona."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO categorias (nome, cor, tipo) VALUES (?, ?, ?)",
            ("Teste Cat", "#ff0000", "receita"),
        )
        cat_id = conn.execute("SELECT id FROM categorias WHERE nome='Teste Cat'").fetchone()[0]

        conn.execute(
            "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
            ("Teste Rec", 100.00, "2025-01-01", cat_id),
        )
        conn.commit()

    # Deleta a categoria
    with get_connection() as conn:
        conn.execute("DELETE FROM categorias WHERE id=?", (cat_id,))
        conn.commit()

    # Verifica que a receita ainda existe mas com categoria_id = NULL
    with get_connection() as conn:
        result = conn.execute("SELECT * FROM receitas WHERE descricao='Teste Rec'").fetchone()
        assert result is not None
        assert result["categoria_id"] is None


def test_orcamento_unique_constraint(temp_db):
    """Verifica que orcamento respeita UNIQUE(categoria_id, mes)."""
    with get_connection() as conn:
        # Pega uma categoria existente
        cat = conn.execute("SELECT id FROM categorias LIMIT 1").fetchone()
        cat_id = cat["id"]

        # Insere orcamento
        conn.execute(
            "INSERT INTO orcamento (categoria_id, limite, mes) VALUES (?, ?, ?)",
            (cat_id, 1000.00, "2025-01"),
        )
        conn.commit()

        # Tenta inserir duplicata - deve falhar
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO orcamento (categoria_id, limite, mes) VALUES (?, ?, ?)",
                (cat_id, 2000.00, "2025-01"),
            )
            conn.commit()


def test_wal_mode_ativado(temp_db):
    """Verifica que WAL mode esta ativo."""
    with get_connection() as conn:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"


def test_foreign_keys_ativadas(temp_db):
    """Verifica que foreign keys estao ativas."""
    with get_connection() as conn:
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1
