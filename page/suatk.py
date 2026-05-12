import tkinter as tk
from tkinter import messagebox, ttk

from common.button import CustomButton
from query.taikhoan_query import TaiKhoanQuery


class SuaTKPage:
    """Màn hình sửa tài khoản, giữ username cũ để cập nhật đúng dòng trong CSV."""

    def __init__(self, master, app_manager, username=None, password=None):
        self.master = master
        self.app_manager = app_manager
        self.old_username = username or ""
        self.old_password = password or ""
        self.q = TaiKhoanQuery()
        self.config()
        self.view()

    def config(self):
        self.master.title("Sửa tài khoản")
        self.master.geometry("420x360")

    def view(self):
        tk.Label(self.master, text="Sửa thông tin tài khoản", font=("Arial", 18, "bold")).pack(pady=15)

        # Lấy toàn bộ thông tin hiện tại để điền sẵn vào form sửa.
        account = self.q.find_exact("username", self.old_username)
        row = account.iloc[0].to_dict() if not account.empty else {}

        frame = tk.Frame(self.master)
        frame.pack(padx=35, pady=10, fill="x")

        labels = ["Username:", "Password mới:", "Họ tên:", "SĐT:", "Role:"]
        for idx, text in enumerate(labels):
            tk.Label(frame, text=text, width=12, anchor="w").grid(row=idx, column=0, padx=5, pady=6)

        self.entry_username = tk.Entry(frame)
        self.entry_username.grid(row=0, column=1, sticky="ew")
        self.entry_password = tk.Entry(frame, show="*")
        self.entry_password.grid(row=1, column=1, sticky="ew")
        self.entry_hoten = tk.Entry(frame)
        self.entry_hoten.grid(row=2, column=1, sticky="ew")
        self.entry_sdt = tk.Entry(frame)
        self.entry_sdt.grid(row=3, column=1, sticky="ew")
        self.entry_chuc_vu = ttk.Combobox(frame, values=("User", "Admin"), state="readonly")
        self.entry_chuc_vu.grid(row=4, column=1, sticky="ew")
        frame.columnconfigure(1, weight=1)

        self.entry_username.insert(0, row.get("username", self.old_username))
        # Không hiển thị hash thật; để trống nghĩa là giữ mật khẩu cũ.
        self.entry_password.insert(0, "")
        self.entry_hoten.insert(0, row.get("ho_ten", ""))
        self.entry_sdt.insert(0, row.get("sdt", ""))
        self.entry_chuc_vu.set(row.get("chuc_vu", "User"))

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=15)
        CustomButton(button_frame, text="Lưu", command=self.save_changes, style_type="success").pack(side="left", padx=8)
        CustomButton(button_frame, text="Hủy", command=self.cancel, style_type="secondary").pack(side="left", padx=8)

    def save_changes(self):
        # Kiểm tra dữ liệu và trùng username trước khi ghi lại CSV.
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        ho_ten = self.entry_hoten.get().strip()
        sdt = self.entry_sdt.get().strip()
        chuc_vu = self.entry_chuc_vu.get().strip()

        if not username or not ho_ten:
            messagebox.showerror("Lỗi", "Vui lòng nhập username và họ tên")
            return

        if self.q.username_exists(username, exclude_username=self.old_username):
            messagebox.showerror("Lỗi", "Username đã tồn tại")
            return

        account = self.q.find_exact("username", self.old_username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return

        # Code cũ giữ lại:
        # account_id = account.iloc[0]["id"]
        # self.q.update("username", self.old_username, [account_id, username, password, ho_ten, sdt, chuc_vu])

        # Code mới: update_account sẽ hash password mới, hoặc giữ hash cũ nếu ô password trống.
        row = account.iloc[0]
        password_to_save = password or row["password"]
        self.q.update_account(
            self.old_username,
            username,
            password_to_save,
            ho_ten,
            sdt,
            chuc_vu,
            row.get("ngay_tao", ""),
        )
        messagebox.showinfo("Thành công", "Đã cập nhật tài khoản")
        self.app_manager.show_quanlytk_page()

    def cancel(self):
        self.app_manager.show_quanlytk_page()
