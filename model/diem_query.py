import pandas as pd

from .base import CSVQuery


class DiemQuery(CSVQuery):
    """Query cho bảng điểm, hỗ trợ join thông tin sinh viên/môn khi hiển thị."""

    def __init__(self):
        super().__init__(
            "database/diem.csv",
            ["id", "ma_sv", "ma_mon", "diem_cc", "diem_kt1", "diem_kt2", "diem_ck"],
        )

    def get_display_data(self):
        """Trả về dữ liệu điểm đã gắn thêm tên sinh viên, tên môn và điểm tổng kết."""
        diem = self.get_all()
        sinhvien = (
            pd.read_csv("database/sinhvien.csv", encoding="utf-8", dtype=str)
            .fillna("")
            .drop_duplicates("ma_sv")
        )
        monhoc = (
            pd.read_csv("database/monhoc.csv", encoding="utf-8", dtype=str)
            .fillna("")
            .drop_duplicates("ma_mon")
        )

        for column in ["diem_cc", "diem_kt1", "diem_kt2", "diem_ck"]:
            diem[column] = pd.to_numeric(diem[column], errors="coerce")

        data = diem.merge(sinhvien[["ma_sv", "ho_ten"]], on="ma_sv", how="left")
        data = data.merge(monhoc[["ma_mon", "ten_mon"]], on="ma_mon", how="left")
        data["ho_ten"] = data["ho_ten"].fillna("Không tìm thấy SV")
        data["ten_mon"] = data["ten_mon"].fillna("Không tìm thấy môn")
        data["diem_tong_ket"] = (
            data["diem_cc"] * 0.1
            + data["diem_kt1"] * 0.15
            + data["diem_kt2"] * 0.15
            + data["diem_ck"] * 0.6
        ).round(2)
        data["xep_loai"] = data["diem_tong_ket"].apply(self.xep_loai)
        return data

    def xep_loai(self, diem):
        """Chuyển điểm tổng kết sang xếp loại chữ."""
        if pd.isna(diem):
            return ""
        if diem >= 8:
            return "A"
        if diem >= 6.5:
            return "B"
        if diem >= 5:
            return "C"
        return "D"

    def delete_by_student(self, ma_sv):
        """Khi xóa sinh viên, xóa luôn các bản ghi điểm liên quan."""
        data = self.get_all()
        data = data[data["ma_sv"].astype(str) != str(ma_sv)]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def subject_has_grades(self, ma_mon):
        """Kiểm tra môn học có đang được dùng trong bảng điểm hay không."""
        data = self.get_all()
        return not data[data["ma_mon"].astype(str) == str(ma_mon)].empty

    def gpa_by_student(self):
        """Tính GPA trung bình theo sinh viên từ dữ liệu đã join."""
        data = self.get_display_data()
        return (
            data.groupby(["ma_sv", "ho_ten"], as_index=False)["diem_tong_ket"]
            .mean()
            .round(2)
        )

    def get_top_students_by_gpa(self, limit=5):
        """Lấy top sinh viên có GPA cao nhất."""
        gpa = self.gpa_by_student()
        return gpa.sort_values("diem_tong_ket", ascending=False).head(limit)

    def get_subject_failures(self):
        """Lấy các môn có điểm tổng kết dưới 4."""
        data = self.get_display_data()
        return data[data["diem_tong_ket"] < 4].copy()

    def get_high_scores(self):
        """Lấy các môn có điểm tổng kết trên 8."""
        data = self.get_display_data()
        return data[data["diem_tong_ket"] > 8].copy()

    def delete_by_keys(self, ma_sv, ma_mon):
        """Xóa bản ghi theo cặp khóa sinh viên/môn, dùng khi cần thao tác theo khóa tự nhiên."""
        data = self.get_all()
        data = data[
            ~(
                data["ma_sv"].astype(str).eq(str(ma_sv))
                & data["ma_mon"].astype(str).eq(str(ma_mon))
            )
        ]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def update_by_keys(self, ma_sv, ma_mon, new_data):
        """Cập nhật bản ghi theo cặp khóa sinh viên/môn thay vì id."""
        data = self.get_all()
        mask = data["ma_sv"].astype(str).eq(str(ma_sv)) & data["ma_mon"].astype(str).eq(
            str(ma_mon)
        )
        if not mask.any():
            return False
        data.loc[mask, self.columns] = new_data
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def get_average_by_subject(self):
        """Tính điểm trung bình theo môn từ dữ liệu đã join để phục vụ thống kê."""
        data = self.get_display_data()
        return data.groupby("ma_mon", as_index=False)["diem_tong_ket"].mean().round(2)
