import customtkinter as ctk
from database import get_connection
from utils import formatar_moeda
from components.modals import ConfirmarExclusaoModal


class MetasView(ctk.CTkFrame):
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
            text="Metas de Economia",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(side="left")

    def criar_formulario(self):
        form = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        form.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(form, text="Nome:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_nome = ctk.CTkEntry(form, placeholder_text="Ex: Viagem")
        self.entry_nome.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Valor Alvo:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.entry_valor = ctk.CTkEntry(form, placeholder_text="0,00")
        self.entry_valor.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Prazo:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.entry_prazo = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD")
        self.entry_prazo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkButton(
            form,
            text="Criar Meta",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.adicionar,
        ).grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

    def criar_lista(self):
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        self.lista_frame.grid_columnconfigure(0, weight=1)

        self.atualizar_lista()

    def adicionar(self):
        nome = self.entry_nome.get()
        valor = self.entry_valor.get().replace(",", ".")
        prazo = self.entry_prazo.get()

        if not nome or not valor:
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO metas (nome, valor_alvo, valor_atual, prazo) VALUES (?, ?, 0, ?)",
            (nome, float(valor), prazo),
        )
        conn.commit()
        conn.close()

        self.entry_nome.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.entry_prazo.delete(0, "end")

        self.atualizar_lista()

    def atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        metas = conn.execute(
            "SELECT id, nome, valor_alvo, valor_atual, prazo FROM metas ORDER BY prazo"
        ).fetchall()
        conn.close()

        if not metas:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma meta cadastrada",
                text_color="#a0a0a0",
            ).grid(row=0, column=0, pady=20)
            return

        for i, m in enumerate(metas):
            row = ctk.CTkFrame(self.lista_frame, fg_color="#16213e", corner_radius=8)
            row.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                info_frame,
                text=m["nome"],
                font=ctk.CTkFont(size=14, weight="bold"),
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                info_frame,
                text=f"Prazo: {m['prazo']}",
                font=ctk.CTkFont(size=11),
                text_color="#a0a0a0",
            ).grid(row=1, column=0, sticky="w")

            progress_frame = ctk.CTkFrame(row, fg_color="transparent")
            progress_frame.grid(row=0, column=2, columnspan=2, padx=10, pady=10, sticky="ew")
            progress_frame.grid_columnconfigure(0, weight=1)

            percentual = (m["valor_atual"] / m["valor_alvo"] * 100) if m["valor_alvo"] > 0 else 0
            cor_barra = "#10b981" if percentual >= 100 else "#3b82f6"

            progress = ctk.CTkProgressBar(progress_frame, progress_color=cor_barra)
            progress.grid(row=0, column=0, sticky="ew")
            progress.set(min(percentual / 100, 1.0))

            ctk.CTkLabel(
                progress_frame,
                text=f"{formatar_moeda(m['valor_atual'])} / {formatar_moeda(m['valor_alvo'])} ({percentual:.0f}%)",
                font=ctk.CTkFont(size=11),
                text_color="#a0a0a0",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.grid(row=0, column=4, padx=10, pady=10)

            ctk.CTkButton(
                btn_frame,
                text="+",
                width=30,
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda mid=m["id"], val=m["valor_alvo"], cur=m["valor_atual"]: self.adicionar_valor(mid, val, cur),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                btn_frame,
                text="Excluir",
                width=60,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda mid=m["id"]: self.excluir(mid),
            ).pack(side="left", padx=2)

    def adicionar_valor(self, meta_id: int, valor_alvo: float, valor_atual: float):
        modal = ctk.CTkToplevel(self)
        modal.title("Adicionar Valor")
        modal.geometry("300x150")
        modal.grab_set()

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Valor a adicionar:").pack(pady=(0, 10))
        entry = ctk.CTkEntry(frame, placeholder_text="0,00")
        entry.pack(fill="x", pady=(0, 10))

        def confirmar():
            try:
                valor = float(entry.get().replace(",", "."))
                conn = get_connection()
                conn.execute(
                    "UPDATE metas SET valor_atual = ? WHERE id = ?",
                    (valor_atual + valor, meta_id),
                )
                conn.commit()
                conn.close()
                modal.destroy()
                self.atualizar_lista()
            except ValueError:
                pass

        ctk.CTkButton(
            frame,
            text="Confirmar",
            fg_color="#10b981",
            hover_color="#059669",
            command=confirmar,
        ).pack(fill="x")

    def excluir(self, meta_id: int):
        modal = ConfirmarExclusaoModal(
            self,
            "Excluir Meta",
            "Tem certeza que deseja excluir esta meta?",
        )
        self.wait_window(modal)

        if modal.resultado:
            conn = get_connection()
            conn.execute("DELETE FROM metas WHERE id = ?", (meta_id,))
            conn.commit()
            conn.close()
            self.atualizar_lista()
