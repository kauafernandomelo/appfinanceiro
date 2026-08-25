import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "financeiro.db"


CATEGORIAS_PADRAO = [
    ("Salario", "#00b894", "receita"),
    ("Freelance", "#00cec9", "receita"),
    ("Investimentos", "#6c5ce7", "receita"),
    ("Outros Receita", "#a29bfe", "receita"),
    ("Alimentacao", "#d63031", "despesa"),
    ("Transporte", "#e17055", "despesa"),
    ("Moradia", "#fdcb6e", "despesa"),
    ("Saude", "#00b894", "despesa"),
    ("Educacao", "#0984e3", "despesa"),
    ("Lazer", "#e84393", "despesa"),
    ("Vestuario", "#fd79a8", "despesa"),
    ("Contas Fixas", "#636e72", "despesa"),
    ("Outros Despesa", "#b2bec3", "despesa"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            cor TEXT DEFAULT '#3B82F6',
            tipo TEXT CHECK(tipo IN ('receita', 'despesa')) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS investimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor_investido REAL NOT NULL,
            valor_atual REAL NOT NULL,
            data TEXT NOT NULL,
            cor TEXT DEFAULT '#6c5ce7',
            observacao TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS orcamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            limite REAL NOT NULL,
            mes TEXT NOT NULL,
            UNIQUE(categoria_id, mes),
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_alvo REAL NOT NULL,
            valor_atual REAL DEFAULT 0,
            prazo TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recorrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT CHECK(tipo IN ('receita', 'despesa')) NOT NULL,
            categoria_id INTEGER,
            dia_mes INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );
    """)

    existe = c.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
    if existe == 0:
        c.executemany(
            "INSERT INTO categorias (nome, cor, tipo) VALUES (?, ?, ?)",
            CATEGORIAS_PADRAO,
        )

    conn.commit()
    conn.close()
