import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda
from components.modals import ConfirmarExclusaoModal


class RecorrentesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.criar_header()
        self.criar_formulario()
        self.criar_lista()

    def criar_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            header,
            text="Contas Recorrentes",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(form, text="Descrição:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_descricao = ctk.CTkEntry(form, placeholder_text="Ex: Aluguel")
        self.entry_descricao.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Valor:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.entry_valor = ctk.CTkEntry(form, placeholder_text="0,00")
        self.entry_valor.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Tipo:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(form, values=["receita", "despesa"])
        self.combo_tipo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Dia do Mês:").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.entry_dia = ctk.CTkEntry(form, placeholder_text="1-31")
        self.entry_dia.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            form,
            text="Adicionar",
            fg_color="#ec4899",
            hover_color="#db2777",
            command=self.adicionar,
        ).grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")

    def criar_lista(self):
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        self.lista_frame.grid_columnconfigure(0, weight=1)

        self.atualizar_lista()

    def adicionar(self):
        descricao = self.entry_descricao.get()
        valor = self.entry_valor.get().replace(",", ".")
        tipo = self.combo_tipo.get()
        dia = self.entry_dia.get()

        if not descricao or not valor or not dia:
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO recorrentes (descricao, valor, tipo, dia_mes) VALUES (?, ?, ?, ?)",
            (descricao, float(valor), tipo, int(dia)),
        )
        conn.commit()
        conn.close()

        self.entry_descricao.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_dia.delete(0, "end")

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        recorrentes = conn.execute(
            "SELECT id, descricao, valor, tipo, dia_mes, ativo FROM recorrentes ORDER BY tipo, dia_mes"
        ).fetchall()
        conn.close()

        if not recorrentes:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma conta recorrente cadastrada",
                text_color="#a0a0a0",
            ).grid(row=0, column=0, pady=20)
            return

        for i, r in enumerate(recorrentes):
            row = ctk.CTkFrame(self.lista_frame, fg_color="#16213e", corner_radius=8)
            row.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=r["descricao"],
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

            tipo_color = "#10b981" if r["tipo"] == "receita" else "#ef4444"
            ctk.CTkLabel(
                row,
                text=r["tipo"].capitalize(),
                font=ctk.CTkFont(size=12),
                text_color=tipo_color,
            ).grid(row=0, column=1, padx=10, pady=10)

            ctk.CTkLabel(
                row,
                text=f"Dia {r['dia_mes']}",
                font=ctk.CTkFont(size=12),
                text_color="#a0a0a0",
            ).grid(row=0, column=2, padx=10, pady=10)

            ctk.CTkLabel(
                row,
                text=formatar_moeda(r["valor"]),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=tipo_color,
            ).grid(row=0, column=3, padx=10, pady=10)

            status = "Ativo" if r["ativo"] else "Inativo"
            status_color = "#10b981" if r["ativo"] else "#a0a0a0"
            ctk.CTkButton(
                row,
                text=status,
                width=60,
                fg_color=status_color,
                hover_color="#059669" if r["ativo"] else "#606060",
                command=lambda rid=r["id"], ativo=r["ativo"]: self.toggle_status(rid, ativo),
            ).grid(row=0, column=4, padx=5, pady=10)

            ctk.CTkButton(
                row,
                text="Excluir",
                width=60,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda rid=r["id"]: self.excluir(rid),
            ).grid(row=0, column=5, padx=5, pady=10)

    def toggle_status(self, recorrente_id: int, atual: bool):
        conn = get_connection()
        conn.execute(
            "UPDATE recorrentes SET ativo = ? WHERE id = ?",
            (0 if atual else 1, recorrente_id),
        )
        conn.commit()
        conn.close()
        self.atualizar_lista()

    def excluir(self, recorrente_id: int):
        modal = ConfirmarExclusaoModal(
            self,
            "Excluir Recorrente",
            "Tem certeza que deseja excluir esta conta recorrente?",
        )
        self.wait_window(modal)

        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM recorrentes WHERE id = ?", (recorrente_id,))
            conn.commit()
            conn.close()
            self.atualizar_lista()
