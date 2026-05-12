import tkinter as tk
from tkinter import ttk, messagebox

from query.diem_query import DiemQuery
from query.monhoc_query import MonHocQuery
from query.sinhvien_query import SinhVienQuery


class QuanLyDiemPage:
    """CRUD điểm, hiển thị dữ liệu đã join và thống kê bằng Pandas."""

    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = DiemQuery()
        # Dùng để kiểm tra khóa ngoại trước khi lưu điểm.
        self.sv_query = SinhVienQuery()
        self.mon_query = MonHocQuery()
        self.selected_id = None
        # current_data là tập dữ liệu hiện tại sau tìm kiếm/thống kê, dùng cho phân trang.
        self.current_page = 1
        self.page_size = 10
        self.current_data = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.master, text="Quản lý điểm", font=("Arial", 20, "bold")).pack(pady=10)

        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=5)

        self.entries = {}
        fields = [
            ("ma_sv", "Mã sinh viên"),
            ("ma_mon", "Mã môn"),
            ("diem_cc", "Điểm CC"),
            ("diem_kt1", "Điểm KT1"),
            ("diem_kt2", "Điểm KT2"),
            ("diem_ck", "Điểm CK"),
        ]
        for idx, (key, label) in enumerate(fields):
            # Mỗi hàng đặt 3 cặp label/input để form gọn.
            row = idx // 3
            col = (idx % 3) * 2
            tk.Label(input_frame, text=label + ":", width=13, anchor="w").grid(row=row, column=col, padx=4, pady=4)
            entry = tk.Entry(input_frame, width=18)
            entry.grid(row=row, column=col + 1, padx=4, pady=4)
            self.entries[key] = entry

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=8)

        tk.Button(button_frame, text="Thêm", width=10, command=self.them).pack(side="left", padx=4)
        tk.Button(button_frame, text="Xóa", width=10, command=self.xoa).pack(side="left", padx=4)
        tk.Button(button_frame, text="Sửa", width=10, command=self.sua).pack(side="left", padx=4)
        tk.Button(button_frame, text="Tìm", width=10, command=self.tim).pack(side="left", padx=4)
        tk.Button(button_frame, text="Hiển thị tất cả", width=13, command=self.load_data).pack(side="left", padx=4)

        self.combo_thong_ke = ttk.Combobox(
            button_frame,
            values=("Top 5 điểm cao nhất", "Sinh viên nợ môn", "GPA theo sinh viên"),
            state="readonly",
            width=18,
        )
        self.combo_thong_ke.current(0)
        self.combo_thong_ke.pack(side="left", padx=4)
        tk.Button(button_frame, text="Thống kê", width=10, command=self.thong_ke).pack(side="left", padx=4)
        tk.Button(button_frame, text="Quay lại", width=10, command=self.back).pack(side="left", padx=4)

        columns = (
            "id",
            "ma_sv",
            "ho_ten",
            "ten_mon",
            "diem_cc",
            "diem_kt1",
            "diem_kt2",
            "diem_ck",
            "diem_tong_ket",
            "xep_loai",
        )
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings")
        headings = {
            "id": "ID",
            "ma_sv": "Mã SV",
            "ho_ten": "Tên SV",
            "ten_mon": "Tên Môn",
            "diem_cc": "CC",
            "diem_kt1": "KT1",
            "diem_kt2": "KT2",
            "diem_ck": "CK",
            "diem_tong_ket": "Điểm Số",
            "xep_loai": "Xếp Loại",
        }
        for column, heading in headings.items():
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=90, anchor="center")
        self.tree.column("ho_ten", width=180)
        self.tree.column("ten_mon", width=180)

        self.tree.pack(fill="both", expand=True, padx=15, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        pagination_frame = tk.Frame(self.master)
        pagination_frame.pack(pady=5)
        tk.Button(pagination_frame, text="Trước", width=10, command=self.prev_page).pack(side="left", padx=5)
        self.page_label = tk.Label(pagination_frame, text="Trang 1/1", width=22)
        self.page_label.pack(side="left", padx=5)
        tk.Button(pagination_frame, text="Sau", width=10, command=self.next_page).pack(side="left", padx=5)

        self.status_label = tk.Label(self.master, text="Sẵn sàng", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def fill_tree(self, data):
        # Xóa bảng cũ trước khi nạp dữ liệu mới để tránh trùng dòng.
        for item in self.tree.get_children():
            self.tree.delete(item)
        columns = self.tree["columns"]
        for _, row in data.iterrows():
            self.tree.insert("", "end", iid=str(row["id"]), values=[row[column] for column in columns])

    def load_data(self):
        # Code cũ giữ lại:
        # self.fill_tree(self.q.get_display_data())
        # Code mới: lưu vào current_data để phân trang.
        self.current_page = 1
        self.current_data = self.q.get_display_data()
        self.show_current_page()
        self.status_label.config(text="Đã hiển thị danh sách điểm tổng hợp")

    def show_current_page(self):
        # Cắt DataFrame theo current_page/page_size, mỗi trang tối đa 10 dòng.
        if self.current_data is None:
            self.current_data = self.q.get_display_data()
        total_records = len(self.current_data)
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        self.current_page = min(max(1, self.current_page), total_pages)
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        self.fill_tree(self.current_data.iloc[start:end])
        self.page_label.config(text=f"Trang {self.current_page}/{total_pages} ({total_records} dòng)")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.show_current_page()

    def next_page(self):
        if self.current_data is None:
            return
        total_pages = max(1, (len(self.current_data) + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.show_current_page()

    def on_select(self, event):
        # Chọn dòng trong bảng để lấy id thật dùng cho sửa/xóa.
        selected = self.tree.focus()
        if not selected:
            return
        data = self.q.find_exact("id", selected)
        if data.empty:
            return
        row = data.iloc[0]
        self.selected_id = row["id"]
        for column in ["ma_sv", "ma_mon", "diem_cc", "diem_kt1", "diem_kt2", "diem_ck"]:
            self.entries[column].delete(0, tk.END)
            self.entries[column].insert(0, row[column])

    def clear_input(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def validate_input(self):
        # Gom dữ liệu từ form và kiểm tra khóa ngoại/điểm trước khi ghi CSV.
        values = {column: self.entries[column].get().strip() for column in self.entries}
        if any(value == "" for value in values.values()):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return None
        if self.sv_query.find_exact("ma_sv", values["ma_sv"]).empty:
            messagebox.showerror("Lỗi", "Mã sinh viên không tồn tại")
            return None
        if self.mon_query.find_exact("ma_mon", values["ma_mon"]).empty:
            messagebox.showerror("Lỗi", "Mã môn không tồn tại")
            return None
        for column in ["diem_cc", "diem_kt1", "diem_kt2", "diem_ck"]:
            try:
                values[column] = float(values[column])
            except ValueError:
                messagebox.showerror("Lỗi", "Các cột điểm phải là số")
                return None
            if values[column] < 0 or values[column] > 10:
                messagebox.showerror("Lỗi", "Điểm phải nằm trong khoảng 0 đến 10")
                return None
        return values

    def is_duplicate(self, ma_sv, ma_mon):
        # Một sinh viên chỉ có một dòng điểm cho mỗi môn.
        data = self.q.get_all()
        duplicate = data[(data["ma_sv"] == ma_sv) & (data["ma_mon"] == ma_mon)]
        if self.selected_id is not None:
            duplicate = duplicate[duplicate["id"].astype(str) != str(self.selected_id)]
        return not duplicate.empty

    def them(self):
        values = self.validate_input()
        if values is None:
            return
        if self.is_duplicate(values["ma_sv"], values["ma_mon"]):
            messagebox.showerror("Lỗi", "Sinh viên đã có điểm cho môn này")
            return
        self.q.create([
            self.q.next_id(),
            values["ma_sv"],
            values["ma_mon"],
            values["diem_cc"],
            values["diem_kt1"],
            values["diem_kt2"],
            values["diem_ck"],
        ])
        self.load_data()
        self.clear_input()

    def xoa(self):
        if self.selected_id is None:
            messagebox.showerror("Lỗi", "Vui lòng chọn điểm cần xóa")
            return
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa điểm này?"):
            return
        self.q.delete("id", self.selected_id)
        self.load_data()
        self.clear_input()

    def sua(self):
        if self.selected_id is None:
            messagebox.showerror("Lỗi", "Vui lòng chọn điểm cần sửa")
            return
        values = self.validate_input()
        if values is None:
            return
        if self.is_duplicate(values["ma_sv"], values["ma_mon"]):
            messagebox.showerror("Lỗi", "Sinh viên đã có điểm cho môn này")
            return
        self.q.update("id", self.selected_id, [
            self.selected_id,
            values["ma_sv"],
            values["ma_mon"],
            values["diem_cc"],
            values["diem_kt1"],
            values["diem_kt2"],
            values["diem_ck"],
        ])
        self.load_data()
        self.clear_input()

    def tim(self):
        # Tìm theo mã sinh viên và/hoặc mã môn trên dữ liệu đã join để vẫn hiển thị tên đầy đủ.
        ma_sv = self.entries["ma_sv"].get().strip()
        ma_mon = self.entries["ma_mon"].get().strip()
        data = self.q.get_display_data()
        if ma_sv:
            data = data[data["ma_sv"].astype(str).str.contains(ma_sv, case=False, na=False)]
        if ma_mon:
            data = data[data["ma_mon"].astype(str).str.contains(ma_mon, case=False, na=False)]
        if data.empty:
            messagebox.showinfo("Thông báo", "Không tìm thấy")
        self.current_page = 1
        self.current_data = data
        self.show_current_page()
        self.status_label.config(text=f"Tìm thấy {len(data)} dòng")

    def thong_ke(self):
        # Thống kê dùng Pandas trên điểm tổng kết đã tính trong DiemQuery.
        data = self.q.get_display_data()
        lua_chon = self.combo_thong_ke.get()
        if lua_chon == "Sinh viên nợ môn":
            result = data[data["diem_tong_ket"] < 4].sort_values("diem_tong_ket")
            self.status_label.config(text=f"Có {len(result)} sinh viên nợ môn")
        elif lua_chon == "GPA theo sinh viên":
            # Code mới: GPA dùng groupby('ma_sv').mean() trong DiemQuery.
            gpa = self.q.gpa_by_student()
            names = data[["ma_sv", "ho_ten"]].drop_duplicates("ma_sv")
            result = gpa.merge(names, on="ma_sv", how="left")
            result["id"] = range(1, len(result) + 1)
            result["ten_mon"] = "GPA"
            result["diem_cc"] = ""
            result["diem_kt1"] = ""
            result["diem_kt2"] = ""
            result["diem_ck"] = ""
            result["xep_loai"] = result["diem_tong_ket"].apply(self.q.xep_loai)
            result = result[["id", "ma_sv", "ho_ten", "ten_mon", "diem_cc", "diem_kt1", "diem_kt2", "diem_ck", "diem_tong_ket", "xep_loai"]]
            self.status_label.config(text=f"GPA của {len(result)} sinh viên")
        else:
            result = data.sort_values("diem_tong_ket", ascending=False).head(5)
            self.status_label.config(text="Top 5 sinh viên điểm cao nhất")
        self.current_page = 1
        self.current_data = result
        self.show_current_page()

    def back(self):
        self.app_manager.show_quanlytk_page()
