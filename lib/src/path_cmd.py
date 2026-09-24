"""path 命令实现：PATH 条目的查看、增删与清空（临时 + 永久）。

PATH 在 Dox 环境变量体系中属于“用户变量”，且是列表型变量：
- 永久条目保存在 config/path.json，由 lib/env.py 统一读写；
- 临时条目仅存在于当前进程，Dox 退出即丢失。

用法：
    path                 查看生效 PATH（临时 + 永久去重合并）
    path list            分别列出永久/临时条目
    path add <目录> [-p|-t|--all]
    path rm <目录> [-p|-t|--all]
    path clear [-p|-t|--all]
"""

from lib.lib import _print
from lib import env


def _parse_scope(flags, default=env.SCOPE_PERSIST):
    """解析 -p/--persist、-t/--temp、--all 作用域开关。"""
    flags = set(f.lower() for f in flags)
    if ("--all" in flags) or ("-a" in flags):
        return "all"
    if ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags):
        return env.SCOPE_PERSIST
    if ("-t" in flags) or ("--temp" in flags):
        return env.SCOPE_TEMP
    return default


def path_cmd(input_str):
    """path 命令入口。"""
    import os
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    sub = args[0].lower() if args else "show"

    persistent_path_list = env.path_entries(env.SCOPE_PERSIST)
    temp_path_list = env.path_entries(env.SCOPE_TEMP)

    # show/get：输出合并后的生效 PATH 与条目统计
    if sub in {"show", "get"}:
        effective_list = env.get_path_list()
        _print("_47_\n", items=[os.pathsep.join(effective_list)])
        _print("_48_\n", items=[str(len(persistent_path_list))])
        _print("_49_\n", items=[str(len(temp_path_list))])
        return

    # list：分别列出永久与临时条目
    if sub == "list":
        _print("_50_\n", items=[str(len(persistent_path_list))])
        for idx, entry in enumerate(persistent_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        _print("_52_\n", items=[str(len(temp_path_list))])
        for idx, entry in enumerate(temp_path_list, start=1):
            _print("_51_\n", items=[str(idx), str(entry)])
        return

    # add / rm：解析作用域后交给环境变量模块处理
    if sub in {"add", "rm", "remove"}:
        if len(args) < 2:
            _print("_60_\n", "red")
            return

        value = env.normalize_path_entry(args[1])
        if not value:
            _print("_60_\n", "red")
            return

        scope = _parse_scope(args[2:], default=env.SCOPE_PERSIST)
        # --all 时两个作用域都处理
        targets = [env.SCOPE_PERSIST, env.SCOPE_TEMP] if scope == "all" else [scope]

        if sub == "add":
            statuses = []
            for target in targets:
                statuses.append(
                    env.add_path(value, persist=(target == env.SCOPE_PERSIST))
                )
            if all(s == "exists" for s in statuses):
                _print("_55_\n", "yellow", [value])
                return
            for target, status in zip(targets, statuses):
                if status != "ok":
                    continue
                if target == env.SCOPE_PERSIST:
                    _print("_53_\n", items=[value])
                else:
                    _print("_54_\n", items=[value])
            return

        # rm/remove
        statuses = []
        for target in targets:
            statuses.append(env.remove_path(value, scope=target))
        if all(s == "notfound" for s in statuses):
            _print("_58_\n", "yellow", [value])
            return
        for target, status in zip(targets, statuses):
            if status != "ok":
                continue
            if target == env.SCOPE_PERSIST:
                _print("_56_\n", items=[value])
            else:
                _print("_57_\n", items=[value])
        return

    # clear：必须显式指定作用域，避免误清空
    if sub == "clear":
        scope = _parse_scope(args[1:], default=None)
        if scope not in {"all", env.SCOPE_PERSIST, env.SCOPE_TEMP}:
            _print("_61_\n", "red")
            return
        env.clear_path(scope=scope)
        if scope in {"all", env.SCOPE_PERSIST}:
            _print("_59_\n")
        if scope in {"all", env.SCOPE_TEMP}:
            _print("_62_\n")
        return

    _print("_65_\n", "red", [sub])
