import tkinter as tk
from page.login import LoginPage
from page.taotk import TaoTKPage
from page.quanlytk import QuanLyTKPage
from page.suatk import SuaTKPage
from page.quanly_sv import QuanLySVPage

class AppManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ứng dụng Đăng nhập")
        self.root.geometry("300x200")
        self.current_page = None
        self.show_login_page()

    def clear_current_page(self):
        """Xóa tất cả widget của page hiện tại"""
        if self.current_page:
            for widget in self.root.winfo_children():
                widget.destroy()

    def show_login_page(self):
        """Hiển thị trang đăng nhập"""
        self.clear_current_page()
        self.root.geometry("300x230")
        self.current_page = LoginPage(self.root, self)

    def show_taotk_page(self):
        """Hiển thị trang tạo tài khoản"""
        self.clear_current_page()
        self.root.geometry("300x200")
        self.current_page = TaoTKPage(self.root, self)

    def show_quanlytk_page(self):
        """Hiển thị trang quản lý tài khoản"""
        self.clear_current_page()
        self.root.geometry("600x400")
        self.current_page = QuanLyTKPage(self.root, self)

    def show_suatk_page(self, username=None, password=None):
        """Hiển thị trang sửa tài khoản"""
        self.clear_current_page()
        self.root.geometry("400x300")
        self.current_page = SuaTKPage(self.root, self, username, password)

    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

    def show_quanly_sv_page(self):
        self.clear_current_page()
        self.root.geometry("600x400")
        self.current_page = QuanLySVPage(self.root, self)