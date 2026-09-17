"""cd 命令实现：切换当前工作目录。"""

from lib.lib import _print


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
