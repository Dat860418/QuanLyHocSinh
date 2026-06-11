from tkinter import messagebox

from common.validation import ValidationError, validate_account_payload
from model.taikhoan_query import TaiKhoanQuery
from views.suatk_view import SuaTKView


class SuaTKController:
    def __init__(self, master, app_manager, username=None, password=None):
        self.app_manager = app_manager
        self.old_username = username or ""
        self.old_password = password or ""
        self.model = TaiKhoanQuery()
        self.view = SuaTKView(
            master, self.handle_save, self.handle_back, self.handle_toggle
        )
        self.load_account()

    def handle_toggle(self):
        self.view.set_password_visible(self.view.show_password.get())

    def handle_back(self):
        self.app_manager.show_quanlytk_page()

    def load_account(self):
        account = self.model.find_exact("username", self.old_username)
        row = account.iloc[0].to_dict() if not account.empty else {}
        self.view.set_values(row)

    def handle_save(self):
        try:
            payload = validate_account_payload(
                self.view.get_payload_values(),
                require_password=False,
            )
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if self.model.username_exists(
            payload["username"], exclude_username=self.old_username
        ):
            messagebox.showerror("Lỗi", "Username đã tồn tại")
            return

        account = self.model.find_exact("username", self.old_username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return

        row = account.iloc[0]
        password_to_save = payload["password"] or row["password"]
        self.model.update_account(
            self.old_username,
            payload["username"],
            password_to_save,
            payload["ho_ten"],
            payload["sdt"],
            payload["chuc_vu"],
            row.get("ngay_tao", ""),
        )
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")
        self.app_manager.show_quanlytk_page()
