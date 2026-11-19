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

Kỹ sư cổng (vòng 1): thiết kế và viết **3 cổng phòng ngừa** trong `lab10/guards.py` (`pre_guard`, `write_gate`); điền **câu 1.3** (Phiếu A mục A2, cột "Offline"), **câu 2.2** (Phiếu B mục B2), **câu 2.6** (Phiếu B mục B7.1) và **câu 2.7** (Phiếu B mục B7.2).
Không phụ trách `lab10/monitors.py` — phần chỉ số theo dõi do thành viên cùng vai đảm nhiệm; không nhận phần xác thực `approval` cho thẻ S8 (phần vòng 2 của trưởng nhóm).

### Đóng góp cụ thể

- **Câu 1.3 — offline metric cho bước "ghi lỗi hãng" (Phiếu A · A2, cột Offline):** chọn bước duy nhất ghi vào quyền lợi của bên thứ ba ngoài LogiX; định nghĩa thước đo "tỉ lệ lần chạy có quyết định lỗi hãng sai so với tracking DB + chính sách đang hiệu lực" với `expected_parcel` = kiện trễ nhất, `should_fault = (db_delay ≥ late.min_days_fee) và (delay_cause ∈ fault_causes)`, `did_fault` theo tập `(carrier_id, parcel_id)`; ghi rõ mẫu số (chỉ trial có `tracking`), cách xử lý ca thiếu dữ liệu và 4 điểm mù.
- **Câu 2.2 — bảng soát lỗi `T-002@55` (Phiếu B · B2):** dò trace và ghi **2 lỗi chìm**: (1) `model_override {db: 2, ticket: 5}` → `proposal/issue_refund 20.000đ` trái chính sách (trễ 2 < 3 ngày); (2) ghi lỗi hãng `VNX/O-1002-P1, delay_days: 5` trong khi tracking ghi 2 ngày → hãng và tài xế bị oan. Chỉ ra nguồn "đầu vào" (model đặt trọng số cho số khách tự khai), hướng xử lý bằng cổng code và dòng đối chứng `--stage after` (`SỔ CÁI []`, `LỖI HÃNG []`, `ĐẠT`).
- **Câu 2.6 — 3 cổng vòng 1 trong `lab10/guards.py` (Phiếu B · B7.1):** mọi cổng đọc nguồn sự thật DB, không xử lý theo mã ticket hay câu chữ:
  1. `_refund_gate` (`write_gate` / `issue_refund`): tính lại `H.entitlement_vnd(policy, order, db_delay, cause)` từ `parcels` + `policies`; lệch thì `modify`, quyền lợi = 0 thì `deny`; `deny` nếu `ledger_rows(order_id=...)` đã có dòng (chống ghi trùng, kể cả retry sau 429); dữ liệu trong ticket không được đổi `payer`.
  2. `_carrier_fault_gate` (`write_gate` / `file_carrier_fault`): chỉ cho ghi khi `H.carrier_at_fault(policy, parcel, db_delay)` (nguyên nhân ∈ `fault_causes` và đủ `late.min_days_fee`); `modify delay_days` ghi sang hãng về đúng tracking.
  3. `pre_guard`: ghim `policy_id = H.effective_policy(policies, ctx.as_of)` bằng `Verdict.allow(policy_id=...)`, không tin cờ `index_active` (drift `REFUND-v4` từ 2026-12-01).
  Kết quả: bộ nền 22 ticket × 5 seed từ **0.9909** (hỏng `T-002@55`: hoàn sai 20.000đ + 1 lỗi hãng oan) → **1.0**, **0 ca mới hỏng**, `unittest` 13/13 OK; `lab10.gate` **exit 0**, 9/9 ngưỡng đã ký đạt.
- **Câu 2.7 — 2 bước tránh rò rỉ dữ liệu (Phiếu B · B7.2):** (1) tách bộ chỉnh khỏi bộ chấm — chỉ chỉnh trên 22 ticket bộ nền + ticket `--adhoc` tự viết, không dùng `incidents/Sx/` hay test ẩn, luật viết dạng tổng quát theo DB; (2) đóng băng `prepared` bằng `lab10.checkpoint`, review chéo bởi người không viết code và chạy lại regression trên bộ nền; vòng 2 chỉ **thêm** cổng vào file gốc, không sửa `guards_round1.py` / `operating_gates.round1.json` / `round1.lock`.

### Bằng chứng

- **Mã commit:** `6eef39e` (câu 1.3 — `templates/form-a-criteria.md`); `a42a5bb` (câu 2.2 — `templates/form-b-evaluation-gates.md` mục B2); `0b15792` (câu 2.6–2.7 + 121 dòng cổng vòng 1 trong `lab10/guards.py`); `4f3fd42` (chốt `prepared`/v1 — `lab10/guards_round1.py` giữ nguyên 3 cổng này, hash checkpoint `e5b78164`).
- **Mã lần chạy:** `R-base-before-20261119-160059-b45eeb` (baseline 110 trial: pass 0.9909, hoàn sai 20.000đ, 1 lỗi hãng oan) → `R-base-after-20261119-165729-afa3ca` (65 trial trong phạm vi HN+HCM: pass 1.0, hoàn sai 0đ, 0 lỗi hãng oan, 0 PII, escalation 0.2308, cost 5.165đ/ticket, ROI 0.94) → `R-base-prepared-20261119-171435-ffe0e1` (pass 1.0, đóng băng `prepared`).
- **Trong phiếu:** Phiếu A mục A2 cột "Offline" (câu 1.3); Phiếu B mục B2 (đủ 3 phần); B7.1 (3 cổng, cột "ca đang đúng bị hỏng" = **không**); B7.2 (2 bước).
- **Kiểm chứng:** `python -m unittest discover -s tests` → `Ran 13 tests … OK`; `python -m lab10.gate --run runs/R-base-after-20261119-165729-afa3ca/report.json` → exit 0, in `tiêu chí hash dd15d588 · đã ký, còn nguyên`; trace `T-002@55` base → `SỔ CÁI 20.000đ`, `LỖI HÃNG VNX delay 5`, `HỎNG`; `--stage after` → `SỔ CÁI []`, `LỖI HÃNG []`, `ĐẠT`.

### Exit ticket

- **Một điều học được:** "đúng" phải kiểm trên **nguồn sự thật** chứ không theo bề mặt — model trả lời trôi chảy không thay được tracking DB, và file tiêu chí đã ký phải đúng **bytes** chứ không chỉ đúng nội dung (Windows CRLF làm hash lệch dù JSON không đổi, phải khôi phục đúng blob đã ký `dd15d588`).
- **Một điều còn chưa chắc:** khi LLM bị 429/retry hoặc `delay_cause` bị bỏ trống, liệu các cổng hiện tại có luôn phân biệt được "thiếu dữ liệu" với "dữ liệu xấu" để chọn `deny`/`escalate` đúng, và chi phí hàng chờ người duyệt có tăng quá mức khi siết các cổng này trong pilot thật hay không.

## NguyenDinhTruong-2A202603837


### Đóng góp cụ thể

### Bằng chứng


### Exit ticket


## NguyenManhCuong-2A202603904


### Đóng góp cụ thể


### Bằng chứng

