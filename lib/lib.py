"""
通用基础层：配置读取、运行路径、多语言输出与通用工具函数。

分层约定：
- 本文件只保留与具体命令无关的“通用语法”能力（路径/配置/语言/输出/通用文件与下载工具）；
- 具体命令实现统一放在 lib/src/ 下；
- 命令分发入口 command() 位于 lib/command.py，基础层不反向依赖业务层。
"""

_config = None


# 获取main.py所在的路径
def get_run_path():
    import os
    import sys

    # PyInstaller(onefile) 下，__file__ 指向 _MEI 临时目录。
    # 返回 "<exe_dir>/lib" 可保持现有 "../config" "../resources" 相对路径逻辑不变。
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "lib")

    return os.path.dirname(os.path.abspath(__file__))


# 获取配置文件的信息
def get_config():
    global _config
    if _config == None:
        config_file_path = get_run_path() + "/../config/config.json"
        import json

        with open(config_file_path, "r", encoding="utf-8") as f:
            _config = json.load(f)
    return _config


# 获取当前语言设置
def get_lang():
    config = get_config()
    lang = config["Config"]["Lang"]
    return lang


_VT_ENABLED = False


def _enable_virtual_terminal_processing() -> None:
    """在 Windows 终端上启用 ANSI 转义序列处理（尽力而为）。"""
    global _VT_ENABLED
    if _VT_ENABLED:
        return
    _VT_ENABLED = True

    import os

    if os.name != "nt":
        return

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return

        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        return


# 基于print的封装，根据本地语言设置输出对应语言的信息
def _print(input_str="\n", color=None, items=[]):
    import json
    import re

    # 确保 Windows 终端可以正常显示 ANSI 颜色（尽力而为）
    try:
        _enable_virtual_terminal_processing()
    except Exception:
        pass

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",  # 重置颜色
        "bold": "\033[1m",  # 加粗
        "underline": "\033[4m",
    }

    color_code = COLORS.get(color, "")
    reset_code = COLORS["reset"] if color else ""

    lang = get_lang()
    lang_file_path = f"{get_run_path()}/../resources/lang/src/{lang}.json"

    try:
        with open(lang_file_path, "r", encoding="utf-8") as f:
            lang_data = json.load(f)["msg"]
        pattern = re.compile(r"_(\d+)_")

        def replace_match(match):
            key = match.group(1)
            return lang_data.get(key, match.group(0))

        output_str = pattern.sub(replace_match, input_str)

        # 现在格式化其中的%s，按照顺序讲items中的值替换进去
        output_str = output_str % tuple(items)

        print(f"{color_code}{output_str}{reset_code}", end="")
    except FileNotFoundError:
        print(f"Error: Language file not found at {lang_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in language file {lang_file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")


# 初始化控制台，载入信息
def load():
    config = get_config()
    version = config["About"]["Version"]
    _print("_0_[v" + version + "]\n")
    _print("_1_\n")
    _print()


# 获取关于信息
def get_about():
    config = get_config()
    about = config["About"]
    return str(about)


# 清除屏幕内容
def clear():
    """清屏"""
    import os

    os.system("cls" if os.name == "nt" else "clear")


# rm 删除文件或者目录
def rm(paths, recursive=False, force=False):
    """删除文件或目录

    参数：
        paths (list): 要删除的文件/目录路径列表
        recursive (bool): 是否递归删除目录
        force (bool): 是否强制删除（无确认）
    """
    import os
    import shutil

    for path in paths:
        # 检查路径是否存在
        if not os.path.exists(path):
            if not force:
                _print("_20_\n", "red", [path])  # 文件或目录不存在
            continue  # 强制模式下忽略不存在的文件
        # 删除文件
        if os.path.isfile(path):
            try:
                if not force:
                    _print("_22_\n", "yellow", [path])  # 确认删除文件
                    confirm = input().strip().lower()
                    if confirm != "y":
                        _print("_24_\n")  # 取消删除
                        continue
                os.remove(path)
                _print("_21_\n", items=[path])  # 成功删除文件
            except Exception as e:
                _print(f"_29_: {str(e)}\n", "red", [path])  # 删除失败
        # 删除目录
        elif os.path.isdir(path):
            if not recursive:
                _print("_25_\n", "red")  # 需要-r参数
                continue
            try:
                if not force:
                    _print("_27_\n", "yellow", [path])  # 确认删除目录
                    confirm = input().strip().lower()
                    if confirm != "y":
                        _print("_24_\n")
                        continue
                shutil.rmtree(path, ignore_errors=force)  # 强制模式下忽略错误
                _print("_26_\n", items=[path])  # 成功删除目录
            except Exception as e:
                if not force:
                    _print(f"_29_: {str(e)}\n", "red", [path])
        else:
            _print("_28_\n", "red", [path])  # 未知类型


# 下载文件(高级版本，支持动态显示下载过程，不支持断点续传)
def download(file_url, file_path):
    import requests
    import os
    import time

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }

    # 将字节数转换为易读的容量文本
    def human_readable_size(size_bytes):
        if size_bytes <= 0:
            return "0B"
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = size_bytes
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        return f"{size:.2f} {units[unit_index]}"

    # 将秒数格式化为 时:分:秒 / 分:秒
    def format_time(seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    try:
        r = requests.get(file_url, stream=True)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        total_size = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        start_time = time.time()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    elapsed_time = time.time() - start_time
                    speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                    human_downloaded = human_readable_size(downloaded)
                    speed_h = human_readable_size(speed) + "/s"
                    time_str = format_time(elapsed_time)
                    # 已知总大小时绘制进度条，否则只显示已下载量与速度
                    if total_size > 0:
                        percent = downloaded / total_size * 100
                        progress_width = 20
                        filled = int(progress_width * percent / 100)
                        bar = (
                            "=" * filled + ">" + " " * (progress_width - filled - 1)
                            if filled < progress_width
                            else "=" * progress_width
                        )
                        human_total = human_readable_size(total_size)
                        remaining_time = (
                            (total_size - downloaded) / speed if speed > 0 else 0
                        )
                        eta_str = format_time(remaining_time) if speed > 0 else "--:--"
                        progress_line = f"\r{percent:.1f}% [{bar}] {human_downloaded}/{human_total} {speed_h} Time: {time_str} ETA: {eta_str}"
                    else:
                        progress_line = f"\rDownloaded: {human_downloaded} at {speed_h} Time: {time_str}"
                    color_code = COLORS["green"]
                    reset_code = COLORS["reset"]
                    print(
                        f"{color_code}{progress_line}{reset_code}", end="", flush=True
                    )
            print(f"{COLORS['reset']}\n", end="")
        return True
    except Exception as e:
        _print(f"download() : {str(e)}\n", color="red")
        return False
