import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class QuanLyTKView:
    def __init__(
        self,
        master,
        on_refresh,
        on_create,
        on_delete,
        on_edit,
        on_reset,
        on_import,
        on_export,
        on_back,
        on_search,
    ):
        self.root = master
        self.on_refresh = on_refresh
        self.on_create = on_create
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.on_reset = on_reset
        self.on_import = on_import
        self.on_export = on_export
        self.on_back = on_back
        self.on_search = on_search
        self._build_ui()

    def _build_ui(self):
        self.root.title("Quản lý tài khoản")

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(
            container,
            text="Quản lý tài khoản",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(0, 10))

        search_frame = ctk.CTkFrame(container)
        search_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(search_frame, text="Tìm theo:").pack(side="left", padx=6)
        self.search_column = ctk.CTkComboBox(
            search_frame,
            values=["id", "username", "ho_ten", "sdt", "chuc_vu"],
            state="readonly",
            width=160,
        )
        self.search_column.set("id")
        self.search_column.pack(side="left", padx=6)
        self.search_keyword = ctk.CTkEntry(
            search_frame, width=220, placeholder_text="Nhập từ khóa (hỗ trợ regex)"
        )
        self.search_keyword.pack(side="left", padx=6)
        ctk.CTkButton(search_frame, text="Tìm", width=90, command=self.on_search).pack(
            side="left", padx=6
        )

        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=6)

        ctk.CTkButton(
            button_frame, text="Làm mới", width=110, command=self.on_refresh
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Tạo tài khoản", width=140, command=self.on_create
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Xóa tài khoản", width=120, command=self.on_delete
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Sửa tài khoản", width=120, command=self.on_edit
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Reset mật khẩu", width=130, command=self.on_reset
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Import CSV", width=110, command=self.on_import
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Export CSV", width=110, command=self.on_export
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Quay lại", width=100, command=self.on_back
        ).pack(side="left", padx=6)

        self.tree_frame = ctk.CTkFrame(container)
        self.tree_frame.pack(fill="both", expand=True, pady=(8, 6))

        columns = ("id", "username", "ho_ten", "sdt", "chuc_vu", "ngay_tao")
        self.account_tree = ttk.Treeview(
            self.tree_frame, columns=columns, show="headings", height=15
        )
        # Ghi chú: auto-resize giúp cột tài khoản điều chỉnh phù hợp khi container thay đổi kích thước.
        # Trọng số column_weights định nghĩa mức ưu tiên chiều rộng cho từng cột.
        self.column_weights = {
            "id": 7,
            "username": 16,
            "ho_ten": 20,
            "sdt": 12,
            "chuc_vu": 12,
            "ngay_tao": 13,
        }

        headings = {
            "id": "ID",
            "username": "Username",
            "ho_ten": "Họ tên",
            "sdt": "SĐT",
            "chuc_vu": "Role",
            "ngay_tao": "Ngày tạo",
        }
        for column, text in headings.items():
            self.account_tree.heading(column, text=text)
            self.account_tree.column(column, width=130, anchor="center")
        self.account_tree.column("ho_ten", width=220)

        scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=self.account_tree.yview
        )
        self.account_tree.configure(yscrollcommand=scrollbar.set)
        self.account_tree.pack(
            side="left", expand=True, fill="both", padx=(6, 0), pady=6
        )
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.tree_frame.bind("<Configure>", self._resize_tree_columns)

        self.status_label = ctk.CTkLabel(container, text="Sẵn sàng", anchor="w")
        self.status_label.pack(fill="x", pady=(6, 0))

    def _resize_tree_columns(self, event=None):
        width = self.tree_frame.winfo_width()
        if width <= 0:
            return
        available = max(width - 24, 160)
        total_weight = sum(self.column_weights.values())
        for column, weight in self.column_weights.items():
            self.account_tree.column(
                column, width=max(int(available * weight / total_weight), 80)
            )

    def set_status(self, text):
        self.status_label.configure(text=text)

    def get_keyword(self):
        return self.search_keyword.get().strip()

    def get_search_column(self):
        return self.search_column.get()

    def clear_search(self):
        self.search_keyword.delete(0, tk.END)
        self.search_column.set("id")

    def populate_tree(self, data):
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        for _, row in data.iterrows():
            self.account_tree.insert(
                "",
                "end",
                values=[
                    row["id"],
                    row["username"],
                    row["ho_ten"],
                    row["sdt"],
                    row["chuc_vu"],
                    row.get("ngay_tao", ""),
                ],
            )

    def get_selected_username(self):
        selected_item = self.account_tree.selection()
        if not selected_item:
            return None
        values = self.account_tree.item(selected_item[0], "values")
        return values[1]
