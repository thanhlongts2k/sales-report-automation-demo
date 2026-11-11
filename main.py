"""Demo: tu dong bao cao ban hang + nhac no qua email (DU LIEU GIA).

Day la project PORTFOLIO cua Louis — viet moi tu dau, chi dung du lieu gia
trong data/sample_sales.xlsx. Khong dung code, du lieu hay anh chup cua
bat ky cong ty hay khach hang that nao (dac biet khong dung du lieu MISA
cua cong ty anh dang lam).

Chay:  python main.py [--ngay 2026-11-11] [--gui-that]
  --ngay: ngay bao cao, mac dinh 2026-11-11 (ngay cua bo du lieu mau).
  --gui-that: KHONG co tac dung gui mail that trong demo nay — co nay chi
    de minh hoa: neu bat len ma chua cau hinh SMTP thi chuong trinh bao
    loi ro rang thay vi im lang. Mac dinh chi ghi NHAP email ra file.

Dau ra (thu muc output/):
  bao-cao-YYYY-MM-DD.xlsx : TongHop, TheoSanPham, TheoKhuVuc, NhacNo
  tom-tat.md               : ban tom tat de doc nhanh / chup man hinh
  dashboard.html           : bang dashboard don gian, mo bang trinh duyet
  emails/NN-<ten>.txt      : nhap mail nhac no cho tung khach (khong gui)
  sent_log.csv             : nhat ky chong gui trung — cung ngay, cung
    khach thi chi tao nhap 1 lan, lan 2 se ghi "da_tao_nhap" thay vi
    tao trung.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "sample_sales.xlsx"
OUT_DIR = ROOT / "output"
EMAIL_DIR = OUT_DIR / "emails"
LOG_FILE = OUT_DIR / "sent_log.csv"

CONG_TY_GIA = "Cong ty TNHH An Phuc (DU LIEU GIA — moi so lieu deu la bia ra)"


def doc_du_lieu() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA.exists():
        print(f"LOI: khong thay file du lieu mau {DATA}", file=sys.stderr)
        print("Chay truoc: python scripts/generate_sample_data.py", file=sys.stderr)
        raise SystemExit(1)
    don = pd.read_excel(DATA, sheet_name="DonHang")
    no = pd.read_excel(DATA, sheet_name="CongNo")
    return don, no


def tong_hop(don: pd.DataFrame) -> dict:
    return {
        "tong_don": int(len(don)),
        "tong_doanh_thu": int(don["thanh_tien"].sum()),
        "don_trung_binh": int(don["thanh_tien"].mean()),
        "san_pham_ban_chay": str(don.groupby("san_pham")["so_luong"].sum().idxmax()),
    }


def bang_theo(don: pd.DataFrame, cot: str) -> pd.DataFrame:
    bang = (
        don.groupby(cot)
        .agg(so_don=("ma_don", "count"), so_luong=("so_luong", "sum"),
             doanh_thu=("thanh_tien", "sum"))
        .reset_index()
        .sort_values("doanh_thu", ascending=False)
    )
    return bang


def tim_no_qua_han(no: pd.DataFrame, ngay: date) -> pd.DataFrame:
    han = pd.to_datetime(no["han_thanh_toan"]).dt.date
    qua_han = no[(no["trang_thai"] == "chua_thanh_toan") & (han < ngay)].copy()
    qua_han["so_ngay_qua_han"] = [(ngay - h).days for h in han[qua_han.index]]
    return qua_han.sort_values("so_ngay_qua_han", ascending=False)


def da_tao_nhap(ngay: date, khach: str) -> bool:
    if not LOG_FILE.exists():
        return False
    with open(LOG_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ngay"] == ngay.isoformat() and row["khach_hang"] == khach:
                return True
    return False


def ghi_log(ngay: date, khach: str, so_tien: int, trang_thai: str) -> None:
    moi = not LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ngay", "khach_hang", "so_tien", "trang_thai"])
        if moi:
            w.writeheader()
        w.writerow({"ngay": ngay.isoformat(), "khach_hang": khach,
                    "so_tien": so_tien, "trang_thai": trang_thai})


def viet_nhap_email(ngay: date, khach: str, khoan: pd.DataFrame) -> Path:
    tong = int(khoan["so_tien"].sum())
    dong = "\n".join(
        f"- {r.ma_cong_no}: {r.so_tien:,} VND, han {r.han_thanh_toan}, "
        f"qua han {r.so_ngay_qua_han} ngay"
        for r in khoan.itertuples()
    )
    noi_dung = (
        f"To: ke-toan@vi-du-gia.vn\n"
        f"Subject: [NHAP — KHONG GUI THAT] Nhac thanh toan cong no — {khach}\n\n"
        f"Kinh gui {khach},\n\n"
        f"{CONG_TY_GIA} xin nhac anh/chi thanh toan cac khoan sau:\n\n"
        f"{dong}\n\n"
        f"Tong cong: {tong:,} VND.\n"
        f"Neu anh/chi da thanh toan, xin bo qua email nay.\n\n"
        f"Tran trong,\nPhong Ke toan (ban nhap tu dong, ngay {ngay.isoformat()})\n"
    )
    ten_file = EMAIL_DIR / f"NN-{khach.replace(' ', '_')}.txt"
    ten_file.write_text(noi_dung, encoding="utf-8")
    return ten_file


def viet_dashboard(ngay: date, th: dict, theo_sp: pd.DataFrame,
                   theo_kv: pd.DataFrame, qua_han: pd.DataFrame) -> Path:
    def bang_html(df: pd.DataFrame) -> str:
        return df.to_html(index=False, border=1)

    html = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Dashboard ban hang — {ngay.isoformat()} (du lieu gia)</title></head>
<body><h1>Dashboard ban hang — {ngay.isoformat()}</h1>
<p>{CONG_TY_GIA}</p>
<p>Tong don: <b>{th['tong_don']}</b> — Doanh thu: <b>{th['tong_doanh_thu']:,} VND</b>
— Don trung binh: <b>{th['don_trung_binh']:,} VND</b>
— San pham ban chay: <b>{th['san_pham_ban_chay']}</b></p>
<p>Khoan no qua han: <b>{len(qua_han)}</b> khoan,
tong <b>{int(qua_han['so_tien'].sum()) if len(qua_han) else 0:,} VND</b></p>
<h2>Theo san pham</h2>{bang_html(theo_sp)}
<h2>Theo khu vuc</h2>{bang_html(theo_kv)}
<h2>No qua han</h2>{bang_html(qua_han) if len(qua_han) else '<p>Khong co khoan qua han.</p>'}
</body></html>"""
    p = OUT_DIR / "dashboard.html"
    p.write_text(html, encoding="utf-8")
    return p


def main() -> None:
    ap = argparse.ArgumentParser(description="Demo bao cao ban hang + nhac no (du lieu gia)")
    ap.add_argument("--ngay", default="2026-11-11",
                    help="Ngay bao cao YYYY-MM-DD (mac dinh 2026-11-11)")
    ap.add_argument("--gui-that", action="store_true",
                    help="Chi minh hoa: demo nay KHONG gui mail that")
    args = ap.parse_args()
    ngay = date.fromisoformat(args.ngay)

    if args.gui_that:
        print("LOI: demo nay khong gui mail that. Bo co --gui-that de chi tao file nhap.",
              file=sys.stderr)
        raise SystemExit(2)

    don, no = doc_du_lieu()
    th = tong_hop(don)
    theo_sp = bang_theo(don, "san_pham")
    theo_kv = bang_theo(don, "khu_vuc")
    qua_han = tim_no_qua_han(no, ngay)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EMAIL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. File bao cao Excel
    bao_cao = OUT_DIR / f"bao-cao-{ngay.isoformat()}.xlsx"
    with pd.ExcelWriter(bao_cao, engine="openpyxl") as w:
        pd.DataFrame([th]).to_excel(w, sheet_name="TongHop", index=False)
        theo_sp.to_excel(w, sheet_name="TheoSanPham", index=False)
        theo_kv.to_excel(w, sheet_name="TheoKhuVuc", index=False)
        qua_han.to_excel(w, sheet_name="NhacNo", index=False)

    # 2. Nhap email nhac no — co chong tao trung trong ngay
    moi, trung = 0, 0
    for khach, khoan in qua_han.groupby("khach_hang"):
        tong = int(khoan["so_tien"].sum())
        if da_tao_nhap(ngay, khach):
            ghi_log(ngay, khach, tong, "da_tao_nhap")
            trung += 1
            continue
        viet_nhap_email(ngay, khach, khoan)
        ghi_log(ngay, khach, tong, "da_tao_nhap")
        moi += 1

    # 3. Tom tat + dashboard
    tom_tat = (
        f"# Tom tat bao cao — {ngay.isoformat()} (DU LIEU GIA)\n\n"
        f"- Tong don: {th['tong_don']}\n"
        f"- Doanh thu: {th['tong_doanh_thu']:,} VND\n"
        f"- Don trung binh: {th['don_trung_binh']:,} VND\n"
        f"- San pham ban chay: {th['san_pham_ban_chay']}\n"
        f"- No qua han: {len(qua_han)} khoan, "
        f"{int(qua_han['so_tien'].sum()) if len(qua_han) else 0:,} VND\n"
        f"- Nhap email nhac no: {moi} moi, {trung} trung (da co trong ngay)\n"
    )
    (OUT_DIR / "tom-tat.md").write_text(tom_tat, encoding="utf-8")
    viet_dashboard(ngay, th, theo_sp, theo_kv, qua_han)

    print(f"Doanh thu: {th['tong_doanh_thu']:,} VND / {th['tong_don']} don")
    print(f"No qua han: {len(qua_han)} khoan, "
          f"{int(qua_han['so_tien'].sum()) if len(qua_han) else 0:,} VND")
    print(f"Nhap email: {moi} moi, {trung} trung")
    print(f"Bao cao: {bao_cao}")


if __name__ == "__main__":
    main()
