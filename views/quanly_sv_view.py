import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class QuanLySVView:
    def __init__(self, master, callbacks):
        self.root = master
        self.callbacks = callbacks
        self._build_ui()

    def _build_ui(self):
        self.root.title("Quản lý sinh viên")

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(
            container,
            text="Quản lý sinh viên",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(0, 10))

        input_frame = ctk.CTkFrame(container)
        input_frame.pack(fill="x", pady=6)

        self.entries = {}
        fields = [
            ("ma_sv", "Mã SV"),
            ("ho_ten", "Họ tên"),
            ("ngay_sinh", "Ngày sinh"),
            ("gioi_tinh", "Giới tính"),
            ("lop", "Lớp"),
            ("dia_chi", "Địa chỉ"),
            ("sdt", "SĐT"),
            ("email", "Email"),
            ("trang_thai", "Trạng thái"),
        ]

        for idx, (key, label) in enumerate(fields):
            row = idx // 3
            col = (idx % 3) * 2
            ctk.CTkLabel(input_frame, text=label + ":", width=110, anchor="w").grid(
                row=row, column=col, padx=6, pady=6, sticky="w"
            )
            if key == "trang_thai":
                entry = ctk.CTkComboBox(
                    input_frame,
                    values=["Đang học", "Đã nghỉ"],
                    state="readonly",
                    width=180,
                )
                entry.set("Đang học")
            else:
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

        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=6)
        ctk.CTkButton(
            button_frame, text="Thêm", width=90, command=self.callbacks["add"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Xóa", width=90, command=self.callbacks["delete"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Sửa", width=90, command=self.callbacks["edit"]
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame,
            text="Hiển thị tất cả",
            width=140,
            command=self.callbacks["refresh"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame,
            text="Import CSV",
            width=120,
            command=self.callbacks["import_csv"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame,
            text="Export CSV",
            width=120,
            command=self.callbacks["export_csv"],
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            button_frame, text="Quay lại", width=100, command=self.callbacks["back"]
        ).pack(side="left", padx=6)

        self.tree_frame = ctk.CTkFrame(container)
        self.tree_frame.pack(fill="both", expand=True, pady=(8, 6))

        columns = self.callbacks["columns"]
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        headings = [
            "Mã SV",
            "Họ tên",
            "Ngày sinh",
            "Giới tính",
            "Lớp",
            "Địa chỉ",
            "SĐT",
            "Email",
            "Trạng thái",
        ]
        # Ghi chú: các cột sẽ co dãn theo kích thước của tree_frame khi cửa sổ thay đổi.
        # Trọng số column_weights xác định tỷ lệ phân bổ chiều rộng giữa các cột.
        self.column_weights = {
            "ma_sv": 10,
            "ho_ten": 18,
            "ngay_sinh": 12,
            "gioi_tinh": 9,
            "lop": 10,
            "dia_chi": 15,
            "sdt": 10,
            "email": 15,
            "trang_thai": 11,
        }
        for column, heading in zip(columns, headings):
            self.tree.heading(column, text=heading, anchor="center")
            self.tree.column(column, width=110, anchor="center")
        self.tree.column("ho_ten", width=180, anchor="w")
        self.tree.column("dia_chi", width=160, anchor="w")
        self.tree.column("email", width=180, anchor="w")

        scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.tree_frame.bind("<Configure>", self._resize_tree_columns)
        self.tree.bind("<<TreeviewSelect>>", self.callbacks["select"])

        pagination_frame = ctk.CTkFrame(container, fg_color="transparent")
        pagination_frame.pack(pady=4)
        ctk.CTkButton(
            pagination_frame, text="Trước", width=90, command=self.callbacks["prev"]
        ).pack(side="left", padx=6)
        self.page_label = ctk.CTkLabel(pagination_frame, text="Trang 1/1", width=240)
        self.page_label.pack(side="left", padx=6)
        ctk.CTkButton(
            pagination_frame, text="Sau", width=90, command=self.callbacks["next"]
        ).pack(side="left", padx=6)

        self.status_label = ctk.CTkLabel(container, text="Sẵn sàng", anchor="w")
        self.status_label.pack(fill="x", pady=(6, 0))

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

    def get_form_values(self):
        values = []
        for column in self.callbacks["columns"]:
            entry = self.entries[column]
            values.append(entry.get().strip())
        return values

    def populate_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in data.iterrows():
            self.tree.insert(
                "", "end", values=[row[column] for column in self.callbacks["columns"]]
            )

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def set_page_label(self, text):
        self.page_label.configure(text=text)

    def set_status(self, text):
        self.status_label.configure(text=text)

    def clear_input(self):
        for column, entry in self.entries.items():
            if column == "trang_thai":
                entry.set("Đang học")
            else:
                entry.delete(0, tk.END)

    def fill_entry_values(self, values):
        for column, value in zip(self.callbacks["columns"], values):
            entry = self.entries[column]
            entry.delete(0, tk.END)
            if column == "trang_thai":
                entry.set(value)
            else:
                entry.insert(0, value)

    def get_search_keyword(self):
        return self.search_keyword.get().strip()

    def get_search_column(self):
        return self.search_column.get()

    def get_selected_values(self):
        selected = self.tree.focus()
        return self.tree.item(selected, "values")
