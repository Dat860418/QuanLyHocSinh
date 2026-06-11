import tkinter as tk

import customtkinter as ctk


class LoginView:
    def __init__(self, master, on_login, on_toggle_password):
        self.root = master
        self.on_login = on_login
        self.on_toggle_password = on_toggle_password
        self._build_ui()

    def _build_ui(self):
        self.root.title("Đăng nhập")
        self.root.geometry("360x240")
        self.root.minsize(320, 240)

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=16, pady=16)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=2)

        ctk.CTkLabel(
            container, text="Đăng nhập", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(container, text="Username:", anchor="w").grid(
            row=1, column=0, padx=6, pady=6, sticky="ew"
        )
        self.entry_username = ctk.CTkEntry(container)
        self.entry_username.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        ctk.CTkLabel(container, text="Password:", anchor="w").grid(
            row=2, column=0, padx=6, pady=6, sticky="ew"
        )
        self.entry_password = ctk.CTkEntry(container, show="*")
        self.entry_password.grid(row=2, column=1, padx=6, pady=6, sticky="ew")

        self.show_password = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            container,
            text="Hiển thị mật khẩu",
            variable=self.show_password,
            command=self.on_toggle_password,
        ).grid(row=3, column=1, padx=6, pady=(0, 6), sticky="w")

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(button_frame, text="Đăng nhập", command=self.on_login).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

    def get_username(self):
        return self.entry_username.get().strip()

    def get_password(self):
        return self.entry_password.get().strip()

    def set_password_visible(self, visible):
        self.entry_password.configure(show="" if visible else "*")
