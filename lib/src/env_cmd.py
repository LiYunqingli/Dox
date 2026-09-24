"""env 命令实现：Dox 环境变量的查看与管理。

变量作用域（Dox 内部概念）：
- 系统变量：来源 config/config.json，进入 Dox 时读入内存，使用 env refresh 刷新；
- 永久变量：用户添加，写入 config/path.json，重启后仍存在（-p/--persist）；
- 临时变量：用户添加，仅当前进程有效（默认作用域）。

用法：
    env                       列出全部变量（临时/永久/系统）
    env list [-t|-p|-s|--all] 按作用域列出变量
    env get <名>              查看变量值与来源
    env <名>                  等价于 env get <名>
    env set <名> <值> [-p|-s] 设置变量（默认临时；-s 写回 config.json）
    env unset <名> [-t|-p|--all]  删除用户变量
    env clear [-t|-p|--all]   清空用户变量
    env refresh               重新读取 config.json 与 path.json
    env path                  查看 PATH（等价于 path show）
"""

from lib.lib import _print, _msg
from lib import env


# 解析作用域开关，返回 all/persist/temp/system
def _parse_scope(flags, default="all"):
    flags = set(f.lower() for f in flags)
    if ("--all" in flags) or ("-a" in flags):
        return "all"
    if ("-s" in flags) or ("--system" in flags):
        return env.SCOPE_SYSTEM
    if ("-p" in flags) or ("--persist" in flags) or ("--permanent" in flags):
        return env.SCOPE_PERSIST
    if ("-t" in flags) or ("--temp" in flags) or ("--temporary" in flags):
        return env.SCOPE_TEMP
    return default


# 取作用域的中文/本地化名称
def _scope_label(scope):
    key = {
        env.SCOPE_TEMP: "101",
        env.SCOPE_PERSIST: "102",
        env.SCOPE_SYSTEM: "103",
        env.SCOPE_PROCESS: "104",
    }.get(scope)
    if key is None:
        return str(scope)
    return _msg(key) or str(scope)


# 输出一个变量的值与其来源
def _print_var(name, value, scope):
    _print("_66_", items=[name, value])
    _print("  " + _scope_label(scope) + "\n", "cyan")


def _list_scope(scope):
    """输出某个作用域下的变量清单。"""
    data = env.list_vars(scope)
    if scope == env.SCOPE_TEMP:
        _print("_81_\n", items=[str(len(data))])
    elif scope == env.SCOPE_PERSIST:
        _print("_82_\n", items=[str(len(data))])
    else:
        _print("_83_\n", items=[str(len(data))])
    for key in sorted(data.keys()):
        _print("_100_\n", items=[key, str(data[key])])


def env_cmd(input_str):
    """env 命令入口。"""
    import shlex

    try:
        parts = shlex.split(input_str, posix=False)
    except Exception:
        parts = input_str.split()

    args = parts[1:]
    sub = args[0].lower() if args else "list"

    # 无参数：列出全部作用域
    if not args:
        for scope in (env.SCOPE_TEMP, env.SCOPE_PERSIST, env.SCOPE_SYSTEM):
            _list_scope(scope)
        return

    # list：按作用域列出
    if sub in {"list", "ls", "all"}:
        scope = _parse_scope(args[1:], default="all")
        if scope == "all":
            for one in (env.SCOPE_TEMP, env.SCOPE_PERSIST, env.SCOPE_SYSTEM):
                _list_scope(one)
        else:
            _list_scope(scope)
        return

    # refresh/reload/init：重新读取 config.json 与 path.json
    if sub in {"refresh", "reload", "init"}:
        stats = env.init_env(keep_temp=True)
        _print("_88_\n", "green", [str(stats[env.SCOPE_SYSTEM])])
        _print(
            "_89_\n",
            "green",
            [str(stats[env.SCOPE_PERSIST] + stats[env.SCOPE_TEMP])],
        )
        return

    # set：设置用户变量（-s 写回 config.json 成为系统变量）
    if sub in {"set", "add"}:
        if len(args) < 3:
            _print("_90_\n", "red")
            return
        name = args[1]
        value = args[2]
        flags = args[3:]
        if any(f.lower() in {"-s", "--system"} for f in flags):
            if not env.normalize_key(name):
                _print("_79_\n", "red")
                return
            if not env.set_config_value(name, value):
                _print("_46_\n", "red", [name])
                return
            _print("_96_\n", "green", [name, value])
            return
        scope = _parse_scope(flags, default=env.SCOPE_TEMP)
        status = env.set_var(name, value, persist=(scope == env.SCOPE_PERSIST))
        if status == "empty":
            _print("_79_\n", "red")
        elif status == "exists":
            _print("_98_\n", "yellow", [value])
        elif scope == env.SCOPE_PERSIST:
            _print("_85_\n", "green", [env.normalize_key(name), value])
        else:
            _print("_84_\n", "green", [env.normalize_key(name), value])
        return

    # unset/rm/remove/del：删除用户变量
    if sub in {"unset", "rm", "remove", "del", "delete"}:
        if len(args) < 2:
            _print("_91_\n", "red")
            return
        name = args[1]
        if env.normalize_key(name) == env.PATH_KEY:
            scope = _parse_scope(args[2:], default="all")
            if scope == env.SCOPE_SYSTEM:
                _print("_91_\n", "red")
                return
            value = next((a for a in args[2:] if not a.startswith("-")), None)

            # 未给路径：按作用域清空 PATH
            if not value:
                env.clear_path(scope=scope)
                if scope in {"all", env.SCOPE_PERSIST}:
                    _print("_59_\n")
                if scope in {"all", env.SCOPE_TEMP}:
                    _print("_62_\n")
                return

            # 给了路径：按作用域逐个移除条目
            targets = (
                [env.SCOPE_PERSIST, env.SCOPE_TEMP] if scope == "all" else [scope]
            )
            statuses = [env.remove_path(value, scope=t) for t in targets]
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

        scope = _parse_scope(args[2:], default="all")
        status = env.unset_var(name, scope=scope)
        if status == "empty":
            _print("_79_\n", "red")
        elif status == "system":
            real_path = env.config_path_of(name)
            _print("_87_\n", "red", [name, real_path, real_path])
        elif status == "notfound":
            _print("_80_\n", "yellow", [name])
        else:
            _print("_86_\n", items=[env.normalize_key(name)])
        return

    # clear：清空用户变量（系统变量不受影响）
    if sub == "clear":
        scope = _parse_scope(args[1:], default=None)
        if scope not in {"all", env.SCOPE_TEMP, env.SCOPE_PERSIST}:
            _print("_92_\n", "red")
            return
        env.clear_vars(scope=scope)
        if scope in {"all", env.SCOPE_PERSIST}:
            _print("_94_\n", "green")
        if scope in {"all", env.SCOPE_TEMP}:
            _print("_93_\n", "green")
        return

    # path：等价于 path show（PATH 是列表型变量）
    if sub == "path":
        from lib.src.path_cmd import path_cmd

        path_cmd("path show")
        return

    # get <名> 或直接 env <名>
    if sub in {"get", "show"}:
        if len(args) < 2:
            _print("_78_\n", "red")
            return
        name = args[1]
    else:
        name = args[0]

    if env.normalize_key(name) == env.PATH_KEY:
        import os

        entries = env.get_path_list()
        _print("_66_\n", items=[env.PATH_KEY, os.pathsep.join(entries)])
        return

    scope = env.get_var_scope(name)
    if scope is None:
        _print("_80_\n", "yellow", [name])
        return
    _print_var(env.normalize_key(name), env.get_var(name, ""), scope)
