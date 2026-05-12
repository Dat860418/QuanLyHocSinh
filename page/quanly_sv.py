import tkinter as tk
from tkinter import ttk, messagebox

from query.diem_query import DiemQuery
from query.sinhvien_query import SinhVienQuery


class QuanLySVPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = SinhVienQuery()
        self.diem_query = DiemQuery()
        self.selected_ma_sv = None
        # current_data lưu tập dữ liệu hiện tại sau khi tìm kiếm để nút Trước/Sau phân trang đúng.
        self.current_page = 1
        self.page_size = 10
        self.current_data = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.master, text="Quản lý sinh viên", font=("Arial", 20, "bold")).pack(pady=10)

        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=5)

        self.entries = {}
        # Cấu hình các trường nhập theo schema CSV, giúp form dễ mở rộng khi thêm cột.
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
            # Chia form thành 3 cột input để màn hình sinh viên không quá dài.
            row = idx // 3
            col = (idx % 3) * 2
            tk.Label(input_frame, text=label + ":", width=12, anchor="w").grid(row=row, column=col, padx=4, pady=4)
            if key == "trang_thai":
                entry = ttk.Combobox(input_frame, values=("Đang học", "Đã nghỉ"), state="readonly", width=18)
                entry.current(0)
            else:
                entry = tk.Entry(input_frame, width=21)
            entry.grid(row=row, column=col + 1, padx=4, pady=4)
            self.entries[key] = entry

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=8)

        tk.Button(button_frame, text="Thêm", width=10, command=self.them).pack(side="left", padx=5)
        tk.Button(button_frame, text="Xóa", width=10, command=self.xoa).pack(side="left", padx=5)
        tk.Button(button_frame, text="Sửa", width=10, command=self.sua).pack(side="left", padx=5)
        tk.Button(button_frame, text="Tìm", width=10, command=self.tim).pack(side="left", padx=5)
        tk.Button(button_frame, text="Hiển thị tất cả", width=13, command=self.load_data).pack(side="left", padx=5)
        tk.Button(button_frame, text="Quay lại", command=self.back).pack(side="left", padx=5)

        columns = self.q.columns
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings")
        headings = ["Mã SV", "Họ tên", "Ngày sinh", "Giới tính", "Lớp", "Địa chỉ", "SĐT", "Email", "Trạng thái"]
        for column, heading in zip(columns, headings):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=110)
        self.tree.column("ho_ten", width=180)
        self.tree.column("dia_chi", width=160)
        self.tree.column("email", width=180)

        self.tree.pack(fill="both", expand=True, padx=12, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        pagination_frame = tk.Frame(self.master)
        pagination_frame.pack(pady=5)
        tk.Button(pagination_frame, text="Trước", width=10, command=self.prev_page).pack(side="left", padx=5)
        self.page_label = tk.Label(pagination_frame, text="Trang 1/1", width=22)
        self.page_label.pack(side="left", padx=5)
        tk.Button(pagination_frame, text="Sau", width=10, command=self.next_page).pack(side="left", padx=5)

    def get_form_values(self):
        # Trả dữ liệu đúng thứ tự cột của SinhVienQuery để ghi CSV không lệch cột.
        return [self.entries[column].get().strip() for column in self.q.columns]

    def load_data(self):
        # Tải lại toàn bộ danh sách và đưa phân trang về trang đầu.
        self.current_page = 1
        self.current_data = self.q.get_all()
        self.show_current_page()

    def fill_tree(self, data):
        # Làm mới Treeview trước khi đổ dữ liệu của trang hiện tại.
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in data.iterrows():
            self.tree.insert("", "end", values=[row[column] for column in self.q.columns])

    def show_current_page(self):
        # Cắt current_data thành từng trang, mỗi trang tối đa 10 dòng.
        if self.current_data is None:
            self.current_data = self.q.get_all()

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
        # Click một dòng sẽ fill dữ liệu lên form để người dùng sửa/xóa.
        selected = self.tree.focus()
        values = self.tree.item(selected, "values")
        if not values:
            return
        self.selected_ma_sv = values[0]
        for column, value in zip(self.q.columns, values):
            self.entries[column].delete(0, tk.END)
            self.entries[column].insert(0, value)

    def clear_input(self):
        # Reset form sau thao tác thêm/sửa/xóa.
        self.selected_ma_sv = None
        for column, entry in self.entries.items():
            entry.delete(0, tk.END)
            if column == "trang_thai":
                entry.set("Đang học")

    def them(self):
        # Tối thiểu cần mã sinh viên và họ tên; các trường khác có thể bổ sung sau.
        values = self.get_form_values()
        ma_sv, ho_ten = values[0], values[1]
        if not ma_sv or not ho_ten:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã sinh viên và họ tên")
            return
        # Code cũ giữ lại:
        # if not self.q.find_exact("ma_sv", ma_sv).empty:
        # Code mới: dùng isin() đúng yêu cầu validation bằng Pandas.
        if self.q.get_all()["ma_sv"].astype(str).isin([ma_sv]).any():
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
            return
        self.q.create(values)
        self.load_data()
        self.clear_input()

    def xoa(self):
        ma_sv = self.entries["ma_sv"].get().strip()
        if not ma_sv:
            messagebox.showerror("Lỗi", "Nhập mã sinh viên để xóa")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa sinh viên này?"):
            # Code cũ giữ lại:
            # self.q.delete("ma_sv", ma_sv)
            # Code mới: xóa sinh viên và quét sang diem.csv để xóa điểm liên quan.
            self.q.delete("ma_sv", ma_sv)
            self.diem_query.delete_by_student(ma_sv)
            self.load_data()
            self.clear_input()

    def sua(self):
        # Sửa theo mã sinh viên cũ để vẫn cập nhật đúng dòng nếu người dùng đổi mã.
        if not self.selected_ma_sv:
            messagebox.showerror("Lỗi", "Vui lòng chọn sinh viên cần sửa")
            return
        values = self.get_form_values()
        if not values[0] or not values[1]:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã sinh viên và họ tên")
            return
        if values[0] != self.selected_ma_sv and not self.q.find_exact("ma_sv", values[0]).empty:
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
            return
        self.q.update("ma_sv", self.selected_ma_sv, values)
        self.load_data()
        self.clear_input()

    def tim(self):
        # Ưu tiên tìm theo mã SV, tiếp theo họ tên, cuối cùng là mã lớp.
        keyword = (
            self.entries["ma_sv"].get().strip()
            or self.entries["ho_ten"].get().strip()
            or self.entries["lop"].get().strip()
        )
        if self.entries["ma_sv"].get().strip():
            column = "ma_sv"
        elif self.entries["ho_ten"].get().strip():
            column = "ho_ten"
        else:
            column = "lop"
        self.current_page = 1
        # Code cũ giữ lại:
        # self.current_data = self.q.search(column, keyword)
        # Code mới: regex=True cho phép tìm nâng cao theo mẫu tên hoặc mã lớp.
        data = self.q.get_all()
        self.current_data = data[data[column].astype(str).str.contains(keyword, case=False, na=False, regex=True)]
        self.show_current_page()

    def back(self):
        self.app_manager.show_quanlytk_page()
