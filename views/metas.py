import logging
import sqlite3

import customtkinter as ctk

from components.base_view import BaseView
from components.datepicker import DatePicker
from components.toast import mostrar_toast
from components.tooltip import Tooltip
from database import get_connection
from utils import formatar_moeda

logger = logging.getLogger("financeiro.metas")


class MetasView(BaseView):
    def __init__(self, master, colors=None):
        super().__init__(master, colors)
        self.grid_rowconfigure(2, weight=1)
        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self._criar_titulo(header, "Metas de Economia").pack(side="left")

    def _criar_formulario(self):
        form = self._criar_card_frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        g = ctk.CTkFrame(form, fg_color="transparent")
        g.pack(fill="x", padx=16, pady=14)
        g.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._criar_label(g, "Nome*").grid(row=0, column=0, sticky="w")
        self.entry_nome = self._criar_entry(g, "Ex: Viagem, Carro...")
        self.entry_nome.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Valor Alvo (R$)*").grid(row=0, column=1, sticky="w")
        self.entry_valor = self._criar_entry(g, "0,00")
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        self._criar_label(g, "Prazo*").grid(row=0, column=2, sticky="w")
        self.dp_prazo = DatePicker(g)
        self.dp_prazo.grid(row=1, column=2, sticky="ew", padx=(0, 6))

        ctk.CTkButton(g, text="+ Criar Meta", height=36, corner_radius=8,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=self.colors.get("primary", "#6c5ce7"),
                       hover_color=self.colors.get("primary_hover", "#5a4bd1"),
                       command=self._adicionar).grid(row=1, column=3, sticky="ew")

    def _criar_lista(self):
        self.container, self.lista = self._criar_lista_frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self._atualizar()

    def _adicionar(self):
        nome = self.entry_nome.get().strip()
        val_str = self.entry_valor.get().replace(",", ".").strip()
        prazo = self.dp_prazo.get()

        if not self._validar_campos({"Nome": nome, "Valor": val_str, "Prazo": prazo}):
            return
        val = self._validar_valor(val_str)
        if val is None:
            return

        try:
            with get_connection() as conn:
                conn.execute("INSERT INTO metas (nome,valor_alvo,valor_atual,prazo) VALUES (?, ?, 0, ?)",
                             (nome, val, prazo))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao criar meta: %s", e)
            mostrar_toast(self, f"Erro ao criar meta: {e}", "erro")
            return

        self.entry_nome.delete(0, "end")
        self.entry_valor.delete(0, "end")
        mostrar_toast(self, f"Meta '{nome}' criada!")
        self._atualizar()

    def _adicionar_valor_inline(self, mid, entry_widget):
        val_str = entry_widget.get().replace(",", ".").strip()
        if not val_str:
            mostrar_toast(self, "Informe um valor", "erro")
            return
        val = self._validar_valor(val_str)
        if val is None:
            return

        try:
            with get_connection() as conn:
                atual = conn.execute("SELECT valor_atual FROM metas WHERE id=?", (mid,)).fetchone()
                if not atual:
                    mostrar_toast(self, "Meta nao encontrada", "erro")
                    return
                novo_valor = atual["valor_atual"] + val
                conn.execute("UPDATE metas SET valor_atual=? WHERE id=?", (novo_valor, mid))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao adicionar valor: %s", e)
            mostrar_toast(self, f"Erro ao adicionar valor: {e}", "erro")
            return

        entry_widget.delete(0, "end")
        mostrar_toast(self, f"R$ {val:,.2f} adicionado!".replace(",", "X").replace(".", ",").replace("X", "."))
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        try:
            with get_connection() as conn:
                rows = conn.execute("SELECT id,nome,valor_alvo,valor_atual,prazo FROM metas ORDER BY prazo").fetchall()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao carregar metas: %s", e)
            mostrar_toast(self, f"Erro ao carregar metas: {e}", "erro")
            return

        if not rows:
            ctk.CTkLabel(self.lista, text="Nenhuma meta criada\n\nCrie uma meta para comecar a economizar!",
                          text_color=self.colors.get("text_dim", "#a0a0a0"),
                          font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=60)
            return

        for i, m in enumerate(rows):
            row = ctk.CTkFrame(self.lista, fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                corner_radius=8, height=90)
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(1, weight=1)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=0, padx=16, pady=10, sticky="w")
            ctk.CTkLabel(info, text=m["nome"], font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Prazo: {m['prazo']}", font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).pack(anchor="w")

            bf = ctk.CTkFrame(row, fg_color="transparent")
            bf.grid(row=0, column=1, padx=12, pady=10, sticky="ew")
            bf.grid_columnconfigure(0, weight=1)

            pct = (m["valor_atual"] / m["valor_alvo"] * 100) if m["valor_alvo"] > 0 else 0
            if pct >= 100:
                bc = self.colors.get("green", "#00b894")
            elif pct >= 50:
                bc = self.colors.get("yellow", "#fdcb6e")
            else:
                bc = self.colors.get("red", "#d63031")

            bar = ctk.CTkProgressBar(bf, progress_color=bc, height=8, corner_radius=4)
            bar.grid(row=0, column=0, sticky="ew")
            bar.set(min(pct / 100, 1.0))

            ctk.CTkLabel(bf, text=f"{formatar_moeda(m['valor_atual'])} / {formatar_moeda(m['valor_alvo'])}  ({pct:.0f}%)",
                          font=ctk.CTkFont(size=11),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(row=1, column=0, sticky="w", pady=(4, 0))

            add_frame = ctk.CTkFrame(bf, fg_color="transparent")
            add_frame.grid(row=2, column=0, sticky="ew", pady=(6, 0))
            add_frame.grid_columnconfigure(0, weight=1)

            entry_add = self._criar_entry(add_frame, "Valor...")
            entry_add.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            btn_add = ctk.CTkButton(add_frame, text="Adicionar", width=90, height=30, corner_radius=6,
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     fg_color=self.colors.get("green", "#00b894"), hover_color="#00a884",
                                     command=lambda mid=m["id"], e=entry_add: self._adicionar_valor_inline(mid, e))
            btn_add.grid(row=0, column=1)

            btns = ctk.CTkFrame(row, fg_color="transparent")
            btns.grid(row=0, column=2, padx=12, pady=10)

            btn_excluir = ctk.CTkButton(btns, text="✕", width=32, height=32, corner_radius=6,
                           font=ctk.CTkFont(size=12, weight="bold"),
                           fg_color=self.colors.get("red", "#d63031"), hover_color="#c0392b",
                           command=lambda mid=m["id"]: self._excluir(mid))
            btn_excluir.pack(side="left", padx=2)
            Tooltip(btn_excluir, "Excluir meta")

    def _excluir(self, mid):
        if not self._confirmar_exclusao("Excluir Meta", "Deseja excluir esta meta?"):
            return
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM metas WHERE id=?", (mid,))
                conn.commit()
        except (sqlite3.Error, ValueError) as e:
            logger.error("Erro ao excluir meta: %s", e)
            mostrar_toast(self, f"Erro ao excluir meta: {e}", "erro")
            return
        mostrar_toast(self, "Meta excluida!", "sucesso")
        self._atualizar()
