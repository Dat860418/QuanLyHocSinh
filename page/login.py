import tkinter as tk
from tkinter import messagebox

from common.button import CustomButton

# Create main window.


class LoginPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.config()
        self.view()

    def config(self):
        self.master.title("Đăng nhập")
        self.master.geometry("300x200")

    def view(self):
        # Add a label
        label = tk.Label(self.master, text="Đăng nhập", font=("Arial", 20))
        label.pack(pady=30)
        lib_user = tk.Label(self.master, text="Username:")
        lib_user.place(x=20, y=70)

        lib_pass = tk.Label(self.master, text="Password:")
        lib_pass.place(x=20, y=100)

        self.entry_username = tk.Entry(self.master)
        self.entry_username.place(x=90, y=60)

        self.entry_password = tk.Entry(self.master, show="*")
        self.entry_password.place(x=90, y=100)

        btn = CustomButton(self.master, text="Tạo tài khoản", command=self.tao_tk, style_type="primary")
        btn.place(x=40, y=140)

        btn = CustomButton(self.master, text="Đăng nhập", command=self.login, style_type="success")
        btn.place(x=160, y=140)

    def tao_tk(self):
        print("Chuyển sang trang tạo tài khoản")
        self.app_manager.show_taotk_page()

    def login(self):
        try:
            with open("database/tk.csv", "r") as file:
                for line in file:
                    tk_info = line.strip().split(",")
                    if len(tk_info) >= 2 and \
                            self.entry_username.get() == tk_info[0] and \
                            self.entry_password.get() == tk_info[1]:
                        messagebox.showinfo("Thông báo", "Đăng nhập thành công")
                        self.app_manager.show_quanlytk_page()
                        return  # 🔥 QUAN TRỌNG

            messagebox.showerror("Thông báo", "Đăng nhập thất bại")

        except FileNotFoundError:
            messagebox.showerror("Thông báo", "Chưa có tài khoản nào được tạo")