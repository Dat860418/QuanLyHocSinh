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
        return hashlib.sha256(str(password).encode("utf-8")).hexdigest()

    def authenticate(self, username, password):
        data = self.get_all()
        password_hash = self.hash_password(password)
        result = data[
            (data["username"].astype(str) == str(username))
            & (data["password"].astype(str) == password_hash)
        ]
        if result.empty:
            return None
        return result.iloc[0].to_dict()

    def create_account(self, username, password, ho_ten, sdt="", chuc_vu="User"):
        role = chuc_vu.strip() or "User"
        return self.create(
            [
                self.next_id(),
                username,
                self.hash_password(password),
                ho_ten,
                sdt,
                role,
                date.today().isoformat(),
            ]
        )

    def update_account(
        self, old_username, username, password, ho_ten, sdt, chuc_vu, ngay_tao
    ):
        password_text = str(password)
        password_value = (
            password_text
            if len(password_text) == 64
            else self.hash_password(password_text)
        )
        account = self.find_exact("username", old_username)
        if account.empty:
            return False
        account_id = account.iloc[0]["id"]
        return self.update(
            "username",
            old_username,
            [
                account_id,
                username,
                password_value,
                ho_ten,
                str(sdt),
                chuc_vu,
                ngay_tao,
            ],
        )

    def reset_password(self, username, new_password="12345"):
        account = self.find_exact("username", username)
        if account.empty:
            return False
        row = account.iloc[0]
        return self.update(
            "username",
            username,
            [
                row["id"],
                row["username"],
                self.hash_password(new_password),
                row["ho_ten"],
                row["sdt"],
                row["chuc_vu"],
                row.get("ngay_tao", date.today().isoformat()),
            ],
        )

    def username_exists(self, username, exclude_username=None):
        data = self.get_all()
        result = data[data["username"].astype(str) == str(username)]
        if exclude_username is not None:
            result = result[result["username"].astype(str) != str(exclude_username)]
        return not result.empty

    def count_admins(self):
        data = self.get_all()
        return len(data[data["chuc_vu"].astype(str).str.lower() == "admin"])
