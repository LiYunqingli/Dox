from lib.lib import _print
from lib.lib import get_config


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
    
    