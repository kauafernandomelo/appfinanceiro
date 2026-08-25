import customtkinter as ctk
from datetime import datetime, timedelta
import calendar


class DatePicker(ctk.CTkFrame):
    def __init__(self, master, on_select=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_select = on_select
        self.selected_date = datetime.now()

        self.entry = ctk.CTkEntry(
            self, placeholder_text="AAAA-MM-DD", height=36, width=130,
            corner_radius=8, fg_color="#0f0f1a", border_color="#2d2d44",
        )
        self.entry.pack(side="left")
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        self.entry.bind("<FocusOut>", self._on_entry_change)

        self.btn = ctk.CTkButton(
            self, text="\U0001F4C5", width=36, height=36, corner_radius=8,
            fg_color="#1a1a2e", hover_color="#16213e",
            command=self._toggle_calendar,
        )
        self.btn.pack(side="left", padx=(4, 0))

        self.cal_window = None

    def get(self):
        return self.entry.get().strip()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def _on_entry_change(self, event=None):
        pass

    def _toggle_calendar(self):
        if self.cal_window and self.cal_window.winfo_exists():
            self.cal_window.destroy()
            self.cal_window = None
            return

        self.cal_window = ctk.CTkToplevel(self)
        self.cal_window.title("")
        self.cal_window.geometry("300x280")
        self.cal_window.configure(fg_color="#1a1a2e")
        self.cal_window.resizable(False, False)
        self.cal_window.grab_set()

        try:
            x = self.btn.winfo_rootx()
            y = self.btn.winfo_rooty() + 40
            self.cal_window.geometry(f"300x280+{x}+{y}")
        except Exception:
            pass

        self._build_calendar()

    def _build_calendar(self):
        if not self.cal_window or not self.cal_window.winfo_exists():
            return

        for w in self.cal_window.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self.cal_window, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(header, text="<", width=30, height=28, corner_radius=6,
                       fg_color="#2d2d44", hover_color="#3d3d54",
                       command=self._prev_month).pack(side="left")

        self.lbl_month = ctk.CTkLabel(header, text=self.selected_date.strftime("%B %Y").capitalize(),
                                       font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_month.pack(side="left", expand=True)

        ctk.CTkButton(header, text=">", width=30, height=28, corner_radius=6,
                       fg_color="#2d2d44", hover_color="#3d3d54",
                       command=self._next_month).pack(side="right")

        days_frame = ctk.CTkFrame(self.cal_window, fg_color="transparent")
        days_frame.pack(fill="x", padx=10)

        for d in ["Se", "Te", "Qa", "Qi", "Se", "Sa", "Do"]:
            ctk.CTkLabel(days_frame, text=d, font=ctk.CTkFont(size=10, weight="bold"),
                          text_color="#a0a0a0", width=36).grid(row=0, column=["Se","Te","Qa","Qi","Se","Sa","Do"].index(d), padx=1, pady=2)

        cal = calendar.monthcalendar(self.selected_date.year, self.selected_date.month)
        today = datetime.now()

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue

                is_today = (day == today.day and self.selected_date.month == today.month
                           and self.selected_date.year == today.year)
                is_selected = (day == self.selected_date.day and self.selected_date.month == self.selected_date.month
                              and self.selected_date.year == self.selected_date.year)

                fg = "#6c5ce7" if is_selected else "#0f0f1a"
                text_c = "#ffffff"

                btn = ctk.CTkButton(
                    days_frame, text=str(day), width=36, height=28, corner_radius=6,
                    fg_color=fg, hover_color="#5a4bd1", text_color=text_c,
                    font=ctk.CTkFont(size=11),
                    command=lambda d=day: self._select_day(d),
                )
                btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1)

        bottom = ctk.CTkFrame(self.cal_window, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(bottom, text="Hoje", height=28, corner_radius=6,
                       fg_color="#2d2d44", hover_color="#3d3d54",
                       font=ctk.CTkFont(size=11),
                       command=self._go_today).pack(side="left")

        ctk.CTkButton(bottom, text="OK", height=28, corner_radius=6,
                       fg_color="#6c5ce7", hover_color="#5a4bd1",
                       font=ctk.CTkFont(size=11, weight="bold"),
                       command=self._confirm).pack(side="right")

    def _prev_month(self):
        if self.selected_date.month == 1:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year - 1, month=12)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month - 1)
        self._build_calendar()

    def _next_month(self):
        if self.selected_date.month == 12:
            self.selected_date = self.selected_date.replace(year=self.selected_date.year + 1, month=1)
        else:
            self.selected_date = self.selected_date.replace(month=self.selected_date.month + 1)
        self._build_calendar()

    def _select_day(self, day):
        self.selected_date = self.selected_date.replace(day=day)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        self._build_calendar()

    def _go_today(self):
        self.selected_date = datetime.now()
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        self._build_calendar()

    def _confirm(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date.strftime("%Y-%m-%d"))
        if self.on_select:
            self.on_select(self.selected_date.strftime("%Y-%m-%d"))
        if self.cal_window:
            self.cal_window.destroy()
            self.cal_window = None
