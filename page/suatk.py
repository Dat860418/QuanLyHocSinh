import tkinter as tk
from tkinter import messagebox
import csv
import os

from common.button import CustomButton


class SuaTKPage:
    def __init__(self, master, app_manager, username=None, password=None):
        self.master = master
        self.app_manager = app_manager
        self.old_username = username or ""
        self.old_password = password or ""
        self.config()
        self.view()

    def config(self):
        self.master.title("Sửa tài khoản")
        self.master.geometry("400x300")

    def view(self):
        # Title
        title_label = tk.Label(self.master, text="Sửa thông tin tài khoản", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # Old account info frame
        old_frame = tk.LabelFrame(main_frame, text="Thông tin hiện tại", font=("Arial", 12, "bold"))
        old_frame.pack(fill="x", pady=(0, 20))

        tk.Label(old_frame, text=f"Tên đăng nhập: {self.old_username}", font=("Arial", 11)).pack(anchor="w", padx=10,
                                                                                                 pady=5)
        tk.Label(old_frame, text=f"Mật khẩu: {'*' * len(self.old_password)}", font=("Arial", 11)).pack(anchor="w",
                                                                                                       padx=10, pady=5)

        # New account info frame
        new_frame = tk.LabelFrame(main_frame, text="Thông tin mới", font=("Arial", 12, "bold"))
        new_frame.pack(fill="both", expand=True)

        # Username input
        username_frame = tk.Frame(new_frame)
        username_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(username_frame, text="Tên đăng nhập mới:", width=15, anchor="w").pack(side="left")
        self.entry_username = tk.Entry(username_frame, font=("Arial", 11))
        self.entry_username.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.entry_username.insert(0, self.old_username)

        # Password input
        password_frame = tk.Frame(new_frame)
        password_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(password_frame, text="Mật khẩu mới:", width=15, anchor="w").pack(side="left")
        self.entry_password = tk.Entry(password_frame, show="*", font=("Arial", 11))
        self.entry_password.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.entry_password.insert(0, self.old_password)

        # Show password checkbox
        show_pass_frame = tk.Frame(new_frame)
        show_pass_frame.pack(fill="x", padx=10, pady=5)

        self.show_password = tk.BooleanVar()
        show_pass_check = tk.Checkbutton(show_pass_frame, text="Hiển thị mật khẩu",
                                         variable=self.show_password, command=self.toggle_password)
        show_pass_check.pack(side="right")

        # Validation info
        info_frame = tk.Frame(new_frame)
        info_frame.pack(fill="x", padx=10, pady=5)

        info_text = "• Tên đăng nhập và mật khẩu không được để trống\n• Tên đăng nhập không được trùng với tài khoản khác"
        tk.Label(info_frame, text=info_text, justify="left", font=("Arial", 9), fg="gray").pack(anchor="w")

        # Buttons frame
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)

        save_btn = CustomButton(button_frame, text="Lưu thay đổi", command=self.save_changes, style_type="success")
        save_btn.pack(side="left", padx=10)

        cancel_btn = CustomButton(button_frame, text="Hủy bỏ", command=self.cancel, style_type="secondary")
        cancel_btn.pack(side="left", padx=10)

        reset_btn = CustomButton(button_frame, text="Khôi phục", command=self.reset_form, style_type="warning")
        reset_btn.pack(side="left", padx=10)

    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="*")

    def reset_form(self):
        """Reset form to original values"""
        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, self.old_username)
        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, self.old_password)

    def validate_input(self):
        """Validate user input"""
        new_username = self.entry_username.get().strip()
        new_password = self.entry_password.get().strip()

        if not new_username or not new_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return False

        # Check if username already exists (excluding current account)
        if new_username != self.old_username and self.username_exists(new_username):
            messagebox.showerror("Lỗi", f"Tên đăng nhập '{new_username}' đã tồn tại")
            return False

        return True

    def username_exists(self, username):
        """Check if username already exists in database"""
        try:
            database_path = "database/tk.csv"
            if not os.path.exists(database_path):
                return False

            with open(database_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 2 and row[0] == username:
                        return True
            return False
        except Exception:
            return False

    def save_changes(self):
        """Save changes to database"""
        if not self.validate_input():
            return

        new_username = self.entry_username.get().strip()
        new_password = self.entry_password.get().strip()

        # Check if any changes were made
        if new_username == self.old_username and new_password == self.old_password:
            messagebox.showinfo("Thông báo", "Không có thay đổi nào được thực hiện")
            return

        try:
            self.update_account_in_file(new_username, new_password)
            messagebox.showinfo("Thành công", "Đã cập nhật tài khoản thành công")
            self.app_manager.show_quanlytk_page()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật tài khoản: {str(e)}")

    def update_account_in_file(self, new_username, new_password):
        """Update account in CSV file"""
        database_path = "database/tk.csv"
        temp_path = "database/tk_temp.csv"

        with open(database_path, "r", encoding="utf-8") as infile, \
                open(temp_path, "w", encoding="utf-8", newline="") as outfile:
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)

            for row in csv_reader:
                if len(row) >= 2:
                    if row[0] == self.old_username:
                        new_row = row.copy()

                        new_row[0] = new_username
                        new_row[1] = new_password

                        csv_writer.writerow(new_row)
                    else:
                        csv_writer.writerow(row)

        # Replace original file with temp file
        os.replace(temp_path, database_path)

    def cancel(self):
        """Cancel and return to account management"""
        if self.has_unsaved_changes():
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy? Các thay đổi sẽ không được lưu."):
                self.app_manager.show_quanlytk_page()
        else:
            self.app_manager.show_quanlytk_page()

    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        current_username = self.entry_username.get().strip()
        current_password = self.entry_password.get().strip()
        return (current_username != self.old_username or current_password != self.old_password)