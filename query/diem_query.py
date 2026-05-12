import pandas as pd

from .base import CSVQuery


class DiemQuery(CSVQuery):
    """Query riêng cho bảng điểm vì cần liên kết sang sinh viên và môn học."""

    def __init__(self):
        super().__init__(
            "database/diem.csv",
            ["id", "ma_sv", "ma_mon", "diem_cc", "diem_kt1", "diem_kt2", "diem_ck"],
        )

    def get_display_data(self):
        # File điểm chỉ lưu ma_sv/ma_mon; tên sinh viên và tên môn được lấy khi hiển thị.
        diem = self.get_all()
        sinhvien = pd.read_csv(
            "database/sinhvien.csv", encoding="utf-8"
        ).drop_duplicates("ma_sv")
        monhoc = pd.read_csv("database/monhoc.csv", encoding="utf-8").drop_duplicates(
            "ma_mon"
        )

        # Ép điểm về số để tính tổng kết và thống kê chính xác.
        for column in ["diem_cc", "diem_kt1", "diem_kt2", "diem_ck"]:
            diem[column] = pd.to_numeric(diem[column], errors="coerce")

        # Left join giữ lại mọi dòng điểm, kể cả khi dữ liệu tham chiếu bị thiếu.
        data = diem.merge(sinhvien[["ma_sv", "ho_ten"]], on="ma_sv", how="left")
        data = data.merge(monhoc[["ma_mon", "ten_mon"]], on="ma_mon", how="left")
        data["ho_ten"] = data["ho_ten"].fillna("Không tìm thấy SV")
        data["ten_mon"] = data["ten_mon"].fillna("Không tìm thấy môn")
        # Công thức tổng kết: chuyên cần 10%, KT1 15%, KT2 15%, cuối kỳ 60%.
        data["diem_tong_ket"] = (
            data["diem_cc"] * 0.1
            + data["diem_kt1"] * 0.15
            + data["diem_kt2"] * 0.15
            + data["diem_ck"] * 0.6
        ).round(2)
        data["xep_loai"] = data["diem_tong_ket"].apply(self.xep_loai)
        return data

    def xep_loai(self, diem):
        # Xếp loại chữ dựa trên điểm tổng kết đã tính trọng số.
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
        # Khi xóa sinh viên, xóa luôn điểm liên quan để tránh dữ liệu rác.
        data = self.get_all()
        data = data[data["ma_sv"].astype(str) != str(ma_sv)]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def subject_has_grades(self, ma_mon):
        # Môn học đã có điểm thì không được xóa ở màn hình môn học.
        data = self.get_all()
        return not data[data["ma_mon"].astype(str) == str(ma_mon)].empty

    def gpa_by_student(self):
        # GPA theo sinh viên: groupby ma_sv rồi lấy trung bình điểm tổng kết.
        data = self.get_display_data()
        return data.groupby("ma_sv", as_index=False)["diem_tong_ket"].mean()
