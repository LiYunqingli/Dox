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
SUPPORTED_TOOLS = {
    "ls",
    "ll",
    "pwd",
    "help",
    "path",
    "env",
    "cd",
    "cat",
}


def ai_action_log(action_type: str, cmd: str):
    from lib.lib import _print

    if action_type == "tool":
        _print(f"\n[工具] : {cmd}\n", "magenta")
    elif action_type == "cmd":
        _print(f"\n[命令] : {cmd}\n", "cyan")
    else:
        _print(f"\n[未知] : {cmd}\n", "yellow")


def get_tool_protocol_prompt() -> str:
    return (
        "当你需要调用 Dox 工具时，请严格使用如下格式输出，不要添加多余解释：\n"
        '<DOX_TOOL_CALL>{"tool":"ls","args":"-a"}</DOX_TOOL_CALL>\n'
        "可用 tool: ls, ll, pwd, help, path, env, cd, cat。args 可以为空字符串。"
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


def _exec_tool_command(tool: str, args: str) -> dict:
    cmd = f"{tool} {args}".strip()
    result = execute_dox_command(cmd, is_tool=True)
    return {
        "ok": bool(result.get("ok")),
        "tool": tool,
        "command": cmd,
        "output": str(result.get("output", "")),
    }


def execute_tool_call(call: dict) -> dict:
    tool = str(call.get("tool", "")).strip().lower()
    args = str(call.get("args", "")).strip()

    if tool in SUPPORTED_TOOLS:
        ai_action_log("tool", f"{tool} {args}".strip())
        return _exec_tool_command(tool, args)

    ai_action_log("tool", f"拦截到非法工具调用: {tool}")
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
    output = str(exec_result.get("output", ""))
    max_len = 4000
    if len(output) > max_len:
        output = (
            output[:max_len]
            + "\n... [输出过长已截断，若需要更多内容请继续调用工具读取具体片段]"
        )
    return (
        "以下是工具执行结果，请基于该结果用自然语言回答用户，不要再次输出工具调用标签。\n"
        "说明：名称末尾带 / 表示目录，名称末尾带 @ 表示符号链接。\n"
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
            "cat",
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


def execute_dox_command(command_text: str, is_tool: bool = False) -> dict:
    from lib.lib import command

    command_text = (command_text or "").strip()
    if not command_text:
        return {"ok": False, "command": "", "output": "空命令，未执行"}

    # 防止递归进入 AI 命令网关
    if command_text.startswith("?"):
        return {"ok": False, "command": command_text, "output": "禁止执行 ? 命令"}

    if not is_tool:
        ai_action_log("cmd", command_text)

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


def execute_dox_commands(command_text: str) -> dict:
    raw = (command_text or "").strip()
    if not raw:
        return {"ok": False, "commands": [], "output": "空命令，未执行"}

    parts = [p.strip() for p in raw.split(";") if p.strip()]
    if not parts:
        return {"ok": False, "commands": [], "output": "空命令，未执行"}

    rows = []
    all_ok = True
    for idx, cmd in enumerate(parts, start=1):
        r = execute_dox_command(cmd)
        ok = bool(r.get("ok"))
        all_ok = all_ok and ok
        out = str(r.get("output", "")).strip()
        status = "OK" if ok else "ERROR"
        rows.append(f"[{idx}] {status} {cmd}")
        if out:
            rows.append(out)

    return {
        "ok": all_ok,
        "commands": parts,
        "output": "\n".join(rows).strip(),
    }
