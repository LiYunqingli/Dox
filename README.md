# Dox

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-green.svg)

一个轻量的终端交互工具：提供类 Linux 的基础命令体验，并额外支持在终端里“看图/看视频（可选依赖）”、下载文件、以及实验性的包元数据管理（pck）。

## 功能

- **交互式 REPL**：无参数启动进入交互模式
- **单命令/批处理执行**：支持 `python main.py <cmd ...>` 与 `-r "cmd1; cmd2"`
- **类 Linux 常用命令**：`cd` / `ls` / `ll` / `pwd` / `rm` / `clear` / `version`
- **终端渲染**：
  - `img`：将图片低分辨率渲染到终端（彩色块/灰度/纯 ASCII）
  - `video`：将视频以帧方式渲染到终端（需要额外安装 OpenCV）
- **下载器**：`download <url> <path>`（带进度条）
- **多语言输出**：基于 `resources/lang/src/*.json` 的消息映射

## 依赖

### Python

- Python 3.9+（项目中使用了 `tuple[int, int]` 这类类型注解语法）

### 第三方库（pip）

- `requests`：用于 `download` 命令
- `Pillow (PIL)`：用于 `img` / `video` 的帧/图片处理
- `opencv-python`（可选）：仅 `video` 命令需要

依赖清单见 `requirements.txt`。

### 外部命令（可选）

- `curl`：目前 `pck update` 使用 `curl` 做连通性与元数据拉取（需要系统 PATH 可用）

## 安装

```bash
pip install -r requirements.txt
```

如果需要 `video` 命令：

```bash
pip install opencv-python
```

## 运行与使用

### 交互模式

```bash
python main.py
```

进入后使用：

```text
help
ls
ll
cd <path>
pwd
```

### 单命令模式

```bash
python main.py ls -l
python main.py img test
python main.py video test --fps 15
```

### 启动时工作目录（cwd）行为

- 交互模式（无参数启动）：默认 `cd` 到用户 HOME 目录（更像普通 shell 的体验）
- 非交互模式（带参数或 `-r`）：默认 `cd` 到 `main.py` 所在目录（方便从任意目录执行时使用项目相对路径）

可用参数覆盖默认行为：

- `--cd-script` / `--cd-script-dir`：启动时切到脚本目录
- `--cd-home`：启动时切到 HOME
- `--no-cd` / `--keep-cwd`：不改变当前工作目录

### 批处理模式（-r）

```bash
python main.py -r "cd ..; ls; pwd"
```

## 命令概览

| 命令 | 说明 |
| --- | --- |
| `help [cmd]` | 显示帮助（按语言包输出） |
| `version` | 显示版本信息 |
| `cd <path>` | 切换目录 |
| `ls [-l]` / `ll` | 列目录（`-l` 详细信息） |
| `pwd` | 输出当前路径 |
| `clear` | 清屏 |
| `rm [-r] [-f] <path...>` | 删除文件/目录（`-r` 递归，`-f` 强制） |
| `img <path/test> [-w N] [-h N] [--gray] [--no-color]` | 终端看图 |
| `video <path/test> [-w N] [-h N] [--fps N] [--loop] [--gray] [--no-color]` | 终端看视频（可选依赖） |
| `download <url> <path>` | 下载文件（显示进度） |
| `pck <subcmd ...>` | 软件包元数据管理（实验性） |
| `donghua` | 彩蛋动画 |
| `exit` | 退出 |

## 配置

配置文件：`config/config.json`

- `Config.Lang`：语言（例如 `zh-CN` / `en-US`）
- `Config.Pck`：pck 服务器配置（名称/地址）

## pck（实验性）

当前实现以“元数据查询/更新”为主：

- `pck update`：从配置的服务器地址拉取 `package/Release.json`
- `pck list`：列出 Release.json 中的 apps
- `pck search <name>`：查找并输出某个包元数据
- `pck install ...`：目前仍是占位逻辑（会输出待安装列表，但未完成真实安装流程）

## 项目结构

```text
main.py                 入口（参数模式/交互模式）
lib/lib.py              命令分发与通用工具函数
lib/src/img.py           终端图片渲染（Pillow）
lib/src/video.py         终端视频渲染（OpenCV + Pillow）
lib/src/pck.py           pck 元数据相关逻辑
config/config.json       配置
resources/lang/src/*     多语言消息与帮助
package/Release.json     pck 元数据缓存
```

## 贡献

欢迎 PR / Issue。

- 新命令建议放在 `lib/lib.py` 的 `command()` 分发处，并在语言包里补齐 help 文案
- 新增依赖请同步更新 `requirements.txt` 与本 README 的“依赖”章节

## 许可证

MIT，见 LICENSE。