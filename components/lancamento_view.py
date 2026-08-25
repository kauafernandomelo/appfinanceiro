import calendar
import logging
import sqlite3
from datetime import datetime

import customtkinter as ctk

from components.base_view import BaseView
from components.datepicker import DatePicker
from components.empty_state import EmptyState
from components.pagination import PaginationBar
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from constants import (
    ACTION_BUTTON_SIZE,
    BUTTON_CORNER_RADIUS,
    FONT_BODY,
    FONT_SMALL,
    ICONS,
    ITENS_POR_PAGINA,
    ROW_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
)
from database import get_connection
from utils import formatar_moeda, obter_data_atual, validar_data

logger = logging.getLogger("financeiro.lancamento_view")


class LancamentoView(BaseView):
    """View generica para lancamentos (receitas ou despesas)."""

    TIPO = "receita"
    TITULO = "Receitas"
    COR = "#00b894"
    COR_HOVER = "#00a884"
    CATEGORIA_TIPO = "receita"
    ICONE = "💰"

    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(3, weight=1)
        self._edit_id = None
        self._page = 1
        self._criar_header()
        self._criar_formulario()
        self._criar_search()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_LG))
        self._criar_titulo(header, self.TITULO).pack(side="left")
        self.lbl_total = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors.get("green" if self.TIPO == "receita" else "red", self.COR),
        )
        self.lbl_total.pack(side="right")
        self._atualizar_total()

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, SPACING_MD))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=SPACING_LG, pady=SPACING_LG)
        g.grid_columnconfigure((0, 1, 2, 3), weight=1)

        placeholder_desc = "Ex: Salario, Freelance..." if self.TIPO == "receita" else "Ex: Aluguel, Supermercado..."

        self._criar_label(g, "Descricao*").grid(row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        self.entry_desc = self._criar_entry(g, placeholder_desc)
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Valor (R$)*").grid(row=0, column=1, sticky="w", pady=(0, SPACING_SM))
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Data*").grid(row=0, column=2, sticky="w", pady=(0, SPACING_SM))
        self.dp_data = DatePicker(g, colors=self.colors)
        self.dp_data.grid(row=1, column=2, sticky="ew", padx=(0, SPACING_SM))

        self._criar_label(g, "Categoria").grid(row=0, column=3, sticky="w", pady=(0, SPACING_SM))
        self.combo_cat = self._criar_combo(g, self._cats())
        self.combo_cat.grid(row=1, column=3, sticky="ew")

        self._criar_label(g, "Parcelas").grid(row=2, column=0, sticky="w", pady=(0, SPACING_SM))
        parcelas_frame = ctk.CTkFrame(g, fg_color="transparent")
        parcelas_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, SPACING_SM))
        parcelas_frame.grid_columnconfigure(1, weight=1)

        self.chk_parcelado = ctk.CTkCheckBox(
            parcelas_frame, text="Parcelar?",
            font=ctk.CTkFont(size=FONT_BODY),
            text_color=self.colors.get("text_dim", "#a0a0a0"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._toggle_parcelas,
        )
        self.chk_parcelado.grid(row=0, column=0, sticky="w", padx=(0, SPACING_SM))
        self.entry_parcelas = self._criar_entry(parcelas_frame, "3x")
        self.entry_parcelas.grid(row=0, column=1, sticky="ew")
        self.entry_parcelas.configure(state="disabled")

        self.btn_add = ctk.CTkButton(
            g, text=f"{ICONS['add']} Adicionar",
            height=38, corner_radius=BUTTON_CORNER_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._salvar,
        )
        self.btn_add.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(SPACING_SM, 0))

    def _toggle_parcelas(self):
        if self.chk_parcelado.get():
            self.entry_parcelas.configure(state="normal")
        else:
            self.entry_parcelas.configure(state="disabled")

    def _criar_search(self):
        search_card = self._criar_card_frame(self)
        search_card.grid(row=2, column=0, sticky="ew", pady=(0, SPACING_SM))
        sg = ctk.CTkFrame(search_card, fg_color="transparent")
        sg.pack(fill="x", padx=SPACING_MD, pady=SPACING_SM)
        sg.grid_columnconfigure(0, weight=3)
        sg.grid_columnconfigure(1, weight=1)

        placeholder_search = f"{ICONS['search']}  Buscar {self.TIPO}..."
        self.entry_search = self._criar_entry(sg, placeholder_search)
        self.entry_search.grid(row=0, column=0, sticky="ew", padx=(0, SPACING_SM))
        self.entry_search.bind("<KeyRelease>", lambda e: self._filtrar())

        cats = ["Todas"] + [c for c in self._cats() if c != "Sem categoria"]
        self.combo_filtro_cat = self._criar_combo(sg, cats, command=lambda v: self._filtrar())
        self.combo_filtro_cat.grid(row=0, column=1, sticky="ew")
        self.combo_filtro_cat.set("Todas")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=3, column=0, sticky="nsew")
        self._carregar_dados()

    def _cats(self):
        try:
            with get_connection() as conn:
                cats = conn.execute(
                    "SELECT nome FROM categorias WHERE tipo=? ORDER BY nome",
                    (self.CATEGORIA_TIPO,),
                ).fetchall()
            return [c["nome"] for c in cats] if cats else ["Sem categoria"]
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar categorias: %s", e)
            mostrar_toast(self, "Erro ao carregar categorias", "erro")
            return ["Sem categoria"]

    def _atualizar_total(self):
        try:
            with get_connection() as conn:
                t = conn.execute(
                    f"SELECT COALESCE(SUM(valor),0) FROM {self.TIPO}s WHERE strftime('%Y-%m',data)=?",
                    (obter_data_atual()[:7],),
                ).fetchone()[0]
            self.lbl_total.configure(text=f"Total: {formatar_moeda(t)}")
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao calcular total: %s", e)
            mostrar_toast(self, "Erro ao calcular total", "erro")

    def _salvar(self):
        desc = self.entry_desc.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        data = self.dp_data.get()

        if not self._validar_campos({"Descricao": desc, "Valor": val_str, "Data": data}):
            return
        if not validar_data(data):
            mostrar_toast(self, "Data invalida! Use AAAA-MM-DD", "erro")
            return
        val = self._validar_valor(val_str)
        if val is None:
            return

        cat = self.combo_cat.get()
        parcelado = self.chk_parcelado.get()
        tabela = f"{self.TIPO}s"

        try:
            with get_connection() as conn:
                c = conn.execute("SELECT id FROM categorias WHERE nome=?", (cat,)).fetchone()
                cid = c["id"] if c else None

                if self._edit_id:
                    conn.execute(
                        f"UPDATE {tabela} SET descricao=?,valor=?,data=?,categoria_id=? WHERE id=?",
                        (desc, val, data, cid, self._edit_id),
                    )
                    conn.commit()
                    mostrar_toast(self, f"{self.TITULO[:-1].title()} '{desc}' atualizada!")
                    self._edit_id = None
                    self.btn_add.configure(
                        text=f"{ICONS['add']} Adicionar",
                        fg_color=self.colors.get("primary", "#6c5ce7"),
                    )
                elif parcelado:
                    n_str = self.entry_parcelas.get().replace("x", "").replace("X", "").strip()
                    if not n_str or not n_str.isdigit() or int(n_str) < 2:
                        mostrar_toast(self, "Informe o numero de parcelas (minimo 2)", "erro")
                        return
                    n = int(n_str)
                    valor_parcela = round(val / n, 2)
                    dt = datetime.strptime(data, "%Y-%m-%d")
                    for i in range(n):
                        m = dt.month + i
                        y = dt.year + (m - 1) // 12
                        m = (m - 1) % 12 + 1
                        d = min(dt.day, calendar.monthrange(y, m)[1])
                        data_parcela = f"{y:04d}-{m:02d}-{d:02d}"
                        desc_p = f"{desc} ({i+1}/{n})"
                        if i == 0:
                            diff = round(val - valor_parcela * n, 2)
                            valor_p = valor_parcela + diff
                        else:
                            valor_p = valor_parcela
                        conn.execute(
                            f"INSERT INTO {tabela} (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                            (desc_p, valor_p, data_parcela, cid),
                        )
                    conn.commit()
                    mostrar_toast(self, f"{n} parcelas de {formatar_moeda(valor_parcela)} criadas!")
                else:
                    conn.execute(
                        f"INSERT INTO {tabela} (descricao,valor,data,categoria_id) VALUES (?,?,?,?)",
                        (desc, val, data, cid),
                    )
                    conn.commit()
                    mostrar_toast(self, f"{self.TITULO[:-1].title()} '{desc}' adicionada!")

            self.entry_desc.delete(0, "end")
            self.entry_valor.delete(0, "end")
            self.dp_data.set(obter_data_atual())
            self.chk_parcelado.deselect()
            self.entry_parcelas.delete(0, "end")
            self.entry_parcelas.configure(state="disabled")
            self._carregar_dados()
            self._atualizar_total()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao salvar lancamento: %s", e)
            mostrar_toast(self, "Erro ao salvar", "erro")

    def _editar(self, rid):
        tabela = f"{self.TIPO}s"
        try:
            with get_connection() as conn:
                r = conn.execute(f"SELECT * FROM {tabela} WHERE id=?", (rid,)).fetchone()
                if not r:
                    return
                cat_name = None
                if r["categoria_id"]:
                    c = conn.execute("SELECT nome FROM categorias WHERE id=?", (r["categoria_id"],)).fetchone()
                    if c:
                        cat_name = c["nome"]

            self._edit_id = rid
            self.entry_desc.delete(0, "end")
            self.entry_desc.insert(0, r["descricao"])
            self.entry_valor.delete(0, "end")
            self.entry_valor.insert(0, str(r["valor"]))
            self.dp_data.set(r["data"])
            if cat_name:
                self.combo_cat.set(cat_name)
            self.btn_add.configure(
                text=f"{ICONS['check']} Salvar Edicao",
                fg_color=self.colors.get("primary", "#6c5ce7"),
            )
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar lancamento: %s", e)
            mostrar_toast(self, f"Erro ao carregar {self.TIPO}", "erro")

    def _excluir(self, rid):
        titulo_modal = f"Excluir {self.TITULO[:-1].title()}"
        msg_modal = f"Deseja excluir esta {self.TIPO}?"
        if self._confirmar_exclusao(titulo_modal, msg_modal):
            tabela = f"{self.TIPO}s"
            try:
                with get_connection() as conn:
                    conn.execute(f"DELETE FROM {tabela} WHERE id=?", (rid,))
                    conn.commit()
                mostrar_toast(self, f"{self.TIPO.title()} excluida!", "sucesso")
                self._carregar_dados()
                self._atualizar_total()
            except (sqlite3.Error, ValueError) as e:
                logger.error("Erro ao excluir lancamento: %s", e)
                mostrar_toast(self, "Erro ao excluir", "erro")

    def _carregar_dados(self):
        busca = self.entry_search.get().strip()
        filtro = self.combo_filtro_cat.get()
        tabela = f"{self.TIPO}s"

        try:
            with get_connection() as conn:
                query = f"""
                    SELECT r.id, r.descricao, r.valor, r.data,
                           COALESCE(c.nome,'Sem categoria') as cat
                    FROM {tabela} r
                    LEFT JOIN categorias c ON r.categoria_id=c.id
                    WHERE 1=1
                """
                params = []

                if busca:
                    query += " AND r.descricao LIKE ?"
                    params.append(f"%{busca}%")

                if filtro and filtro != "Todas":
                    query += " AND c.nome = ?"
                    params.append(filtro)

                count_query = f"SELECT COUNT(*) FROM ({query})"
                total = conn.execute(count_query, params).fetchone()[0]

                total_pages = max(1, (total + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)
                if self._page > total_pages:
                    self._page = total_pages

                query += " ORDER BY r.data DESC LIMIT ? OFFSET ?"
                params.extend([ITENS_POR_PAGINA, (self._page - 1) * ITENS_POR_PAGINA])
                rows = conn.execute(query, params).fetchall()

                self._renderizar(rows, total, total_pages)
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar dados: %s", e)
            mostrar_toast(self, "Erro ao carregar dados", "erro")
            self._renderizar([], 0, 1)

    def _filtrar(self):
        self._page = 1
        self._carregar_dados()

    def _renderizar(self, rows, total, total_pages):
        for w in self.lista.winfo_children():
            w.destroy()

        if not rows:
            EmptyState(
                self.lista,
                icone=ICONS["search"],
                titulo=f"Nenhum(a) {self.TIPO} encontrado(a)",
                subtitulo=f"Clique em '{ICONS['add']} Adicionar' acima para cadastrar",
                colors=self.colors,
            ).grid(row=0, column=0, pady=60)
            return

        hdr = ctk.CTkFrame(
            self.lista,
            fg_color=self.colors.get("bg_card", "#161630"),
            corner_radius=6, height=36,
        )
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING_SM))
        hdr.grid_propagate(False)

        colunas = ["Data", "Descricao", "Categoria", "Valor", "", ""]
        for col, txt in enumerate(colunas):
            ctk.CTkLabel(
                hdr, text=txt,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                text_color=self.colors.get("text_secondary", "#a0a0b8"),
            ).grid(row=0, column=col, padx=12, pady=4, sticky="w")

        start = (self._page - 1) * ITENS_POR_PAGINA
        end = min(start + ITENS_POR_PAGINA, total)

        for i, r in enumerate(rows):
            row_bg = (
                self.colors.get("bg_card", "#161630")
                if i % 2 == 0
                else self.colors.get("bg_elevated", "#1e1e3a")
            )
            row = ctk.CTkFrame(
                self.lista, fg_color=row_bg,
                corner_radius=BUTTON_CORNER_RADIUS, height=ROW_HEIGHT,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=r["data"],
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=0, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                row, text=r["descricao"],
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=self.colors.get("text", "#f0f0f8"),
            ).grid(row=0, column=1, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                row, text=r["cat"],
                font=ctk.CTkFont(size=FONT_SMALL),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=2, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(
                row, text=formatar_moeda(r["valor"]),
                font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
                text_color=self.colors.get("green", "#00b894") if self.TIPO == "receita"
                else self.colors.get("red", "#d63031"),
            ).grid(row=0, column=3, padx=12, pady=8, sticky="w")

            btn_edit = ctk.CTkButton(
                row, text=ICONS["edit"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=self.colors.get("primary", "#6c5ce7"),
                hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                command=lambda rid=r["id"]: self._editar(rid),
            )
            btn_edit.grid(row=0, column=4, padx=(SPACING_SM, SPACING_XS), pady=8)
            Tooltip(btn_edit, "Editar", self.colors)

            btn_del = ctk.CTkButton(
                row, text=ICONS["delete"],
                width=ACTION_BUTTON_SIZE, height=ACTION_BUTTON_SIZE,
                corner_radius=BUTTON_CORNER_RADIUS,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=self.colors.get("negative", "#d63031"),
                hover_color=self.colors.get("negative_muted", "#a32525"),
                command=lambda rid=r["id"]: self._excluir(rid),
            )
            btn_del.grid(row=0, column=5, padx=(SPACING_XS, SPACING_SM), pady=8)
            Tooltip(btn_del, "Excluir", self.colors)

            def on_enter(e, frame=row):
                frame.configure(fg_color=self.colors.get("bg_hover", "#252550"))

            def on_leave(e, frame=row, bg=row_bg):
                frame.configure(fg_color=bg)

            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)

        pag = PaginationBar(
            self.lista, colors=self.colors,
            on_page_change=lambda p: self._mudar_pagina_para(p),
        )
        pag.grid(row=len(rows) + 2, column=0, sticky="ew", pady=(SPACING_SM, SPACING_XS))
        pag.atualizar(self._page, total_pages, total, start + 1, end)

    def _mudar_pagina_para(self, page):
        self._page = page
        self._carregar_dados()

    def _mudar_pagina(self, delta):
        self._page += delta
        self._carregar_dados()
