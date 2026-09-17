"""donghua 命令实现：输出彩色逐字随机色动画（彩蛋）。"""

from lib.lib import get_run_path


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
