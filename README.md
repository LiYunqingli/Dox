# Dox 终端工具

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-green.svg)

一个跨平台的命令行工具，提供类Linux操作体验，支持视频播放、多语言交互和丰富的扩展功能。

## 🌟 功能特性

- **类Linux命令** - 支持常用命令如 `ls`, `cd`, `pwd`, `clear` 等
- **多语言支持** - 中英文双语切换（默认中文）
- **彩色终端输出** - 支持多种颜色和高亮显示
- **视频播放** - 直接在控制台播放视频（测试视频彩蛋）
- **批处理模式** - 支持通过参数批量执行命令
- **扩展框架** - 模块化设计，易于功能扩展

## 📥 安装与运行

### 前置要求
- Python 3.7+
- 推荐终端：
  - Windows: Windows Terminal / PowerShell
  - Linux/macOS: 默认终端

```bash
# 克隆仓库
git clone https://gitea.lihuarong.cn:8080/LiHuarong/Dox.git
cd Dox
# 安装依赖
pip install -r requirements.txt
# 运行程序
python main.py

```

## 📖 使用说明

### 交互模式

```bash
help
cd Documents
Documents >> ls -l
```

### 命令行参数模式

```bash
# 单命令模式
python main.py ls -l
# 批量命令模式
python main.py -r "cd /; ls; pwd"
```

## 📚 命令手册

| 命令 | 描述 | 使用示例 |
| --- | --- | --- |
| ```help``` | 显示帮助信息 | help ls |
| ```cd``` | 切换工作目录 | cd ../ |
| ```ls``` | 列出目录内容 | ls -l (详细模式) |
| ```ll``` | 同 ls -l | ll |
| ```pwd``` | 显示当前路径 | pwd |
| ```clear``` | 清空屏幕 | clear |
| ```version``` | 显示版本信息 | version |
| ```video``` | 播放视频 | video test (测试视频) |
| ```img``` | 查看图片（低分辨率渲染） | img test / img D:\\a.png |
| ```exit``` | 退出程序 | exit |

## 🌍 多语言支持

修改 config/config.json 中的语言设置：

```json
{
  "Config": {
    "Lang": "zh-CN"  // 可选 en-US
  }
}
```

## 🛠️ 开发与贡献

欢迎提交 Pull Request 或 Issue，共同改进项目。请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (git checkout -b feature/your-feature)
3. 提交修改 (git commit -m 'Add some feature')
4. 推送到分支 (git push origin feature/your-feature)
5. 创建 Pull Request

代码规范：

- 清晰的目录架构，核心功能和附加功能分开不同的文件封装
- 新增功能需添加对应单元测试
- 修改语言文件需同步更新中英文版本
- 代码注释清晰，便于他人理解和维护
- config.json 文件中新增配置项需添加注释说明

## 📜 许可证

本项目遵循 MIT 许可证。请查看 LICENSE 文件了解更多信息。

## 🎮 彩蛋功能

输入 ```donghua``` 命令体验特殊动画效果（开发者预留惊喜）

## 🛠️ 功能路线图

### ✅ 已实现功能

**核心功能**
- [x] 类Linux文件系统操作（ls/cd/pwd）
- [x] 多语言支持系统（中/英文）
- [x] 终端彩色输出系统
- [x] 批处理命令模式（-r参数）
- [x] 控制台视频播放器（ASCII渲染）

**先进的**
- [x] Windows/Linux/macOS多平台适配
- [x] 动态路径自动补全
- [x] 权限错误处理机制
- [x] 安全命令沙箱环境

### 🔜 未来规划
**包管理 (pck)** 🚧
- [x] `pck install` - 安装Dox生态软件包
- [ ] `pck remove` - 卸载Dox生态软件包
- [x] `pck list` - 列出已安装的Dox生态软件包
- [x] `pck install package -y` - 忽略确认安装
- [x] `pck search` - 搜索可用软件包
- [x] `pck update` - 更新本地软件仓库
- [ ] `pck build` - 创建自定义软件包

**扩展插件**
- [ ] 插件热加载框架
- [x] 官方软件包市场
- [ ] 沙箱化插件运行时
- [ ] 插件签名验证系统

**终端增强**
- [ ] 客户端局域网集成
- [ ] 终端主题商店（配色方案）
- [x] ASCII艺术生成器

**游戏 & 娱乐** 🎮
- [ ] 终端贪吃蛇游戏
- [ ] 每日开发者彩蛋

**DevOps工具**
- [ ] 内置HTTP服务器
- [ ] 开发者常用工具

**安全**
- [ ] 操作审计日志
- [x] 加密文件保险箱