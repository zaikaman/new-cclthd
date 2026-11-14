"""Script kiểm thử my_academic_server MCP - gọi trực tiếp qua managers."""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(__file__))

from my_mcp_server import server
from pydantic import ValidationError

tm = server._tool_manager
pm = server._prompt_manager
rm = server._resource_manager


async def call_tool(name, kwargs):
    tool = tm._tools.get(name)
    if not tool:
        return ("ERROR", f"Tool '{name}' not found")
    try:
        result = await tool.run(kwargs, {})
        return ("OK", result)
    except (ValidationError, TypeError) as e:
        return ("VALIDATION_ERROR", f"{type(e).__name__}: {e}")
    except Exception as e:
        return ("ERROR", f"{type(e).__name__}: {e}")


def get_resource_data(uri):
    for key, r in rm._resources.items():
        if str(key) == uri or (hasattr(r, 'uri') and str(r.uri) == uri):
            return r
    # fallback: iterate by string match
    for key in rm._resources:
        if uri in str(key):
            return rm._resources[key]
    return None


def call_prompt(name, kwargs=None):
    kwargs = kwargs or {}
    prompt_obj = pm._prompts.get(name)
    if not prompt_obj:
        return ("ERROR", f"Prompt '{name}' not found")
    try:
        result = prompt_obj.fn(**kwargs)
        return ("OK", result)
    except Exception as e:
        return ("ERROR", f"{type(e).__name__}: {e}")


async def main():
    sep = "=" * 60

    # =====================================================
    print(sep)
    print("=== TASK 1: tool calculate_tuition ===")
    print(sep)

    cases_tuition = [
        {"credits": 3},
        {"credits": 0},
        {"credits": 17, "fee_per_credit": 600000},
        {"credits": "ba"},
    ]
    labels = ["a", "b", "c", "d"]
    for lbl, c in zip(labels, cases_tuition):
        status, result = await call_tool("calculate_tuition", c)
        print(f"  1{lbl}. Input : {c}")
        print(f"      [{status}] {result}")
        print()

    # =====================================================
    print(sep)
    print("=== TASK 2: resource academic://graduation/standards ===")
    print(sep)

    uri = "academic://graduation/standards"
    r = get_resource_data(uri)
    if r is not None:
        content = r.fn()
        mime = getattr(r, 'mime_type', 'N/A')
        print(f"  MIME type : {mime}")
        print(f"  Nội dung  : {content}")
    else:
        # Try via read_resource
        try:
            from mcp.types import AnyUrl
            result = await server.read_resource(AnyUrl(uri))
            print(f"  read_resource result: {result}")
        except Exception as e:
            print(f"  KHÔNG TÌM THẤY resource '{uri}': {type(e).__name__}: {e}")
    print()

    # =====================================================
    print(sep)
    print("=== TASK 3: prompt exam_guide ===")
    print(sep)

    s1, r1 = call_prompt("exam_guide", {})
    print("  Lần 1 — Input: {}")
    print(f"  [{s1}] {r1}")
    print()

    s2, r2 = call_prompt("exam_guide", {"subject": "Cấu trúc dữ liệu"})
    print('  Lần 2 — Input: {"subject": "Cấu trúc dữ liệu"}')
    print(f"  [{s2}] {r2}")
    print()

    # =====================================================
    print(sep)
    print("=== TASK 4: tool check_academic_warning ===")
    print(sep)

    cases_warning = [
        {"gpa": 1.0, "failed_credits": 10},
        {"gpa": 2.8, "failed_credits": 0},
        {"gpa": 1.2, "failed_credits": 20},
        {"gpa": 2.8, "failed_credits": 21},
        {"gpa": -1,  "failed_credits": 0},
    ]
    for i, c in enumerate(cases_warning, 1):
        status, result = await call_tool("check_academic_warning", c)
        print(f"  4-{i}. Input : {c}")
        print(f"       [{status}] {result}")
        print()

    # =====================================================
    print(sep)
    print("=== TASK 5: prompt plan_weekly_routine ===")
    print(sep)

    sa, ra = call_prompt("plan_weekly_routine", {})
    print("  Lần 1 — Input: {}")
    print(f"  [{sa}] {ra}")
    print()

    sb, rb = call_prompt("plan_weekly_routine", {"target_hours_per_day": "3"})
    print('  Lần 2 — Input: {"target_hours_per_day": "3"}')
    print(f"  [{sb}] {rb}")
    print()

    # Kiểm tra điều kiện
    print(sep)
    print("=== TASK 5: KIỂM TRA ĐIỀU KIỆN ===")
    print(sep)
    cond1 = "Mục tiêu: 3 giờ/ngày." in str(rb)
    cond2 = "Mục tiêu: 3 giờ/ngày." not in str(ra)
    cond3 = str(ra).endswith("Bạn muốn điều chỉnh phần nào của kế hoạch?")
    cond4 = str(rb).endswith("Bạn muốn điều chỉnh phần nào của kế hoạch?")
    print(f"  ✔ Lần 2 chứa 'Mục tiêu: 3 giờ/ngày.'          : {'PASS ✅' if cond1 else 'FAIL ❌'}")
    print(f"  ✔ Lần 1 KHÔNG chứa 'Mục tiêu: 3 giờ/ngày.'    : {'PASS ✅' if cond2 else 'FAIL ❌'}")
    print(f"  ✔ Lần 1 kết thúc bằng câu hỏi điều chỉnh       : {'PASS ✅' if cond3 else 'FAIL ❌'}")
    print(f"  ✔ Lần 2 kết thúc bằng câu hỏi điều chỉnh       : {'PASS ✅' if cond4 else 'FAIL ❌'}")

    overall = all([cond1, cond2, cond3, cond4])
    print()
    print(f"  Kết quả tổng thể Task 5: {'ALL PASS ✅' if overall else 'CÓ LỖI ❌'}")
    print()
    print("=== HOÀN TẤT KIỂM THỬ ===")


asyncio.run(main())
