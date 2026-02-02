"""
Create at 2025.4.26 16:54:52 from Mr.LiHuarong
"""

from lib.lib import load, _print, command#,  clear
import os
import sys
from pathlib import Path

if sys.platform == "linux":
    try:
        import readline
        
    except (ImportError, ModuleNotFoundError, Exception):
        # 捕获所有导入相关异常，静默跳过（也可添加日志提示）
        pass


def _script_dir() -> str:
    return str(Path(__file__).resolve().parent)


def _home_dir() -> str:
    return os.path.expanduser('~')


def _apply_start_cwd(mode: str) -> None:
    """应用启动工作目录模式.

    模式:
      - 'script': 切换工作目录到包含 main.py 的目录
      - 'home':   切换工作目录到用户的主目录
      - 'keep':   保持当前工作目录不变
    """
    if mode == "keep":
        return
    if mode == "home":
        os.chdir(_home_dir())
        return
    if mode == "script":
        os.chdir(_script_dir())
        return
    raise ValueError(f"未知模式: {mode}")


def _parse_cwd_flags(argv: list[str]) -> tuple[str | None, list[str]]:
    """解析 cwd 标志并返回 (mode, remaining_argv)。"""
    mode: str | None = None
    remaining: list[str] = []

    for arg in argv:
        if arg in {"--cd-script", "--cd-script-dir"}:
            mode = "script"
            continue
        if arg in {"--cd-home"}:
            mode = "home"
            continue
        if arg in {"--no-cd", "--keep-cwd"}:
            mode = "keep"
            continue
        remaining.append(arg)

    return mode, remaining

if __name__ == '__main__':
    raw_args = sys.argv[1:]
    cwd_flag_mode, args = _parse_cwd_flags(raw_args)

    # 非交互模式（带参数或 -r）：默认切到脚本目录，方便从任意目录执行且相对路径可用
    # 交互模式（无参数）：默认切到 HOME，保持“像 shell 一样”的体验
    if cwd_flag_mode is None:
        default_mode = "script" if (len(args) > 0 or "-r" in args) else "home"
        _apply_start_cwd(default_mode)
    else:
        _apply_start_cwd(cwd_flag_mode)

    # 检查是否存在 -r 参数
    if '-r' in args:
        try:
            r_index = args.index('-r')
            cmd_str = args[r_index + 1]
        except IndexError:
            _print("Dox _10_\n", )
            sys.exit(1)
        
        commands = cmd_str.split(';')
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:  # 跳过空命令
                if cmd.lower() == "exit":
                    _print("_11_\n", "red")
                else:
                    command(cmd)
                # print(f"\n----end: {cmd}----\n")
        sys.exit()
    
    # 无 -r 参数时的逻辑
    if len(args) > 0:
        cmd = ' '.join(args)
        if cmd.lower() == "exit":
            _print("_11_\n", "red")
        else:
            command(cmd)
        sys.exit()
    
    # 交互模式（无参数时）
    
    # clear()
    load()
    try:
        while True:
            try:
                userPath = os.getcwd()
                base_name = os.path.basename(userPath) #只显示当前目录名
                if base_name == "":
                    base_name = "/" #如果当前目录为根目录，则显示为"/" 注意需要考虑windows下的兼容性（目前仅考虑Ubuntu）
                # _print("Dox:" + base_name + ">>")
                input_str = input("Dox:" + base_name + ">>")
                if input_str.lower() == "exit":
                    print("exit")
                    sys.exit()
                command(input_str)
            except KeyboardInterrupt:
                print("^C")  # 处理换行，使提示符出现在新行
                continue
    except Exception as e:
        _print(f"Error: {e}\n", "red")
        input("警告：程序出现错误，抱歉您的工作区无法恢复，按任意键退出程序...")