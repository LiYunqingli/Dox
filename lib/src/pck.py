from lib.lib import _print, get_config, get_run_path, download


#pck软件包管理器

# 安装软件包，packages为数组，保存所有需要安装的软件包，ask为True是询问是否安装，为False是直接安装
def pck_install(packages, ask=True):
    print(str(packages))
    if ask:
        # 查询本地
        pass
    else:
        for package in packages:
            print("正在安装" + package)

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
            if download(releaseFile, run_path + "/../downloads/Release.json"):
                _print("获取软件包数据成功\n", "green")
            else:
                _print("软件包获取失败\n", "red")
                return False


        else:
            _print("你的dox版本不受支持，pck无法找到对应的版本依赖\n")
            pass

        
    else:
        _print("_15_\n", "red")