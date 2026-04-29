import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from query import Query

class QuanLyMonHocPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = Query("database/monhoc.csv", ["stt", "ten_mon", "ma_mon"])

        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.master, text="Quản lý môn học", font=("Arial", 20)).pack()

        frame = tk.Frame(self.master)
        frame.pack(pady=10)

        tk.Label(frame, text="Tên môn:", width=15, anchor="w").grid(row=0, column=0)
        self.entry_ten = tk.Entry(frame)
        self.entry_ten.grid(row=0, column=1)

        tk.Label(frame, text="Mã môn:", width=15, anchor="w").grid(row=1, column=0)
        self.entry_ma = tk.Entry(frame)
        self.entry_ma.grid(row=1, column=1)

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Thêm", command=self.them).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Xoá", command=self.xoa).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Sửa", command=self.sua).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Tìm", command=self.tim).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Hiển thị tất cả", command=self.load_data).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Quay lại", command=self.back).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.master, columns=("stt", "ten", "ma"), show="headings")
        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Tên môn")
        self.tree.heading("ma", text="Mã môn")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        data = self.q.get_all()
        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def on_select(self, event):
        selected = self.tree.focus()
        values = self.tree.item(selected, "values")

        if values:
            self.entry_ten.delete(0, tk.END)
            self.entry_ten.insert(0, values[1])

            self.entry_ma.delete(0, tk.END)
            self.entry_ma.insert(0, values[2])

    def them(self):
        ten = self.entry_ten.get().strip()
        ma = self.entry_ma.get().strip()

        if not ten or not ma:
            messagebox.showerror("Lỗi", "Nhập đầy đủ thông tin")
            return

        if not self.q.search("ma_mon", ma).empty:
            messagebox.showerror("Lỗi", "Mã môn đã tồn tại")
            return

        max_stt = self.q.max("stt")
        stt = 1 if pd.isna(max_stt) else int(max_stt) + 1

        self.q.create([stt, ten, ma])
        self.load_data()

    def xoa(self):
        ma = self.entry_ma.get().strip()
        if not ma:
            return

        self.q.delete("ma_mon", ma)
        self.load_data()

    def sua(self):
        selected = self.tree.focus()
        if not selected:
            return

        old = self.tree.item(selected, "values")
        old_ma = old[2]

        ten = self.entry_ten.get().strip()
        ma = self.entry_ma.get().strip()

        data = self.q.search("ma_mon", old_ma)
        stt = data.iloc[0]["stt"]

        self.q.update("ma_mon", old_ma, [stt, ten, ma])
        self.load_data()

    def tim(self):
        ma = self.entry_ma.get().strip()

        for i in self.tree.get_children():
            self.tree.delete(i)

        data = self.q.search("ma_mon", ma)

        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def back(self):
        self.app_manager.show_quanlytk_page()