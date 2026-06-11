import customtkinter as ctk

from controllers.home_controller import HomeController
from controllers.login_controller import LoginController
from controllers.quanly_diem_controller import QuanLyDiemController
from controllers.quanly_monhoc_controller import QuanLyMonHocController
from controllers.quanly_sv_controller import QuanLySVController
from controllers.quanlytk_controller import QuanLyTKController
from controllers.suatk_controller import SuaTKController
from controllers.taotk_controller import TaoTKController


class AppManager:
    """Điều phối chuyển màn hình và phiên đăng nhập cho ứng dụng."""

    def __init__(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Quản lý sinh viên")
        self.root.geometry("300x230")
        self.current_page = None
        self.current_user = None
        self.show_login_page()

    def clear_current_page(self):
        """Xóa toàn bộ widget của màn hình hiện tại trước khi chuyển trang."""
        if self.current_page:
            for widget in self.root.winfo_children():
                widget.destroy()

    def show_login_page(self):
        self.current_user = None
        self.clear_current_page()
        self.root.geometry("300x230")
        self.current_page = LoginController(self.root, self)

    def show_home_page(self):
        self.clear_current_page()
        self.root.geometry("760x420")
        self.current_page = HomeController(self.root, self)

    def set_current_user(self, user):
        """Lưu thông tin tài khoản đang đăng nhập để kiểm tra quyền truy cập."""
        self.current_user = user

    def is_admin(self):
        """Kiểm tra xem tài khoản hiện tại có quyền mở màn quản lý tài khoản không."""
        if not self.current_user:
            return False
        return str(self.current_user.get("chuc_vu", "")).lower() == "admin"

    def show_taotk_page(self):
        self.clear_current_page()
        self.root.geometry("320x330")
        self.current_page = TaoTKController(self.root, self)

    def show_quanlytk_page(self):
        self.clear_current_page()
        self.root.geometry("1200x620")
        self.current_page = QuanLyTKController(self.root, self)

    def show_suatk_page(self, username=None, password=None):
        self.clear_current_page()
        self.root.geometry("420x360")
        self.current_page = SuaTKController(self.root, self, username, password)

    def show_quanly_sv_page(self):
        self.clear_current_page()
        self.root.geometry("1200x620")
        self.current_page = QuanLySVController(self.root, self)

    def show_quanly_monhoc_page(self):
        self.clear_current_page()
        self.root.geometry("1200x620")
        self.current_page = QuanLyMonHocController(self.root, self)

    def show_quanly_diem_page(self):
        self.clear_current_page()
        self.root.geometry("1200x620")
        self.current_page = QuanLyDiemController(self.root, self)

    def run(self):
        self.root.mainloop()
