# Demo: Tự động báo cáo bán hàng + nhắc nợ

> dữ liệu giả lập - thông tin khách hàng đều được bảo mật. Không dùng code,
> dữ liệu hay ảnh chụp của bất kỳ công ty hay khách hàng thật nào.

Repo này là portfolio của Louis (Python dev) — minh họa đúng việc anh làm
cho khách doanh nghiệp vừa và nhỏ: thay vì mỗi sáng kế toán mở file Excel,
cộng tay và gửi mail nhắc nợ bằng tay, hệ thống chạy 1 lệnh là ra đủ bộ.

## Chạy thử trong 2 phút

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py   # tạo dữ liệu giả (60 đơn, 12 khoản công nợ)
python main.py                           # chạy báo cáo ngày 2026-11-11
python -m unittest discover -s tests -v  # chạy test
```

Chạy lại lần 2 trong cùng ngày để xem chống trùng:

```bash
python main.py   # lần 2: không tạo trùng nháp email, chỉ ghi log "da_tao_nhap"
```

## Nó làm được gì

Input là 1 file Excel `data/sample_sales.xlsx` với 2 sheet:

- `DonHang` — 60 đơn hàng tháng 11/2026 (sản phẩm, số lượng, đơn giá, khu vực, nhân viên)
- `CongNo` — 12 khoản công nợ, có hạn thanh toán và trạng thái đã / chưa thanh toán

Chạy `python main.py` sẽ ra:

| Output | Nội dung |
|---|---|
| `output/bao-cao-2026-11-11.xlsx` | 4 sheet: TongHop, TheoSanPham, TheoKhuVuc, NhacNo |
| `output/tom-tat.md` | Tóm tắt doanh thu + nợ quá hạn để đọc nhanh |
| `output/dashboard.html` | Dashboard 1 file duy nhất (CSS + JS nhúng sẵn, không cần mạng): thẻ KPI, biểu đồ thanh theo sản phẩm / khu vực, bảng bấm tiêu đề để sắp xếp, ô tìm kiếm + nút lọc nhắc nợ theo mức độ (Nhắc / Gấp / Rất gấp). Mở bằng trình duyệt là xem được, chụp màn hình gửi khách được ngay |
| `output/emails/NN-*.txt` | Nháp mail nhắc nợ cho từng khách quá hạn — **chỉ là file nháp, không gửi mail thật** |
| `output/sent_log.csv` | Nhật ký chống gửi trùng: cùng ngày, cùng khách chỉ tạo nháp 1 lần |

Ví dụ kết quả với dữ liệu mẫu (đã chạy thật): 60 đơn, doanh thu
185.470.000 VND, 6 khoản nợ quá hạn, tổng 73.450.000 VND,
6 nháp email nhắc nợ.

## Kỹ năng minh họa

- Python + pandas + openpyxl: đọc / tổng hợp / xuất Excel
- Logic nghiệp vụ thật: tổng hợp theo sản phẩm, khu vực; xác định nợ quá hạn theo ngày; gom nhắc nợ theo từng khách
- Chống gửi trùng bằng nhật ký `sent_log.csv` (cùng ý tưởng với cổng chống gửi trùng trong hệ thống thật, viết lại từ đầu cho demo)
- Lỗi rõ ràng thay vì im lặng: thiếu file dữ liệu thì báo lỗi và hướng dẫn chạy lệnh tạo dữ liệu; bật `--gui-that` mà chưa cấu hình SMTP thì báo lỗi, không gửi lén
- Test bằng `unittest` chuẩn của Python, không cần cài thêm gì

## Dịch vụ liên quan

Demo này tương ứng với 3 gói dịch vụ automation của Louis:

1. **Báo cáo tự động mỗi sáng** — 5–10tr / dự án
2. **Nhắc nợ tự động** (gói 1 + gửi mail nhắc nợ đúng giờ) — 5–12tr / dự án
3. **Dashboard nội bộ** (gói 2 + dashboard + đồng bộ dữ liệu) — 10–20tr / dự án

Quy trình: trao đổi 30 phút → báo giá → chạy thử 3–5 sáng trên môi trường test của khách → bàn giao. Không nhận job trùng với dữ liệu hay hệ thống của công ty anh đang làm, và không dùng dữ liệu thật của khách cũ cho khách mới.

## Đẩy lên GitHub (dành cho Louis)

```bash
cd automation-demo
git init
git add .
git commit -m "feat: demo bao cao ban hang + nhac no (du lieu gia)"
git branch -M main
git remote add origin https://github.com/thanhlongts2k/sales-report-automation-demo.git
git push -u origin main
```

(Tạo repo `sales-report-automation-demo` trên GitHub trước, để ở chế độ Public để khách xem được.)

---

## English summary

A clean, self-contained Python demo: read a fake sales Excel file, produce a
summary report (by product, by region), find overdue receivables, and draft
per-customer reminder emails as text files (never sends real mail). Includes a
same-day duplicate guard via `sent_log.csv` and unit tests. All names and
amounts are invented sample data.
