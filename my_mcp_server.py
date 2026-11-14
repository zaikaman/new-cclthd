"""Server MCP cho bài thực hành số 12 với dữ liệu minh họa."""

from mcp.server.mcpserver import MCPServer
from pydantic import StrictFloat, StrictInt

GRADUATION_STANDARDS_URI = "academic://graduation/standards"

server = MCPServer(name="my_academic_server", version="1.0.0")


@server.tool(name="calculate_tuition", description="Tính học phí tạm tính")
def calculate_tuition(
    credits: StrictInt, fee_per_credit: StrictInt = 520_000
) -> dict[str, int | str | bool]:
    if credits <= 0 or fee_per_credit <= 0:
        return {"hop_le": False, "thong_bao": "Giá trị phải lớn hơn 0."}

    total = credits * fee_per_credit
    formatted_total = f"{total:,}".replace(",", ".")
    return {
        "hop_le": True,
        "so_tin_chi": credits,
        "don_gia": fee_per_credit,
        "tong_hoc_phi": total,
        "dinh_dang": f"{formatted_total} VNĐ",
    }


@server.resource(uri=GRADUATION_STANDARDS_URI, name="Chuẩn tốt nghiệp", mime_type="text/plain")
def get_graduation_standards() -> str:
    return (
        "Dữ liệu minh họa: tối thiểu 152 tín chỉ; GPA từ 2.00; "
        "đạt ngoại ngữ VSTEP Bậc 3 hoặc tương đương; "
        "hoàn thành giáo dục thể chất và quốc phòng - an ninh."
    )


@server.prompt(name="exam_guide", description="Lập kế hoạch ôn thi")
def exam_guide(subject: str | None = None) -> str:
    prompt = (
        "Hỏi danh sách môn thi, số ngày còn lại và thời gian mỗi ngày; "
        "lập bảng ôn tập theo ưu tiên, có mốc kiểm tra."
    )
    if subject:
        prompt += f" Ưu tiên môn: {subject}."
    return prompt


@server.tool(name="check_academic_warning", description="Kiểm tra cảnh báo học vụ")
def check_academic_warning(gpa: StrictFloat, failed_credits: StrictInt) -> dict[str, bool | str]:
    if not 0 <= gpa <= 4 or failed_credits < 0:
        return {"hop_le": False, "thong_bao": "Dữ liệu không hợp lệ."}

    return {"hop_le": True, "canh_bao": gpa < 1.2 or failed_credits > 20}


@server.prompt(name="plan_weekly_routine")
def plan_weekly_routine(target_hours_per_day: str | None = None) -> str:
    prompt = (
        "Hỏi các môn học, hạn nộp bài và thời gian rảnh trong tuần; "
        "lập lịch theo ngày, cân bằng học và nghỉ."
    )
    if target_hours_per_day:
        prompt += f" Mục tiêu: {target_hours_per_day} giờ/ngày."
    return prompt + " Bạn muốn điều chỉnh phần nào của kế hoạch?"
