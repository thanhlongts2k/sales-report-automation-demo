"""Tao du lieu MAU (gia) cho demo automation.

Moi ten cong ty, ten khach hang, so tien trong file nay deu la
du lieu gia lap - thong tin khach hang deu duoc bao mat; khong phai
du lieu that cua bat ky cong ty hay khach hang nao.
Chay:  python scripts/generate_sample_data.py
Ghi ra: data/sample_sales.xlsx  (2 sheet: DonHang, CongNo)
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sample_sales.xlsx"

random.seed(20261111)

SAN_PHAM = [
    ("Giay the thao A", 850_000),
    ("Giay chay B", 1_200_000),
    ("Ao thun C", 250_000),
    ("Quan jeans D", 650_000),
    ("Ba lo E", 480_000),
]
KHU_VUC = ["Ha Noi", "TP.HCM", "Da Nang", "Hai Phong", "Can Tho"]
NHAN_VIEN = ["An", "Binh", "Chi", "Dung"]
KHACH_HANG = [
    "Cua hang Minh Anh", "Shop Thu Ha", "Cua hang Quang Huy",
    "Shop Lan Phuong", "Cua hang Duc Thang", "Shop Hoang Nam",
    "Cua hang Thanh Tam", "Shop Quoc Bao",
]


def tao_don_hang() -> pd.DataFrame:
    rows = []
    for i in range(1, 61):
        ten_sp, don_gia = random.choice(SAN_PHAM)
        so_luong = random.randint(1, 8)
        ngay = date(2026, 11, 1) + timedelta(days=random.randint(0, 9))
        rows.append({
            "ma_don": f"DH-{i:03d}",
            "ngay": ngay,
            "khach_hang": random.choice(KHACH_HANG),
            "san_pham": ten_sp,
            "so_luong": so_luong,
            "don_gia": don_gia,
            "thanh_tien": so_luong * don_gia,
            "khu_vuc": random.choice(KHU_VUC),
            "nhan_vien": random.choice(NHAN_VIEN),
        })
    return pd.DataFrame(rows)


def tao_cong_no() -> pd.DataFrame:
    # Han thanh toan gia dinh: don thang 10, han 7-30 ngay sau ngay mua.
    # "Hom nay" cua demo la 11/11/2026 — cac khoan han truoc ngay nay
    # va chua thanh toan se roi vao dien nhac no.
    rows = []
    du_lieu = [
        ("CN-01", "Cua hang Minh Anh", 12_500_000, "2026-10-05", "2026-10-20", "chua_thanh_toan"),
        ("CN-02", "Shop Thu Ha", 8_300_000, "2026-10-08", "2026-10-28", "chua_thanh_toan"),
        ("CN-03", "Cua hang Quang Huy", 15_750_000, "2026-10-12", "2026-11-05", "chua_thanh_toan"),
        ("CN-04", "Shop Lan Phuong", 4_200_000, "2026-10-15", "2026-11-15", "chua_thanh_toan"),
        ("CN-05", "Cua hang Duc Thang", 9_800_000, "2026-10-18", "2026-11-02", "chua_thanh_toan"),
        ("CN-06", "Shop Hoang Nam", 6_100_000, "2026-10-20", "2026-11-10", "chua_thanh_toan"),
        ("CN-07", "Cua hang Thanh Tam", 21_000_000, "2026-10-22", "2026-11-08", "chua_thanh_toan"),
        ("CN-08", "Shop Quoc Bao", 3_400_000, "2026-10-25", "2026-11-25", "chua_thanh_toan"),
        ("CN-09", "Cua hang Minh Anh", 7_200_000, "2026-10-10", "2026-10-25", "da_thanh_toan"),
        ("CN-10", "Shop Thu Ha", 5_600_000, "2026-10-14", "2026-11-01", "da_thanh_toan"),
        ("CN-11", "Cua hang Quang Huy", 11_900_000, "2026-10-28", "2026-11-20", "chua_thanh_toan"),
        ("CN-12", "Shop Lan Phuong", 2_750_000, "2026-10-30", "2026-11-12", "chua_thanh_toan"),
    ]
    for ma, khach, so_tien, ngay_mua, han, trang_thai in du_lieu:
        rows.append({
            "ma_cong_no": ma,
            "khach_hang": khach,
            "so_tien": so_tien,
            "ngay_mua": ngay_mua,
            "han_thanh_toan": han,
            "trang_thai": trang_thai,
            "email": "ke-toan@vi-du-gia.vn",
        })
    return pd.DataFrame(rows)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl") as w:
        tao_don_hang().to_excel(w, sheet_name="DonHang", index=False)
        tao_cong_no().to_excel(w, sheet_name="CongNo", index=False)
    print(f"Da tao {OUT} (60 don hang, 12 khoan cong no — dữ liệu giả lập - thông tin khách hàng đều được bảo mật)")


if __name__ == "__main__":
    main()
