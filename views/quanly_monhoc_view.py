import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class QuanLyMonHocView:
    def __init__(self, master, callbacks):
        self.root = master
        self.callbacks = callbacks
        self._build_ui()

    def _build_ui(self):
        self.root.title("Quản lý môn học")

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(
            container, text="Quản lý môn học", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 10))

        input_frame = ctk.CTkFrame(container)
        input_frame.pack(fill="x", pady=6)

        self.entries = {}
        fields = [
            ("ma_mon", "Mã môn"),
            ("ten_mon", "Tên môn"),
            ("so_tin_chi", "Số tín chỉ"),
        ]
        for idx, (key, label) in enumerate(fields):
            row = idx // 3
            col = (idx % 3) * 2
            ctk.CTkLabel(input_frame, text=label + ":", width=110, anchor="w").grid(
                row=row, column=col, padx=6, pady=6, sticky="w"
            )
            entry = ctk.CTkEntry(input_frame, width=180)
            entry.grid(row=row, column=col + 1, padx=6, pady=6, sticky="ew")
            self.entries[key] = entry

        for c in [1, 3, 5]:
            input_frame.grid_columnconfigure(c, weight=1)

        search_frame = ctk.CTkFrame(container)
        search_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(search_frame, text="Tìm theo:").pack(side="left", padx=6)
        self.search_column = ctk.CTkComboBox(
            search_frame,
            values=list(self.callbacks["columns"]),
            state="readonly",
            width=160,
        )
        self.search_column.set(list(self.callbacks["columns"])[0])
        self.search_column.pack(side="left", padx=6)
        self.search_keyword = ctk.CTkEntry(
            search_frame, width=220, placeholder_text="Nhập từ khóa (hỗ trợ regex)"
        )
        self.search_keyword.pack(side="left", padx=6)
        ctk.CTkButton(
            search_frame, text="Tìm", width=90, command=self.callbacks["search"]
        ).pack(side="left", padx=6)

        btn_frame = ctk.CTkFrame(container)
        btn_frame.pack(fill="x", pady=6)
        ctk.CTkButton(
            btn_frame, text="Thêm", width=90, command=self.callbacks["add"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame, text="Xóa", width=90, command=self.callbacks["delete"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame, text="Sửa", width=90, command=self.callbacks["edit"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame,
            text="Hiển thị tất cả",
            width=140,
            command=self.callbacks["refresh"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame,
            text="Import CSV",
            width=120,
            command=self.callbacks["import_csv"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame,
            text="Export CSV",
            width=120,
            command=self.callbacks["export_csv"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame, text="Quay lại", width=100, command=self.callbacks["back"]
        ).pack(side="left", padx=6)

        tree_frame = ctk.CTkFrame(container)
        tree_frame.pack(fill="both", expand=True, pady=(8, 6))

        self.tree_frame = ctk.CTkFrame(container)
        self.tree_frame.pack(fill="both", expand=True, pady=(8, 6))

        self.tree = ttk.Treeview(
            self.tree_frame, columns=self.callbacks["columns"], show="headings"
        )
        # Ghi chú: phân bổ lại chiều rộng cột dựa trên trọng số khi cửa sổ thay đổi.
        # Điều này giúp bảng môn học luôn hiển thị cân đối trên mọi kích thước màn hình.
        self.column_weights = {
            "ma_mon": 12,
            "ten_mon": 24,
            "so_tin_chi": 8,
        }
        self.tree.heading("ma_mon", text="Mã môn")
        self.tree.heading("ten_mon", text="Tên môn")
        self.tree.heading("so_tin_chi", text="Số tín chỉ")
        self.tree.column("ma_mon", width=120, anchor="center")
        self.tree.column("ten_mon", width=260)
        self.tree.column("so_tin_chi", width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)

        scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.tree_frame.bind("<Configure>", self._resize_tree_columns)
        self.tree.bind("<<TreeviewSelect>>", self.callbacks["select"])

        self.status_label = ctk.CTkLabel(container, text="Sẵn sàng", anchor="w")
        self.status_label.pack(fill="x", pady=(6, 0))

    def get_form_values(self):
        return [
            self.entries[column].get().strip() for column in self.callbacks["columns"]
        ]

    def populate_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in data.iterrows():
            self.tree.insert(
                "", "end", values=[row[column] for column in self.callbacks["columns"]]
            )

    def _resize_tree_columns(self, event=None):
        width = self.tree_frame.winfo_width()
        if width <= 0:
            return
        available = max(width - 24, 120)
        total_weight = sum(self.column_weights.values())
        for column, weight in self.column_weights.items():
            self.tree.column(
                column, width=max(int(available * weight / total_weight), 80)
            )

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_input(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def set_status(self, text):
        self.status_label.configure(text=text)

    def get_search_keyword(self):
        return self.search_keyword.get().strip()

    def get_search_column(self):
        return self.search_column.get()

    def get_selected_values(self):
        selected = self.tree.focus()
        return self.tree.item(selected, "values")

    def fill_entry_values(self, values):
        for column, value in zip(self.callbacks["columns"], values):
            entry = self.entries[column]
            entry.delete(0, tk.END)
            entry.insert(0, value)
