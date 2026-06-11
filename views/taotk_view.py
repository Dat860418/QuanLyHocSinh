import tkinter as tk

import customtkinter as ctk


class TaoTKView:
    def __init__(self, master, on_create, on_back, on_toggle_password):
        self.root = master
        self.on_create = on_create
        self.on_back = on_back
        self.on_toggle_password = on_toggle_password
        self._build_ui()

    def _build_ui(self):
        self.root.title("Tạo tài khoản")
        self.root.geometry("420x380")
        self.root.minsize(380, 360)

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=16, pady=16)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=2)

        ctk.CTkLabel(
            container, text="Tạo tài khoản", font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        labels = ["Username:", "Password:", "Họ tên:", "SĐT:", "Role:"]
        for idx, text in enumerate(labels):
            ctk.CTkLabel(container, text=text, anchor="w").grid(
                row=idx + 1, column=0, padx=6, pady=6, sticky="ew"
            )

        self.entry_username = ctk.CTkEntry(container)
        self.entry_username.grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        self.entry_password = ctk.CTkEntry(container, show="*")
        self.entry_password.grid(row=2, column=1, padx=6, pady=6, sticky="ew")
        self.entry_hoten = ctk.CTkEntry(container)
        self.entry_hoten.grid(row=3, column=1, padx=6, pady=6, sticky="ew")
        self.entry_sdt = ctk.CTkEntry(container)
        self.entry_sdt.grid(row=4, column=1, padx=6, pady=6, sticky="ew")
        self.entry_chuc_vu = ctk.CTkComboBox(
            container, values=["User", "Admin"], state="readonly"
        )
        self.entry_chuc_vu.set("User")
        self.entry_chuc_vu.grid(row=5, column=1, padx=6, pady=6, sticky="ew")

        self.show_password = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            container,
            text="Hiển mật khẩu",
            variable=self.show_password,
            command=self.on_toggle_password,
        ).grid(row=6, column=1, padx=6, pady=(0, 6), sticky="w")

        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(button_frame, text="Tạo tài khoản", command=self.on_create).grid(
            row=0, column=0, padx=6, sticky="ew"
        )
        ctk.CTkButton(button_frame, text="Quay lại", command=self.on_back).grid(
            row=0, column=1, padx=6, sticky="ew"
        )

    def set_password_visible(self, visible):
        self.entry_password.configure(show="" if visible else "*")

    def get_payload_values(self):
        return [
            self.entry_username.get(),
            self.entry_password.get(),
            self.entry_hoten.get(),
            self.entry_sdt.get(),
            self.entry_chuc_vu.get(),
        ]
