from lib.lib import _print, get_config, get_run_path, download


#pck软件包管理器

# 查找软件包
def pck_search(packageName, isOutPut=False):
    import os, json
    releaseFile = get_run_path() + "/../package/Release.json"

    if os.path.exists(releaseFile):
        with open(releaseFile, "r", encoding="utf-8") as f:
            release = json.load(f)
            apps = release["apps"]
            for app in apps:
                if app["name"] == packageName:
                    if isOutPut:
                        #格式化json到字符串
                        _print(json.dumps(app, indent=4, ensure_ascii=False) + "\n", "green")
                        # _print(str(app), "green")
                    return app
                else:
                    continue
            if isOutPut:
                _print("没有找到软件包：'" + packageName + "'\n", "red")
            return None # 没有找到
    else:
        print("Release.json不存在", "red")


# 安装软件包，packages为数组，保存所有需要安装的软件包，ask为True是询问是否安装，为False是直接安装
def pck_install(packages, ask=True):
    print("pck list: " + str(packages))

    def install_packages(packages):
        #首先查找本地列表
        for package in packages:
            _print("正在安装" + package + "\n")

    if ask:
        _print("_32_")
        if input() == "y":
            install_packages(packages)
    else:
        install_packages(packages)

# 软件包依赖关系元数据更新
def pck_update():
    _print("更新软件列表\n")
    #读取本地配置文件中的远程地址
    config = get_config()
    pckConfig = config["Config"]["Pck"]
    pckName = pckConfig["Name"]
    pckAddr = pckConfig["Addr"]
    
    _print("Connecting  " + pckName + "  " + pckAddr + "\n")
    
    import subprocess
    # 简单校验合法性以及服务器连通性（特定目录文件是否存在）
    test_result = subprocess.run(
        ["curl", "-s", f"{pckAddr}/metadata/lastes/version"],
        capture_output=True,
        text=True,
    )

    if test_result.returncode == 0:
        _print("_14_\n", "green")
        #服务器可到达
        dox_version = config["About"]["Version"]
        releaseFile = f"{pckAddr}/metadata/{dox_version}/Release.json"
        dox_version_result = subprocess.run(
            ["curl", "-s", releaseFile],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if dox_version_result.returncode == 0:
            _print("远程服务器中找到了\n")
            #下载Release.json
            
            #当前目录位置获取
            run_path = get_run_path()
            #下载Release.json
            if download(releaseFile, run_path + "/../package/Release.json"):
                _print("软件包数据更新成功\n", "green")
            else:
                _print("软件包更新失败\n", "red")
                return False


        else:
            _print("你的dox版本不受支持，pck无法找到对应的版本依赖\n")
            pass

        
    else:
        _print("_15_\n", "red")

# 展示元数据中可用package
def pck_list():
    import os, json
    releaseFile = get_run_path() + "/../package/Release.json"

    if os.path.exists(releaseFile):
        with open(releaseFile, "r", encoding="utf-8") as f:
            release = json.load(f)
            _print("可用的软件包\n")
            for package in release["apps"]:
                print(package['name'] + "\t" + package['version'])
    else:
        print("Release.json不存在", "red")