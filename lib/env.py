"""Dox 环境变量体系核心（基础层：只负责数据与读写，不负责输出文案）。

概念约定（仅限 Dox 环境内部）：
- 系统变量(system)：来源 config/config.json。进入 Dox 时由 init_env() 读取/刷新，
  以内存快照形式存在；业务代码读取配置一律走本模块，不再直接打开 config.json。
- 用户变量(user)：用户通过 env / path 命令自行添加的变量，分两种：
    - 永久变量(persist)：保存在 config/path.json，重启 Dox 后依然存在；
    - 临时变量(temp)：仅保存在当前进程内，Dox 退出即丢失。

取值优先级：临时变量 > 永久变量 > 系统变量 > 进程真实环境变量(os.environ)。

命名规则：系统变量按 config.json 的点分路径打平为大写下划线形式，
例如 Config.Lang -> CONFIG_LANG、AI.Max_tool_steps -> AI_MAX_TOOL_STEPS。
用户变量同样使用大写下划线形式（写成点分路径也会被归一化）。

持久化文件结构（config/path.json）：
    {
        "PATH": ["/a", "/b"],   # 永久 PATH 路径列表（列表型变量）
        "Vars": {"FOO": "bar"}  # 其它永久用户变量
    }
"""

import json
import os

from lib.lib import get_run_path

# 作用域常量
SCOPE_TEMP = "temp"  # 用户临时变量（仅当前进程）
SCOPE_PERSIST = "persist"  # 用户永久变量（config/path.json）
SCOPE_SYSTEM = "system"  # 系统变量（config/config.json）
SCOPE_PROCESS = "process"  # 兜底：进程真实环境变量 os.environ

# PATH 是列表型变量，单独用列表维护
PATH_KEY = "PATH"

# 进程内状态（退出即释放）
_SYSTEM = {}  # key -> 值（保留 config.json 中的原始类型：str/int/bool）
_SYSTEM_PATHS = {}  # key -> ["AI", "Max_tool_steps"]，用于还原配置结构
_PERSIST_VARS = {}  # key -> str（来自 path.json 的 Vars）
_TEMP_VARS = {}  # key -> str（仅进程内）
_PERSIST_PATH = []  # 永久 PATH 路径列表
_TEMP_PATH = []  # 临时 PATH 路径列表
_LOADED = False  # 是否已完成初始化


# ---------------------------------------------------------------------------
# 路径与文件读写
# ---------------------------------------------------------------------------
def config_file_path():
    """config.json 的绝对路径。"""
    return get_run_path() + "/../config/config.json"


def path_file_path():
    """path.json 的绝对路径（用户永久变量存储位置）。"""
    return get_run_path() + "/../config/path.json"


def _read_json(path, default=None):
    """读取 JSON 文件，失败或结构不符时返回 default。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default
    return data if isinstance(data, dict) else default


def _write_json(path, data):
    """写入 JSON 文件，成功返回 True。"""
    try:
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n")
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 变量名与取值格式化
# ---------------------------------------------------------------------------
def normalize_key(name):
    """把变量名/配置路径归一化为大写下划线形式。

    AI.API_KEY / ai_api_key / AI_API_KEY -> AI_API_KEY
    """
    raw = str(name or "").strip()
    if not raw:
        return ""

    raw = raw.replace(".", "_")
    chars = []
    for ch in raw:
        chars.append(ch if (ch.isalnum() or ch == "_") else "_")
    key = "".join(chars).upper()
    while "__" in key:
        key = key.replace("__", "_")
    return key.strip("_")


def format_value(value):
    """把变量值格式化为可显示的文本。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    if value is None:
        return ""
    return str(value)


def _config_path_segments(key_path):
    """取配置项在 config.json 中的层级路径，如 AI.Max_tool_steps -> ["AI","Max_tool_steps"]。"""
    return [seg for seg in str(key_path or "").split(".") if seg]


# ---------------------------------------------------------------------------
# 初始化 / 刷新
# ---------------------------------------------------------------------------
def _flatten_config(node, prefix, flat, paths):
    """把 config.json 的嵌套结构打平为环境变量表。"""
    for key, value in node.items():
        segments = prefix + [str(key)]
        if isinstance(value, dict):
            _flatten_config(value, segments, flat, paths)
            continue
        env_key = normalize_key("_".join(segments))
        if not env_key:
            continue
        flat[env_key] = value
        paths[env_key] = segments


def _load_user_persist():
    """读取 path.json 中的用户永久变量（含永久 PATH）。"""
    global _PERSIST_PATH

    data = _read_json(path_file_path(), None)
    if data is None:
        # 文件不存在或损坏：初始化一份空结构，保证后续写入正常
        data = {PATH_KEY: [], "Vars": {}}
        _write_json(path_file_path(), data)

    raw_path = data.get(PATH_KEY)
    _PERSIST_PATH = [str(p) for p in raw_path if str(p).strip()] if isinstance(raw_path, list) else []

    _PERSIST_VARS.clear()
    raw_vars = data.get("Vars")
    if isinstance(raw_vars, dict):
        for key, value in raw_vars.items():
            env_key = normalize_key(key)
            if env_key:
                _PERSIST_VARS[env_key] = format_value(value)


def init_env(keep_temp=True):
    """初始化/刷新环境变量（Dox 启动时调用，也可用 `env refresh` 手动刷新）。

    参数：
        keep_temp：是否保留当前进程内的临时变量（默认保留）。

    返回：
        {"system": n, "persist": n, "temp": n} 各作用域的变量数量。
    """
    global _LOADED

    # 1) config.json -> 系统变量
    config_data = _read_json(config_file_path(), {}) or {}
    _SYSTEM.clear()
    _SYSTEM_PATHS.clear()
    _flatten_config(config_data, [], _SYSTEM, _SYSTEM_PATHS)

    # 2) path.json -> 用户永久变量
    _load_user_persist()

    # 3) 临时变量按需保留
    if not keep_temp:
        _TEMP_VARS.clear()
        _TEMP_PATH.clear()

    _LOADED = True
    return {
        SCOPE_SYSTEM: len(_SYSTEM),
        SCOPE_PERSIST: len(_PERSIST_VARS) + len(_PERSIST_PATH),
        SCOPE_TEMP: len(_TEMP_VARS) + len(_TEMP_PATH),
    }


def _ensure_loaded():
    """惰性初始化：保证任何读取入口在未显式初始化时也能工作。"""
    if not _LOADED:
        init_env(keep_temp=True)


def refresh(keep_temp=True):
    """刷新环境变量（init_env 的语义化别名）。"""
    return init_env(keep_temp=keep_temp)


# ---------------------------------------------------------------------------
# 配置读取（系统变量视图）
# ---------------------------------------------------------------------------
def get_config():
    """按 config.json 的结构，用系统变量重建配置字典。

    注意：这里只反映系统变量（config.json）的原始值，不叠加用户临时/永久覆盖，
    因此可直接用于写回配置文件（set 命令、AI 配置补全等）。
    """
    _ensure_loaded()

    root = {}
    for env_key, segments in _SYSTEM_PATHS.items():
        if env_key not in _SYSTEM:
            continue
        node = root
        for seg in segments[:-1]:
            child = node.get(seg)
            if not isinstance(child, dict):
                child = {}
                node[seg] = child
            node = child
        node[segments[-1]] = _SYSTEM[env_key]
    return root


def get_config_value(key_path, default=None):
    """读取配置项：临时变量 > 永久变量 > 系统变量，全都没有时返回 default。"""
    _ensure_loaded()

    key = normalize_key(key_path)
    if not key:
        return default
    if key in _TEMP_VARS:
        return _TEMP_VARS[key]
    if key in _PERSIST_VARS:
        return _PERSIST_VARS[key]
    if key in _SYSTEM:
        return _SYSTEM[key]
    return default


def get_config_int(key_path, default):
    """读取整数配置项，无法转换（缺失/空/非数字）时回退默认值。"""
    try:
        return int(get_config_value(key_path, default))
    except (TypeError, ValueError):
        return default


def _assign_config_value(config_data, key_path, value):
    """在配置字典中写入配置项（自动补全缺失的中间层级）。"""
    segments = _config_path_segments(key_path)
    if not segments:
        return False

    node = config_data
    for seg in segments[:-1]:
        child = node.get(seg)
        if not isinstance(child, dict):
            child = {}
            node[seg] = child
        node = child
    node[segments[-1]] = value
    return True


def save_config(config_data):
    """把配置字典写回 config.json，并自动刷新系统变量。"""
    if not isinstance(config_data, dict):
        return False
    if not _write_json(config_file_path(), config_data):
        return False
    # 配置已变化，重新打平为系统变量（保留用户临时变量）
    init_env(keep_temp=True)
    return True


def set_config_value(key_path, value):
    """修改单个配置项：写回 config.json 并刷新系统变量。"""
    config_data = get_config()
    if not _assign_config_value(config_data, key_path, value):
        return False
    return save_config(config_data)


def update_config_items(items):
    """批量写入多个配置项（键为点分路径），只刷新一次系统变量。"""
    if not isinstance(items, dict) or not items:
        return False

    config_data = get_config()
    changed = False
    for key_path, value in items.items():
        changed = _assign_config_value(config_data, key_path, value) or changed
    if not changed:
        return False
    return save_config(config_data)


# ---------------------------------------------------------------------------
# 便捷读取：系统变量快照
# ---------------------------------------------------------------------------
def system_vars():
    """返回系统变量快照 {key: 原始值}（只读用途，请勿直接修改）。"""
    _ensure_loaded()
    return dict(_SYSTEM)


def system_paths():
    """返回系统变量对应的 config.json 层级路径 {key: [segments]}。"""
    _ensure_loaded()
    return {k: list(v) for k, v in _SYSTEM_PATHS.items()}


def config_path_of(name):
    """返回变量在 config.json 中的点分路径；非系统变量时原样返回变量名。"""
    _ensure_loaded()

    segments = _SYSTEM_PATHS.get(normalize_key(name))
    if not segments:
        return str(name)
    return ".".join(segments)


# ---------------------------------------------------------------------------
# 变量查询
# ---------------------------------------------------------------------------
def get_var(name, default=None):
    """按优先级查询变量值，返回字符串形式；未找到时返回 default。

    查询顺序：临时变量 > 永久变量 > 系统变量 > 进程真实环境变量(os.environ)。
    """
    _ensure_loaded()

    key = normalize_key(name)
    if not key:
        return default

    if key == PATH_KEY:
        entries = get_path_list()
        if not entries:
            return default if default is not None else ""
        return os.pathsep.join(entries)

    if key in _TEMP_VARS:
        return format_value(_TEMP_VARS[key])
    if key in _PERSIST_VARS:
        return format_value(_PERSIST_VARS[key])
    if key in _SYSTEM:
        return format_value(_SYSTEM[key])
    if key in os.environ:
        return os.environ.get(key, default)
    return default


def get_var_scope(name):
    """返回变量所在作用域，未找到时返回 None。"""
    _ensure_loaded()

    key = normalize_key(name)
    if not key:
        return None
    if key == PATH_KEY:
        if _TEMP_PATH or _PERSIST_PATH:
            return SCOPE_TEMP if _TEMP_PATH else SCOPE_PERSIST
        return SCOPE_PROCESS if PATH_KEY in os.environ else None
    if key in _TEMP_VARS:
        return SCOPE_TEMP
    if key in _PERSIST_VARS:
        return SCOPE_PERSIST
    if key in _SYSTEM:
        return SCOPE_SYSTEM
    if key in os.environ:
        return SCOPE_PROCESS
    return None


def list_vars(scope=SCOPE_SYSTEM):
    """列出指定作用域的变量 {key: 显示值}。scope 可取 system/persist/temp。"""
    _ensure_loaded()

    if scope == SCOPE_SYSTEM:
        return {k: format_value(v) for k, v in _SYSTEM.items()}
    if scope == SCOPE_PERSIST:
        data = {k: format_value(v) for k, v in _PERSIST_VARS.items()}
        if _PERSIST_PATH:
            data[PATH_KEY] = os.pathsep.join(_PERSIST_PATH)
        return dict(sorted(data.items()))
    if scope == SCOPE_TEMP:
        data = {k: format_value(v) for k, v in _TEMP_VARS.items()}
        if _TEMP_PATH:
            data[PATH_KEY] = os.pathsep.join(_TEMP_PATH)
        return dict(sorted(data.items()))
    return {}


# ---------------------------------------------------------------------------
# 用户变量写入
# ---------------------------------------------------------------------------
def _save_user_persist():
    """写回 path.json（永久 PATH + 永久变量）。"""
    data = {PATH_KEY: list(_PERSIST_PATH), "Vars": dict(_PERSIST_VARS)}
    return _write_json(path_file_path(), data)


def add_path(entry, persist=False):
    """向 PATH 追加目录。返回 ok / exists / empty。"""
    global _PERSIST_PATH, _TEMP_PATH

    value = normalize_path_entry(entry)
    if not value:
        return "empty"

    target = _PERSIST_PATH if persist else _TEMP_PATH
    if path_key(value) in {path_key(normalize_path_entry(p)) for p in target}:
        return "exists"

    target.append(value)
    if persist:
        _PERSIST_PATH = target
        _save_user_persist()
    else:
        _TEMP_PATH = target
    return "ok"


def remove_path(entry, scope="all"):
    """从 PATH 移除目录。scope 可取 all/persist/temp。返回 ok / notfound / empty。"""
    global _PERSIST_PATH, _TEMP_PATH

    value = normalize_path_entry(entry)
    if not value:
        return "empty"
    target_key = path_key(value)

    removed = False
    if scope in ("all", SCOPE_PERSIST):
        before = len(_PERSIST_PATH)
        _PERSIST_PATH = [
            p for p in _PERSIST_PATH if path_key(normalize_path_entry(p)) != target_key
        ]
        if len(_PERSIST_PATH) != before:
            removed = True
            _save_user_persist()
    if scope in ("all", SCOPE_TEMP):
        before = len(_TEMP_PATH)
        _TEMP_PATH = [
            p for p in _TEMP_PATH if path_key(normalize_path_entry(p)) != target_key
        ]
        if len(_TEMP_PATH) != before:
            removed = True

    return "ok" if removed else "notfound"


def clear_path(scope="all"):
    """清空 PATH。scope 可取 all/persist/temp。"""
    global _PERSIST_PATH, _TEMP_PATH

    if scope in ("all", SCOPE_PERSIST):
        _PERSIST_PATH = []
        _save_user_persist()
    if scope in ("all", SCOPE_TEMP):
        _TEMP_PATH = []
    return "ok"


def get_path_list():
    """返回生效的 PATH 列表（临时在前、永久在后，去重）。"""
    _ensure_loaded()

    seen = set()
    result = []
    for item in list(_TEMP_PATH) + list(_PERSIST_PATH):
        norm = normalize_path_entry(item)
        if not norm:
            continue
        k = path_key(norm)
        if k in seen:
            continue
        seen.add(k)
        result.append(norm)
    return result


def path_entries(scope=SCOPE_PERSIST):
    """返回指定作用域的原始 PATH 列表。"""
    _ensure_loaded()
    if scope == SCOPE_TEMP:
        return list(_TEMP_PATH)
    return list(_PERSIST_PATH)


def set_var(name, value, persist=False):
    """设置用户变量（PATH 走 add_path）。

    返回 ok / exists / empty。
    """
    _ensure_loaded()

    key = normalize_key(name)
    if not key:
        return "empty"
    if key == PATH_KEY:
        return add_path(value, persist=persist)

    if persist:
        _PERSIST_VARS[key] = format_value(value)
        _save_user_persist()
    else:
        _TEMP_VARS[key] = format_value(value)
    return "ok"


def unset_var(name, value=None, scope="all"):
    """删除用户变量。

    - 普通变量：按 scope(all/persist/temp) 删除；
    - PATH：给了 value 则移除该目录，未给 value 则按 scope 清空。
    返回 ok / notfound / system / empty。
    """
    _ensure_loaded()

    key = normalize_key(name)
    if not key:
        return "empty"

    if key == PATH_KEY:
        if value:
            return remove_path(value, scope=scope)
        clear_path(scope=scope)
        return "ok"

    removed = False
    if scope in ("all", SCOPE_TEMP) and key in _TEMP_VARS:
        del _TEMP_VARS[key]
        removed = True
    if scope in ("all", SCOPE_PERSIST) and key in _PERSIST_VARS:
        del _PERSIST_VARS[key]
        _save_user_persist()
        removed = True

    if removed:
        return "ok"
    # 系统变量不允许删除：请通过 set / env set -s 修改配置文件
    if key in _SYSTEM:
        return "system"
    return "notfound"


def clear_vars(scope="all"):
    """清空用户变量（含用户 PATH）。系统变量不受影响。"""
    global _PERSIST_VARS, _TEMP_VARS

    if scope in ("all", SCOPE_PERSIST):
        _PERSIST_VARS = {}
        _PERSIST_PATH.clear()
        _save_user_persist()
    if scope in ("all", SCOPE_TEMP):
        _TEMP_VARS = {}
        _TEMP_PATH.clear()
    return "ok"


# ---------------------------------------------------------------------------
# 路径工具
# ---------------------------------------------------------------------------
def normalize_path_entry(p):
    """去掉引号与首尾空白，展开 ~ 并规范化路径。"""
    text = str(p or "").strip().strip('"').strip("'")
    if text == "":
        return ""
    return os.path.normpath(os.path.expanduser(text))


def path_key(p):
    """生成用于去重比较的路径键（大小写与分隔符归一）。"""
    return os.path.normcase(os.path.normpath(p))
