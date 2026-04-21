import tkinter as tk
from tkinter import ttk, messagebox
from query import Query

class QuanLySVPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.q = Query("database/sinhvien.csv",
                       ["stt","ten","ma_sv"])

        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.master, text="Quản lý sinh viên", font=("Arial", 20)).pack()

        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=10)

        # Tên sinh viên
        tk.Label(input_frame, text="Tên sinh viên:", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        self.entry_ten = tk.Entry(input_frame)
        self.entry_ten.grid(row=0, column=1, padx=5, pady=5)

        # Mã sinh viên
        tk.Label(input_frame, text="Mã sinh viên:", width=15, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ma = tk.Entry(input_frame)
        self.entry_ma.grid(row=1, column=1, padx=5, pady=5)

        # tk.Button(self.master, text="Thêm", command=self.them).pack()
        # tk.Button(self.master, text="Xoá", command=self.xoa).pack()
        # tk.Button(self.master, text="Sửa", command=self.sua).pack()
        # tk.Button(self.master, text="Tìm", command=self.tim).pack()

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Thêm", width=10, command=self.them).pack(side="left", padx=5) #side left xep ngang
        tk.Button(button_frame, text="Xoá", width=10, command=self.xoa).pack(side="left", padx=5)
        tk.Button(button_frame, text="Sửa", width=10, command=self.sua).pack(side="left", padx=5)
        tk.Button(button_frame, text="Tìm", width=10, command=self.tim).pack(side="left", padx=5)
        tk.Button(button_frame, text="Hiển thị tất cả", width=10, command=self.load_data).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.master,
                                 columns=("stt","ten","ma"),
                                 show="headings")

        self.tree.heading("stt", text="STT")
        self.tree.heading("ten", text="Tên")
        self.tree.heading("ma", text="Mã SV")

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)#Click vào bảng → tự fill input

    def on_select(self, event):
        selected = self.tree.focus()
        values = self.tree.item(selected, "values")

        if values:
            self.entry_ten.delete(0, tk.END)
            self.entry_ten.insert(0, values[1])

            self.entry_ma.delete(0, tk.END)
            self.entry_ma.insert(0, values[2])

    def clear_input(self):
        self.entry_ten.delete(0, tk.END)
        self.entry_ma.delete(0, tk.END)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        data = self.q.get_all()

        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def them(self):
        ten = self.entry_ten.get().strip()
        ma = self.entry_ma.get().strip()

        if not ten or not ma:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # kiểm tra trùng mã
        data = self.q.search("ma_sv", ma)
        if not data.empty:
            messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
            return

        stt = self.q.max("stt") + 1
        self.q.create([stt, ten, ma])

        self.load_data()  # luôn load lại full
        self.clear_input()

    def xoa(self):
        ma = self.entry_ma.get().strip()

        if not ma:
            messagebox.showerror("Lỗi", "Nhập mã sinh viên để xoá")
            return

        data = self.q.search("ma_sv", ma)
        if data.empty:
            messagebox.showerror("Lỗi", "Không tìm thấy sinh viên")
            return

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xoá?"):
            return

        self.q.delete("ma_sv", ma)

        self.load_data()  # reload full
        self.clear_input()

    def sua(self):
        selected = self.tree.focus()

        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn sinh viên để sửa")
            return

        ten = self.entry_ten.get().strip()
        ma = self.entry_ma.get().strip()

        if not ten or not ma:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # Lấy dữ liệu cũ từ dòng đã chọn
        old_values = self.tree.item(selected, "values")
        old_ma = old_values[2]

        # Nếu đổi mã → check trùng
        if ma != old_ma:
            data = self.q.search("ma_sv", ma)
            if not data.empty:
                messagebox.showerror("Lỗi", "Mã sinh viên đã tồn tại")
                return

        # XÁC NHẬN
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn sửa sinh viên này?"):
            return

        # Lấy stt cũ
        data = self.q.search("ma_sv", old_ma)
        if data.empty:
            messagebox.showerror("Lỗi", "Dữ liệu không tồn tại")
            return

        stt = data.iloc[0]["stt"]

        # Update theo mã cũ
        self.q.update("ma_sv", old_ma, [stt, ten, ma])

        messagebox.showinfo("Thành công", "Cập nhật thành công")

        self.load_data()
        self.clear_input()

    def tim(self):
        ma = self.entry_ma.get().strip()

        if not ma:
            self.load_data()  # nếu rỗng → show full
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        data = self.q.search("ma_sv", ma)

        if data.empty:
            messagebox.showinfo("Thông báo", "Không tìm thấy")
            return

        for _, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))