def update():
    from lib.lib import _print
    from lib.lib import get_config
    import requests
    

    local_version = get_config()["About"]["Version"]
    _print("当前dox版本为: " + local_version + "\n")

    new_version = "x.x.x"