"""ls / ll 命令实现：增强版目录列表。"""

from lib.lib import _print, _enable_virtual_terminal_processing


def ls_cmd(input_str: str) -> None:
    """解析并执行 ls/ll（增强版）。

    兼容原行为：
      - `ls`：短列表
      - `ls -l` / `ll`：详细列表

    额外支持：
      - `-a`：显示隐藏文件（以 . 开头）
      - `-1`：单列输出
      - `-r`：反向排序
      - `--sort name|time|size`：指定排序字段
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

    # 逐个解析参数
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

        # 未知的选项
        if a.startswith("-"):
            _print("_13_\n", "red")
            return

        # 路径参数（最多一个）
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

    # 计算字符串的终端显示宽度（中文等宽字符按 2 列计）
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

    # 按显示宽度右侧补空格
    def _pad(s: str, width: int) -> str:
        return s + (" " * max(width - _display_width(s), 0))

    # 将字节数转换为易读容量
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

    # 格式化修改时间
    def _format_mtime(ts: float) -> str:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))

    # 格式化权限位（rwxrwxrwx）
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

    # 按条目类型着色（目录蓝、链接青、可执行绿、隐藏文件暗淡）
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

    # 校验目标目录
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

    # 采集目录项信息
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

    # 排序取值函数
    def key_value(e: _Entry):
        if sort_key == "time":
            return e.mtime
        if sort_key == "size":
            return e.size
        return e.name.casefold()

    # 组合排序键：目录优先 + 指定字段
    def combined_key(e: _Entry):
        prefix = 0
        if dirs_first:
            prefix = 0 if e.is_dir else 1
        return (prefix, key_value(e))

    entries = sorted(entries, key=combined_key, reverse=reverse)

    # 详细列表
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

    # 短格式列表：预先计算纯文本与带色文本
    labels_plain: list[str] = []
    labels_colored: list[str] = []
    widths: list[int] = []
    for e in entries:
        suffix = "/" if e.is_dir else "@" if e.is_link else ""
        plain = f"{e.name}{suffix}"
        labels_plain.append(plain)
        labels_colored.append(_colorize(plain, e))
        widths.append(_display_width(plain))

    # 单列输出
    if one_per_line:
        for s in labels_colored:
            _print(s + "\n")
        return

    # 获取终端列数以计算多列布局
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

    # 按列优先顺序逐行输出，超宽名称做省略处理
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
