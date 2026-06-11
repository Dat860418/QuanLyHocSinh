import time
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd

from common.loading import AsyncTaskRunner
from common.validation import ValidationError, validate_student_payload
from model.diem_query import DiemQuery
from model.sinhvien_query import SinhVienQuery
from views.quanly_sv_view import QuanLySVView


class QuanLySVController:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = SinhVienQuery()
        self.diem_query = DiemQuery()
        self.selected_ma_sv = None
        self.current_page = 1
        self.page_size = 10
        self.current_data = None
        self.view = QuanLySVView(
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
                "prev": self.prev_page,
                "next": self.next_page,
            },
        )
        self.load_data()

    def load_data(self):
        """Tải lại dữ liệu sinh viên và reset về trang đầu tiên."""
        self.selected_ma_sv = None
        self.current_page = 1
        self.current_data = self.q.get_all()
        self.show_current_page()
        self.view.set_status("Đã hiển thị toàn bộ sinh viên")
        self.view.clear_input()

    def show_current_page(self):
        """Cập nhật bảng theo trang hiện tại và hiển thị tổng số trang."""
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
        """Đọc dòng được chọn từ bảng và đưa dữ liệu lên form để sửa."""
        values = self.view.get_selected_values()
        if not values:
            return
        # Dùng mã sinh viên làm khóa chính đang chọn để phục vụ thao tác sửa/xóa.
        self.selected_ma_sv = values[0]
        self.view.fill_entry_values(values)

    def get_form_values(self):
        """Chuẩn hóa dữ liệu từ form về định dạng dùng cho model."""
        return validate_student_payload(self.view.get_form_values())

    def them(self):
        """Thêm mới sinh viên, sau đó tải lại bảng."""
        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if self.q.get_all()["ma_sv"].astype(str).isin([values["ma_sv"]]).any():
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
            return

        self.q.create([values[column] for column in self.q.columns])
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def xoa(self):
        """Xóa sinh viên đang chọn và dọn luôn điểm liên quan để tránh dữ liệu mồ côi."""
        ma_sv = self.view.entries["ma_sv"].get().strip()
        if not ma_sv:
            messagebox.showerror("Lỗi", "Nhập mã sinh viên để xóa")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa sinh viên này?"):
            # Xóa điểm trước để tránh để lại bản ghi tham chiếu đến sinh viên đã mất.
            self.q.delete("ma_sv", ma_sv)
            self.diem_query.delete_by_student(ma_sv)
            self.view.clear_table()
            self.load_data()
            self.view.clear_input()

    def sua(self):
        """Cập nhật thông tin sinh viên đã chọn."""
        if not self.selected_ma_sv:
            messagebox.showerror("Lỗi", "Vui lòng chọn sinh viên cần sửa")
            return

        try:
            values = self.get_form_values()
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if (
            values["ma_sv"] != self.selected_ma_sv
            and not self.q.find_exact("ma_sv", values["ma_sv"]).empty
        ):
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
            return

        if not messagebox.askyesno(
            "Xác nhận sửa",
            "Bạn có chắc muốn lưu thay đổi cho sinh viên này?",
        ):
            return

        self.q.update(
            "ma_sv", self.selected_ma_sv, [values[column] for column in self.q.columns]
        )
        self.view.clear_table()
        self.load_data()
        self.view.clear_input()

    def tim(self):
        """Lọc dữ liệu theo cột đang chọn và từ khóa tìm kiếm."""
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
            self.view.set_status("Đã hiển thị toàn bộ sinh viên")
        self.current_page = 1
        self.show_current_page()
        self.view.clear_input()

    def import_csv(self):
        """Nhập sinh viên từ CSV sau khi kiểm tra cấu trúc và trùng mã."""
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

        for col in self.q.columns:
            imported[col] = imported[col].astype(str).str.strip()
        imported = imported.replace({"nan": ""})
        imported["sdt"] = imported["sdt"].str.replace(r"\D", "", regex=True)

        existing_data = self.q.get_all()
        existing_keys = existing_data["ma_sv"].astype(str)
        new_keys = imported["ma_sv"]

        if new_keys.duplicated().any():
            messagebox.showerror("Lỗi", "File nhập có mã sinh viên trùng trong file")
            return

        existing_conflicts = imported[imported["ma_sv"].isin(existing_keys)]
        new_rows = imported[~imported["ma_sv"].isin(existing_keys)]

        same_keys = []
        changed_rows = []
        for _, row in existing_conflicts.iterrows():
            key = row["ma_sv"]
            existing_row = existing_data[
                existing_data["ma_sv"].astype(str) == key
            ].iloc[0]
            if all(str(existing_row[col]) == str(row[col]) for col in self.q.columns):
                same_keys.append(key)
            else:
                changed_rows.append(row)

        if new_rows.empty and not changed_rows:
            messagebox.showinfo(
                "Không có dữ liệu mới",
                "File nhập không có dòng mới hoặc khác so với dữ liệu hiện tại.",
            )
            return

        if changed_rows:
            if not messagebox.askyesno(
                "Xác nhận nhập",
                f"File nhập chứa {len(changed_rows)} sinh viên có dữ liệu khác so với dữ liệu hiện tại. Tiếp tục ghi đè và thêm mới?",
            ):
                return

        # AsyncTaskRunner sẽ hiển thị loading overlay nếu tác vụ kéo dài quá 3 giây
        runner = AsyncTaskRunner(self.master, "Đang nhập sinh viên...")

        def worker():
            time.sleep(5)  # Kiểm thử loading (quá 3 giây sẽ hiển thị loading overlay)
            imported_count = 0
            for _, row in new_rows.iterrows():
                try:
                    payload = validate_student_payload(
                        [row[column] for column in self.q.columns]
                    )
                except ValidationError as exc:
                    raise ValueError(str(exc)) from exc
                self.q.create([payload[column] for column in self.q.columns])
                imported_count += 1

            for row in changed_rows:
                try:
                    payload = validate_student_payload(
                        [row[column] for column in self.q.columns]
                    )
                except ValidationError as exc:
                    raise ValueError(str(exc)) from exc
                self.q.update(
                    "ma_sv",
                    row["ma_sv"],
                    [payload[column] for column in self.q.columns],
                )
                imported_count += 1

            return imported_count

        def on_success(count):
            self.load_data()
            if changed_rows:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã nhập {len(new_rows)} dòng mới và cập nhật {len(changed_rows)} dòng khác.",
                )
            else:
                messagebox.showinfo(
                    "Thành công",
                    f"Đã nhập {len(new_rows)} dòng mới và bỏ qua {len(same_keys)} dòng giống dữ liệu hiện tại.",
                )

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def export_csv(self):
        """Xuất dữ liệu đang hiển thị (hoặc dữ liệu đã lọc) ra file CSV."""
        if self.current_data is None:
            self.load_data()
            return
        path = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            initialfile="sinhvien_filtered.csv",
        )
        if not path:
            return

        # AsyncTaskRunner sẽ hiển thị loading overlay nếu tác vụ kéo dài quá 3 giây
        runner = AsyncTaskRunner(self.master, "Đang xuất sinh viên...")

        def worker():
            time.sleep(5)  # Kiểm thử loading (quá 3 giây sẽ hiển thị loading overlay)
            self.current_data.to_csv(path, index=False, encoding="utf-8")
            return len(self.current_data)

        def on_success(count):
            messagebox.showinfo("Thành công", f"Đã xuất {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def back(self):
        self.app_manager.show_home_page()
