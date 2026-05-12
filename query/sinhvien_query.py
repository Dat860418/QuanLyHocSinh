from .base import CSVQuery


class SinhVienQuery(CSVQuery):
    """Query cho dữ liệu sinh viên theo schema mới của sinhvien.csv."""

    def __init__(self):
        super().__init__(
            "database/sinhvien.csv",
            ["ma_sv", "ho_ten", "ngay_sinh", "gioi_tinh", "lop", "dia_chi", "sdt", "email", "trang_thai"],
        )
