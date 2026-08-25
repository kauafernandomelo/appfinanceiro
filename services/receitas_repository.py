from database import get_connection


class ReceitaRepository:
    """Repository para operacoes de receitas."""

    @staticmethod
    def buscar(mes: str = None, busca: str = None, categoria: str = None) -> list:
        """Busca receitas com filtros opcionais."""
        query = """
            SELECT r.id, r.descricao, r.valor, r.data,
                   COALESCE(c.nome, 'Sem categoria') as cat,
                   COALESCE(c.cor, '#3B82F6') as cat_cor
            FROM receitas r
            LEFT JOIN categorias c ON r.categoria_id = c.id
            WHERE 1=1
        """
        params = []

        if mes:
            query += " AND strftime('%Y-%m', r.data) = ?"
            params.append(mes)
        if busca:
            query += " AND r.descricao LIKE ?"
            params.append(f"%{busca}%")
        if categoria and categoria != "Todas":
            query += " AND c.nome = ?"
            params.append(categoria)

        query += " ORDER BY r.data DESC"

        with get_connection() as conn:
            return conn.execute(query, params).fetchall()

    @staticmethod
    def total_mes(mes: str) -> float:
        """Retorna o total de receitas do mes."""
        with get_connection() as conn:
            return conn.execute(
                "SELECT COALESCE(SUM(valor), 0) FROM receitas WHERE strftime('%Y-%m', data) = ?",
                (mes,),
            ).fetchone()[0]

    @staticmethod
    def criar(descricao: str, valor: float, data: str, categoria_id: int | None) -> int:
        """Cria uma nova receita. Retorna o ID."""
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
                (descricao, valor, data, categoria_id),
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def atualizar(rid: int, descricao: str, valor: float, data: str, categoria_id: int | None) -> None:
        """Atualiza uma receita existente."""
        with get_connection() as conn:
            conn.execute(
                "UPDATE receitas SET descricao=?, valor=?, data=?, categoria_id=? WHERE id=?",
                (descricao, valor, data, categoria_id, rid),
            )
            conn.commit()

    @staticmethod
    def excluir(rid: int) -> None:
        """Exclui uma receita."""
        with get_connection() as conn:
            conn.execute("DELETE FROM receitas WHERE id=?", (rid,))
            conn.commit()

    @staticmethod
    def obter_por_id(rid: int) -> dict | None:
        """Obtem uma receita pelo ID."""
        with get_connection() as conn:
            return conn.execute("SELECT * FROM receitas WHERE id=?", (rid,)).fetchone()

    @staticmethod
    def ultimas(limite: int = 5) -> list:
        """Retorna as ultimas receitas."""
        with get_connection() as conn:
            return conn.execute(
                """SELECT r.id, r.descricao, r.valor, r.data,
                          COALESCE(c.nome, 'Sem categoria') as cat
                   FROM receitas r
                   LEFT JOIN categorias c ON r.categoria_id = c.id
                   ORDER BY r.data DESC LIMIT ?""",
                (limite,),
            ).fetchall()

    @staticmethod
    def inserir_lote(lotes: list[tuple]) -> int:
        """Insere multiplos lancamentos de uma vez. Retorna quantos foram inseridos."""
        with get_connection() as conn:
            conn.executemany(
                "INSERT INTO receitas (descricao, valor, data, categoria_id) VALUES (?, ?, ?, ?)",
                lotes,
            )
            conn.commit()
            return len(lotes)
