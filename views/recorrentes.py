import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda
from components.modals import ConfirmarExclusaoModal


class RecorrentesView(ctk.CTkFrame):
    def __init__(self, master, colors=None):
        super().__init__(master, fg_color="transparent")
        self.colors = colors or {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._criar_header()
        self._criar_formulario()
        self._criar_lista()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Contas Recorrentes",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors.get("text", "#fff"),
        ).pack(side="left")

    def _criar_formulario(self):
        form = ctk.CTkFrame(
            self,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        form.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=20)
        grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(grid, text="Descricao", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=0, sticky="w")
        self.entry_desc = ctk.CTkEntry(grid, placeholder_text="Ex: Aluguel",
                                        height=38, corner_radius=8,
                                        fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                        border_color=self.colors.get("border", "#2d2d44"))
        self.entry_desc.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Valor (R$)", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=1, sticky="w")
        self.entry_valor = ctk.CTkEntry(grid, placeholder_text="0,00",
                                         height=38, corner_radius=8,
                                         fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                         border_color=self.colors.get("border", "#2d2d44"))
        self.entry_valor.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Tipo", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=2, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(
            grid, values=["receita", "despesa"], height=38, corner_radius=8,
            fg_color=self.colors.get("bg_dark", "#0f0f1a"),
            border_color=self.colors.get("border", "#2d2d44"),
            button_color=self.colors.get("primary", "#6c5ce7"),
        )
        self.combo_tipo.grid(row=1, column=2, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(grid, text="Dia", font=ctk.CTkFont(size=12),
                      text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
            row=0, column=3, sticky="w")
        self.entry_dia = ctk.CTkEntry(grid, placeholder_text="1-31",
                                       height=38, corner_radius=8,
                                       fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                                       border_color=self.colors.get("border", "#2d2d44"))
        self.entry_dia.grid(row=1, column=3, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            grid,
            text="+ Adicionar",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors.get("primary", "#6c5ce7"),
            hover_color=self.colors.get("primary_hover", "#5a4bd1"),
            command=self._adicionar,
        ).grid(row=1, column=4, sticky="ew")

    def _criar_lista(self):
        container = ctk.CTkFrame(
            self,
            fg_color=self.colors.get("bg_card", "#1a1a2e"),
            corner_radius=12,
        )
        container.grid(row=2, column=0, sticky="nsew")

        self.lista = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=self.colors.get("border", "#2d2d44"),
        )
        self.lista.pack(fill="both", expand=True, padx=4, pady=4)
        self.lista.grid_columnconfigure(0, weight=1)

        self._atualizar()

    def _adicionar(self):
        desc = self.entry_desc.get().strip()
        valor = self.entry_valor.get().replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        dia = self.entry_dia.get().strip()

        if not desc or not valor or not dia:
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO recorrentes (descricao, valor, tipo, dia_mes) VALUES (?, ?, ?, ?)",
            (desc, float(valor), tipo, int(dia)),
        )
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")
        self._atualizar()

    def _atualizar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        conn = get_connection()
        rows = conn.execute(
            "SELECT id, descricao, valor, tipo, dia_mes, ativo FROM recorrentes ORDER BY tipo, dia_mes"
        ).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.lista,
                text="Nenhuma conta recorrente cadastrada",
                text_color=self.colors.get("text_dim", "#a0a0a0"),
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=60)
            return

        header = ctk.CTkFrame(self.lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        for col, txt in enumerate(["Descricao", "Tipo", "Dia", "Valor", "Status", ""]):
            ctk.CTkLabel(
                header, text=txt, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors.get("text_dim", "#a0a0a0"),
            ).grid(row=0, column=col, sticky="w", padx=12)

        for i, r in enumerate(rows):
            row = ctk.CTkFrame(
                self.lista,
                fg_color=self.colors.get("bg_dark", "#0f0f1a"),
                corner_radius=8,
                height=44,
            )
            row.grid(row=i + 1, column=0, sticky="ew", pady=2)

            ctk.CTkLabel(row, text=r["descricao"], font=ctk.CTkFont(size=13)).grid(
                row=0, column=0, padx=12, pady=10, sticky="w")

            tipo_color = self.colors.get("green", "#00b894") if r["tipo"] == "receita" else self.colors.get("red", "#d63031")
            ctk.CTkLabel(row, text=r["tipo"].capitalize(), font=ctk.CTkFont(size=12),
                          text_color=tipo_color).grid(row=0, column=1, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(row, text=f"Dia {r['dia_mes']}", font=ctk.CTkFont(size=12),
                          text_color=self.colors.get("text_dim", "#a0a0a0")).grid(
                row=0, column=2, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(row, text=formatar_moeda(r["valor"]),
                          font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=tipo_color).grid(row=0, column=3, padx=12, pady=10, sticky="w")

            status_text = "Ativo" if r["ativo"] else "Inativo"
            status_color = self.colors.get("green", "#00b894") if r["ativo"] else self.colors.get("text_dim", "#a0a0a0")
            ctk.CTkButton(
                row, text=status_text, width=60, height=30, corner_radius=6,
                font=ctk.CTkFont(size=11),
                fg_color=status_color,
                hover_color="#00a884",
                command=lambda rid=r["id"], at=r["ativo"]: self._toggle(rid, at),
            ).grid(row=0, column=4, padx=8, pady=10)

            ctk.CTkButton(
                row, text="X", width=32, height=32,
                corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors.get("red", "#d63031"),
                hover_color="#c0392b",
                command=lambda rid=r["id"]: self._excluir(rid),
            ).grid(row=0, column=5, padx=12, pady=10)

    def _toggle(self, rid, atual):
        conn = get_connection()
        conn.execute("UPDATE recorrentes SET ativo = ? WHERE id = ?",
                     (0 if atual else 1, rid))
        conn.commit()
        conn.close()
        self._atualizar()

    def _excluir(self, rid):
        modal = ConfirmarExclusaoModal(
            self, "Excluir Recorrente", "Deseja excluir esta conta recorrente?",
            colors=self.colors,
        )
        self.wait_window(modal)
        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM recorrentes WHERE id = ?", (rid,))
            conn.commit()
            conn.close()
            self._atualizar()
