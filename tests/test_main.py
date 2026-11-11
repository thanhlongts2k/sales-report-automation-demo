"""Test nho cho logic tong hop + nhac no (dung unittest cua Python)."""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from main import bang_theo, tim_no_qua_han, tong_hop


class TestBaoCao(unittest.TestCase):
    def setUp(self):
        self.don = pd.DataFrame([
            {"ma_don": "DH-1", "san_pham": "Ao", "so_luong": 2,
             "thanh_tien": 500_000, "khu_vuc": "Ha Noi"},
            {"ma_don": "DH-2", "san_pham": "Ao", "so_luong": 1,
             "thanh_tien": 250_000, "khu_vuc": "Ha Noi"},
            {"ma_don": "DH-3", "san_pham": "Quan", "so_luong": 3,
             "thanh_tien": 1_950_000, "khu_vuc": "TP.HCM"},
        ])
        self.no = pd.DataFrame([
            {"ma_cong_no": "CN-1", "khach_hang": "A", "so_tien": 1_000_000,
             "han_thanh_toan": "2026-11-01", "trang_thai": "chua_thanh_toan"},
            {"ma_cong_no": "CN-2", "khach_hang": "B", "so_tien": 2_000_000,
             "han_thanh_toan": "2026-11-20", "trang_thai": "chua_thanh_toan"},
            {"ma_cong_no": "CN-3", "khach_hang": "C", "so_tien": 3_000_000,
             "han_thanh_toan": "2026-10-01", "trang_thai": "da_thanh_toan"},
        ])

    def test_tong_hop(self):
        th = tong_hop(self.don)
        self.assertEqual(th["tong_don"], 3)
        self.assertEqual(th["tong_doanh_thu"], 2_700_000)
        self.assertEqual(th["san_pham_ban_chay"], "Ao")

    def test_bang_theo_sap_xep_giam_dan(self):
        bang = bang_theo(self.don, "san_pham")
        self.assertEqual(list(bang["san_pham"]), ["Quan", "Ao"])

    def test_chi_nhac_no_qua_han_chua_tra(self):
        qua_han = tim_no_qua_han(self.no, date(2026, 11, 11))
        # CN-1 qua han chua tra -> nhac; CN-2 chua toi han -> khong;
        # CN-3 da tra -> khong, du han da qua.
        self.assertEqual(list(qua_han["ma_cong_no"]), ["CN-1"])
        self.assertEqual(int(qua_han.iloc[0]["so_ngay_qua_han"]), 10)


if __name__ == "__main__":
    unittest.main()
