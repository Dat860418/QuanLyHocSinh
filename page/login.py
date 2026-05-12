import tkinter as tk
from tkinter import messagebox

from common.button import CustomButton
from query.taikhoan_query import TaiKhoanQuery


class LoginPage:
    """Màn hình đăng nhập, kiểm tra username/password trong taikhoan.csv."""

    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = TaiKhoanQuery()
        self.config()
        self.view()

    def config(self):
        self.master.title("Đăng nhập")
        self.master.geometry("300x200")

    def view(self):
        tk.Label(self.master, text="Đăng nhập", font=("Arial", 20)).pack(pady=30)

        tk.Label(self.master, text="Username:").place(x=20, y=70)
        tk.Label(self.master, text="Password:").place(x=20, y=100)

        self.entry_username = tk.Entry(self.master)
        self.entry_username.place(x=90, y=70)

        self.entry_password = tk.Entry(self.master, show="*")
        self.entry_password.place(x=90, y=100)

        CustomButton(
            self.master, text="Tạo tài khoản", command=self.tao_tk, style_type="primary"
        ).place(x=40, y=140)
        CustomButton(
            self.master, text="Đăng nhập", command=self.login, style_type="success"
        ).place(x=160, y=140)

    def tao_tk(self):
        self.app_manager.show_taotk_page()

    def login(self):
        # strip() tránh lỗi do người dùng nhập thừa khoảng trắng ở đầu/cuối.
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        user = self.q.authenticate(username, password)
        if user:
            messagebox.showinfo("Thông báo", "Đăng nhập thành công")
            self.app_manager.set_current_user(user)
            # Code cũ giữ lại:
            # self.app_manager.show_quanlytk_page()
            # Code mới: Admin vào quản lý tài khoản, User thường vào quản lý điểm.
            if self.app_manager.is_admin():
                self.app_manager.show_quanlytk_page()
            else:
                self.app_manager.show_quanly_diem_page()
            return

        messagebox.showerror("Thông báo", "Đăng nhập thất bại")
