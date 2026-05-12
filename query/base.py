import os
import pandas as pd


class CSVQuery:
    """Lớp query dùng chung cho các file CSV trong thư mục database."""

    def __init__(self, file_path, columns):
        self.file_path = file_path
        self.columns = columns
        self.ensure_file()

    def ensure_file(self):
        # Tự tạo file CSV rỗng nếu file chưa tồn tại để màn hình không lỗi khi mở.
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            pd.DataFrame(columns=self.columns).to_csv(
                self.file_path, index=False, encoding="utf-8"
            )

    def get_all(self):
        # Đọc UTF-8 để giữ đúng dữ liệu tiếng Việt trong CSV.
        return pd.read_csv(self.file_path, encoding="utf-8")

    def list(self, page=1, page_size=20):
        # Trả dữ liệu dạng phân trang.
        data = self.get_all()
        start = (page - 1) * page_size
        end = start + page_size
        rows = [data.iloc[i].to_dict() for i in range(start, min(end, len(data)))]
        return {
            "page": page,
            "page_size": page_size,
            "total_records": len(data),
            "total_pages": (len(data) + page_size - 1) // page_size,
            "data": rows,
        }

    def search(self, column, keyword):
        data = self.get_all()
        if keyword == "":
            return data
        # Chuyển về chuỗi để tìm được cả cột số như id hoặc sdt.
        return data[
            data[column].astype(str).str.contains(str(keyword), case=False, na=False)
        ]

    def find_exact(self, column, value):
        # Dùng cho các kiểm tra khóa không được trùng như ma_sv, ma_mon, username.
        data = self.get_all()
        return data[data[column].astype(str) == str(value)]

    def create(self, new_data):
        # new_data phải đúng thứ tự self.columns để tránh ghi lệch cột trong CSV.
        data = self.get_all()
        new_row = pd.DataFrame([new_data], columns=self.columns)
        data = pd.concat([data, new_row], ignore_index=True)
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def update(self, column, value, new_data):
        # Cập nhật dòng đầu tiên khớp khóa; các page đã kiểm tra trùng trước khi gọi.
        data = self.get_all()
        idx = data[data[column].astype(str) == str(value)].index
        if len(idx) == 0:
            return False
        data.loc[idx[0], self.columns] = new_data
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def update_fields(self, column, value, fields, values):
        # Dùng khi chỉ cần sửa một số cột thay vì truyền lại cả dòng.
        data = self.get_all()
        mask = data[column].astype(str) == str(value)
        if not mask.any():
            return False
        for field, new_value in zip(fields, values):
            data.loc[mask, field] = new_value
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def delete(self, column, value):
        # Xóa bằng cách lọc bỏ dòng khớp khóa rồi ghi lại toàn bộ file.
        data = self.get_all()
        data = data[data[column].astype(str) != str(value)]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def next_id(self, column="id"):
        # Sinh id tăng dần, bỏ qua giá trị rỗng hoặc không phải số.
        data = self.get_all()
        if data.empty or column not in data.columns:
            return 1
        max_value = pd.to_numeric(data[column], errors="coerce").max()
        return 1 if pd.isna(max_value) else int(max_value) + 1
