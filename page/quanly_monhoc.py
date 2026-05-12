import tkinter as tk
from tkinter import ttk, messagebox

from query.diem_query import DiemQuery
from query.monhoc_query import MonHocQuery


class QuanLyMonHocPage:
    """CRUD môn học; ma_mon là khóa chính được dùng để sửa/xóa/tìm kiếm."""

    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = MonHocQuery()
        self.diem_query = DiemQuery()
        self.selected_ma_mon = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.master, text="Quản lý môn học", font=("Arial", 20, "bold")).pack(
            pady=10
        )

        frame = tk.Frame(self.master)
        frame.pack(pady=10)

        tk.Label(frame, text="Mã môn:", width=15, anchor="w").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.entry_ma = tk.Entry(frame)
        self.entry_ma.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Tên môn:", width=15, anchor="w").grid(
            row=1, column=0, padx=5, pady=5
        )
        self.entry_ten = tk.Entry(frame)
        self.entry_ten.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Số tín chỉ:", width=15, anchor="w").grid(
            row=2, column=0, padx=5, pady=5
        )
        self.entry_so_tc = tk.Entry(frame)
        self.entry_so_tc.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Thêm", width=10, command=self.them).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Xóa", width=10, command=self.xoa).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Sửa", width=10, command=self.sua).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Tìm", width=10, command=self.tim).pack(
            side="left", padx=5
        )
        tk.Button(
            btn_frame, text="Hiển thị tất cả", width=13, command=self.load_data
        ).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Quay lại", command=self.back).pack(
            side="left", padx=5
        )

        self.tree = ttk.Treeview(self.master, columns=self.q.columns, show="headings")
        self.tree.heading("ma_mon", text="Mã môn")
        self.tree.heading("ten_mon", text="Tên môn")
        self.tree.heading("so_tin_chi", text="Số tín chỉ")
        self.tree.column("ma_mon", width=120, anchor="center")
        self.tree.column("ten_mon", width=260)
        self.tree.column("so_tin_chi", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def get_form_values(self):
        # Trả dữ liệu đúng thứ tự cột trong monhoc.csv.
        return [
            self.entry_ma.get().strip(),
            self.entry_ten.get().strip(),
            self.entry_so_tc.get().strip(),
        ]

    def load_data(self):
        self.fill_tree(self.q.get_all())

    def fill_tree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in data.iterrows():
            self.tree.insert(
                "", "end", values=[row[column] for column in self.q.columns]
            )

    def on_select(self, event):
        selected = self.tree.focus()
        values = self.tree.item(selected, "values")
        if not values:
            return
        self.selected_ma_mon = values[0]
        self.entry_ma.delete(0, tk.END)
        self.entry_ma.insert(0, values[0])
        self.entry_ten.delete(0, tk.END)
        self.entry_ten.insert(0, values[1])
        self.entry_so_tc.delete(0, tk.END)
        self.entry_so_tc.insert(0, values[2])

    def clear_input(self):
        self.selected_ma_mon = None
        self.entry_ma.delete(0, tk.END)
        self.entry_ten.delete(0, tk.END)
        self.entry_so_tc.delete(0, tk.END)

    def validate(self):
        # Kiểm tra riêng số tín chỉ vì dữ liệu này cần là số nguyên.
        ma_mon, ten_mon, so_tin_chi, he_so_diem = self.get_form_values()
        if not ma_mon or not ten_mon or not so_tin_chi:
            messagebox.showerror("Lỗi", "Nhập đầy đủ thông tin")
            return None
        try:
            so_tin_chi = int(so_tin_chi)
        except ValueError:
            messagebox.showerror("Lỗi", "Số tín chỉ phải là số nguyên")
            return None
        return [ma_mon, ten_mon, so_tin_chi]

    def them(self):
        values = self.validate()
        if values is None:
            return
        if not self.q.find_exact("ma_mon", values[0]).empty:
            messagebox.showerror("Lỗi", "Mã môn đã tồn tại")
            return
        self.q.create(values)
        self.load_data()
        self.clear_input()

    def xoa(self):
        ma_mon = self.entry_ma.get().strip()
        if not ma_mon:
            messagebox.showerror("Lỗi", "Nhập mã môn để xóa")
            return
        # Code cũ giữ lại:
        # self.q.delete("ma_mon", ma_mon)
        # Code mới: không cho xóa môn học đã có dữ liệu điểm.
        if self.diem_query.subject_has_grades(ma_mon):
            messagebox.showerror("Lỗi", "Không thể xóa môn học đã có dữ liệu điểm")
            return
        self.q.delete("ma_mon", ma_mon)
        self.load_data()
        self.clear_input()

    def sua(self):
        # Sửa theo mã môn cũ để vẫn đúng dòng nếu người dùng đổi mã môn.
        if not self.selected_ma_mon:
            messagebox.showerror("Lỗi", "Vui lòng chọn môn học cần sửa")
            return
        values = self.validate()
        if values is None:
            return
        if (
            values[0] != self.selected_ma_mon
            and not self.q.find_exact("ma_mon", values[0]).empty
        ):
            messagebox.showerror("Lỗi", "Mã môn đã tồn tại")
            return
        self.q.update("ma_mon", self.selected_ma_mon, values)
        self.load_data()
        self.clear_input()

    def tim(self):
        # Ưu tiên tìm theo mã môn; nếu mã trống thì tìm theo tên môn.
        keyword = self.entry_ma.get().strip() or self.entry_ten.get().strip()
        column = "ma_mon" if self.entry_ma.get().strip() else "ten_mon"
        self.fill_tree(self.q.search(column, keyword))

    def back(self):
        self.app_manager.show_quanlytk_page()
