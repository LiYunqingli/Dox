"""video 命令实现：解析参数后在终端播放视频（低分辨率渲染）。"""

from lib.lib import _print, get_run_path


# 指定一个路径在控制台播放视频
def video_cmd(input_str):
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

    # 去掉成对的包裹引号
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

    # 解析播放参数
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

    # test 关键字指向内置示例视频
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
