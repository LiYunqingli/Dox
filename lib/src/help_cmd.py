"""help 命令实现：根据语言包输出帮助信息。"""

from lib.lib import _print, get_run_path, get_lang


# 打印帮助信息（自动根据语言设置选择对应的语言包）
def help_cmd(input_str):
    """显示帮助信息"""
    items = input_str.split()
    items = items[1:]  # 去掉第一个元素（命令本身）

    def help_print(help_id):
        import json

        lang_file_path = f"{get_run_path()}/../resources/lang/src/{get_lang()}.json"
        with open(lang_file_path, "r", encoding="utf-8") as f:
            help_data = json.load(f)["help"]
        # 全部帮助：只输出各命令的总览说明
        if help_id == "ALL":
            _print("\n_12_\n\n")
            for help_item in help_data:
                print(f"{help_item['msg']}")
            print("\n")
        # 指定命令：输出名称、说明与用法明细
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

    # 未携带参数时输出全部帮助，否则逐个命令输出
    if len(items) == 0:
        help_print("ALL")
    else:
        for item in items:
            # 将参数转换为大写以匹配JSON中的命令名称
            help_print(item.upper())
