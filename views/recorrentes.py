"""View de Contas Recorrentes - Dark Premium."""

import calendar
import logging
import sqlite3
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.empty_state import EmptyState
from components.pagination import PaginationBar
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import (
    ACTION_BUTTON_SIZE,
    BUTTON_CORNER_RADIUS,
    FONT_BODY,
    FONT_LABEL,
    FONT_SMALL,
    ICONS,
    ITENS_POR_PAGINA,
    ROW_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
)
from database import get_connection
from utils import formatar_moeda

logger = logging.getLogger("financeiro.recorrentes")


class RecorrentesView(BaseView):
    """View de contas recorrentes com geracao mensal."""

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._pagina = 1
        self._todos = []
        self._criar_header()
        self._criar_formulario()
        self._criar_barra_busca()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, "Contas Recorrentes").pack(side="left")

        ctk.CTkButton(
            header, text=f"{ICONS['recorrentes']} Gerar Mes",
            height=36, corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._gerar_mes,
        ).pack(side="right")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=SPACING_XL, pady=SPACING_XL)
        g.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._criar_label(g, "Descricao*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        self.entry_desc = self._criar_entry(g, "Ex: Aluguel, Netflix...")
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Valor (R$)*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=1, sticky="w", pady=(0, SPACING_SM))
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Tipo*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=2, sticky="w", pady=(0, SPACING_SM))
        self.combo_tipo = self._criar_combo(g, ["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Categoria", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=3, sticky="w", pady=(0, SPACING_SM))
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=3, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Dia do Mes*", font=ctk.CTkFont(size=FONT_LABEL)).grid(
            row=0, column=4, sticky="w", pady=(0, SPACING_SM))
        self.entry_dia = self._criar_entry(g, "1-31")
        self.entry_dia.grid(row=1, column=4, sticky="ew", padx=(0, SPACING_SM))

        ctk.CTkButton(
            g, text=f"{ICONS['add']} Adicionar", height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        ).grid(row=1, column=5, sticky="ew")

    def _criar_barra_busca(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", pady=(0, SPACING_SM))
        bar.grid_columnconfigure(0, weight=1)

        self.entry_busca = self._criar_entry(bar, f"{ICONS['search']} Buscar...")
        self.entry_busca.grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar())

        self.pagination = PaginationBar(
            bar, colors=self.colors, on_page_change=self._mudar_pagina,
        )
        self.pagination.grid(row=0, column=1, sticky="e")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._carregar_dados()

    def _cats(self):
        try:
            with get_connection() as conn:
                cats = conn.execute("SELECT nome FROM categorias ORDER BY nome").fetchall()
            return [c["nome"] for c in cats] if cats else ["Sem categoria"]
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            return ["Sem categoria"]

    def _carregar_dados(self):
        try:
            with get_connection() as conn:
                self._todos = conn.execute("SELECT * FROM recorrentes ORDER BY descricao").fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar recorrentes: %s", e)
            self._todos = []
        self._filtrar()

    def _filtrar(self):
        busca = self.entry_busca.get().strip().lower()
        filtrados = []
        for r in self._todos:
            if busca and busca not in r["descricao"].lower():
                continue
            filtrados.append(r)

        total = len(filtrados)
        total_pag = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
        self._pagina = min(self._pagina, total_pag)

        inicio = (self._pagina - 1) * ITENS_POR_PAGINA
        fim = min(inicio + ITENS_POR_PAGINA, total)
        pagina_dados = filtrados[inicio:fim]

        self.pagination.atualizar(self._pagina, total_pag, total, inicio + 1, fim)
        self._renderizar(pagina_dados)

    def _mudar_pagina(self, nova_pagina):
        self._pagina = nova_pagina
        self._filtrar()

    def _renderizar(self, dados):
        for w in self.lista.winfo_children():
            w.destroy()

        if not dados:
            EmptyState(
                self.lista, icone=ICONS["recorrentes"],
                titulo="Nenhuma recorrente cadastrada",
                subtitulo="Adicione contas que se repetem mensalmente",
                colors=self.colors,
            ).grid(row=0, column=0, pady=40)
            return

        # Header
        hdr = ctk.CTkFrame(
            self.lista, fg_color=self.colors.get("bg_card", "#161630"),
            corner_radius=BUTTON_CORNER_RADIUS, height=36,
        )
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_SM))
        hdr.grid_propagate(False)

        for col, txt in enumerate(["Descricao", "Tipo", "Valor", "Dia", "Ativo", ""]):
            ctk.CTkLabel(
                hdr, text=txt,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).grid(row=0, column=col, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

        for i, r in enumerate(dados):
            row_bg = (self.colors.get("bg_card", "#161630") if i % 2 == 0
                      else self.colors.get("bg_elevated", "#1e1e3a"))
            row = ctk.CTkFrame(
                self.lista, fg_color=row_bg,
                corner_radius=BUTTON_CORNER_RADIUS, height=ROW_HEIGHT,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

            def on_enter(e, r=row):
                r.configure(fg_color=self.colors.get("bg_hover", "#252550"))
            def on_leave(e, r=row, bg=row_bg):
                r.configure(fg_color=bg)
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

            ctk.CTkLabel(
                row, text=r["descricao"],
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).grid(row=0, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            tipo_cor = self.colors.get("positive", "#00b894") if r["tipo"] == "receita" else self.colors.get("negative", "#d63031")
            self._criar_status_badge(row, r["tipo"], tipo_cor).grid(
                row=0, column=1, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            ctk.CTkLabel(
                row, text=formatar_moeda(r["valor"]),
                font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).grid(row=0, column=2, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            ctk.CTkLabel(
                row, text=str(r["dia_mes"]),
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=0, column=3, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            status_text = "Ativo" if r["ativo"] else "Inativo"
            status_cor = self.colors.get("positive", "#00b894") if r["ativo"] else self.colors.get("text_dim", "#606078")
            self._criar_status_badge(row, status_text, status_cor).grid(
                row=0, column=4, padx=SPACING_MD, pady=SPACING_SM, sticky="w")

            # Botoes
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=5, padx=SPACING_MD, pady=SPACING_SM)

            btn_toggle = ctk.CTkButton(
                btn_frame,
                text=ICONS["check"] if r["ativo"] else ICONS["close"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL),
                fg_color=self.colors.get("positive", "#00b894") if r["ativo"]
                else self.colors.get("text_dim", "#606078"),
                hover_color=self.colors.get("positive_muted", "#00875f"),
                command=lambda rid=r["id"], ativo=r["ativo"]: self._toggle(rid, ativo),
            )
            btn_toggle.pack(side="left", padx=2)
            Tooltip(btn_toggle, "Ativar/Desativar", self.colors)

            btn_excluir = ctk.CTkButton(
                btn_frame, text=ICONS["delete"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                fg_color=self.colors.get("negative", "#d63031"),
                hover_color=self.colors.get("negative_muted", "#a32525"),
                command=lambda rid=r["id"]: self._excluir(rid),
            )
            btn_excluir.pack(side="left", padx=2)
            Tooltip(btn_excluir, "Excluir", self.colors)

    def _salvar(self):
        desc = self.entry_desc.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        dia_str = self.entry_dia.get().strip()

        if not self._validar_campos({"Descricao": desc, "Valor": val_str, "Dia": dia_str}):
            return
        val = self._validar_valor(val_str)
        if val is None:
            return

        try:
            dia = int(dia_str)
            if dia < 1 or dia > 31:
                raise ValueError
        except ValueError:
            mostrar_toast(self, "Dia invalido! Use 1-31.", "erro")
            return

        cat = self.combo_cat.get()
        try:
            with get_connection() as conn:
                c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
                cid = c["id"] if c else None
                conn.execute(
                    "INSERT INTO recorrentes (descricao, valor, tipo, categoria_id, dia_mes) VALUES (?, ?, ?, ?, ?)",
                    (desc, val, tipo, cid, dia),
                )
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao salvar recorrente: %s", e)
            mostrar_toast(self, f"Erro ao salvar: {e}", "erro")
            return

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")
        mostrar_toast(self, f"Recorrente '{desc}' adicionada!")
        self._carregar_dados()

    def _toggle(self, rid, atual):
        try:
            with get_connection() as conn:
                conn.execute("UPDATE recorrentes SET ativo=? WHERE id=?", (0 if atual else 1, rid))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao alterar recorrente: %s", e)
            mostrar_toast(self, f"Erro: {e}", "erro")
            return
        self._carregar_dados()

    def _excluir(self, rid):
        if not self._confirmar_exclusao("Excluir Recorrente", "Deseja excluir esta recorrente?"):
            return
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM recorrentes WHERE id=?", (rid,))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao excluir recorrente: %s", e)
            mostrar_toast(self, f"Erro ao excluir: {e}", "erro")
            return
        mostrar_toast(self, "Recorrente excluida!")
        self._carregar_dados()

    def _gerar_mes(self):
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month
        dias_no_mes = calendar.monthrange(ano, mes)[1]

        try:
            with get_connection() as conn:
                ativos = conn.execute("SELECT * FROM recorrentes WHERE ativo=1").fetchall()
                if not ativos:
                    mostrar_toast(self, "Nenhuma recorrente ativa.", "aviso")
                    return

                gerados = 0
                for r in ativos:
                    dia = min(r["dia_mes"], dias_no_mes)
                    data = f"{ano}-{mes:02d}-{dia:02d}"

                    # Verificar duplicata
                    if r["tipo"] == "receita":
                        existe = conn.execute(
                            "SELECT COUNT(*) FROM receitas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                            (r["descricao"], f"{ano}-{mes:02d}"),
                        ).fetchone()[0]
                    else:
                        existe = conn.execute(
                            "SELECT COUNT(*) FROM despesas WHERE descricao=? AND strftime('%Y-%m',data)=?",
                            (r["descricao"], f"{ano}-{mes:02d}"),
                        ).fetchone()[0]

                    if existe > 0:
                        continue

                    cat = conn.execute("SELECT id FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
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

            if gerados > 0:
                mostrar_toast(self, f"{gerados} lancamentos gerados!")
            else:
                mostrar_toast(self, "Todos os lancamentos ja foram gerados.", "aviso")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao gerar recorrentes: %s", e)
            mostrar_toast(self, f"Erro ao gerar: {e}", "erro")
