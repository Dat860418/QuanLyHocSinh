from tkinter import filedialog, messagebox

import pandas as pd

from common.loading import AsyncTaskRunner
from common.validation import ValidationError, validate_monhoc_payload
from model.diem_query import DiemQuery
from model.monhoc_query import MonHocQuery
from views.quanly_monhoc_view import QuanLyMonHocView


class QuanLyMonHocController:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = MonHocQuery()
        self.diem_query = DiemQuery()
        self.selected_ma_mon = None
        self.current_data = None
        self.view = QuanLyMonHocView(
            master,
            {
                "columns": self.q.columns,
                "search": self.tim,
                "add": self.them,
                "delete": self.xoa,
                "edit": self.sua,
                "refresh": self.load_data,
                "import_csv": self.import_csv,
                "export_csv": self.export_csv,
                "back": self.back,
                "select": self.on_select,
            },
        )
        self.load_data()

    def load_data(self):
        """Đọc toàn bộ danh sách môn học và vẽ lại bảng."""
        self.selected_ma_mon = None
        self.current_data = self.q.get_all()
        self.view.populate_tree(self.current_data)
        self.view.set_status("Đã hiển thị toàn bộ môn học")
        self.view.clear_input()

    def on_select(self, event):
        """Lấy dòng được chọn và đổ dữ liệu vào các ô nhập để sửa."""
        values = self.view.get_selected_values()
        if not values:
            return
        self.selected_ma_mon = values[0]
        self.view.fill_entry_values(values)

    def get_form_values(self):
        """Chuẩn hóa dữ liệu form sang cấu trúc dữ liệu mong muốn của model."""
        return validate_monhoc_payload(self.view.get_form_values())

    def them(self):
        """Thêm môn học mới và làm mới danh sách."""
        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if not self.q.find_exact("ma_mon", values["ma_mon"]).empty:
            messagebox.showerror("Lỗi", "Mã môn đã tồn tại")
            return

        self.q.create([values[column] for column in self.q.columns])
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def xoa(self):
        """Chặn xóa môn học nếu đã có điểm, tránh phá vỡ dữ liệu liên kết."""
        ma_mon = self.view.entries["ma_mon"].get().strip()
        if not ma_mon:
            messagebox.showerror("Lỗi", "Nhập mã môn để xóa")
            return
        if self.diem_query.subject_has_grades(ma_mon):
            messagebox.showerror("Lỗi", "Không thể xóa môn học đã có dữ liệu điểm")
            return
        self.q.delete("ma_mon", ma_mon)
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def sua(self):
        """Cập nhật môn học đã chọn."""
        if not self.selected_ma_mon:
            messagebox.showerror("Lỗi", "Vui lòng chọn môn học cần sửa")
            return

        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if (
            values["ma_mon"] != self.selected_ma_mon
            and not self.q.find_exact("ma_mon", values["ma_mon"]).empty
        ):
            messagebox.showerror("Lỗi", "Mã môn đã tồn tại")
            return

        if not messagebox.askyesno(
            "Xác nhận sửa",
            "Bạn có chắc muốn lưu thay đổi cho môn học này?",
        ):
            return

        self.q.update(
            "ma_mon",
            self.selected_ma_mon,
            [values[column] for column in self.q.columns],
        )
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def tim(self):
        """Lọc môn học theo cột và từ khóa."""
        keyword = self.view.get_search_keyword()
        column = self.view.get_search_column()
        self.view.clear_table()
        data = self.q.get_all()
        if keyword:
            self.current_data = data[
                data[column]
                .astype(str)
                .str.contains(keyword, case=False, na=False, regex=True)
            ]
            self.view.set_status(f"Tìm thấy {len(self.current_data)} dòng")
        else:
            self.current_data = data
            self.view.set_status("Đã hiển thị toàn bộ môn học")
        self.view.populate_tree(self.current_data)
        self.view.clear_input()

    def import_csv(self):
        """Nhập danh sách môn học từ CSV sau khi kiểm tra cấu trúc và trùng mã."""
        path = filedialog.askopenfilename(
            title="Chọn file CSV", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        try:
            imported = pd.read_csv(path, encoding="utf-8", dtype=str).fillna("")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file: {e}")
            return

        if list(imported.columns) != self.q.columns:
            messagebox.showerror("Lỗi", "File CSV không đúng cấu trúc")
            return

        existing = self.q.get_all()["ma_mon"].astype(str)
        new_values = imported["ma_mon"].astype(str)
        duplicates = existing.isin(new_values).any() or new_values.duplicated().any()
        if duplicates:
            messagebox.showerror("Lỗi", "File nhập có mã môn trùng hoặc đã tồn tại")
            return

        runner = AsyncTaskRunner(self.master, "Đang nhập môn học...")

        def worker():
            for _, row in imported.iterrows():
                try:
                    payload = validate_monhoc_payload(
                        [row[column] for column in self.q.columns]
                    )
                except ValidationError as exc:
                    raise ValueError(str(exc)) from exc
                self.q.create([payload[column] for column in self.q.columns])
            return len(imported)

        def on_success(count):
            self.load_data()
            messagebox.showinfo("Thành công", f"Đã nhập {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def export_csv(self):
        """Xuất dữ liệu đang được lọc hoặc hiển thị ra file CSV."""
        if self.current_data is None:
            self.current_data = self.q.get_all()
        path = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            initialfile="monhoc_filtered.csv",
        )
        if not path:
            return

        runner = AsyncTaskRunner(self.master, "Đang xuất môn học...")

        def worker():
            self.current_data.to_csv(path, index=False, encoding="utf-8")
            return len(self.current_data)

        def on_success(count):
            messagebox.showinfo("Thành công", f"Đã xuất {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def back(self):
        self.app_manager.show_home_page()
