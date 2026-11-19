"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H
from .tools import Verdict

# ---------------------------------------------------------------------------
# CỔNG VÒNG 1 (mốc "prepared") — cả ba cổng đọc NGUỒN SỰ THẬT trong DB,
# không đọc câu chữ khách viết, không xử lý riêng theo mã ticket.
#
#   Cổng 1 · write_gate/issue_refund  — số tiền ghi sổ phải bằng quyền lợi tính
#            từ tracking + chính sách đang hiệu lực; đơn đã có dòng hoàn thì
#            không ghi thêm.  Ứng với HAZOP `amount_vnd` WRONG / lý do
#            pre-mortem "model tin số ngày khách tự khai" (ticket_trust).
#   Cổng 2 · write_gate/file_carrier_fault — chỉ ghi lỗi hãng khi tracking ghi
#            rõ nguyên nhân thuộc lỗi hãng và độ trễ đã đủ ngưỡng của chính
#            sách.  Ứng với HAZOP `file_carrier_fault` INVALID + lăng kính
#            pháp lý (bên thứ ba bị ghi lỗi oan).
#   Cổng 3 · pre_guard — ghim phiên bản chính sách đang hiệu lực theo ngày,
#            không tin cờ `index_active` của bảng chỉ mục.
#            Ứng với HAZOP `policy` INVALID (stale_clause / drift 2026-12-01).
# ---------------------------------------------------------------------------


def _effective_policy(ctx):
    """Chính sách đang hiệu lực tại ctx.as_of, theo khoảng [effective_from, effective_to]."""
    return H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)


def _parcel_of(order, parcel_id):
    """Kiện hàng mà lệnh ghi đang nói tới (khớp parcel_id), None nếu không thấy."""
    for p in (order or {}).get("parcels", []):
        if parcel_id and p.get("parcel_id") == parcel_id:
            return p
    return None


def pre_guard(ctx):
    # Cổng 3: ghim phiên bản chính sách. Agent mặc định đọc cờ `index_active`
    # của bảng chỉ mục; cờ này do batch đêm cập nhật nên có thể trễ so với
    # ngày hiệu lực (REFUND-v4 hiệu lực 2026-12-01). Không xác định được bản
    # hiệu lực thì dừng, chuyển người — thà chậm còn hơn áp sai chính sách.
    policy = _effective_policy(ctx)
    if policy is None:
        return Verdict.escalate("cổng chính sách: không xác định được phiên bản hiệu lực tại %s" % ctx.as_of)
    ctx.log("policy_pinned", policy_id=policy["policy_id"], as_of=ctx.as_of,
            index_active=bool(policy.get("index_active")))
    return Verdict.allow(policy_id=policy["policy_id"])


def _refund_gate(ctx, action):
    """Cổng 1: tiền ghi sổ = quyền lợi tính từ DB; không ghi trùng."""
    order_id = action.get("order_id")
    order = ctx.tools.lookup_order(order_id) if order_id else None
    if order is None or not order.get("parcels"):
        return Verdict.escalate("cổng hoàn tiền: không tra được đơn %s trong DB" % order_id)

    # (a) Chống ghi trùng: đơn đã có dòng hoàn (kể cả dòng cũ trước hôm nay)
    #     thì không ghi thêm. Bắt cả ca agent thử ghi lại sau khi LLM 429.
    if ctx.tools.ledger_rows(order_id=order_id):
        ctx.log("refund_duplicate_blocked", order_id=order_id)
        return Verdict.deny("cổng hoàn tiền: đơn %s đã có dòng hoàn trong sổ cái" % order_id)

    policy = _effective_policy(ctx)
    if policy is None:
        return Verdict.escalate("cổng hoàn tiền: không xác định được chính sách hiệu lực")

    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
    db_delay = H.db_delay_days(parcel, ctx.as_of)
    cause = parcel.get("delay_cause")
    entitled = H.entitlement_vnd(policy, order, db_delay, cause)
    asked = int(action.get("amount_vnd") or 0)

    # (c) Xác thực phê duyệt (Approval Verification - Vòng 2 cho S8)
    app_id = action.get("approval_id")
    if app_id:
        cands = ctx.tools.lookup_approvals(approval_id=app_id)
        if not cands:
            return Verdict.escalate("cổng hoàn tiền: phê duyệt %s không tồn tại trong hệ thống" % app_id)
        app = cands[0]
        if app.get("ticket_id") != ctx.ticket.get("ticket_id"):
            ctx.log("approval_wrong_ticket", approval_id=app_id, ticket_id=ctx.ticket.get("ticket_id"), app_ticket_id=app.get("ticket_id"))
            return Verdict.escalate("cổng hoàn tiền: phê duyệt %s cấp cho ticket %s, không hợp lệ cho ticket %s"
                                    % (app_id, app.get("ticket_id"), ctx.ticket.get("ticket_id")))
        if app.get("order_id") != order_id:
            return Verdict.escalate("cổng hoàn tiền: phê duyệt %s cấp cho đơn %s, không hợp lệ cho đơn %s"
                                    % (app_id, app.get("order_id"), order_id))
        if app.get("status") != "valid":
            return Verdict.escalate("cổng hoàn tiền: phê duyệt %s không còn hiệu lực (trạng thái: %s)"
                                    % (app_id, app.get("status")))
        if app.get("expires_at", "") < ctx.as_of:
            return Verdict.escalate("cổng hoàn tiền: phê duyệt %s đã hết hạn ngày %s (ngày xử lý: %s)"
                                    % (app_id, app.get("expires_at"), ctx.as_of))
        if asked > app.get("max_vnd", 0):
            return Verdict.escalate("cổng hoàn tiền: số tiền hoàn %dđ vượt hạn mức phê duyệt %dđ của %s"
                                    % (asked, app.get("max_vnd", 0), app_id))
        expected_approver = ctx.gates.get("operations", {}).get("approver_id")
        if expected_approver and app.get("approver_id") != expected_approver:
            return Verdict.escalate("cổng hoàn tiền: người duyệt %s không đúng thẩm quyền quy định (%s)"
                                    % (app.get("approver_id"), expected_approver))

    if asked == entitled:
        if entitled > policy["auto_limit_vnd"] and not app_id:
            return Verdict.escalate("cổng hoàn tiền: quyền lợi %dđ vượt hạn mức tự động %dđ, cần người duyệt"
                                    % (entitled, policy["auto_limit_vnd"]))
        return Verdict.allow()

    ctx.log("refund_clamped", order_id=order_id, asked_vnd=asked, entitled_vnd=entitled,
            db_delay_days=db_delay, cause=cause, policy_id=policy["policy_id"])

    if entitled <= 0:
        return Verdict.deny("cổng hoàn tiền: quyền lợi tính từ tracking DB = 0 "
                            "(trễ %d ngày, lý do %s)" % (db_delay, cause))
    if entitled > policy["auto_limit_vnd"] and not app_id:
        return Verdict.escalate("cổng hoàn tiền: quyền lợi %dđ vượt hạn mức tự động %dđ, cần người duyệt"
                                % (entitled, policy["auto_limit_vnd"]))

    changes = {"amount_vnd": entitled}
    # Dữ liệu (ticket/checkout note) không được ra lệnh đổi người trả tiền.
    if any(e.get("type") == "directive_obeyed" for e in ctx.events):
        changes["payer"] = "LOGIX"
    return Verdict.modify("cổng hoàn tiền: ghi đúng quyền lợi tính từ tracking DB (%dđ)" % entitled,
                          **changes)


def _carrier_fault_gate(ctx, action):
    """Cổng 2: chỉ ghi lỗi hãng khi có nguyên nhân trong tracking và đủ ngưỡng trễ."""
    order = ctx.tools.lookup_order(action.get("order_id"))
    parcel = _parcel_of(order, action.get("parcel_id"))
    if parcel is None:
        return Verdict.deny("cổng lỗi hãng: không tra được kiện %s trong tracking"
                            % action.get("parcel_id"))

    policy = _effective_policy(ctx)
    if policy is None:
        return Verdict.deny("cổng lỗi hãng: không xác định được chính sách hiệu lực")

    db_delay = H.db_delay_days(parcel, ctx.as_of)
    if not H.carrier_at_fault(policy, parcel, db_delay):
        ctx.log("carrier_fault_blocked", order_id=action.get("order_id"),
                parcel_id=parcel.get("parcel_id"), db_delay_days=db_delay,
                recorded_cause=parcel.get("delay_cause"), policy_id=policy["policy_id"])
        return Verdict.deny("cổng lỗi hãng: tracking ghi trễ %d ngày, nguyên nhân %r — "
                            "không thuộc lỗi hãng theo %s"
                            % (db_delay, parcel.get("delay_cause"), policy["policy_id"]))
    if int(action.get("delay_days") or 0) != db_delay:
        # Số ngày ghi sang hãng cũng là dữ liệu đối chất: lấy từ tracking, không lấy
        # từ con số khách tự khai (bên thứ ba không được chịu lỗi nặng hơn thực tế).
        ctx.log("carrier_fault_delay_corrected", order_id=action.get("order_id"),
                parcel_id=parcel.get("parcel_id"), asked_days=action.get("delay_days"),
                db_delay_days=db_delay)
        return Verdict.modify("cổng lỗi hãng: ghi độ trễ theo tracking DB (%d ngày)" % db_delay,
                              delay_days=db_delay)
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    if tool == "issue_refund":
        return _refund_gate(ctx, action)
    if tool == "file_carrier_fault":
        return _carrier_fault_gate(ctx, action)
    return Verdict.allow()
