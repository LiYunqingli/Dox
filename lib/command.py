"""
命令分发入口：解析用户输入并路由到 lib/commands/ 下的各命令实现。

职责约定：
- 本文件只负责“路由”，具体命令逻辑一律放在 lib/commands/ 中（AI 相关命令在 lib/agent/）；
- 各命令实现按需惰性导入，避免启动时加载重依赖（PIL / OpenCV / requests 等）；
- 通用基础能力（配置、路径、语言、输出、rm、download）由 lib/core/base.py 提供。
"""

from lib.core.base import _print, get_about, clear, rm, get_run_path, download


# 处理交互命令
def command(input_str):
    input_str = input_str.strip()
    if input_str.startswith("&"):
        from lib.commands.network import network_cmd

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
        # 属于彩蛋，在help文档中不应该记录关于此命令的信息及用法
        from lib.commands.donghua import donghua

        donghua()
    elif command.lower() == "cd":
        from lib.commands.cd import cd

        if len(input_list) > 1:
            cd(input_list[1])
        else:
            _print("_8_\n")
    elif command.lower() == "ls":
        from lib.commands.ls import ls_cmd

        ls_cmd(input_str)
    elif command.lower() == "ll":
        from lib.commands.ls import ls_cmd

        ls_cmd(input_str)
    elif command.lower() == "pwd":
        from lib.commands.pwd import pwd

        pwd()
    elif command.lower() == "cat":
        from lib.commands.cat import cat

        cat(input_str)
    elif command.lower() == "cmd":
        from lib.commands.cmd import cmd_cmd

        cmd_cmd(input_str)
    elif command.lower() == "help":
        from lib.commands.help import help_cmd

        help_cmd(input_str)
    elif command.lower() == "video":
        from lib.commands.video import video_cmd

        video_cmd(input_str)
    elif command.lower() == "img":
        from lib.commands.img import img_cmd

        img_cmd(input_str)
    elif command.lower() == "pck":
        from lib.commands.pck import pck_cmd

        pck_cmd(input_str)
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
        from lib.commands.path import path_cmd

        path_cmd(input_str)
    elif command.lower() == "env":
        from lib.commands.env import env_cmd

        env_cmd(input_str)
    elif command.lower() == "set":
        from lib.commands.set import set_config

        set_config(input_str)
    elif command.lower() == "update":
        from lib.commands.update import update

        update()
    elif command.lower() == "dox":
        from lib.commands.img import img_cmd

        path = get_run_path() + "/../resources/img/dox.png"
        img_cmd(f'img "{path}"')
    elif command.lower() == "chat":
        from lib.agent.chat import chat_cmd

        chat_cmd(input_str)
    elif command == "?":
        from lib.agent.chat import ai_run_cmd

        ai_run_cmd(input_str)
    elif command == "sc":
        # 脚本执行器
        from lib.commands.script import script_cmd

        script_cmd(input_str)
    else:
        _print("_2_" + command + "\n")
