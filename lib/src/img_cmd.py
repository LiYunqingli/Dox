"""img 命令实现：解析参数后在终端以低分辨率查看图片。"""

from lib.lib import _print, get_run_path


# 指定一个路径在控制台显示图片（低分辨率）
def img_cmd(input_str):
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

    # 去掉成对的包裹引号
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

    # 解析渲染参数
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

    # test 关键字指向内置示例图片
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
