# 2026.4.8 20:46
# by Mr.LiHuaRong

# agent运行过程中根据ai返回的信息选择调用对应的工具或者dox的内置命令

import io
import json
import re
from contextlib import redirect_stdout

TOOL_CALL_START = "<DOX_TOOL_CALL>"
TOOL_CALL_END = "</DOX_TOOL_CALL>"
CMD_CALL_START = "<DOX_CMD_CALL>"
CMD_CALL_END = "</DOX_CMD_CALL>"
SUPPORTED_TOOLS = {"ls", "ll"}


def get_tool_protocol_prompt() -> str:
    return (
        "当你需要调用 Dox 工具时，请严格使用如下格式输出，不要添加多余解释：\n"
        '<DOX_TOOL_CALL>{"tool":"ls","args":"-a"}</DOX_TOOL_CALL>\n'
        "可用 tool: ls, ll。args 可以为空字符串。"
    )


def extract_tool_call(ai_text: str) -> dict | None:
    if not ai_text:
        return None

    pattern = re.compile(
        re.escape(TOOL_CALL_START) + r"(.*?)" + re.escape(TOOL_CALL_END),
        re.DOTALL,
    )
    m = pattern.search(ai_text)
    if not m:
        return None

    payload = (m.group(1) or "").strip()
    try:
        data = json.loads(payload)
    except Exception:
        return None

    tool = str(data.get("tool", "")).strip().lower()
    args = str(data.get("args", "")).strip()
    if tool not in SUPPORTED_TOOLS:
        return None

    return {"tool": tool, "args": args}


def _exec_ls_like(tool: str, args: str) -> dict:
    from lib.lib import ls_cmd

    cmd = f"{tool} {args}".strip()
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            ls_cmd(cmd)
        output = buf.getvalue().strip()
        return {
            "ok": True,
            "tool": tool,
            "command": cmd,
            "output": output,
        }
    except Exception as e:
        return {
            "ok": False,
            "tool": tool,
            "command": cmd,
            "output": f"工具执行异常: {str(e)}",
        }


def execute_tool_call(call: dict) -> dict:
    tool = str(call.get("tool", "")).strip().lower()
    args = str(call.get("args", "")).strip()

    if tool in {"ls", "ll"}:
        return _exec_ls_like(tool, args)

    return {
        "ok": False,
        "tool": tool,
        "command": "",
        "output": f"不支持的工具: {tool}",
    }


def parse_and_execute(ai_text: str) -> dict | None:
    call = extract_tool_call(ai_text)
    if call is None:
        return None
    return execute_tool_call(call)


def build_tool_result_for_ai(exec_result: dict) -> str:
    status = "ok" if exec_result.get("ok") else "error"
    command = exec_result.get("command", "")
    output = exec_result.get("output", "")
    return (
        "以下是工具执行结果，请基于该结果用自然语言回答用户，不要再次输出工具调用标签。\n"
        f"status: {status}\n"
        f"command: {command}\n"
        "output:\n"
        f"{output}"
    )


def extract_command_call(ai_text: str) -> str | None:
    if not ai_text:
        return None

    pattern = re.compile(
        re.escape(CMD_CALL_START) + r"(.*?)" + re.escape(CMD_CALL_END),
        re.DOTALL,
    )
    m = pattern.search(ai_text)
    if not m:
        # 兼容AI直接返回命令文本（无标签）的情况
        text = ai_text.strip()
        if not text:
            return None
        first_line = text.splitlines()[0].strip()
        if first_line.startswith("`"):
            first_line = first_line.strip("` ")

        cmd_head = (first_line.split(" ", 1)[0] if first_line else "").lower()
        allowed = {
            "set",
            "ls",
            "ll",
            "cd",
            "pwd",
            "help",
            "path",
            "env",
            "img",
            "video",
            "download",
            "rm",
            "update",
            "dox",
            "chat",
            "version",
            "clear",
            "pck",
        }
        if cmd_head in allowed:
            return first_line
        return None

    payload = (m.group(1) or "").strip()
    if not payload:
        return None

    try:
        data = json.loads(payload)
        command_text = str(data.get("command", "")).strip()
        return command_text or None
    except Exception:
        return None


def execute_dox_command(command_text: str) -> dict:
    from lib.lib import command

    command_text = (command_text or "").strip()
    if not command_text:
        return {"ok": False, "command": "", "output": "空命令，未执行"}

    # 防止递归进入 AI 命令网关
    if command_text.startswith("?"):
        return {"ok": False, "command": command_text, "output": "禁止执行 ? 命令"}

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            command(command_text)
        return {
            "ok": True,
            "command": command_text,
            "output": buf.getvalue().strip(),
        }
    except Exception as e:
        return {
            "ok": False,
            "command": command_text,
            "output": f"命令执行异常: {str(e)}",
        }
