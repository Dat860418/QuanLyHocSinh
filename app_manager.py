import tkinter as tk

from page.login import LoginPage
from page.taotk import TaoTKPage
from page.quanlytk import QuanLyTKPage
from page.suatk import SuaTKPage
from page.quanly_sv import QuanLySVPage
from page.quanly_monhoc import QuanLyMonHocPage
from page.quanly_diem import QuanLyDiemPage


class AppManager:
    """Quản lý chuyển trang: mỗi lần mở page mới sẽ xóa widget của page cũ."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quản lý sinh viên")
        self.root.geometry("300x230")
        self.current_page = None
        # Session hiện tại: None khi chưa đăng nhập, dict user sau khi đăng nhập thành công.
        self.current_user = None
        self.show_login_page()

    def clear_current_page(self):
        # Tkinter không tự thay trang, nên cần destroy toàn bộ widget trước khi dựng page mới.
        if self.current_page:
            for widget in self.root.winfo_children():
                widget.destroy()

    def show_login_page(self):
        # Mỗi page có kích thước cửa sổ riêng để vừa form hoặc bảng dữ liệu.
        self.current_user = None
        self.clear_current_page()
        self.root.geometry("300x230")
        self.current_page = LoginPage(self.root, self)

    def set_current_user(self, user):
        # Lưu user đăng nhập để các page sau kiểm tra quyền.
        self.current_user = user

    def is_admin(self):
        # RBAC đơn giản: chỉ tài khoản chuc_vu = Admin được vào quản lý tài khoản.
        if not self.current_user:
            return False
        return str(self.current_user.get("chuc_vu", "")).lower() == "admin"

    def show_taotk_page(self):
        self.clear_current_page()
        self.root.geometry("320x330")
        self.current_page = TaoTKPage(self.root, self)

    def show_quanlytk_page(self):
        self.clear_current_page()
        self.root.geometry("1200x520")
        self.current_page = QuanLyTKPage(self.root, self)

    def show_suatk_page(self, username=None, password=None):
        self.clear_current_page()
        self.root.geometry("420x360")
        self.current_page = SuaTKPage(self.root, self, username, password)

    def show_quanly_sv_page(self):
        self.clear_current_page()
        self.root.geometry("1200x520")
        self.current_page = QuanLySVPage(self.root, self)

    def show_quanly_monhoc_page(self):
        self.clear_current_page()
        self.root.geometry("650x430")
        self.current_page = QuanLyMonHocPage(self.root, self)

    def show_quanly_diem_page(self):
        self.clear_current_page()
        self.root.geometry("1200x520")
        self.current_page = QuanLyDiemPage(self.root, self)

    def run(self):
        self.root.mainloop()
