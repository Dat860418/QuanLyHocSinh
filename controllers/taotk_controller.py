from tkinter import messagebox

from common.validation import ValidationError, validate_account_payload
from model.taikhoan_query import TaiKhoanQuery
from views.taotk_view import TaoTKView


class TaoTKController:
    def __init__(self, master, app_manager):
        self.app_manager = app_manager
        self.model = TaiKhoanQuery()
        self.view = TaoTKView(
            master, self.handle_create, self.handle_back, self.handle_toggle
        )

    def handle_toggle(self):
        self.view.set_password_visible(self.view.show_password.get())

    def handle_back(self):
        self.app_manager.show_quanlytk_page()

    def handle_create(self):
        try:
            payload = validate_account_payload(self.view.get_payload_values())
        except ValidationError as exc:
            messagebox.showerror("Lỗi", str(exc))
            return

        if self.model.username_exists(payload["username"]):
            messagebox.showerror("Thông báo", "Username đã tồn tại")
            return

        self.model.create_account(
            payload["username"],
            payload["password"],
            payload["ho_ten"],
            payload["sdt"],
            payload["chuc_vu"],
        )
        messagebox.showinfo("Thông báo", "Tạo tài khoản thành công")
        self.app_manager.show_quanlytk_page()
