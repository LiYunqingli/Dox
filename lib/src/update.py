def update():
    from lib.lib import _print
    from lib.lib import get_config
    import requests

    local_version = get_config()["About"]["Version"]
    dox_run_style = get_config()["Config"]["RunStyle"]
    _print("当前dox版本为: " + local_version + "\n")

    new_version_url = (
        "http://8.138.142.121/LiHuarong/Dox/raw/branch/main/latest_version"
    )
