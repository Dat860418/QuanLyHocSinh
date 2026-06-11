import os
import tkinter as tk
from tkinter import messagebox

from views.home_view import HomeView


class HomeController:
    def __init__(self, master, app_manager):
        self.app_manager = app_manager
        self.view = HomeView(
            master,
            self.go_sv,
            self.go_mon,
            self.go_diem,
            self.go_tk,
            self.show_intro,
            self.show_guide,
            self.logout,
        )

    def go_sv(self):
        self.app_manager.show_quanly_sv_page()

    def go_mon(self):
        self.app_manager.show_quanly_monhoc_page()

    def go_diem(self):
        self.app_manager.show_quanly_diem_page()

    def go_tk(self):
        if not self.app_manager.is_admin():
            messagebox.showerror(
                "Không có quyền", "Chỉ admin mới được quản lý tài khoản"
            )
            return
        self.app_manager.show_quanlytk_page()

    def show_intro(self):
        messagebox.showinfo(
            "Giới thiệu",
            "Phiên bản: 1.0\nTác giả: Nhóm 10 Lớp CNTTK2C\nNgày phát hành: 2026-04-1",
        )

    def show_guide(self):
        pdf_path = self.view.get_pdf_path()
        if not os.path.exists(pdf_path):
            messagebox.showerror("Lỗi", "Không tìm thấy file hướng dẫn PDF")
            return

        try:
            self.view.open_guide_file(pdf_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file hướng dẫn: {e}")

    def logout(self):
        self.app_manager.show_login_page()
