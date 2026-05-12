import tkinter as tk
from tkinter import messagebox, ttk

from common.button import CustomButton
from query.taikhoan_query import TaiKhoanQuery


class TaoTKPage:
    """Màn hình tạo tài khoản mới và ghi vào taikhoan.csv qua TaiKhoanQuery."""

    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = TaiKhoanQuery()
        self.config()
        self.view()

    def config(self):
        self.master.title("Tạo tài khoản")
        self.master.geometry("320x330")

    def view(self):
        tk.Label(self.master, text="Tạo tài khoản", font=("Arial", 20)).pack(pady=10)

        labels = ["Username:", "Password:", "Họ tên:", "SĐT:", "Role:"]
        for idx, text in enumerate(labels):
            tk.Label(self.master, text=text).place(x=20, y=60 + idx * 40)

        self.entry_username = tk.Entry(self.master)
        self.entry_username.place(x=100, y=60)
        self.entry_password = tk.Entry(self.master, show="*")
        self.entry_password.place(x=100, y=100)
        self.entry_hoten = tk.Entry(self.master)
        self.entry_hoten.place(x=100, y=140)
        self.entry_sdt = tk.Entry(self.master)
        self.entry_sdt.place(x=100, y=180)
        self.entry_chuc_vu = ttk.Combobox(self.master, values=("User", "Admin"), state="readonly")
        self.entry_chuc_vu.set("User")
        self.entry_chuc_vu.place(x=100, y=220)

        CustomButton(self.master, text="Tạo tài khoản", command=self.tao_tk, style_type="primary").place(x=45, y=270)
        CustomButton(self.master, text="Quay lại", command=self.back_login, style_type="success").place(x=180, y=270)

    def back_login(self):
        self.app_manager.show_login_page()

    def tao_tk(self):
        # Chỉ bắt buộc 3 trường chính; SĐT/Role có thể bổ sung sau.
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        ho_ten = self.entry_hoten.get().strip()
        sdt = self.entry_sdt.get().strip()
        chuc_vu = self.entry_chuc_vu.get().strip()

        if not username or not password or not ho_ten:
            messagebox.showerror("Thông báo", "Vui lòng nhập đầy đủ username, password và họ tên")
            return

        if self.q.username_exists(username):
            messagebox.showerror("Thông báo", "Username đã tồn tại")
            return

        # Code cũ giữ lại:
        # self.q.create([self.q.next_id(), username, password, ho_ten, sdt, chuc_vu])
        # Code mới: create_account sẽ hash password và tự thêm ngày tạo.
        self.q.create_account(username, password, ho_ten, sdt, chuc_vu)
        messagebox.showinfo("Thông báo", "Tạo tài khoản thành công")
        self.app_manager.show_login_page()
