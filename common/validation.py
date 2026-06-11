import re
from datetime import datetime


class ValidationError(Exception):
    """Lỗi validate dữ liệu nhập."""


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\d{9,11}$")
_USER_RE = re.compile(r"^[A-Za-z0-9_.-]{4,32}$")


def _clean(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def require(value, label):
    value = _clean(value)
    if value == "":
        raise ValidationError(f"{label} không được để trống")
    return value


def validate_username(value):
    value = require(value, "Username")
    if not _USER_RE.fullmatch(value):
        raise ValidationError("Username chỉ được gồm chữ, số, . _ - và dài 4-32 ký tự")
    return value


def validate_password(value, label="Password"):
    value = require(value, label)
    if len(value) < 5:
        raise ValidationError(f"{label} phải có ít nhất 5 ký tự")
    return value


def validate_full_name(value):
    value = require(value, "Họ tên")
    if len(value) < 2:
        raise ValidationError("Họ tên phải có ít nhất 2 ký tự")
    return value


def validate_phone(value):
    value = _clean(value)
    if value == "":
        return ""
    if not _PHONE_RE.fullmatch(value):
        raise ValidationError("SĐT phải gồm 9-11 chữ số")
    return value


def validate_email(value):
    value = _clean(value)
    if value == "":
        return ""
    if not _EMAIL_RE.fullmatch(value):
        raise ValidationError("Email không đúng định dạng")
    return value


def validate_date_yyyy_mm_dd(value):
    value = _clean(value)
    if value == "":
        return ""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError("Ngày sinh phải đúng định dạng YYYY-MM-DD") from exc
    return parsed.strftime("%Y-%m-%d")


def validate_gender(value):
    value = require(value, "Giới tính")
    if value not in {"Nam", "Nữ"}:
        raise ValidationError("Giới tính phải là Nam hoặc Nữ")
    return value


def validate_status(value):
    value = require(value, "Trạng thái")
    if value not in {"Đang học", "Đã nghỉ"}:
        raise ValidationError("Trạng thái phải là Đang học hoặc Đã nghỉ")
    return value


def validate_non_empty(value, label):
    return require(value, label)


def validate_score(value, label):
    value = require(value, label)
    try:
        score = float(value)
    except ValueError as exc:
        raise ValidationError(f"{label} phải là số") from exc
    if score < 0 or score > 10:
        raise ValidationError(f"{label} phải nằm trong khoảng 0 đến 10")
    return score


def validate_credit(value):
    value = require(value, "Số tín chỉ")
    try:
        credits = int(value)
    except ValueError as exc:
        raise ValidationError("Số tín chỉ phải là số nguyên") from exc
    if credits < 1 or credits > 5:
        raise ValidationError("Số tín chỉ phải nằm trong khoảng 1 đến 5")
    return credits


def validate_role(value):
    value = require(value, "Role")
    if value not in {"User", "Admin"}:
        raise ValidationError("Role phải là User hoặc Admin")
    return value


def validate_student_payload(values):
    return {
        "ma_sv": require(values[0], "Mã SV"),
        "ho_ten": validate_full_name(values[1]),
        "ngay_sinh": validate_date_yyyy_mm_dd(values[2]),
        "gioi_tinh": validate_gender(values[3]),
        "lop": require(values[4], "Lớp"),
        "dia_chi": require(values[5], "Địa chỉ"),
        "sdt": validate_phone(values[6]),
        "email": validate_email(values[7]),
        "trang_thai": validate_status(values[8]),
    }


def validate_monhoc_payload(values):
    return {
        "ma_mon": require(values[0], "Mã môn"),
        "ten_mon": require(values[1], "Tên môn"),
        "so_tin_chi": validate_credit(values[2]),
    }


def validate_diem_payload(values):
    return {
        "ma_sv": require(values["ma_sv"], "Mã sinh viên"),
        "ma_mon": require(values["ma_mon"], "Mã môn"),
        "diem_cc": validate_score(values["diem_cc"], "Điểm CC"),
        "diem_kt1": validate_score(values["diem_kt1"], "Điểm KT1"),
        "diem_kt2": validate_score(values["diem_kt2"], "Điểm KT2"),
        "diem_ck": validate_score(values["diem_ck"], "Điểm CK"),
    }


def validate_account_payload(values, require_password=True):
    username = validate_username(values[0])
    password = (
        validate_password(values[1], "Password")
        if require_password
        else _clean(values[1])
    )
    if not require_password and password == "":
        password = ""
    ho_ten = validate_full_name(values[2])
    sdt = validate_phone(values[3])
    role = validate_role(values[4])
    return {
        "username": username,
        "password": password,
        "ho_ten": ho_ten,
        "sdt": sdt,
        "chuc_vu": role,
    }
