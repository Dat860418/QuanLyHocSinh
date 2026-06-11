import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class QuanLyDiemView:
    def __init__(self, master, callbacks):
        self.root = master
        self.callbacks = callbacks
        self._build_ui()

    def _build_ui(self):
        self.root.title("Quản lý điểm")

        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(
            container, text="Quản lý điểm", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 10))

        input_frame = ctk.CTkFrame(container)
        input_frame.pack(fill="x", pady=6)

        self.form_columns = [
            "ma_sv",
            "ma_mon",
            "diem_cc",
            "diem_kt1",
            "diem_kt2",
            "diem_ck",
        ]
        labels = [
            ("ma_sv", "Mã SV"),
            ("ma_mon", "Mã môn"),
            ("diem_cc", "Điểm CC"),
            ("diem_kt1", "Điểm KT1"),
            ("diem_kt2", "Điểm KT2"),
            ("diem_ck", "Điểm CK"),
        ]
        self.entries = {}
        for idx, (key, label) in enumerate(labels):
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
        ctk.CTkLabel(search_frame, text="Thống kê:").pack(side="left", padx=6)
        self.stats_option = ctk.CTkComboBox(
            search_frame,
            values=[
                "Điểm tổng kết môn dưới 4",
                "Điểm tổng kết môn trên 8",
                "Top 5 sinh viên điểm cao nhất",
                "GPA theo sinh viên",
            ],
            state="readonly",
            width=250,
        )
        self.stats_option.set("Điểm tổng kết môn dưới 4")
        self.stats_option.pack(side="left", padx=6)
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
            btn_frame, text="Thống kê", width=110, command=self.callbacks["thong_ke"]
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

        self.tree_frame = ctk.CTkFrame(container)
        self.tree_frame.pack(fill="both", expand=True, pady=(8, 6))

        self.tree = ttk.Treeview(
            self.tree_frame, columns=self.callbacks["columns"], show="headings"
        )
        headings = [
            "ID",
            "Mã SV",
            "Mã môn",
            "Họ tên",
            "Tên môn",
            "Điểm CC",
            "Điểm KT1",
            "Điểm KT2",
            "Điểm CK",
            "Điểm tổng kết",
            "Xếp loại",
        ]
        # Ghi chú: tự động điều chỉnh chiều rộng cột khi tree_frame thay đổi kích thước.
        # Column weights được dùng để phân bố tỷ lệ chiều rộng cho từng cột.
        self.column_weights = {
            "id": 7,
            "ma_sv": 10,
            "ma_mon": 10,
            "ho_ten": 16,
            "ten_mon": 16,
            "diem_cc": 10,
            "diem_kt1": 10,
            "diem_kt2": 10,
            "diem_ck": 10,
            "diem_tong_ket": 11,
            "xep_loai": 10,
        }
        for column, heading in zip(self.callbacks["columns"], headings):
            self.tree.heading(column, text=heading)
            width = 120 if column in {"ho_ten", "ten_mon"} else 90
            self.tree.column(column, width=width, anchor="center")
        self.tree.column("id", width=60, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)

        scrollbar = ttk.Scrollbar(
            self.tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.tree_frame.bind("<Configure>", self._resize_tree_columns)
        self.tree.bind("<<TreeviewSelect>>", self.callbacks["select"])

        pagination_frame = ctk.CTkFrame(container, fg_color="transparent")
        pagination_frame.pack(pady=4)
        ctk.CTkButton(
            pagination_frame,
            text="Trước",
            width=90,
            command=self.callbacks.get("prev"),
        ).pack(side="left", padx=6)
        self.page_label = ctk.CTkLabel(pagination_frame, text="Trang 1/1", width=240)
        self.page_label.pack(side="left", padx=6)
        ctk.CTkButton(
            pagination_frame,
            text="Sau",
            width=90,
            command=self.callbacks.get("next"),
        ).pack(side="left", padx=6)

        self.status_label = ctk.CTkLabel(container, text="Sẵn sàng", anchor="w")
        self.status_label.pack(fill="x", pady=(6, 0))

    def get_form_values(self):
        return [self.entries[column].get().strip() for column in self.form_columns]

    def populate_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in data.iterrows():
            values = [
                row[column] if column in row else ""
                for column in self.callbacks["columns"]
            ]
            self.tree.insert("", "end", values=values)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _resize_tree_columns(self, event=None):
        width = self.tree_frame.winfo_width()
        if width <= 0:
            return
        available = max(width - 24, 140)
        total_weight = sum(self.column_weights.values())
        for column, weight in self.column_weights.items():
            self.tree.column(
                column, width=max(int(available * weight / total_weight), 70)
            )

    def clear_input(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def set_status(self, text):
        self.status_label.configure(text=text)

    def set_page_label(self, text):
        if hasattr(self, "page_label"):
            self.page_label.configure(text=text)

    def get_search_keyword(self):
        return self.search_keyword.get().strip()

    def get_search_column(self):
        return self.search_column.get()

    def get_selected_statistic(self):
        return self.stats_option.get()

    def get_selected_values(self):
        selected = self.tree.focus()
        return self.tree.item(selected, "values")

    def fill_entry_values(self, values):
        for column, value in zip(self.form_columns, values):
            entry = self.entries[column]
            entry.delete(0, tk.END)
            entry.insert(0, value)
