from datetime import date
from tkinter import filedialog, messagebox

import pandas as pd

from common.loading import AsyncTaskRunner
from model.taikhoan_query import TaiKhoanQuery
from views.quanlytk_view import QuanLyTKView


class QuanLyTKController:
    def __init__(self, master, app_manager):
        self.app_manager = app_manager
        self.model = TaiKhoanQuery()
        self.current_data = None

        if not self.app_manager.is_admin():
            messagebox.showerror(
                "Không có quyền", "Chỉ Admin mới được quản lý tài khoản"
            )
            self.app_manager.show_home_page()
            return

        self.view = QuanLyTKView(
            master,
            self.load_accounts,
            self.create_account,
            self.delete_account,
            self.edit_account,
            self.reset_password,
            self.import_accounts,
            self.export_accounts,
            self.back_to_home,
            self.search_accounts,
        )
        self.load_accounts()

    def load_accounts(self):
        self.current_data = self.model.get_all()
        self.view.populate_tree(self.current_data)
        self.view.set_status(f"Đã tải {len(self.current_data)} tài khoản")
        self.view.clear_search()

    def search_accounts(self):
        keyword = self.view.get_keyword()
        column = self.view.get_search_column()
        data = self.model.get_all()
        if keyword:
            self.current_data = data[
                data[column]
                .astype(str)
                .str.contains(keyword, case=False, na=False, regex=True)
            ]
            self.view.set_status(f"Tìm thấy {len(self.current_data)} tài khoản")
        else:
            self.current_data = data
            self.view.set_status(f"Đã tải {len(self.current_data)} tài khoản")
        self.view.populate_tree(self.current_data)

    def delete_account(self):
        username = self.view.get_selected_username()
        if not username:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản")
            return

        account = self.model.find_exact("username", username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return

        role = str(account.iloc[0]["chuc_vu"]).lower()
        if role == "admin" and self.model.count_admins() <= 1:
            messagebox.showerror("Lỗi", "Không thể xóa Admin cuối cùng")
            return

        if messagebox.askyesno(
            "Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"
        ):
            self.model.delete("username", username)
            self.load_accounts()
            messagebox.showinfo("Thành công", "Đã xóa tài khoản")

    def edit_account(self):
        username = self.view.get_selected_username()
        if not username:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản")
            return
        account = self.model.find_exact("username", username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return
        self.app_manager.show_suatk_page(username, account.iloc[0]["password"])

    def reset_password(self):
        username = self.view.get_selected_username()
        if not username:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản")
            return
        if messagebox.askyesno("Xác nhận", f"Reset mật khẩu '{username}' về 12345?"):
            self.model.reset_password(username)
            self.load_accounts()
            messagebox.showinfo("Thành công", "Đã reset mật khẩu về 12345")

    def import_accounts(self):
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

        if list(imported.columns) != self.model.columns:
            messagebox.showerror("Lỗi", "File CSV không đúng cấu trúc")
            return

        existing_usernames = set(self.model.get_all()["username"].astype(str))
        import_usernames = set(imported["username"].astype(str))
        if len(import_usernames) != len(imported) or existing_usernames.intersection(
            import_usernames
        ):
            messagebox.showerror("Lỗi", "File nhập có username trùng hoặc đã tồn tại")
            return

        runner = AsyncTaskRunner(self.view.root, "Đang nhập tài khoản...")

        def worker():
            next_id = self.model.next_id()
            for _, row in imported.iterrows():
                username = str(row["username"]).strip()
                password = str(row["password"]).strip()
                ho_ten = str(row["ho_ten"]).strip()
                if not username or not ho_ten:
                    raise ValueError("Username và họ tên không được rỗng")
                if len(password) != 64:
                    password = self.model.hash_password(password)
                sdt = str(row["sdt"]).strip()
                chuc_vu = str(row["chuc_vu"]).strip() or "User"
                ngay_tao = str(row["ngay_tao"]).strip() or date.today().isoformat()
                self.model.create(
                    [
                        next_id,
                        username,
                        password,
                        ho_ten,
                        sdt,
                        chuc_vu,
                        ngay_tao,
                    ]
                )
                next_id += 1
            return len(imported)

        def on_success(count):
            self.load_accounts()
            messagebox.showinfo("Thành công", f"Đã nhập {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def export_accounts(self):
        if self.current_data is None:
            self.current_data = self.model.get_all()
        path = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            initialfile="taikhoan_filtered.csv",
        )
        if not path:
            return

        runner = AsyncTaskRunner(self.view.root, "Đang xuất tài khoản...")

        def worker():
            self.current_data.to_csv(path, index=False, encoding="utf-8")
            return len(self.current_data)

        def on_success(count):
            messagebox.showinfo("Thành công", f"Đã xuất {count} dòng")

        def on_error(exc):
            messagebox.showerror("Lỗi", str(exc))

        runner.run(worker, on_success=on_success, on_error=on_error)

    def back_to_home(self):
        self.app_manager.show_home_page()

    def create_account(self):
        self.app_manager.show_taotk_page()
