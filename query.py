import pandas as pd

class Query:
    def __init__(self, file_path, columns):
        self.file_path = file_path
        self.columns = columns

    def get_all(self):
        return pd.read_csv(self.file_path)

    def create(self, row):
        df = pd.read_csv(self.file_path)
        df.loc[len(df)] = row
        df.to_csv(self.file_path, index=False)

    def delete(self, col, value):
        df = pd.read_csv(self.file_path)
        df = df[df[col] != value]
        df.to_csv(self.file_path, index=False)

    def update(self, col, value, new_row):
        df = pd.read_csv(self.file_path)
        idx = df[df[col] == value].index
        if len(idx) > 0:
            df.loc[idx[0]] = new_row
        df.to_csv(self.file_path, index=False)

    def search(self, col, value):
        df = pd.read_csv(self.file_path)
        return df[df[col] == value]

    def max(self, col):
        df = pd.read_csv(self.file_path)
        return df[col].max()