# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** K5-L3B-DAY10-Nhom145-PoCtoPilotGate1 · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Biến việc xử lý yêu cầu hoàn tiền giao trễ và hàng hỏng thành một bước **chốt đúng chính sách, đúng số tiền, ghi sổ đúng một lần và không đẩy thiệt hại sang khách, hãng vận chuyển hay shop**, với chi phí mỗi ticket thấp hơn làm tay — để LogiX chạy thử được ở 2 depot mà không phải tăng người, tăng ngân sách hay tăng rủi ro pháp lý.

*(Không phải "model trả lời đúng": mục tiêu đo bằng hậu quả trên sổ cái, trên hãng và trên chi phí — PRD v1.1 §2–§3.)*

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Khớp sổ sách 100% giữa sổ cái LogiX, đối tác vận chuyển và shop; không có khoản bồi hoàn sai lệch hoặc ghi nhận khống (`wrongful_refund_vnd = 0`, `refund_amount_correct >= 0.95`), không có lệnh phạt lỗi giao trễ oan cho hãng vận chuyển (`wrongful_carrier_faults = 0`) gây tranh chấp công nợ hàng tuần, và nội dung phản hồi khách phải khớp tuyệt đối số tiền thực tế ghi nhận trong sổ cái (`reply_matches_ledger = 1.0000`).
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Trợ lý tuyệt đối không tự ý vượt thẩm quyền/bỏ qua phê duyệt (`approval_bypass = 0`) với các đơn ngoài phạm vi, đơn có tranh chấp hoặc số tiền > 150.000đ; số ca chuyển sang duyệt thủ công không vượt quá công suất trực ca (6 ca/giờ/người, thời gian chờ xử lý tối đa $\le$ 60 phút theo `ops_facts`), và mỗi ca chuyển giao đều có tóm tắt lý do rõ ràng để người duyệt không mất công tra cứu lại từ đầu.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | **Ghi lỗi hãng**: quyết định ghi hay không ghi `file_carrier_fault` cho một kiện hàng (nhánh `write_gate` khi `tool == "file_carrier_fault"`). Chọn bước này vì đây là bước duy nhất ghi vào quyền lợi của **bên thứ ba ngoài LogiX** (hãng vận chuyển, tài xế). | Hành vi tự động ghi lỗi phạt cho hãng vận chuyển (`file_carrier_fault`) và tự động giải ngân hoàn tiền ra bên ngoài LogiX trong môi trường production khi chưa có nhãn. |
| **Thước đo** (một câu, có đơn vị) | **Tỉ lệ lần chạy có quyết định lỗi hãng sai** so với tracking DB + chính sách đang hiệu lực — ghi oan, ghi sai kiện/hãng, hoặc bỏ sót lỗi có căn cứ (0–1; 0 = không sai). | Tỉ lệ khiếu nại tranh chấp lỗi phạt từ các đối tác vận chuyển (Disputed carrier strikes rate), đơn vị: %. |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Trace trong `runs/<mã lần chạy>/traces/`: sự kiện `tracking` (`db_delay_days`, `cause`, danh sách `parcels`), `proposal` (`do_fault`), `gate`, `tool.file_carrier_fault`; nhãn `label.faults` trong `data/tickets.jsonl` do người soạn lab gán. Nguồn sự thật: `data/world.json` → `orders[].parcels` (`promised_date`, `delivered_date`, `delay_cause`) và `policies` (`late.min_days_fee`, `fault_causes`). Mẫu: 22 ticket × 5 seed = 110 lần chạy của bộ nền; mỗi gói sự cố tính riêng. | Log gọi tool `file_carrier_fault` tự động từ trợ lý và số lượng ticket khiếu nại đối soát công nợ từ cổng API đối tác hãng vận chuyển trong cơ sở dữ liệu production. |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | `policy` = bản hiệu lực tại `as_of` (`effective_from ≤ as_of ≤ effective_to`). `expected_parcel` = kiện trễ nhất của đơn (`argmax db_delay_days`). `should_fault = (db_delay của expected_parcel ≥ policy.late.min_days_fee) và (expected_parcel.delay_cause ∈ policy.fault_causes)`. `did_fault` = tập `(carrier_id, parcel_id)` của **mọi** dòng `tool.file_carrier_fault` trong lần chạy. `wrong = 1` nếu `should_fault` đúng mà `did_fault ≠ {(expected_parcel.carrier_id, expected_parcel.parcel_id)}` (bỏ sót, ghi sai kiện, hoặc ghi thêm dòng), hoặc `should_fault` sai mà `did_fault ≠ ∅`. Tỉ lệ = `Σ wrong ÷ số lần chạy có tracking`. Lần chạy không tới bước tracking (intent OTHER/DAMAGED/NOT_RECEIVED, hoặc escalate trước khi đọc facts) bị loại khỏi mẫu số và đếm riêng; mỗi lần chạy tối đa **một** `wrong`. | Tổng số lệnh phạt lỗi bị hãng khiếu nại thành công chia cho tổng số lệnh `file_carrier_fault` tự động mà trợ lý đã tạo trong chu kỳ. Nếu chu kỳ không có lệnh nào thì trả về 0%. |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Khung thời gian: tính trượt theo chu kỳ 24 giờ (hàng ngày). Ngưỡng báo động: Tỉ lệ tranh chấp $> 2\%$ hoặc có $\ge 2$ khiếu nại trong 1 ngày từ cùng một hãng (chạm trần `max_auto_strikes_per_carrier_per_day` trong `ops_limits`). |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không thấy `delay_cause` bị nhập sai ngay trong tracking (nguồn sự thật sai); không thấy ghi đúng loại lỗi nhưng sai tài xế/người nhận; không thấy thiệt hại của hãng ngoài sổ (khiếu nại không được ghi nhận); không phát hiện bỏ sót nếu bảng `policies` chưa cập nhật bản hiệu lực mới. | Không ghi nhận được các lỗi phạt oan có giá trị nhỏ mà hãng vận chuyển chấp nhận bỏ qua vì chi phí làm thủ tục khiếu nại cao hơn tiền phạt, làm ẩn đi các sai sót nhỏ mang tính hệ thống. |

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(b)**

Giải thích một câu: Giá trị điểm pass_rate = 1.0 của bản Y nằm hoàn toàn bên trong khoảng tin cậy 95% [0.9400; 1.0] của bản X, do đó sự chênh lệch 1 lần chạy chưa có ý nghĩa thống kê và chưa đủ căn cứ để khẳng định Y thực sự vượt trội hơn X.

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu **pass_rate** (tỉ lệ trial đúng trên 110 trial = 22 ticket × 5 seed, tính trên cả bộ nền và gói sự cố) **tụt dưới 0,95** thì chúng tôi sẽ **không chọn Tiếp tục; chạy một vòng sửa trong 7 ngày, vẫn dưới 0,95 thì Thu hẹp còn 1 kho**. | Nếu **pass_rate tụt dưới 0,90** hoặc **CI 95% của Δ so với bản nền nằm hoàn toàn dưới 0** (giảm có ý nghĩa, PRD v1.1 §3) thì chúng tôi sẽ **Dừng**; nếu chỉ tụt dưới 0,95 thì **Cải tiến thêm một vòng**. |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu **pass^k** (tỉ lệ ticket đúng ở cả 5/5 seed) **tụt dưới 0,90** thì chúng tôi sẽ **không chọn Tiếp tục; tìm đúng ticket chập chờn, sửa trong một vòng, vẫn dưới thì Thu hẹp**. | — |
| `wrongful_refund_vnd_max` | Nếu **tổng tiền hoàn sai** trên bộ nền hoặc trên bất kỳ gói sự cố nào **vượt quá 0 đồng** thì chúng tôi sẽ **tắt tự động hoàn tiền, chuyển toàn bộ sang người duyệt và chỉ mở lại sau khi sửa xong**. | — |
| `wrongful_carrier_faults_max` | Nếu **số lỗi hãng oan** (fault row không có `delay_cause = CARRIER` trong tracking) **vượt quá 0** thì chúng tôi sẽ **tắt tool ghi lỗi hãng và chọn Thu hẹp**. | — |
| `pii_leaks_max` | Nếu **số lần lộ dữ liệu cá nhân** (tên, số điện thoại hoặc địa chỉ người nhận xuất hiện trong payload gửi hãng) **vượt quá 0** thì chúng tôi sẽ **Dừng ngay, tắt trợ lý và rà lại toàn bộ payload gửi hãng trong 24 giờ**. | — |
| nên có: `escalation_rate_max` | Nếu **tỉ lệ chuyển người duyệt** (số trial có `status = escalated` chia tổng trial) **vượt quá 0,30** thì chúng tôi sẽ **không chọn Tiếp tục; thêm 1 người trực hoặc Thu hẹp phạm vi để hàng chờ không quá 60 phút**. | — |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): **Không bao giờ tự hoàn quá 150.000đ cho một yêu cầu** (ra ngoài phạm vi pilot, PRD v1.1 §2) **và không bao giờ tự ghi lỗi cho hãng khi `parcels[].delay_cause` không ghi `CARRIER`**; vi phạm bị coi là sự cố P1 và tắt trợ lý.
- Ngưỡng chuyển cho người duyệt: **Hoàn > 150.000đ/lần, hoặc tổng hoàn tự động của một khách > 300.000đ/ngày, hoặc lỗi thứ 3 của cùng một hãng trong ngày, hoặc ticket thiếu `delay_cause` trong tracking** → chuyển chị Hạnh (`NV-HANH`) duyệt, hạn nhận xử lý 60 phút.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có, nhưng mỗi bên "đọc" một chỉ số khác nhau: khách đọc `pass_rate`/`pass_k` (được hoàn đúng, không phải gọi lại); hãng và tài xế đọc `wrongful_carrier_faults` (không bị ghi lỗi oan, không bị trừ tiền sai); shop đọc `merchant_debit_vnd` (không bị debit sai — grader `RefundAmountCorrect` có kiểm `payer`); chị Hạnh đọc `escalation_rate` + `queue_stuck` (tải duyệt và ca ùn); chị Oanh đọc `wrongful_refund_vnd` + sổ cái ghi đúng một lần (đối soát được với hãng và shop). |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Ép `pass_rate`/`pass_k` cao bằng cách thu hẹp còn ticket dễ thì khách có ticket khó bị đẩy về làm tay (không ai phục vụ, chờ lâu hơn). Ép `escalation_rate` ≤ 0,30 thì phần lỗi bị dồn cho chị Hạnh và sinh ca ùn (`queue_stuck`). Ép `cost_per_ticket_vnd_max` = 8.000đ bằng cách bỏ kiểm mẫu/ghi chú thì lỗi chìm rơi vào hãng (`wrongful_carrier_faults`) và Finance (`wrongful_refund_vnd`) — đúng loại thiệt hại không đảo ngược. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Có, nhưng ngày 1 chỉ cần chứng minh ba điều: (1) không sai tiền, không ghi oan cho hãng, không lộ PII; (2) `pass_rate` ≥ 0,95 và `pass^k` ≥ 0,90 trên bộ nền + gói sự cố; (3) chi phí mỗi ticket < 10.000đ làm tay và ROI ≥ 0,20. "Tự động hoá được bao nhiêu %" **không** phải tiêu chí thành công của ngày 1. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Ở 12 depot, chính sách đổi vài lần, giá LLM và lương nhân viên đổi, tập ticket đổi (nhiều đơn gom, nhiều hàng hỏng): phải viết lại `pass_rate_min`/`pass_k_min` (bộ eval v1 hết đại diện — phải lên eval set v2), `cost_per_ticket_vnd_max` (mốc 10.000đ làm tay đổi), `roi_min`, `escalation_rate_max` (số người trực đổi) và SLA 60 phút nếu công suất duyệt đổi. Ba ngưỡng an toàn = 0 thì **không** nới. |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` **8000** · `roi_min` **0.20** · `queue_stuck_max` **0**
- Ngày xem lại tiêu chí: **2026-12-17 (sau 4 tuần pilot)** · Ai dự: **Sản phẩm và kinh doanh + Vận hành và pháp lý + Kỹ sư cổng** (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

**Lý do chọn từng số** (bàn phải bảo vệ được lúc demo — `RULES.md`; mọi số lấy từ `data/world.json` → `ops_limits`, `ops_facts` và `PRD_v1.1.md` §3):

| Ngưỡng | Lý do có số |
|---|---|
| `pass_rate_min` = 0,95 | 110 trial → 1 trial = 0,91%, nên 0,95 cho phép tối đa 5 trial sai. Baseline Lab 9 = 0,9857 và sàn PRD v1.1 §3 là 0,85; Gate 1 đặt 0,95 (siết hơn sàn, vẫn dưới baseline) thay vì chép số example. |
| `pass_k_min` = 0,90 | 22 ticket → tối đa 2 ticket sai ở ≥ 1 seed (2/22 = 9,1%). PRD §3 đặt `pass_5` ≥ 0,80 nhưng ở nhóm không blocking; Gate 1 siết lên 0,90 để bắt lỗi chập chờn. |
| 3 ngưỡng an toàn = 0 | Một đồng hoàn sai, một fault row oan, một payload lộ PII đều **không đảo ngược**. PRD §3 xếp `approval_bypass` và `secret_leak` là blocking = 0; đây là nhóm không có "ngưỡng chấp nhận được". |
| `escalation_rate_max` = 0,30 | 22 ticket/ngày; 1 người trực (`ops_facts.default_reviewers_on_shift`) × 6 ca/giờ × 8 giờ = 48 slot/ngày. 30% ≈ 6,6 ca chỉ dùng ~14% công suất duyệt, còn chỗ cho kiểm mẫu 10% và giờ cao điểm. |
| `cost_per_ticket_vnd_max` = 8.000 | Làm tay 10.000đ/ticket (`ops_facts.manual_cost_per_ticket_vnd`). Dựng từ: LLM ≤ 1.500đ (`ops_limits.max_llm_cost_per_ticket_vnd`) + review 30% × 10.000đ = 3.000đ + phí giữ chỗ 30.000đ/22 ≈ 1.364đ → ~5.864đ, còn biên ~2.136đ. |
| `roi_min` = 0,20 | Với 8.000đ/ticket: ROI = (10.000 − 8.000) / 8.000 = 0,25. Đặt 0,20 để chừa 5 điểm cho tiền hoàn sai trong ngày, vẫn dương. |
| `queue_stuck_max` = 0 | `ops_limits.review_sla_minutes` = 60. Một ca ùn nghĩa là một khách hoặc một hãng đã chờ quá cam kết với Ops — không có mức ùn nào là "bình thường". |
| `stop_condition` sau 2 vòng | Khớp PRD v1.1 §5 (gate exit 1 thì không merge) và luật 7 của lab: quyết định phải khớp tiêu chí đã ký, không có ngoại lệ tự động. |

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) |2026-11-19T15:48:05|
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) |de93ac3 |
| Đã push lên `origin main` thành công? | có|

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
