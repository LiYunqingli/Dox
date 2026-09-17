"""pck 命令实现：软件包管理器的参数解析与子命令分发。"""

from lib.lib import _print


# 软件包管理器
def pck_cmd(input_str):
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
