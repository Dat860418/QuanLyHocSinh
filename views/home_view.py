import os
import webbrowser

import customtkinter as ctk


class HomeView:
    def __init__(
        self, master, on_sv, on_mon, on_diem, on_tk, on_intro, on_guide, on_logout
    ):
        self.root = master
        self.on_sv = on_sv
        self.on_mon = on_mon
        self.on_diem = on_diem
        self.on_tk = on_tk
        self.on_intro = on_intro
        self.on_guide = on_guide
        self.on_logout = on_logout
        self._build_ui()

    def _build_ui(self):
        self.root.title("Trang chủ")
        self.root.geometry("760x420")

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            container,
            text="Hệ thống quản lý sinh viên",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(8, 18))

        grid = ctk.CTkFrame(container)
        grid.pack(pady=4)

        ctk.CTkButton(
            grid, text="Quản lý sinh viên", width=220, height=80, command=self.on_sv
        ).grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkButton(
            grid, text="Quản lý môn học", width=220, height=80, command=self.on_mon
        ).grid(row=0, column=1, padx=10, pady=8)
        ctk.CTkButton(
            grid, text="Quản lý điểm", width=220, height=80, command=self.on_diem
        ).grid(row=1, column=0, padx=10, pady=8)
        ctk.CTkButton(
            grid, text="Quản lý tài khoản", width=220, height=80, command=self.on_tk
        ).grid(row=1, column=1, padx=10, pady=8)

        bottom = ctk.CTkFrame(container, fg_color="transparent")
        bottom.pack(side="bottom", pady=(18, 0))

        ctk.CTkButton(
            bottom, text="Giới thiệu", width=140, height=40, command=self.on_intro
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            bottom, text="Hướng dẫn", width=140, height=40, command=self.on_guide
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            bottom, text="Đăng xuất", width=140, height=40, command=self.on_logout
        ).pack(side="left", padx=6)

    def get_pdf_path(self):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs",
            "huong_dan.pdf",
        )

    def open_guide_file(self, path):
        if os.name == "nt":
            os.startfile(path)
        else:
            webbrowser.open(path)
