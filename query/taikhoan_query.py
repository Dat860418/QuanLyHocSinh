import hashlib
from datetime import date

from .base import CSVQuery


class TaiKhoanQuery(CSVQuery):
    """Query tài khoản: đăng nhập, hash mật khẩu, phân quyền và reset mật khẩu."""

    def __init__(self):
        super().__init__(
            "database/taikhoan.csv",
            ["id", "username", "password", "ho_ten", "sdt", "chuc_vu", "ngay_tao"],
        )

    def hash_password(self, password):
        # Code mới: dùng SHA-256 để không lưu mật khẩu thô trong CSV.
        return hashlib.sha256(str(password).encode("utf-8")).hexdigest()

    def authenticate(self, username, password):
        data = self.get_all()

        # Code cũ giữ lại để tham khảo:
        # result = data[
        #     (data["username"].astype(str) == str(username))
        #     & (data["password"].astype(str) == str(password))
        # ]
        # return not result.empty

        # Code mới: hash mật khẩu người dùng nhập rồi mới so sánh với CSV.
        password_hash = self.hash_password(password)
        result = data[
            (data["username"].astype(str) == str(username))
            & (data["password"].astype(str) == password_hash)
        ]
        if result.empty:
            return None
        return result.iloc[0].to_dict()

    def create_account(self, username, password, ho_ten, sdt="", chuc_vu="User"):
        # Tạo tài khoản tập trung tại query để nơi nào cũng dùng hash và ngày tạo giống nhau.
        role = chuc_vu.strip() or "User"
        return self.create([
            self.next_id(),
            username,
            self.hash_password(password),
            ho_ten,
            sdt,
            role,
            date.today().isoformat(),
        ])

    def update_account(self, old_username, username, password, ho_ten, sdt, chuc_vu, ngay_tao):
        # Nếu password đã là hash 64 ký tự thì giữ nguyên; nếu là mật khẩu mới thì hash lại.
        password_text = str(password)
        password_value = password_text if len(password_text) == 64 else self.hash_password(password_text)
        account = self.find_exact("username", old_username)
        if account.empty:
            return False
        account_id = account.iloc[0]["id"]
        return self.update("username", old_username, [
            account_id,
            username,
            password_value,
            ho_ten,
            sdt,
            chuc_vu,
            ngay_tao,
        ])

    def reset_password(self, username, new_password="12345"):
        # Admin reset mật khẩu về giá trị mặc định; khi lưu vẫn là chuỗi hash.
        account = self.find_exact("username", username)
        if account.empty:
            return False
        row = account.iloc[0]
        return self.update("username", username, [
            row["id"],
            row["username"],
            self.hash_password(new_password),
            row["ho_ten"],
            row["sdt"],
            row["chuc_vu"],
            row.get("ngay_tao", date.today().isoformat()),
        ])

    def username_exists(self, username, exclude_username=None):
        # exclude_username dùng khi sửa tài khoản để username hiện tại không bị tính là trùng.
        data = self.get_all()
        result = data[data["username"].astype(str) == str(username)]
        if exclude_username is not None:
            result = result[result["username"].astype(str) != str(exclude_username)]
        return not result.empty

    def count_admins(self):
        # Dùng để chặn xóa tài khoản Admin cuối cùng của hệ thống.
        data = self.get_all()
        return len(data[data["chuc_vu"].astype(str).str.lower() == "admin"])
