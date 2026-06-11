from tkinter import messagebox

from model.taikhoan_query import TaiKhoanQuery
from views.login_view import LoginView


class LoginController:
    def __init__(self, master, app_manager):
        self.app_manager = app_manager
        self.model = TaiKhoanQuery()
        self.view = LoginView(master, self.handle_login, self.handle_toggle_password)

    def handle_toggle_password(self):
        self.view.set_password_visible(self.view.show_password.get())

    def handle_login(self):
        username = self.view.get_username()
        password = self.view.get_password()

        user = self.model.authenticate(username, password)
        if user:
            messagebox.showinfo("Thông báo", "Đăng nhập thành công")
            self.app_manager.set_current_user(user)
            self.app_manager.show_home_page()
            return

        messagebox.showerror("Thông báo", "Đăng nhập thất bại")
