from .base import CSVQuery


class MonHocQuery(CSVQuery):
    """Query cho dữ liệu môn học theo schema ma_mon, ten_mon, so_tin_chi, he_so_diem."""

    def __init__(self):
        super().__init__("database/monhoc.csv", ["ma_mon", "ten_mon", "so_tin_chi"])
