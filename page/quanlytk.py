import tkinter as tk
from tkinter import messagebox, ttk

from common.button import CustomButton
from query.taikhoan_query import TaiKhoanQuery


class QuanLyTKPage:
    """Màn hình tài khoản chỉ dành cho Admin."""

    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = TaiKhoanQuery()

        # RBAC: chặn ngay nếu User thường cố tình mở màn hình này.
        if not self.app_manager.is_admin():
            messagebox.showerror("Không có quyền", "Chỉ Admin mới được quản lý tài khoản")
            self.app_manager.show_quanly_sv_page()
            return

        self.config()
        self.view()
        self.load_accounts()

    def config(self):
        self.master.title("Quản lý tài khoản")
        self.master.geometry("1200x520")

    def view(self):
        tk.Label(self.master, text="Quản lý tài khoản", font=("Arial", 20, "bold")).pack(pady=10)

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=5)

        CustomButton(button_frame, text="Làm mới", command=self.load_accounts, style_type="info").pack(side="left", padx=5)
        CustomButton(button_frame, text="Tạo tài khoản", command=self.create_account, style_type="success").pack(side="left", padx=5)
        CustomButton(button_frame, text="Xóa tài khoản", command=self.delete_account, style_type="danger").pack(side="left", padx=5)
        CustomButton(button_frame, text="Sửa tài khoản", command=self.edit_account, style_type="warning").pack(side="left", padx=5)
        CustomButton(button_frame, text="Reset mật khẩu", command=self.reset_password, style_type="warning").pack(side="left", padx=5)
        CustomButton(button_frame, text="Quản lý sinh viên", command=self.go_sv, style_type="info").pack(side="left", padx=5)
        CustomButton(button_frame, text="Quản lý môn học", command=self.go_monhoc, style_type="info").pack(side="left", padx=5)
        CustomButton(button_frame, text="Quản lý điểm", command=self.go_diem, style_type="info").pack(side="left", padx=5)
        CustomButton(button_frame, text="Đăng xuất", command=self.back_to_login, style_type="secondary").pack(side="left", padx=5)

        tree_frame = tk.Frame(self.master)
        tree_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Bảng mới không hiển thị password/hash để tránh lộ dữ liệu nhạy cảm.
        columns = ("id", "username", "ho_ten", "sdt", "chuc_vu", "ngay_tao")
        self.account_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        headings = {
            "id": "ID",
            "username": "Username",
            "ho_ten": "Họ tên",
            "sdt": "SĐT",
            "chuc_vu": "Role",
            "ngay_tao": "Ngày tạo",
        }
        for column, text in headings.items():
            self.account_tree.heading(column, text=text)
            self.account_tree.column(column, width=130, anchor="center")
        self.account_tree.column("ho_ten", width=220)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=scrollbar.set)
        self.account_tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        self.status_label = tk.Label(self.master, text="Sẵn sàng", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def load_accounts(self):
        # Làm mới Treeview từ taikhoan.csv sau khi thêm/sửa/xóa.
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)

        data = self.q.get_all()
        for _, row in data.iterrows():
            self.account_tree.insert("", "end", values=[
                row["id"],
                row["username"],
                row["ho_ten"],
                row["sdt"],
                row["chuc_vu"],
                row.get("ngay_tao", ""),
            ])

        self.status_label.config(text=f"Đã tải {len(data)} tài khoản")

    def get_selected_username(self):
        selected_item = self.account_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản")
            return None
        values = self.account_tree.item(selected_item[0], "values")
        return values[1]

    def delete_account(self):
        username = self.get_selected_username()
        if not username:
            return

        account = self.q.find_exact("username", username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return

        # Code cũ giữ lại:
        # self.q.delete("username", username)
        # Code mới: chặn xóa Admin cuối cùng để hệ thống luôn còn người quản trị.
        role = str(account.iloc[0]["chuc_vu"]).lower()
        if role == "admin" and self.q.count_admins() <= 1:
            messagebox.showerror("Lỗi", "Không thể xóa Admin cuối cùng")
            return

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa tài khoản '{username}'?"):
            self.q.delete("username", username)
            self.load_accounts()
            messagebox.showinfo("Thành công", "Đã xóa tài khoản")

    def edit_account(self):
        username = self.get_selected_username()
        if not username:
            return
        account = self.q.find_exact("username", username)
        if account.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản")
            return
        self.app_manager.show_suatk_page(username, account.iloc[0]["password"])

    def reset_password(self):
        username = self.get_selected_username()
        if not username:
            return
        if messagebox.askyesno("Xác nhận", f"Reset mật khẩu '{username}' về 12345?"):
            self.q.reset_password(username)
            messagebox.showinfo("Thành công", "Đã reset mật khẩu về 12345")

    def back_to_login(self):
        self.app_manager.show_login_page()

    def create_account(self):
        self.app_manager.show_taotk_page()

    def go_sv(self):
        self.app_manager.show_quanly_sv_page()

    def go_monhoc(self):
        self.app_manager.show_quanly_monhoc_page()

    def go_diem(self):
        self.app_manager.show_quanly_diem_page()
