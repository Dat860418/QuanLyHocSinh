import os
import pandas as pd


class CSVQuery:
    """Lớp dùng chung để đọc/ghi dữ liệu CSV trong thư mục database."""

    def __init__(self, file_path, columns):
        self.file_path = file_path
        self.columns = columns
        self.ensure_file()

    def ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            pd.DataFrame(columns=self.columns).to_csv(
                self.file_path, index=False, encoding="utf-8"
            )

    def get_all(self):
        # Đọc tất cả cột dạng chuỗi để giữ nguyên mã, SĐT và tránh lỗi gán string vào cột int64 khi import/update.
        return pd.read_csv(self.file_path, encoding="utf-8", dtype=str).fillna("")

    def list(self, page=1, page_size=20):
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
        return data[
            data[column].astype(str).str.contains(str(keyword), case=False, na=False)
        ]

    def find_exact(self, column, value):
        data = self.get_all()
        return data[data[column].astype(str) == str(value)]

    def create(self, new_data):
        data = self.get_all()
        new_data = ["" if x is None else str(x) for x in new_data]
        new_row = pd.DataFrame([new_data], columns=self.columns)
        data = pd.concat([data, new_row], ignore_index=True)
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def update(self, column, value, new_data):
        data = self.get_all()
        idx = data[data[column].astype(str) == str(value)].index
        if len(idx) == 0:
            return False
        data.loc[idx[0], self.columns] = ["" if x is None else str(x) for x in new_data]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def update_fields(self, column, value, fields, values):
        data = self.get_all()
        mask = data[column].astype(str) == str(value)
        if not mask.any():
            return False
        for field, new_value in zip(fields, values):
            data.loc[mask, field] = "" if new_value is None else str(new_value)
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def delete(self, column, value):
        data = self.get_all()
        data = data[data[column].astype(str) != str(value)]
        data.to_csv(self.file_path, index=False, encoding="utf-8")
        return True

    def next_id(self, column="id"):
        data = self.get_all()
        if data.empty or column not in data.columns:
            return 1
        max_value = pd.to_numeric(data[column], errors="coerce").max()
        return 1 if pd.isna(max_value) else int(max_value) + 1
