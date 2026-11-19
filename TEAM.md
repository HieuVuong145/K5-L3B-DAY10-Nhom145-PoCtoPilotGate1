# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): Nhom145
- Lớp: `L3B`
- Repo của bàn: `https://github.com/HieuVuong145/K5-L3B-DAY10-Nhom145-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S8

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; thêm dòng nếu cần. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 |     Vương Toàn Minh Hiếu      |   2A202603853   |   Kỹ sư cổng  |       X      |
|   2 |      Vũ Quang Thanh     |   2A202603736   |  Kỹ sư cổng   |             |
|   3 |      Nguyễn Đình Trường     |   2A202603837   |   Sản phẩm và kinh doanh  |             |
|   4 |      Nguyễn Mạnh Cường     |   2A202603904   |   Vận hành và pháp lý  |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## VuongToanMinhHieu-2A202603853

### Phần việc phụ trách
Trưởng nhóm · Kỹ sư cổng: Phụ trách thiết kế và lập trình các chốt chặn an toàn trong `lab10/guards.py` (Vòng 1 và Vòng 2), chỉ số theo dõi trong `lab10/monitors.py`, thực hiện chốt cổng checkpoint và chạy kiểm tra bài nộp `lab10.check_submission`.

### Đóng góp cụ thể
- Lập trình hàm `_refund_gate` chống ghi trùng, ghim chính sách DB, và xác thực 6 điều kiện hiệu lực của `approval` cho sự cố S8.
- Xây dựng 2 metric theo dõi `cskh_recheck_rate` và `invalid_approval_rate` trong `lab10/monitors.py`.
- Đồng bộ hệ thống kiểm tra và xác nhận đạt chuẩn 38/38 mục nộp bài.

### Bằng chứng
Mã commit: `de93ac3`, `4f3fd42`, `76ccbba`; mã lần chạy: `R-S8-after-20261119-192737-bd7417`, `R-S8-grade-20261119-192736-bd7417`.

### Exit ticket
- **Một điều học được:** AI agent trong doanh nghiệp bắt buộc phải có Gate chặn trước lệnh ghi nhạy cảm để xác thực quyền hạn và tính toàn vẹn dữ liệu, không thể thả lỏng cho model tự quyết định.
- **Một điều còn chưa chắc:** Cơ chế bảo đảm tính toàn vẹn khi hệ thống gặp lỗi gián đoạn mạng hoặc retry bất đồng bộ từ phía LLM.

## VuQuangThanh-2A202603736

### Phần việc phụ trách


### Đóng góp cụ thể


### Bằng chứng


### Exit ticket


## NguyenDinhTruong-2A202603837


### Đóng góp cụ thể

### Bằng chứng


### Exit ticket


## NguyenManhCuong-2A202603904


### Đóng góp cụ thể


### Bằng chứng

