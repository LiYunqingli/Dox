"""pwd 命令实现：输出当前工作路径。"""

from lib.lib import _print


# 输出当前工作路径
def pwd():
    """返回当前路径"""
    import os

    path = os.getcwd()
    _print("\n" + path + "\n\n")
    return path
