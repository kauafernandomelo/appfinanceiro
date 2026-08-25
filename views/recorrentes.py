import calendar
import logging
import sqlite3
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.toast import mostrar_toast
from constants import ITENS_POR_PAGINA
from database import get_connection
from utils import formatar_moeda, obter_mes_atual

logger = logging.getLogger("financeiro.recorrentes")


class RecorrentesView(BaseView):
    """View para gerenciar contas recorrentes (receitas e despesas que se repetem mensalmente)."""

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._pagina_atual = 0
        self._termo_busca = ""
        self._todos_registros = []
        self._criar_header()
        self._criar_formulario()
        self._criar_barra_busca()
        self._criar_lista()

    def _criar_header(self):
        """Construi o cabecalho da view com titulo e botao de gerar lancamentos."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Contas Recorrentes").pack(side="left")

        ctk.CTkButton(
            header,
            text="Gerar Lancamentos do Mes",
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors.get("yellow", "#fdcb6e"),
            hover_color="#e0b341",
            text_color="#000",
            command=self._gerar_mes,
        ).pack(side="right")

    def _criar_formulario(self):
        """Construi o formulario para adicionar novas contas recorrentes."""
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._criar_label(g, "Descricao*").grid(row=0, column=0, sticky="w")
        self.entry_desc = self._criar_entry(g, "Ex: Aluguel")
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Valor (R$)*").grid(row=0, column=1, sticky="w")
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Tipo").grid(row=0, column=2, sticky="w")
        self.combo_tipo = self._criar_combo(g, ["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Categoria").grid(row=0, column=3, sticky="w")
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, 5))

        self._criar_label(g, "Dia do Mes*").grid(row=0, column=4, sticky="w")
        self.entry_dia = self._criar_entry(g, "1-31")
        self.entry_dia.grid(row=1, column=4, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            g,
            text="+ Adicionar",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._adicionar,
        ).grid(row=1, column=5, sticky="ew")

    def _criar_barra_busca(self):
        """Construi a barra de busca e paginacao."""
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        barra.grid_columnconfigure(0, weight=1)

        self.entry_busca = self._criar_entry(barra, "Buscar contas recorrentes...")
        self.entry_busca.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._on_busca())

        self.lbl_pagina = ctk.CTkLabel(
            barra,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_dim", "#a0a0b0"),
        )
        self.lbl_pagina.grid(row=0, column=1, padx=(0, 8))

        self.btn_prev = ctk.CTkButton(
            barra,
            text="<",
            width=32,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors.get("border", "#2d2d44"),
            hover_color="#3d3d54",
            command=lambda: self._mudar_pagina(-1),
        )
        self.btn_prev.grid(row=0, column=2, padx=(0, 4))

        self.btn_next = ctk.CTkButton(
            barra,
            text=">",
            width=32,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors.get("border", "#2d2d44"),
            hover_color="#3d3d54",
            command=lambda: self._mudar_pagina(1),
        )
        self.btn_next.grid(row=0, column=3)

    def _criar_lista(self):
        """Construi a area de exibicao da lista de contas recorrentes."""
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._atualizar()

    def _cats(self):
        """Retorna a lista de categorias disponiveis."""
        try:
            with get_connection() as conn:
                cats = conn.execute(
                    "SELECT nome FROM categorias ORDER BY nome"
                ).fetchall()
            return [c["nome"] for c in cats] if cats else ["Sem categoria"]
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            return ["Sem categoria"]

    def _on_busca(self):
        """Lida com a busca em tempo real, filtrando registros."""
        self._termo_busca = self.entry_busca.get().strip().lower()
        self._pagina_atual = 0
        self._atualizar()

    def _mudar_pagina(self, direcao):
        """Muda a pagina atual da listagem."""
        total_paginas = self._total_paginas()
        nova_pagina = self._pagina_atual + direcao
        if 0 <= nova_pagina < total_paginas:
            self._pagina_atual = nova_pagina
            self._atualizar()

    def _total_paginas(self):
        """Calcula o total de paginas com base nos registros filtrados."""
        registros_filtrados = self._filtrar_registros(self._todos_registros)
        total = len(registros_filtrados)
        if total == 0:
            return 1
        return (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA

    def _filtrar_registros(self, registros):
        """Filtra registros com base no termo de busca."""
        if not self._termo_busca:
            return registros
        resultado = []
        for r in registros:
            descricao = r["descricao"].lower()
            categoria = r["cat"].lower()
            tipo = r["tipo"].lower()
            if (
                self._termo_busca in descricao
                or self._termo_busca in categoria
                or self._termo_busca in tipo
            ):
                resultado.append(r)
        return resultado

    def _adicionar(self):
        """Adiciona uma nova conta recorrente ao banco de dados."""
        desc = self.entry_desc.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        cat = self.combo_cat.get()
        dia = self.entry_dia.get().strip()

        if not self._validar_campos({"Descricao": desc, "Valor": val_str, "Dia": dia}):
            return
        val = self._validar_valor(val_str)
        if val is None:
            return
        try:
            dia_int = int(dia)
            if not 1 <= dia_int <= 31:
                raise ValueError
        except ValueError:
            mostrar_toast(self, "Dia invalido! Use 1-31", "erro")
            return

        try:
            with get_connection() as conn:
                c = conn.execute(
                    "SELECT id FROM categorias WHERE nome=?", (cat,)
                ).fetchone()
                cid = c["id"] if c else None
                conn.execute(
                    "INSERT INTO recorrentes (descricao,valor,tipo,categoria_id,dia_mes) VALUES (?,?,?,?,?)",
                    (desc, val, tipo, cid, dia_int),
                )
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao adicionar recorrente: %s", e)
            mostrar_toast(self, f"Erro ao adicionar: {e}", "erro")
            return

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")
        mostrar_toast(self, f"'{desc}' adicionada!")
        self._atualizar()

    def _gerar_mes(self):
        """Gera os lancamentos do mes atual para todas as contas recorrentes ativas."""
        mes = obter_mes_atual()
        ano_num = datetime.now().year
        mes_num = datetime.now().month
        dias_no_mes = calendar.monthrange(ano_num, mes_num)[1]

        try:
            with get_connection() as conn:
                ativos = conn.execute(
                    "SELECT * FROM recorrentes WHERE ativo=1"
                ).fetchall()

                if not ativos:
                    mostrar_toast(self, "Nenhuma conta recorrente ativa!", "erro")
                    return

                gerados = 0
                for r in ativos:
                    dia = min(r["dia_mes"], dias_no_mes)
                    data = f"{ano_num}-{mes_num:02d}-{dia:02d}"
                    cat = conn.execute(
                        "SELECT id FROM categorias WHERE id=?", (r["categoria_id"],)
                    ).fetchone()
                    cid = cat["id"] if cat else None

                    if r["tipo"] == "receita":
                        conn.execute(
                            "INSERT INTO receitas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                            (r["descricao"], r["valor"], data, cid),
                        )
                    else:
                        conn.execute(
                            "INSERT INTO despesas (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                            (r["descricao"], r["valor"], data, cid),
                        )
                    gerados += 1

                conn.commit()

            mostrar_toast(self, f"{gerados} lancamentos gerados para {mes}!")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao gerar lancamentos: %s", e)
            mostrar_toast(self, f"Erro ao gerar lancamentos: {e}", "erro")

    def _atualizar(self):
        """Atualiza a lista de contas recorrentes exibida na tela."""
        for w in self.lista.winfo_children():
            w.destroy()

        try:
            with get_connection() as conn:
                self._todos_registros = conn.execute(
                    "SELECT r.id, r.descricao, r.valor, r.tipo, r.dia_mes, r.ativo, "
                    "COALESCE(c.nome,'Sem categoria') as cat "
                    "FROM recorrentes r LEFT JOIN categorias c ON r.categoria_id=c.id "
                    "ORDER BY r.tipo, r.dia_mes"
                ).fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar recorrentes: %s", e)
            self._todos_registros = []

        registros_filtrados = self._filtrar_registros(self._todos_registros)
        total_registros = len(registros_filtrados)
        total_paginas = self._total_paginas()

        if not registros_filtrados:
            msg = (
                "Nenhuma conta recorrente encontrada"
                if self._termo_busca
                else "Nenhuma conta recorrente\n\nAdicione contas que se repetem todo mes"
            )
            ctk.CTkLabel(
                self.lista,
                text=msg,
                text_color=self.colors.get("text_dim", "#a0a0a0"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=60)
            self._atualizar_paginacao(total_registros, total_paginas)
            return

        hdr = ctk.CTkFrame(self.lista, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col, txt in enumerate(
            ["Descricao", "Tipo", "Categoria", "Dia", "Valor", "Status", ""]
        ):
            self._criar_label(
                hdr, txt, font=ctk.CTkFont(size=10, weight="bold")
            ).grid(row=0, column=col, padx=8)

        inicio = self._pagina_atual * ITENS_POR_PAGINA
        fim = min(inicio + ITENS_POR_PAGINA, total_registros)
        registros_pagina = registros_filtrados[inicio:fim]

        for i, r in enumerate(registros_pagina):
            row = ctk.CTkFrame(
                self.lista,
                fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                corner_radius=8,
                height=42,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(
                row,
                text=r["descricao"],
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=0, padx=8, pady=8, sticky="w")

            tc = (
                self.colors.get("green", "#00b894")
                if r["tipo"] == "receita"
                else self.colors.get("red", "#d63031")
            )
            badge = ctk.CTkFrame(row, fg_color=tc, corner_radius=10)
            badge.grid(row=0, column=1, padx=6, pady=8)
            ctk.CTkLabel(
                badge,
                text=r["tipo"].capitalize(),
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color="#fff",
            ).pack(padx=8, pady=2)

            ctk.CTkLabel(
                row,
                text=r["cat"],
                font=ctk.CTkFont(size=11),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=2, padx=8, pady=8, sticky="w")

            ctk.CTkLabel(
                row,
                text=f"Dia {r['dia_mes']}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=3, padx=8, pady=8, sticky="w")

            ctk.CTkLabel(
                row,
                text=formatar_moeda(r["valor"]),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=tc,
            ).grid(row=0, column=4, padx=8, pady=8, sticky="w")

            st = "Ativo" if r["ativo"] else "Inativo"
            sc = (
                self.colors.get("green", "#00b894")
                if r["ativo"]
                else self.colors.get("text_dim", "#a0a0a0")
            )
            ctk.CTkButton(
                row,
                text=st,
                width=52,
                height=26,
                corner_radius=6,
                font=ctk.CTkFont(size=10),
                fg_color=sc,
                hover_color="#00a884",
                command=lambda rid=r["id"], at=r["ativo"]: self._toggle(rid, at),
            ).grid(row=0, column=5, padx=6, pady=8)

            ctk.CTkButton(
                row,
                text="X",
                width=26,
                height=26,
                corner_radius=6,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color="#c0392b",
                command=lambda rid=r["id"]: self._excluir(rid),
            ).grid(row=0, column=6, padx=8, pady=8)

        self._atualizar_paginacao(total_registros, total_paginas)

    def _atualizar_paginacao(self, total_registros, total_paginas):
        """Atualiza os controles de paginacao e o label informativo."""
        inicio = self._pagina_atual * ITENS_POR_PAGINA + 1
        fim = min((self._pagina_atual + 1) * ITENS_POR_PAGINA, total_registros)

        if total_registros == 0:
            self.lbl_pagina.configure(text="0 de 0")
        else:
            self.lbl_pagina.configure(
                text=f"{inicio}-{fim} de {total_registros}"
            )

        if self._pagina_atual <= 0:
            self.btn_prev.configure(state="disabled")
        else:
            self.btn_prev.configure(state="normal")

        if self._pagina_atual >= total_paginas - 1:
            self.btn_next.configure(state="disabled")
        else:
            self.btn_next.configure(state="normal")

    def _toggle(self, rid, atual):
        """Alterna o status ativo/inativo de uma conta recorrente."""
        try:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE recorrentes SET ativo=? WHERE id=?",
                    (0 if atual else 1, rid),
                )
                conn.commit()
            mostrar_toast(self, "Status atualizado!")
            self._atualizar()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao atualizar recorrente: %s", e)
            mostrar_toast(self, f"Erro ao atualizar: {e}", "erro")

    def _excluir(self, rid):
        """Exclui uma conta recorrente do banco de dados apos confirmacao."""
        if self._confirmar_exclusao(
            "Excluir Recorrente", "Deseja excluir esta conta?"
        ):
            try:
                with get_connection() as conn:
                    conn.execute("DELETE FROM recorrentes WHERE id=?", (rid,))
                    conn.commit()
                mostrar_toast(self, "Conta excluida!", "sucesso")
                self._atualizar()
            except (sqlite3.Error, ValueError) as e:
                logger.error("Erro ao excluir recorrente: %s", e)
                mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
