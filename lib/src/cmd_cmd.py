"""cmd 命令实现：执行系统终端命令，或进入系统终端交互模式。

用法：
    cmd                          进入系统终端交互模式（需要交互式终端）
    cmd <命令>                    执行单条系统命令并回显输出
    cmd --timeout <秒> <命令>     指定执行超时（默认 60 秒，0 表示不限制）

说明：
    - 选项只在命令前生效，避免吞掉系统命令自身的参数（如 ping -t）。
    - 单条命令统一捕获 stdout/stderr 后回显，因此也能被 chat / ? 的 AI 通道取到输出。
"""

import re
import sys

from lib.lib import _print, get_config_int

# 单条命令的默认执行超时（秒），0 表示不限制
# 可在 config.json 中通过 Config.CmdTimeout 覆盖，缺失时使用此兜底值
DEFAULT_TIMEOUT = 60

# 前置超时选项：--timeout 30 或 --timeout=30
_TIMEOUT_RE = re.compile(r"^\s*--timeout(?:=|\s+)(\d+)\s*", re.IGNORECASE)


def _system_shell():
    """返回当前系统终端的启动命令（参数列表）。"""
    import os

    if os.name == "nt":
        return [os.environ.get("COMSPEC") or "cmd.exe"]
    return [os.environ.get("SHELL") or "/bin/sh"]


def _decode_output(data: bytes) -> str:
    """把系统命令的输出字节解码为文本。

    优先按 UTF-8 解码（兼容 chcp 65001 的场景），失败后回退到 Windows 的
    OEM/ANSI 代码页或系统的首选编码，最后才用替换字符兜底，避免中文乱码。
    """
    if not data:
        return ""

    import locale
    import os

    encodings = ["utf-8"]

    if os.name == "nt":
        try:
            import ctypes

            for name in ("GetOEMCP", "GetACP"):
                codepage = getattr(ctypes.windll.kernel32, name)()
                if codepage:
                    encodings.append(f"cp{codepage}")
        except Exception:
            pass

    try:
        encodings.append(locale.getpreferredencoding(False))
    except Exception:
        pass

    for enc in dict.fromkeys(encodings):
        if not enc:
            continue
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue

    return data.decode("utf-8", errors="replace")


def run_system_command(cmdline, timeout=None):
    """执行一条系统命令。

    返回 (状态, 退出码, 输出文本)，状态取值为 ok / timeout / error。
    """
    import os
    import subprocess

    if os.name == "nt":
        argv = _system_shell() + ["/c", cmdline]
    else:
        argv = _system_shell() + ["-c", cmdline]

    try:
        proc = subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout if timeout else None,
        )
    except subprocess.TimeoutExpired as e:
        return "timeout", None, _decode_output(e.stdout or b"")
    except Exception as e:
        return "error", None, str(e)

    return "ok", proc.returncode, _decode_output(proc.stdout or b"")


def run_interactive_terminal():
    """在当前终端启动系统终端（继承标准输入输出），返回退出码。"""
    import subprocess

    try:
        return subprocess.call(_system_shell())
    except Exception as e:
        _print("_75_\n", "red", [str(e)])
        return -1


def _emit(text: str):
    """回显命令输出，保证末尾换行。"""
    if not text:
        return
    print(text if text.endswith("\n") else text + "\n", end="")


def cmd_cmd(input_str):
    """cmd 命令入口。"""
    # 取 "cmd" 之后的原始内容，保留用户输入的引号与空格
    raw_rest = input_str.strip()[3:]

    # 解析前置 --timeout 选项，未指定时取配置中的默认值
    timeout = get_config_int("Config.CmdTimeout", DEFAULT_TIMEOUT)
    rest = raw_rest
    while True:
        m = _TIMEOUT_RE.match(rest)
        if not m:
            break
        timeout = int(m.group(1))
        rest = rest[m.end() :]

    cmdline = rest.strip()

    # 只给了选项没给命令：提示用法，避免误入交互终端
    if not cmdline and raw_rest.strip():
        _print("_70_\n", "red")
        return

    # 不带命令：进入系统终端交互模式
    if not cmdline:
        if not sys.stdin.isatty():
            # 非交互式终端（管道/批处理/AI 通道）下启动会导致阻塞
            _print("_71_\n", "red")
            return
        _print("_72_\n", "cyan")
        code = run_interactive_terminal()
        _print("_73_\n", items=[str(code)])
        return

    status, code, output = run_system_command(cmdline, timeout)

    if status == "error":
        _print("_75_\n", "red", [output])
        return

    _emit(output)

    if status == "timeout":
        _print("_76_\n", "yellow", [str(timeout)])
        return

    if code != 0:
        _print("_74_\n", "yellow", [str(code)])
