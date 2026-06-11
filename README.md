# 📚 Hệ thống quản lý sinh viên

## 📋 Mô tả

Ứng dụng desktop được xây dựng bằng **Python** với giao diện **CustomTkinter** nhằm quản lý toàn diện sinh viên, môn học, điểm số và tài khoản người dùng. Dự án được tổ chức theo **mô hình MVC** (Model-View-Controller) để đảm bảo cấu trúc sạch, dễ bảo trì và mở rộng:

- **Model** (`model/`): xử lý thao tác dữ liệu CSV, truy vấn và lưu trữ thông tin
- **View** (`views/`): thiết kế giao diện người dùng cho từng màn hình chức năng
- **Controller** (`controllers/`): điều phối logic nghiệp vụ, xử lý sự kiện và tương tác giữa View và Model

## ✨ Tính năng chính

### Quản lý dữ liệu
- **Quản lý sinh viên**: thêm, sửa, xóa, tìm kiếm, phân trang, import/export CSV
- **Quản lý môn học**: thêm, sửa, xóa, tìm kiếm, import/export CSV
- **Quản lý điểm số**: thêm, sửa, xóa, tìm kiếm, thống kê, import/export CSV
- **Quản lý tài khoản**: tạo tài khoản, sửa tài khoản (dành cho Admin)

### Tính năng bảo mật
- Hệ thống xác thực người dùng (Login/Logout)
- Quản lý phiên đăng nhập
- Hiển thị/ẩn mật khẩu khi nhập liệu
- Validation dữ liệu tập trung

### Tối ưu hóa hiệu năng
- Tác vụ nặng chạy nền bằng `AsyncTaskRunner` để tránh treo giao diện
- Giao diện mền mại và phản hồi nhanh

## 🛠️ Yêu cầu hệ thống

- **Python**: 3.10 hoặc cao hơn
- **Thư viện cần thiết**:
  - pandas (xử lý dữ liệu CSV)
  - customtkinter (xây dựng giao diện đẹp và hiện đại)

## 📥 Cài đặt

### 1. Tạo môi trường ảo (tùy chọn nhưng khuyến nghị)

```bash
python -m venv .venv
# Trên Windows
.\.venv\Scripts\activate
# Trên Linux/macOS
source .venv/bin/activate
```

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Hoặc cài đặt thủ công:

```bash
pip install pandas customtkinter
```

### 3. Chạy ứng dụng

```bash
python Main.py
```

## 📁 Cấu trúc thư mục

```
AAAAA/
├── Main.py                          # Điểm vào (entry point) của ứng dụng
├── app_manager.py                   # Điều phối màn hình, quản lý phiên đăng nhập
├── README.md                        # Tài liệu hướng dẫn
│
├── common/                          # Các tiện ích dùng chung
│   ├── loading.py                   # Component loading (tải dữ liệu)
│   └── validation.py                # Hàm kiểm tra dữ liệu (validation)
│
├── controllers/                     # Xử lý logic nghiệp vụ (Controller)
│   ├── home_controller.py           # Điều khiển màn hình chính
│   ├── login_controller.py          # Xử lý đăng nhập
│   ├── quanly_diem_controller.py    # Quản lý điểm số
│   ├── quanly_monhoc_controller.py  # Quản lý môn học
│   ├── quanly_sv_controller.py      # Quản lý sinh viên
│   ├── quanlytk_controller.py       # Quản lý tài khoản
│   ├── suatk_controller.py          # Sửa tài khoản
│   └── taotk_controller.py          # Tạo tài khoản mới
│
├── views/                           # Giao diện người dùng (View)
│   ├── home_view.py                 # Màn hình chính/dashboard
│   ├── login_view.py                # Màn hình đăng nhập
│   ├── quanly_diem_view.py          # Giao diện quản lý điểm
│   ├── quanly_monhoc_view.py        # Giao diện quản lý môn học
│   ├── quanly_sv_view.py            # Giao diện quản lý sinh viên
│   ├── quanlytk_view.py             # Giao diện quản lý tài khoản
│   ├── suatk_view.py                # Giao diện sửa tài khoản
│   └── taotk_view.py                # Giao diện tạo tài khoản
│
├── model/                           # Truy vấn dữ liệu (Model)
│   ├── __init__.py
│   ├── base.py                      # Lớp cơ sở cho các model
│   ├── diem_query.py                # Truy vấn dữ liệu điểm số
│   ├── monhoc_query.py              # Truy vấn dữ liệu môn học
│   ├── sinhvien_query.py            # Truy vấn dữ liệu sinh viên
│   └── taikhoan_query.py            # Truy vấn dữ liệu tài khoản
│
├── database/                        # Dữ liệu dạng CSV
│   ├── sinhvien.csv                 # Danh sách sinh viên
│   ├── monhoc.csv                   # Danh sách môn học
│   ├── diem.csv                     # Danh sách điểm số
│   └── taikhoan.csv                 # Danh sách tài khoản người dùng
│
└── docs/                            # Tài liệu bổ sung (nếu có)
```

## 🔄 Luồng xử lý chính

```
1. Main.py
   ↓
2. AppManager khởi tạo ứng dụng
   ↓
3. Hiển thị màn hình LoginView
   ↓
4. Người dùng nhập tài khoản/mật khẩu
   ↓
5. LoginController xác thực
   ├─→ Hợp lệ: Chuyển đến HomeView
   └─→ Không hợp lệ: Hiển thị lỗi
   ↓
6. HomeView hiển thị các tùy chọn quản lý
   ↓
7. Người dùng chọn chức năng
   ├─→ Quản lý sinh viên → QuanLySVController + QuanLySVView
   ├─→ Quản lý môn học → QuanLyMonHocController + QuanLyMonHocView
   ├─→ Quản lý điểm → QuanLyDiemController + QuanLyDiemView
   ├─→ Quản lý tài khoản → QuanLyTKController + QuanLyTKView
   ├─→ Tạo tài khoản → TaoTKController + TaoTKView (Admin)
   └─→ Sửa tài khoản → SuaTKController + SuaTKView (Admin)
   ↓
8. Controller xử lý dữ liệu thông qua Model (Query classes)
   ↓
9. Model đọc/ghi từ file CSV trong thư mục database/
   ↓
10. Dữ liệu được trả về View để hiển thị
```

### Chi tiết từng bước:
- **View**: chỉ chịu trách nhiệm về giao diện, input và hiển thị dữ liệu
- **Controller**: điều khiển logic, gọi Model, cập nhật View
- **Model**: đơn thuần là truy vấn và lưu trữ dữ liệu từ CSV

## 💾 Dữ liệu mẫu

Các file dữ liệu được lưu trong thư mục `database/` dưới định dạng CSV:

| File | Nội dung |
|------|---------|
| `sinhvien.csv` | Thông tin sinh viên (MSSV, tên, email, lớp, v.v.) |
| `monhoc.csv` | Danh sách môn học (mã môn, tên môn, tín chỉ, v.v.) |
| `diem.csv` | Điểm số của sinh viên (MSSV, mã môn, điểm, v.v.) |
| `taikhoan.csv` | Tài khoản người dùng (username, password, role, v.v.) |

**Lưu ý**: Các file CSV được sử dụng trực tiếp làm nguồn dữ liệu. Khi chỉnh sửa cấu trúc cột, cần cập nhật lại các file Query tương ứng trong thư mục `model/`.

## 📝 Quy ước phát triển

### Khi thêm chức năng mới:
1. **Tạo Query class** trong `model/` nếu cần làm việc với dữ liệu mới
2. **Tạo Controller** trong `controllers/` để xử lý logic nghiệp vụ
3. **Tạo View** trong `views/` để thiết kế giao diện
4. **Đăng ký route** trong `app_manager.py` để kết nối màn hình

### Quy tắc chung:
- ✅ Mọi thay đổi dữ liệu nên đi qua `Model` (Query classes)
- ✅ Mọi thay đổi giao diện nên thực hiện trong `View`
- ✅ Mọi logic nghiệp vụ nên xử lý trong `Controller`
- ✅ Dữ liệu đầu vào phải đi qua `common/validation.py` để kiểm tra
- ✅ Các thao tác nặng (import/export, xử lý dữ liệu lớn) nên dùng `AsyncTaskRunner`
- ❌ Tuyệt đối không để logic phức tạp trong View
- ❌ Không truy cập trực tiếp file CSV từ View hoặc Controller

## 💡 Ghi chú quan trọng

### Khi mở rộng ứng dụng:
- Để bổ sung màn hình mới, hãy tạo cặp `*_controller.py` + `*_view.py` tương ứng
- Đăng ký các route mới trong phương thức của `AppManager` (thường theo cấu trúc `show_*.py`)
- Tên các lớp nên tuân theo quy ước: `QuanLy<TênChứcNăng>Controller` và `QuanLy<TênChứcNăng>View`

### Về dữ liệu:
- Các file CSV trong `database/` được sử dụng trực tiếp, nên cần backup trước khi thay đổi
- Khi thêm cột mới vào CSV, phải cập nhật kèm theo Query class tương ứng
- Hiện tại dữ liệu được lưu **in-memory**, không có database thực (SQLite, MySQL, v.v.)

### Hiệu năng:
- Những thao tác tốn thời gian (load dữ liệu lớn, export CSV) nên chạy trong thread riêng
- Luôn sử dụng `AsyncTaskRunner` cho các tác vụ I/O hoặc tính toán nặng

### Bảo trì:
- Luôn viết comment cho các hàm phức tạp
- Sử dụng docstring cho các class và phương thức public
- Kiểm tra validation dữ liệu tại Model layer để đảm bảo tính nhất quán

---

## 📞 Liên hệ & Hỗ trợ

Nếu có câu hỏi hoặc gặp vấn đề, vui lòng:
- Kiểm tra file ghi chú (nếu có) trong thư mục `docs/`
- Xem lại quy ước phát triển ở trên
- Kiểm tra các file `*_controller.py` và `*_view.py` tương ứng để hiểu cách chúng hoạt động

---

**Phiên bản**: 1.0  
**Cập nhật lần cuối**: 2026
