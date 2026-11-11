"""Demo: tu dong bao cao ban hang + nhac no qua email (du lieu gia lap).

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
  dashboard.html           : dashboard 1 file (CSS + JS nhung san, khong
    can mang): the KPI, bieu do thanh, bang sap xep duoc, tim kiem
    va loc nhac no theo muc do; mo bang trinh duyet la xem duoc
  emails/NN-<ten>.txt      : nhap mail nhac no cho tung khach (khong gui)
  sent_log.csv             : nhat ky chong gui trung — cung ngay, cung
    khach thi chi tao nhap 1 lan, lan 2 se ghi "da_tao_nhap" thay vi
    tao trung.
"""
from __future__ import annotations

import argparse
import csv
import html
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "sample_sales.xlsx"
OUT_DIR = ROOT / "output"
EMAIL_DIR = OUT_DIR / "emails"
LOG_FILE = OUT_DIR / "sent_log.csv"

CONG_TY_GIA = "Cong ty TNHH An Phuc (dữ liệu giả lập - thông tin khách hàng đều được bảo mật)"


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
    """Viet dashboard.html — 1 file duy nhat, CSS + JS nhung san ben trong.

    Khong dung CDN hay thu vien ngoai, mo bang trinh duyet la xem duoc
    ngay ca khi khong co mang. JS chi lam 2 viec nho: tim kiem trong
    bang no qua han, va sap xep bang khi bam vao tieu de cot.
    """
    tong_no = int(qua_han["so_tien"].sum()) if len(qua_han) else 0

    def hang_thanh(label: str, gia_tri: str, ty_le: float,
                   mau: str = "#2563eb") -> str:
        ty_le = max(2.0, min(100.0, ty_le))
        return (
            f'<div class="bar-row"><span class="bar-label">'
            f"{html.escape(label)}</span>"
            f'<div class="bar-track"><div class="bar-fill" style="width:{ty_le:.1f}%;'
            f'background:{mau}"></div></div>'
            f'<span class="bar-value">{html.escape(gia_tri)}</span></div>'
        )

    def bieu_do(df: pd.DataFrame, cot_nhan: str, cot_tien: str) -> str:
        lon_nhat = float(df[cot_tien].max()) if len(df) else 1.0
        mau = ["#2563eb", "#0891b2", "#059669", "#d97706", "#dc2626"]
        hang = "".join(
            hang_thanh(str(getattr(r, cot_nhan)),
                       f"{int(getattr(r, cot_tien)):,} VND",
                       float(getattr(r, cot_tien)) / lon_nhat * 100,
                       mau[i % len(mau)])
            for i, r in enumerate(df.itertuples())
        )
        return f'<div class="bars">{hang}</div>'

    def bang(df: pd.DataFrame, id_bang: str, dinh_dang_tien: set | None = None) -> str:
        dinh_dang_tien = dinh_dang_tien or set()
        tieu_de = "".join(
            f"<th data-kieu=\"{'so' if df[c].dtype.kind in 'iuf' else 'chu'}\">"
            f"{html.escape(str(c))}</th>" for c in df.columns
        )
        dong = ""
        for r in df.itertuples(index=False):
            o = "".join(
                f"<td>{int(v):,} VND</td>" if c in dinh_dang_tien
                else f"<td>{html.escape(str(v))}</td>"
                for c, v in zip(df.columns, r)
            )
            dong += f"<tr>{o}</tr>"
        return (f'<table id="{id_bang}" class="bang"><thead><tr>{tieu_de}'
                f"</tr></thead><tbody>{dong}</tbody></table>")

    def muc_do(ngay_qua: int) -> tuple[str, str]:
        if ngay_qua > 20:
            return "rat-gap", "Rất gấp"
        if ngay_qua >= 10:
            return "gap", "Gấp"
        return "nhac", "Nhắc"

    hang_no = ""
    for r in qua_han.itertuples():
        lop, nhan = muc_do(int(r.so_ngay_qua_han))
        hang_no += (
            f'<tr data-khach="{html.escape(str(r.khach_hang).lower())}" '
            f'data-muc="{lop}"><td>{html.escape(str(r.ma_cong_no))}</td>'
            f"<td>{html.escape(str(r.khach_hang))}</td>"
            f"<td>{int(r.so_tien):,} VND</td>"
            f"<td>{html.escape(str(r.han_thanh_toan))}</td>"
            f"<td>{int(r.so_ngay_qua_han)} ngày</td>"
            f'<td><span class="badge {lop}">{nhan}</span></td></tr>'
        )
    bang_no = (
        '<table id="bang-no" class="bang"><thead><tr>'
        "<th>Mã</th><th>Khách hàng</th><th>Số tiền</th>"
        "<th>Hạn thanh toán</th><th>Quá hạn</th><th>Mức độ</th>"
        "</tr></thead><tbody>" + hang_no + "</tbody></table>"
        if hang_no else "<p class='trong'>Không có khoản quá hạn. 🎉</p>"
    )

    css = """
:root{--xanh:#2563eb;--do:#dc2626;--xam:#64748b;--nen:#f1f5f9;--vien:#e2e8f0}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--nen);color:#0f172a}
header{background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;padding:28px 24px}
header .wrap,main{max-width:1020px;margin:0 auto}
header h1{margin:0 0 6px;font-size:26px}
header p{margin:4px 0;color:#dbeafe}
.badge-gia{display:inline-block;background:#facc15;color:#422006;font-size:12px;font-weight:700;padding:3px 10px;border-radius:999px}
main{padding:20px 16px 40px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0 24px}
.kpi{background:#fff;border:1px solid var(--vien);border-radius:14px;padding:16px}
.kpi .nhan{font-size:13px;color:var(--xam)}
.kpi .so{font-size:24px;font-weight:800;margin-top:4px}
.kpi .phu{font-size:13px;color:var(--xam);margin-top:2px}
.kpi.do .so{color:var(--do)}
section{background:#fff;border:1px solid var(--vien);border-radius:14px;padding:18px;margin-bottom:18px}
section h2{margin:0 0 4px;font-size:18px}
section .mo-ta{color:var(--xam);font-size:13px;margin:0 0 14px}
.bar-row{display:grid;grid-template-columns:150px 1fr 130px;gap:10px;align-items:center;padding:7px 0}
.bar-label{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{background:#e2e8f0;border-radius:999px;height:12px;overflow:hidden}
.bar-fill{height:100%;border-radius:999px}
.bar-value{text-align:right;font-size:13px;font-weight:600}
.bang{width:100%;border-collapse:collapse;font-size:14px}
.bang th,.bang td{padding:9px 10px;border-bottom:1px solid var(--vien);text-align:left}
.bang thead th{background:#f8fafc;cursor:pointer;white-space:nowrap}
.bang tbody tr:hover{background:#eff6ff}
.bang td:last-child,.bang th:last-child{text-align:right}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700}
.badge.rat-gap{background:#fee2e2;color:#991b1b}
.badge.gap{background:#fef3c7;color:#92400e}
.badge.nhac{background:#dbeafe;color:#1e40af}
.trong{color:var(--xam)}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.toolbar input{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--vien);border-radius:10px;font-size:14px}
.nut{padding:9px 14px;border:1px solid var(--vien);background:#fff;border-radius:10px;cursor:pointer;font-size:14px}
.nut.chon{background:#2563eb;color:#fff;border-color:#2563eb}
footer{color:var(--xam);font-size:13px;text-align:center;padding-bottom:20px}
@media(max-width:640px){.bar-row{grid-template-columns:110px 1fr 90px}.kpi .so{font-size:20px}}
"""
    js = """
function locNo(){
  var tu=document.getElementById('tim-no').value.toLowerCase();
  var muc=document.querySelector('.nut.chon').dataset.muc;
  document.querySelectorAll('#bang-no tbody tr').forEach(function(r){
    var hopTu=!tu||r.dataset.khach.indexOf(tu)>-1||r.textContent.toLowerCase().indexOf(tu)>-1;
    var hopMuc=muc==='tat-ca'||r.dataset.muc===muc;
    r.style.display=(hopTu&&hopMuc)?'':'none';
  });
}
document.querySelectorAll('.nut').forEach(function(n){
  n.addEventListener('click',function(){
    document.querySelectorAll('.nut').forEach(function(x){x.classList.remove('chon')});
    n.classList.add('chon');locNo();
  });
});
document.querySelectorAll('.bang thead th').forEach(function(th,i){
  th.addEventListener('click',function(){
    var bang=th.closest('table'),tb=bang.tBodies[0];
    var hang=Array.from(tb.rows),tang=bang.dataset.tang!=='1';
    bang.dataset.tang=tang?'1':'0';
    hang.sort(function(a,b){
      var x=a.cells[i].textContent.trim(),y=b.cells[i].textContent.trim();
      var sx=parseFloat(x.replace(/[^0-9.-]/g,'')),sy=parseFloat(y.replace(/[^0-9.-]/g,''));
      if(!isNaN(sx)&&!isNaN(sy))return tang?sx-sy:sy-sx;
      return tang?x.localeCompare(y,'vi'):y.localeCompare(x,'vi');
    });
    hang.forEach(function(r){tb.appendChild(r)});
  });
});
"""
    noi_dung = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard bán hàng — {ngay.isoformat()} (dữ liệu giả lập)</title>
<style>{css}</style></head>
<body><header><div class="wrap">
<h1>📊 Dashboard bán hàng — {ngay.isoformat()}</h1>
<p>{html.escape(CONG_TY_GIA)}</p>
<p><span class="badge-gia">Dữ liệu giả lập - thông tin khách hàng đều được bảo mật</span></p>
</div></header>
<main>
<div class="kpis">
<div class="kpi"><div class="nhan">Doanh thu</div><div class="so">{th['tong_doanh_thu']:,} VND</div><div class="phu">{th['tong_don']} đơn hàng</div></div>
<div class="kpi"><div class="nhan">Đơn trung bình</div><div class="so">{th['don_trung_binh']:,} VND</div><div class="phu">Sản phẩm bán chạy: {html.escape(str(th['san_pham_ban_chay']))}</div></div>
<div class="kpi do"><div class="nhan">Nợ quá hạn</div><div class="so">{len(qua_han)} khoản</div><div class="phu">Tổng {tong_no:,} VND — cần nhắc ngay</div></div>
</div>
<section><h2>Doanh thu theo sản phẩm</h2><p class="mo-ta">Bấm vào tiêu đề bảng để sắp xếp. Thanh dài hơn nghĩa là doanh thu cao hơn.</p>{bieu_do(theo_sp, 'san_pham', 'doanh_thu')}{bang(theo_sp, 'bang-sp', {'doanh_thu'})}</section>
<section><h2>Doanh thu theo khu vực</h2><p class="mo-ta">Khu vực nào bán mạnh, khu vực nào còn yếu — nhìn thanh là thấy.</p>{bieu_do(theo_kv, 'khu_vuc', 'doanh_thu')}{bang(theo_kv, 'bang-kv', {'doanh_thu'})}</section>
<section><h2>Nhắc nợ quá hạn</h2><p class="mo-ta">Gõ tên khách để tìm nhanh, bấm nút để lọc theo mức độ. Mức độ tính theo số ngày quá hạn: dưới 10 ngày thì nhắc, 10–20 ngày thì gấp, trên 20 ngày thì rất gấp.</p>
<div class="toolbar"><input id="tim-no" type="search" placeholder="Tìm khách hàng, mã công nợ…" oninput="locNo()">
<button class="nut chon" data-muc="tat-ca">Tất cả</button>
<button class="nut" data-muc="rat-gap">Rất gấp</button>
<button class="nut" data-muc="gap">Gấp</button>
<button class="nut" data-muc="nhac">Nhắc</button></div>
{bang_no}</section>
</main>
<footer>Dashboard tự sinh bởi <code>python main.py</code> — dữ liệu giả lập - thông tin khách hàng đều được bảo mật.</footer>
<script>{js}</script>
</body></html>"""
    p = OUT_DIR / "dashboard.html"
    p.write_text(noi_dung, encoding="utf-8")
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
        f"# Tom tat bao cao — {ngay.isoformat()} (dữ liệu giả lập - thông tin khách hàng đều được bảo mật)\n\n"
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
