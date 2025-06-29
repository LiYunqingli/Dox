
from lib.lib import get_run_path, _print

# bookmark 书签管理器(环境变量管理器)

# 新建环境变量
def add_bookmark(name='', value=''):
    if name == '' or value == '':
        return False
    else:
        if check_bookmark(name):
            pass
        else:
            _print("变量名已存在","red")


def check_bookmark(name):
    import os, json
    bookmarkFile = get_run_path() + "/../config/bookmark.json"
    #格式是[{"name":"name","value":"value","type":"type","created_at":""},{...},...]
    #判断name是否存在
    if os.path.exists(bookmarkFile):
        with open(bookmarkFile, "r", encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if i["name"] == name:
                    return True
            return False
    else:
        #创建文件
        with open(bookmarkFile, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)