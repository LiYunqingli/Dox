"""cat 命令实现：以文本方式显示文件内容，支持首尾截取。"""

from lib.lib import _print


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

    # 解析 -head/-l 与 -tail 参数
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
