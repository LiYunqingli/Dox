def update():
    from lib.lib import _print
    from lib.lib import get_config
    from lib.lib import get_config_value
    import requests

    local_version = get_config()["About"]["Version"]
    dox_run_style = get_config()["Config"]["RunStyle"]
    _print("当前dox版本为: " + local_version + "\n")

    # 优先使用配置中的更新地址，缺失时回退到内置默认地址
    new_version_url = get_config_value(
        "Update.LatestVersionURL",
        "http://8.138.142.121/LiHuarong/Dox/raw/branch/main/latest_version",
    )
