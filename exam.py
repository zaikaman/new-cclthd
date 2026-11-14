"""Chạy các ca kiểm chứng của Phần A và Phần B bằng MCP Python SDK."""

import asyncio
import json
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError
from mcp.types import CallToolResult, GetPromptResult, InputRequiredResult, TextContent

from my_mcp_server import GRADUATION_STANDARDS_URI, server


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    try:
        result = await server.call_tool(name, arguments)
    except UnexpectedToolError:
        raise
    except ToolError:
        return "ToolError (invalid params)"

    assert isinstance(result, CallToolResult)
    assert isinstance(result.content[0], TextContent)
    return json.dumps(json.loads(result.content[0].text), ensure_ascii=False)


async def get_prompt_text(name: str, arguments: dict[str, str]) -> str:
    result = await server.get_prompt(name, arguments)
    assert isinstance(result, GetPromptResult)
    message = result.messages[0].content
    assert isinstance(message, TextContent)
    return message.text


async def main() -> None:
    print("Phần A")
    print("Học phí 3 tín chỉ:", await call_tool("calculate_tuition", {"credits": 3}))
    print("Học phí 0 tín chỉ:", await call_tool("calculate_tuition", {"credits": 0}))
    print(
        "Học phí 17 tín chỉ, đơn giá 600.000:",
        await call_tool("calculate_tuition", {"credits": 17, "fee_per_credit": 600_000}),
    )
    print("Số tín chỉ là chữ:", await call_tool("calculate_tuition", {"credits": "ba"}))

    resources = await server.read_resource(GRADUATION_STANDARDS_URI)
    assert not isinstance(resources, InputRequiredResult)
    resource = next(iter(resources))
    print("Resource:", resource.mime_type, "|", resource.content)

    for arguments in ({"subject": "Cấu trúc dữ liệu"}, {}):
        print("exam_guide", arguments, "->", await get_prompt_text("exam_guide", arguments))

    for gpa, failed_credits in ((1.0, 10), (2.8, 0), (1.2, 20), (2.8, 21), (-1, 0)):
        result = await call_tool(
            "check_academic_warning", {"gpa": gpa, "failed_credits": failed_credits}
        )
        print(f"Cảnh báo GPA={gpa}, nợ={failed_credits}:", result)

    print("\nPhần B")
    for arguments in ({}, {"target_hours_per_day": "3"}):
        print(
            "plan_weekly_routine",
            arguments,
            "->",
            await get_prompt_text("plan_weekly_routine", arguments),
        )


if __name__ == "__main__":
    asyncio.run(main())
