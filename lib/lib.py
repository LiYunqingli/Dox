"""
所有常用的方法封装的地方，如需添加新的方法，请注意规范且编写注释
"""

_config = None


# 初始化控制台，载入信息
def load():
    config = get_config()
    version = config["About"]["Version"]
    _print("_0_[v" + version + "]\n")
    _print("_1_\n")
    _print()


# 获取配置文件的信息
def get_config():
    global _config
    if _config == None:
        config_file_path = get_run_path() + "/../config/config.json"
        import json

        with open(config_file_path, "r", encoding="utf-8") as f:
            _config = json.load(f)
    return _config


# 获取main.py所在的路径
def get_run_path():
    import os

    return os.path.dirname(os.path.abspath(__file__))


# 获取当前语言设置
def get_lang():
    config = get_config()
    lang = config["Config"]["Lang"]
    return lang


# 基于print的封装，根据本地语言设置输出对应语言的信息
def _print(input_str="\n", color=None, items=[]):
    import json
    import re

    # Ensure ANSI colors work on Windows (best-effort)
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


# 获取关于信息
def get_about():
    config = get_config()
    about = config["About"]
    return str(about)


# 加载动画
def donghua():
    """打印动画"""
    import time
    import random

    with open(
        get_run_path() + "/../resources/donghua/donghua", "r", encoding="utf-8"
    ) as f:
        for line in f:
            for char in line:
                print(f"\033[38;5;{random.randint(0, 255)}m{char}\033[0m", end="")
                time.sleep(0.001)
    print("\n")


# 清除屏幕内容
def clear():
    """清屏"""
    import os

    os.system("cls" if os.name == "nt" else "clear")


_VT_ENABLED = False


def _enable_virtual_terminal_processing() -> None:
    """Enable ANSI escape sequence processing on Windows terminals (best-effort)."""
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


# 打印帮助信息（自动根据语言设置选择对应的语言包）
def help(input_str):
    """显示帮助信息"""
    items = input_str.split()
    items = items[1:]  # 去掉第一个元素（命令本身）

    def help_print(help_id):
        import json

        lang_file_path = f"{get_run_path()}/../resources/lang/src/{get_lang()}.json"
        with open(lang_file_path, "r", encoding="utf-8") as f:
            help_data = json.load(f)["help"]
        if help_id == "ALL":
            _print("\n_12_\n\n")
            for help_item in help_data:
                # print(f"\n===============[{help_item["name"]}]===============\n")
                # print(help_item["msg"] + "\n")
                # for usage_item in help_item["usage"]:
                #     print(f"{usage_item}：{help_item['usage'][usage_item]}")
                # print("\n")

                # _print(f"{help_item['name']}","bold")#加粗命令
                print(f"{help_item['msg']}")
            print("\n")
        else:
            found = False
            for help_item in help_data:
                if help_item["name"] == help_id:
                    print(f"\n[{help_item['name']}]\n")
                    print(help_item["msg"] + "\n")
                    for usage_item in help_item["usage"]:
                        print(f"{usage_item}：{help_item['usage'][usage_item]}")
                    print(
                        "--------------------------------------------------------------------------------------\n"
                    )
                    found = True
                    break
            if not found:
                _print(f"_3_{help_id}\n", "red")

    if len(items) == 0:
        help_print("ALL")
    else:
        for item in items:
            # 将参数转换为大写以匹配JSON中的命令名称
            help_print(item.upper())


# 进入一个新的目录
def cd(path):
    """改变当前工作目录"""
    import os

    try:
        os.chdir(path)
    except FileNotFoundError:
        _print("_4_\n")
    except NotADirectoryError:
        _print("_5_\n")
    except PermissionError:
        _print("_6_\n")
    except Exception as e:
        _print(f"_7_{str(e)}\n")


def ls_cmd(input_str: str) -> None:
    """解析并执行 ls/ll（增强版）。

    兼容原行为：
      - `ls`：短列表
      - `ls -l` / `ll`：详细列表

    额外支持：
      - `-a`：显示隐藏文件（以 . 开头）
      - `-1`：单列输出
      - `-r`：反向排序
      - `--sort name|time|size`
      - `--no-color`：关闭颜色
      - `--no-dirs-first`：不将目录置顶
      - `[path]`：列出指定目录（不支持多个路径）
    """
    import os
    import shlex
    import stat
    import time
    import unicodedata
    from dataclasses import dataclass

    _enable_virtual_terminal_processing()

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    cmd = parts[0].lower() if parts else "ls"
    args = parts[1:]

    detailed = cmd == "ll"
    show_all = False
    one_per_line = False
    sort_key = "name"
    reverse = False
    no_color = False
    dirs_first = True
    target = None

    i = 0
    while i < len(args):
        a = args[i]
        if a == "-l":
            detailed = True
            i += 1
            continue
        if a == "-a":
            show_all = True
            i += 1
            continue
        if a == "-1":
            one_per_line = True
            i += 1
            continue
        if a == "-r":
            reverse = True
            i += 1
            continue
        if a == "--no-color":
            no_color = True
            i += 1
            continue
        if a == "--no-dirs-first":
            dirs_first = False
            i += 1
            continue
        if a == "--sort":
            if i + 1 >= len(args):
                _print("_13_\n", "red")
                return
            sort_key = (args[i + 1] or "").lower()
            if sort_key not in {"name", "time", "size"}:
                _print("_13_\n", "red")
                return
            i += 2
            continue

        if a.startswith("-"):
            _print("_13_\n", "red")
            return

        # path token
        if target is not None:
            _print("_13_\n", "red")
            return
        target = a
        i += 1

    @dataclass(frozen=True)
    class _Entry:
        name: str
        is_dir: bool
        is_link: bool
        mode: int
        size: int
        mtime: float

    def _display_width(s: str) -> int:
        w = 0
        for ch in s:
            if ch == "\t":
                w += 4
                continue
            if unicodedata.east_asian_width(ch) in {"W", "F"}:
                w += 2
            else:
                w += 1
        return w

    def _pad(s: str, width: int) -> str:
        return s + (" " * max(width - _display_width(s), 0))

    def _human_size(num: int) -> str:
        n = float(num)
        units = ["B", "K", "M", "G", "T", "P"]
        idx = 0
        while n >= 1024 and idx < len(units) - 1:
            n /= 1024
            idx += 1
        if idx == 0:
            return f"{int(n)}{units[idx]}"
        if n >= 10:
            return f"{n:.0f}{units[idx]}"
        return f"{n:.1f}{units[idx]}"

    def _format_mtime(ts: float) -> str:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))

    def _format_mode(mode: int, is_dir: bool, is_link: bool) -> str:
        file_type = "d" if is_dir else "l" if is_link else "-"

        def bit(ch: str, mask: int) -> str:
            return ch if (mode & mask) else "-"

        return (
            file_type
            + bit("r", stat.S_IRUSR)
            + bit("w", stat.S_IWUSR)
            + bit("x", stat.S_IXUSR)
            + bit("r", stat.S_IRGRP)
            + bit("w", stat.S_IWGRP)
            + bit("x", stat.S_IXGRP)
            + bit("r", stat.S_IROTH)
            + bit("w", stat.S_IWOTH)
            + bit("x", stat.S_IXOTH)
        )

    def _colorize(label: str, e: _Entry) -> str:
        if no_color:
            return label
        blue = "\033[34m"
        cyan = "\033[36m"
        green = "\033[32m"
        dim = "\033[2m"
        reset = "\033[0m"

        color = ""
        if e.is_dir:
            color = blue
        elif e.is_link:
            color = cyan
        elif e.mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            color = green

        if e.name.startswith("."):
            color = (dim + color) if color else dim

        return f"{color}{label}{reset}" if color else label

    base = target or os.getcwd()
    try:
        if not os.path.exists(base):
            _print("_4_\n", "red")
            return
        if not os.path.isdir(base):
            _print("_5_\n", "red")
            return
    except Exception as e:
        _print(f"_7_{str(e)}\n", "red")
        return

    entries: list[_Entry] = []
    try:
        with os.scandir(base) as it:
            for de in it:
                if (not show_all) and de.name.startswith("."):
                    continue
                try:
                    st = de.stat(follow_symlinks=False)
                    entries.append(
                        _Entry(
                            name=de.name,
                            is_dir=de.is_dir(follow_symlinks=False),
                            is_link=de.is_symlink(),
                            mode=st.st_mode,
                            size=int(getattr(st, "st_size", 0) or 0),
                            mtime=float(getattr(st, "st_mtime", 0.0) or 0.0),
                        )
                    )
                except Exception:
                    continue
    except PermissionError:
        _print("_6_\n", "red")
        return
    except Exception as e:
        _print(f"_7_{str(e)}\n", "red")
        return

    def key_value(e: _Entry):
        if sort_key == "time":
            return e.mtime
        if sort_key == "size":
            return e.size
        return e.name.casefold()

    def combined_key(e: _Entry):
        prefix = 0
        if dirs_first:
            prefix = 0 if e.is_dir else 1
        return (prefix, key_value(e))

    entries = sorted(entries, key=combined_key, reverse=reverse)

    if detailed:
        size_strs = [_human_size(e.size) for e in entries]
        size_w = max((len(s) for s in size_strs), default=1)
        for e, size_s in zip(entries, size_strs):
            suffix = "/" if e.is_dir else "@" if e.is_link else ""
            name = _colorize(f"{e.name}{suffix}", e)
            _print(
                f"{_format_mode(e.mode, e.is_dir, e.is_link)} {size_s:>{size_w}} {_format_mtime(e.mtime)} {name}\n"
            )
        return

    # short listing
    labels_plain: list[str] = []
    labels_colored: list[str] = []
    widths: list[int] = []
    for e in entries:
        suffix = "/" if e.is_dir else "@" if e.is_link else ""
        plain = f"{e.name}{suffix}"
        labels_plain.append(plain)
        labels_colored.append(_colorize(plain, e))
        widths.append(_display_width(plain))

    if one_per_line:
        for s in labels_colored:
            _print(s + "\n")
        return

    try:
        term_cols, _ = os.get_terminal_size()
        term_cols = max(int(term_cols), 20)
    except Exception:
        term_cols = 80

    if not labels_plain:
        _print("\n")
        return

    maxw = min(max(widths), 60)
    colw = maxw + 2
    ncols = max(1, term_cols // colw)
    nrows = (len(labels_plain) + ncols - 1) // ncols

    for r in range(nrows):
        parts = []
        for c in range(ncols):
            idx = c * nrows + r
            if idx >= len(labels_plain):
                continue
            plain = labels_plain[idx]
            colored = labels_colored[idx]
            if _display_width(plain) > maxw:
                keep = maxw - 1
                cut = plain
                while _display_width(cut) > keep and len(cut) > 0:
                    cut = cut[1:]
                short_plain = "…" + cut
                colored = _colorize(short_plain, entries[idx])
            parts.append(_pad(colored, maxw) + "  ")
        _print("".join(parts).rstrip() + "\n")


# 输出当前工作路径
def pwd():
    """返回当前路径"""
    import os

    _print("\n" + os.getcwd() + "\n\n")


def cat(input_str):
    """
    显示文件内容
    支持：
      cat <file>                 打印所有内容
      cat <file> -head 10        前10行（也可以用 -l 10）
      cat <file> -tail 10        后10行
    """
    items = input_str.split()[1:]
    if not items:
        _print("用法: cat <文件名> [-head <行数>] [-tail <行数>]\n", "red")
        return

    import os

    file_path = items[0]
    head_n = None
    tail_n = None

    if len(items) > 1:
        i = 1
        while i < len(items):
            if items[i] in ("-head", "-l") and i + 1 < len(items):
                try:
                    head_n = int(items[i + 1])
                except ValueError:
                    _print("参数错误：行数必须是整数\n", "red")
                    return
                i += 2
            elif items[i] == "-tail" and i + 1 < len(items):
                try:
                    tail_n = int(items[i + 1])
                except ValueError:
                    _print("参数错误：行数必须是整数\n", "red")
                    return
                i += 2
            else:
                i += 1

    if not os.path.isfile(file_path):
        from lib.lib import _print

        _print("_20_\n", "red", [file_path])
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        _print("无法读取文件内容（可能不是文本文件或不是UTF-8编码）\n", "red")
        return
    except Exception as e:
        _print(f"读取文件失败: {e}\n", "red")
        return

    out_lines = lines
    if head_n is not None:
        out_lines = lines[:head_n]
    elif tail_n is not None:
        out_lines = lines[-tail_n:]

    for line in out_lines:
        print(line, end="")
    if out_lines and not out_lines[-1].endswith("\n"):
        print()


# 指定一个路径在控制台播放视频
def video(input_str):
    """在终端播放视频（低分辨率渲染）

    用法：
        video [视频路径|test] [-w 宽度] [-h 高度] [--fps 15] [--loop] [--gray] [--no-color]
    """

    items = input_str.split()[1:]  # 去除命令本身
    if len(items) == 0:
        _print("_13_\n", "red")
        return

    # 兼容包含空格的路径：
    # - 可以不加引号：video D:\a b\c.mp4 -w 80
    # - 也可以使用单/双引号包裹：video "D:\a b\c.mp4" 或 video 'D:\a b\c.mp4'
    option_tokens = {
        "-w",
        "--width",
        "-h",
        "--height",
        "--fps",
        "--loop",
        "-l",
        "--gray",
        "--grey",
        "-g",
        "--no-color",
        "--ascii",
    }

    path_end = 0
    while path_end < len(items) and items[path_end] not in option_tokens:
        path_end += 1

    path = " ".join(items[:path_end]).strip()

    def _strip_wrapping_quotes(s: str) -> str:
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            return s[1:-1]
        return s

    path = _strip_wrapping_quotes(path)

    items = items[path_end:]
    max_width = None
    max_height = None
    fps = None
    loop = False
    grayscale = False
    no_color = False

    i = 0
    while i < len(items):
        arg = items[i]
        if arg in ("-w", "--width"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_width = int(items[i + 1])
            i += 2
            continue
        if arg in ("-h", "--height"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_height = int(items[i + 1])
            i += 2
            continue
        if arg in ("--fps",):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            fps = float(items[i + 1])
            i += 2
            continue
        if arg in ("--loop", "-l"):
            loop = True
            i += 1
            continue
        if arg in ("--gray", "--grey", "-g"):
            grayscale = True
            i += 1
            continue
        if arg in ("--no-color", "--ascii"):
            no_color = True
            i += 1
            continue

        _print("_13_\n", "red")
        return

    import os

    if path.lower() == "test":
        path = get_run_path() + "/../resources/video/kun.mp4"

    if not os.path.exists(path):
        _print("\n_7__5_\n\n")
        return

    try:
        from lib.src.video import video_in_cmd

        video_in_cmd(
            path,
            max_width=max_width,
            max_height=max_height,
            fps=fps,
            loop=loop,
            grayscale=grayscale,
            no_color=no_color,
            page_break=True,
        )
    except Exception as e:
        _print(f"\n_7_{str(e)}\n\n", "red")


# 指定一个路径在控制台显示图片（低分辨率）
def img(input_str):
    """在终端以较低分辨率查看图片

    用法：
        img [图片路径] [-w 宽度] [-h 高度] [--gray] [--no-color]
    """

    items = input_str.split()[1:]  # 去除命令本身
    if len(items) == 0:
        _print("_13_\n", "red")
        return

    # 兼容包含空格的路径（同 video 命令）：
    # img D:\a b\c.png -w 80
    # img "D:\a b\c.png" / img 'D:\a b\c.png'
    option_tokens = {
        "-w",
        "--width",
        "-h",
        "--height",
        "--gray",
        "--grey",
        "-g",
        "--no-color",
        "--ascii",
    }

    path_end = 0
    while path_end < len(items) and items[path_end] not in option_tokens:
        path_end += 1

    path = " ".join(items[:path_end]).strip()

    def _strip_wrapping_quotes(s: str) -> str:
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            return s[1:-1]
        return s

    path = _strip_wrapping_quotes(path)

    items = items[path_end:]
    max_width = None
    max_height = None
    grayscale = False
    no_color = False

    i = 0
    while i < len(items):
        arg = items[i]
        if arg in ("-w", "--width"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_width = int(items[i + 1])
            i += 2
            continue
        if arg in ("-h", "--height"):
            if i + 1 >= len(items):
                _print("_13_\n", "red")
                return
            max_height = int(items[i + 1])
            i += 2
            continue
        if arg in ("--gray", "--grey", "-g"):
            grayscale = True
            i += 1
            continue
        if arg in ("--no-color", "--ascii"):
            no_color = True
            i += 1
            continue

        # 未识别参数
        _print("_13_\n", "red")
        return

    import os

    if path.lower() == "test":
        path = get_run_path() + "/../resources/img/test_img.png"

    if not os.path.exists(path):
        _print("\n_7__5_\n\n")
        return

    from lib.src.img import image_in_cmd

    image_in_cmd(
        path,
        max_width=max_width,
        max_height=max_height,
        grayscale=grayscale,
        no_color=no_color,
    )


# 软件包管理器
def pck(input_str):
    items = input_str.split()[1:]  # 去除命令本身
    if len(items) == 0:
        _print("_16_\n")  # 至少需要一个参数
    else:
        if items[0] == "install":
            items = items[1:]
            from lib.src.pck import pck_install

            if len(items) == 0:
                _print("_17_\n")  # 最少需要一个包名
            elif "-y" in items:
                items.remove("-y")
                pck_install(items, False)
            else:
                # 询问安装
                pck_install(items, True)
        elif items[0] == "update":
            from lib.src.pck import pck_update

            items = items[1:]
            if len(items) != 0:
                _print("_18_\n")  # pck update 用法错误（携带参数非法）
            else:
                pck_update()
        elif items[0] == "list":
            from lib.src.pck import pck_list

            items = items[1:]
            if len(items) != 0:
                _print("_18_\n")
            else:
                pck_list()
        elif items[0] == "search":
            items = items[1:]
            if len(items) == 0:
                _print("_33_\n")
            else:
                from lib.src.pck import pck_search

                pck_search(items[0], isOutPut=True)
        else:
            _print("_19_" + items[0] + "\n")  # 非法的pck参数


# 修改配置文件
def set_config(input_str):
    import json
    import shlex

    def format_value(value):
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    def parse_value(value_str):
        value_str = value_str.strip()
        if value_str == "":
            return ""
        try:
            return json.loads(value_str)
        except Exception:
            return value_str

    def is_yes(s: str) -> bool:
        s = (s or "").strip().lower()
        return s in {"y", "yes", "true", "1", "是", "好", "ok"}

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    if len(parts) < 3:
        _print("_34_\n", "red")
        return

    key_path = (parts[1] or "").strip().strip(".")
    if not key_path:
        _print("_34_\n", "red")
        return

    value_str = " ".join(parts[2:])
    new_value = parse_value(value_str)

    config = get_config()
    config_root = config

    segments = [seg for seg in key_path.split(".") if seg]
    if not segments:
        _print("_34_\n", "red")
        return

    parent = config_root
    missing_path = None
    non_object_at = None

    for i, seg in enumerate(segments[:-1]):
        if seg not in parent:
            missing_path = ".".join(segments[: i + 1])
            break
        if not isinstance(parent[seg], dict):
            non_object_at = ".".join(segments[: i + 1])
            break
        parent = parent[seg]

    if non_object_at is not None:
        _print("_44_\n", "red", [non_object_at])
        return

    final_key = segments[-1]
    exists_final = missing_path is None and final_key in parent

    # Key missing (either intermediate path or final key)
    if missing_path is not None or not exists_final:
        _print("_39_\n", "yellow", [key_path])
        _print("_40_\n", items=[format_value(new_value)])
        _print("_41_", "yellow", [key_path])
        if not is_yes(input()):
            _print("_43_\n")
            return

        # Create missing intermediate dicts
        parent = config_root
        for seg in segments[:-1]:
            if seg not in parent:
                parent[seg] = {}
            elif not isinstance(parent[seg], dict):
                _print("_44_\n", "red", [seg])
                return
            parent = parent[seg]

        parent[final_key] = new_value
        try:
            config_file_path = get_run_path() + "/../config/config.json"
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                f.write("\n")
            _print("_42_\n", items=[key_path])
        except Exception as e:
            _print("_46_\n", "red", [str(e)])
        return

    # Key exists; show old/new and confirm
    old_value = parent.get(final_key)
    _print("_35_\n", items=[key_path])
    _print("_36_\n", items=[format_value(old_value)])
    _print("_37_\n", items=[format_value(new_value)])
    _print("_38_", "yellow", [key_path])
    if not is_yes(input()):
        _print("_43_\n")
        return

    parent[final_key] = new_value
    try:
        config_file_path = get_run_path() + "/../config/config.json"
        with open(config_file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            f.write("\n")
        _print("_42_\n", items=[key_path])
    except Exception as e:
        _print("_46_\n", "red", [str(e)])


# rm 删除文件或者目录
def rm(paths, recursive=False, force=False):
    """删除文件或目录
    Args:
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


# 处理交互命令
def command(input_str):
    input_str = input_str.strip()
    if input_str.startswith("&"):
        from lib.src.network import network_cmd

        network_cmd(input_str)
        return

    input_list = input_str.split()
    if len(input_list) == 0:
        return

    # 全局帮助后缀：任意命令后携带 --help 等同于 help <命令名>
    # 例：ls --help  => help ls
    #     pck list --help => help pck
    if input_list[-1].lower() == "--help":
        if len(input_list) == 1:
            input_str = "help"
            input_list = ["help"]
        else:
            input_str = f"help {input_list[0]}"
            input_list = ["help", input_list[0]]

    command = input_list[0]
    if command.lower() == "version":
        _print(get_about() + "\n")
    elif command.lower() == "clear":
        clear()
    elif command.lower() == "donghua":
        donghua()  # 属于彩蛋，在help文档中不应该记录关于此命令的信息及用法
    elif command.lower() == "cd":
        if len(input_list) > 1:
            cd(input_list[1])
        else:
            _print("_8_\n")
    elif command.lower() == "ls":
        ls_cmd(input_str)
    elif command.lower() == "ll":
        ls_cmd(input_str)
    elif command.lower() == "pwd":
        pwd()
    elif command.lower() == "cat":
        cat(input_str)
    elif command.lower() == "help":
        help(input_str)
    elif command.lower() == "video":
        video(input_str)
    elif command.lower() == "img":
        img(input_str)
    elif command.lower() == "pck":
        pck(input_str)
    elif command.lower() == "download":
        file_url = input_list[1]
        file_path = input_list[2]
        download(file_url, file_path)
    elif command.lower() == "rm":
        items = input_list[1:]  # 去除命令本身
        if not items:
            _print("_30_\n", "red")  # 缺少参数
            return
        recursive = False
        force = False
        paths = []
        # 解析参数
        for item in items:
            if item.startswith("-"):
                if "r" in item or "R" in item:
                    recursive = True
                if "f" in item:
                    force = True
            else:
                paths.append(item)
        if not paths:
            _print("_31_\n", "red")  # 未指定文件或目录
            return
        # 调用rm函数
        rm(paths, recursive, force)
    elif command.lower() == "path":
        path_cmd(input_str)
    elif command.lower() == "env":
        env_cmd(input_str)
    elif command.lower() == "set":
        set_config(input_str)
    elif command.lower() == "update":
        from lib.src.update import update

        update()
    elif command.lower() == "dox":
        path = get_run_path() + "/../resources/img/dox.png"
        img(f'img "{path}"')
    elif command.lower() == "chat":
        from lib.src.chat import chat_cmd

        chat_cmd(input_str)
    elif command == "?":
        from lib.src.chat import ai_run_cmd

        ai_run_cmd(input_str)
    else:
        _print("_2_" + command + "\n")


_TEMP_ENV = {
    "PATH": [],
}


def _path_json_path():
    return get_run_path() + "/../config/path.json"


def _load_persistent_env():
    import json
    import os

    path = _path_json_path()
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"PATH": []}, f, ensure_ascii=False, indent=4)
                f.write("\n")
        except Exception:
            return {"PATH": []}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        if "PATH" not in data or not isinstance(data.get("PATH"), list):
            data["PATH"] = []
        return data
    except Exception as e:
        _print("_63_\n", "red", [str(e)])
        return {"PATH": []}


def _save_persistent_env(data):
    import json

    try:
        with open(_path_json_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n")
        return True
    except Exception as e:
        _print("_64_\n", "red", [str(e)])
        return False


def _normalize_path_entry(p: str) -> str:
    import os

    p = (p or "").strip().strip('"').strip("'")
    if p == "":
        return ""
    p = os.path.expanduser(p)
    return os.path.normpath(p)


def _path_key(p: str) -> str:
    import os

    return os.path.normcase(os.path.normpath(p))


def _effective_path_list(persistent_list, temp_list):
    seen = set()
    result = []
    for item in temp_list + persistent_list:
        norm = _normalize_path_entry(item)
        if not norm:
            continue
        k = _path_key(norm)
        if k in seen:
            continue
        seen.add(k)
        result.append(norm)
    return result


def path_cmd(input_str):
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    sub = args[0].lower() if args else "show"

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])

    if sub in {"show", "get"}:
        effective_list = _effective_path_list(persistent_path_list, temp_path_list)
        _print("_47_\n", items=[os.pathsep.join(effective_list)])
        _print("_48_\n", items=[str(len(persistent_path_list))])
        _print("_49_\n", items=[str(len(temp_path_list))])
        return

    if sub == "list":
        _print("_50_\n", items=[str(len(persistent_path_list))])
        for idx, entry in enumerate(persistent_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        _print("_52_\n", items=[str(len(temp_path_list))])
        for idx, entry in enumerate(temp_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        return

    if sub in {"add", "rm", "remove"}:
        if len(args) < 2:
            _print("_60_\n", "red")
            return

        raw_value = args[1]
        value = _normalize_path_entry(raw_value)
        if not value:
            _print("_60_\n", "red")
            return

        flags = set(a.lower() for a in args[2:])
        use_temp = ("-t" in flags) or ("--temp" in flags)
        use_persist = (
            ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        )
        use_all = ("--all" in flags) or ("-a" in flags)
        if not (use_temp or use_persist or use_all):
            use_persist = True
        if use_all:
            use_temp = True
            use_persist = True

        if sub == "add":
            added_any = False
            if use_persist:
                if _path_key(value) in {
                    _path_key(_normalize_path_entry(p)) for p in persistent_path_list
                }:
                    _print("_55_\n", "yellow", [value])
                else:
                    persistent_path_list.append(value)
                    persistent["PATH"] = persistent_path_list
                    if _save_persistent_env(persistent):
                        _print("_53_\n", items=[value])
                        added_any = True
            if use_temp:
                if _path_key(value) in {
                    _path_key(_normalize_path_entry(p)) for p in temp_path_list
                }:
                    _print("_55_\n", "yellow", [value])
                else:
                    temp_path_list.append(value)
                    _TEMP_ENV["PATH"] = temp_path_list
                    _print("_54_\n", items=[value])
                    added_any = True

            if not added_any:
                return
            return

        # rm/remove
        removed_any = False
        if use_persist:
            before = list(persistent_path_list)
            persistent_path_list = [
                p
                for p in persistent_path_list
                if _path_key(_normalize_path_entry(p)) != _path_key(value)
            ]
            if len(before) != len(persistent_path_list):
                persistent["PATH"] = persistent_path_list
                if _save_persistent_env(persistent):
                    _print("_56_\n", items=[value])
                    removed_any = True
        if use_temp:
            before = list(temp_path_list)
            temp_path_list = [
                p
                for p in temp_path_list
                if _path_key(_normalize_path_entry(p)) != _path_key(value)
            ]
            if len(before) != len(temp_path_list):
                _TEMP_ENV["PATH"] = temp_path_list
                _print("_57_\n", items=[value])
                removed_any = True

        if not removed_any:
            _print("_58_\n", "yellow", [value])
        return

    if sub == "clear":
        flags = set(a.lower() for a in args[1:])
        use_temp = ("-t" in flags) or ("--temp" in flags)
        use_persist = (
            ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags)
        )
        use_all = ("--all" in flags) or ("-a" in flags)
        if use_all:
            use_temp = True
            use_persist = True
        if not (use_temp or use_persist):
            _print("_61_\n", "red")
            return

        if use_persist:
            persistent["PATH"] = []
            if _save_persistent_env(persistent):
                _print("_59_\n")
        if use_temp:
            _TEMP_ENV["PATH"] = []
            _print("_62_\n")
        return

    _print("_65_\n", "red", [sub])


def env_cmd(input_str):
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    var = args[0].upper() if args else "PATH"
    if var != "PATH":
        # fallback to actual process env for other vars
        _print("_66_\n", items=[var, os.environ.get(var, "")])
        return

    persistent = _load_persistent_env()
    persistent_path_list = persistent.get("PATH", [])
    temp_path_list = _TEMP_ENV.get("PATH", [])
    effective_list = _effective_path_list(persistent_path_list, temp_path_list)
    _print("_66_\n", items=["PATH", os.pathsep.join(effective_list)])
