from tkinter import filedialog, messagebox

import pandas as pd

from common.loading import AsyncTaskRunner
from common.validation import ValidationError, validate_diem_payload
from model.diem_query import DiemQuery
from model.monhoc_query import MonHocQuery
from model.sinhvien_query import SinhVienQuery
from views.quanly_diem_view import QuanLyDiemView


class QuanLyDiemController:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = DiemQuery()
        self.sv_q = SinhVienQuery()
        self.mon_q = MonHocQuery()
        self.selected_id = None
        self.current_page = 1
        self.page_size = 10
        self.current_data = None
        display_columns = [
            "id",
            "ma_sv",
            "ma_mon",
            "ho_ten",
            "ten_mon",
            "diem_cc",
            "diem_kt1",
            "diem_kt2",
            "diem_ck",
            "diem_tong_ket",
            "xep_loai",
        ]
        self.view = QuanLyDiemView(
            master,
            {
                "columns": display_columns,
                "search": self.tim,
                "add": self.them,
                "delete": self.xoa,
                "edit": self.sua,
                "thong_ke": self.thong_ke,
                "refresh": self.load_data,
                "import_csv": self.import_csv,
                "export_csv": self.export_csv,
                "back": self.back,
                "select": self.on_select,
                "prev": self.prev_page,
                "next": self.next_page,
            },
        )
        self.load_data()

    def load_data(self):
        """Đọc toàn bộ dữ liệu điểm và hiển thị lại bảng."""
        self.selected_id = None
        self.current_page = 1
        self.current_data = self.q.get_display_data()
        self.show_current_page()
        self.view.set_status("Đã hiển thị toàn bộ điểm")
        self.view.clear_input()

    def show_current_page(self):
        if self.current_data is None:
            self.current_data = self.q.get_all()

        total_records = len(self.current_data)
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        self.current_page = min(max(1, self.current_page), total_pages)

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        self.view.populate_tree(self.current_data.iloc[start:end])
        self.view.set_page_label(
            f"Trang {self.current_page}/{total_pages} ({total_records} dòng)"
        )

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.show_current_page()

    def next_page(self):
        if self.current_data is None:
            return
        total_pages = max(
            1, (len(self.current_data) + self.page_size - 1) // self.page_size
        )
        if self.current_page < total_pages:
            self.current_page += 1
            self.show_current_page()

    def on_select(self, event):
        """Khi chọn một dòng, lấy id thật từ file CSV rồi đổ dữ liệu lên form."""
        values = self.view.get_selected_values()
        if not values:
            return
        self.selected_id = None
        ma_sv = values[1]
        ma_mon = values[2]
        row = self.q.get_all()
        row = row[
            (row["ma_sv"].astype(str) == str(ma_sv))
            & (row["ma_mon"].astype(str) == str(ma_mon))
        ]
        if not row.empty:
            self.selected_id = int(row.iloc[0]["id"])
        self.view.fill_entry_values(
            [values[1], values[2], values[5], values[6], values[7], values[8]]
        )

    def get_form_values(self):
        """Chuyển dữ liệu từ form sang cấu trúc dùng cho validate_diem_payload."""
        raw = self.view.get_form_values()
        return validate_diem_payload(
            {
                "ma_sv": raw[0],
                "ma_mon": raw[1],
                "diem_cc": raw[2],
                "diem_kt1": raw[3],
                "diem_kt2": raw[4],
                "diem_ck": raw[5],
            }
        )

    def them(self):
        """Thêm bản ghi điểm mới và tự sinh id."""
        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if (
            not self.sv_q.find_exact("ma_sv", values["ma_sv"]).empty
            and not self.mon_q.find_exact("ma_mon", values["ma_mon"]).empty
        ):
            existing = self.q.find_exact("ma_sv", values["ma_sv"])
            existing = existing[existing["ma_mon"] == values["ma_mon"]]
            if not existing.empty:
                messagebox.showerror("Lỗi", "Sinh viên đã có điểm cho môn này")
                return
        else:
            messagebox.showerror("Lỗi", "Mã sinh viên hoặc mã môn không tồn tại")
            return

        # id được tạo tự động để tránh trùng khi nhập nhiều dòng hoặc import CSV.
        self.q.create(
            [
                self.q.next_id(),
                values["ma_sv"],
                values["ma_mon"],
                values["diem_cc"],
                values["diem_kt1"],
                values["diem_kt2"],
                values["diem_ck"],
            ]
        )
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def xoa(self):
        """Xóa bản ghi điểm đã chọn."""
        if self.selected_id is None:
            messagebox.showerror("Lỗi", "Vui lòng chọn điểm cần xóa")
            return
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa điểm này?"):
            return
        self.q.delete("id", self.selected_id)
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def sua(self):
        """Cập nhật điểm của bản ghi đang chọn."""
        if self.selected_id is None:
            messagebox.showerror("Lỗi", "Vui lòng chọn điểm cần sửa")
            return

        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if self.sv_q.find_exact("ma_sv", values["ma_sv"]).empty:
            messagebox.showerror("Lỗi", "Mã sinh viên không tồn tại")
            return
        if self.mon_q.find_exact("ma_mon", values["ma_mon"]).empty:
            messagebox.showerror("Lỗi", "Mã môn không tồn tại")
            return

        duplicates = self.q.get_all()
        duplicates = duplicates[
            (duplicates["ma_sv"].astype(str) == values["ma_sv"])
            & (duplicates["ma_mon"].astype(str) == values["ma_mon"])
        ]
        if not duplicates.empty and str(int(duplicates.iloc[0]["id"])) != str(
            self.selected_id
        ):
            messagebox.showerror("Lỗi", "Sinh viên đã có điểm cho môn này")
            return

        if not messagebox.askyesno(
            "Xác nhận sửa",
            "Bạn có chắc muốn lưu thay đổi điểm này?",
        ):
            return

        self.q.update(
            "id",
            self.selected_id,
            [
                self.selected_id,
                values["ma_sv"],
                values["ma_mon"],
                values["diem_cc"],
                values["diem_kt1"],
                values["diem_kt2"],
                values["diem_ck"],
            ],
        )
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def tim(self):
        """Lọc bảng điểm theo cột và từ khóa."""
        keyword = self.view.get_search_keyword()
        column = self.view.get_search_column()
        data = self.q.get_display_data()
        if keyword:
            self.current_data = data[
                data[column]
                .astype(str)
                .str.contains(keyword, case=False, na=False, regex=True)
            ]
            self.view.set_status(f"Tìm thấy {len(self.current_data)} dòng")
        else:
            self.current_data = data
            self.view.set_status("Đã hiển thị toàn bộ điểm")
        self.current_page = 1
        self.show_current_page()
        self.view.clear_input()

    def thong_ke(self):
        """Hiển thị thống kê đã chọn và cập nhật bảng dữ liệu."""
        option = self.view.get_selected_statistic()
        if option == "Điểm tổng kết môn dưới 4":
            self.current_data = self.q.get_subject_failures()
        elif option == "Điểm tổng kết môn trên 8":
            self.current_data = self.q.get_high_scores()
        elif option == "Top 5 sinh viên điểm cao nhất":
            self.current_data = self.q.get_top_students_by_gpa()
        elif option == "GPA theo sinh viên":
            self.current_data = self.q.gpa_by_student()
        else:
            self.current_data = self.q.get_display_data()

        if self.current_data.empty:
            messagebox.showinfo("Thống kê", "Không có dữ liệu phù hợp")
            self.current_data = self.q.get_display_data()
        self.current_page = 1
        self.show_current_page()
        self.view.set_status(
            f"Hiển thị kết quả thống kê: {option} ({len(self.current_data)} dòng)"
        )
        self.view.clear_input()

    def import_csv(self):
        """Nhập điểm từ CSV, đồng thời kiểm tra mã sinh viên và môn học tồn tại."""
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

        runner = AsyncTaskRunner(self.master, "Đang nhập điểm...")

        def worker():
            for _, row in imported.iterrows():
                try:
                    payload = validate_diem_payload(
                        {
                            "ma_sv": row["ma_sv"],
                            "ma_mon": row["ma_mon"],
                            "diem_cc": row["diem_cc"],
                            "diem_kt1": row["diem_kt1"],
                            "diem_kt2": row["diem_kt2"],
                            "diem_ck": row["diem_ck"],
                        }
                    )
                except ValidationError as exc:
                    raise ValueError(str(exc)) from exc

                self.q.create(
                    [
                        int(row.get("id", self.q.next_id())),
                        payload["ma_sv"],
                        payload["ma_mon"],
                        payload["diem_cc"],
                        payload["diem_kt1"],
                        payload["diem_kt2"],
                        payload["diem_ck"],
                    ]
                )
            return len(imported)

        def on_success(count):
            self.load_data()
            messagebox.showinfo("Thành công", f"Đã nhập {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def export_csv(self):
        """Xuất dữ liệu đang hiển thị hoặc dữ liệu đã lọc ra file CSV."""
        if self.current_data is None:
            self.current_data = self.q.get_all()

        export_data = self.current_data
        if all(column in export_data.columns for column in self.q.columns):
            export_data = export_data[self.q.columns]

        path = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            initialfile="diem_export.csv",
        )
        if not path:
            return

        runner = AsyncTaskRunner(self.master, "Đang xuất điểm...")

        def worker():
            export_data.to_csv(path, index=False, encoding="utf-8")
            return len(export_data)

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        def on_success(count):
            messagebox.showinfo("Thành công", f"Đã xuất {count} dòng")

        runner.run(worker, on_success=on_success, on_error=on_error)

    def back(self):
        self.app_manager.show_home_page()
