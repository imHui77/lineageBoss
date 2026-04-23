# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python/Tkinter 桌面应用，用于天堂游戏资源（精灵/图标）的批量可视化与复制。使用 PyInstaller onedir 模式打包为 Windows 应用文件夹。

## 构建与打包

使用 Pipenv 管理依赖：

```bash
pipenv install
```

**一键打包（推荐）**：双击 `build.bat`，自动清理旧构建并编译。
- `build.bat` — 仅编译
- `build.bat release` — 编译 + 打包发布用 zip（`dist/LineageBossVisualization-YYYYMMDD.zip`）

**手动打包**：

```bash
pipenv run python -m PyInstaller LineageBossVisualization.spec
```

输出位置：`dist/LineageBossVisualization/`
- `LineageBossVisualization.exe`（启动器，~2MB）
- `_internal/`（Python runtime + `pubilc/` 资源，~2GB）

**为何使用 onedir 而非 onefile**：`pubilc/` 包含 ~2GB 游戏素材（3300+ 个 `.spr` 文件）。onefile 模式每次启动都会把这些素材解压到 `%TEMP%`，导致 3-10 秒的启动延迟。onedir 模式资源持久化在磁盘上，启动时间 < 1 秒。

## 发布流程

执行 `build.bat release` 生成 `dist/LineageBossVisualization-YYYYMMDD.zip`，上传到 GitHub Releases。用户解压后运行文件夹内的 EXE。

## 代码风格

使用 Black 格式化 Python 代码：

```bash
black .
```

## 分支流程

- 功能开发在 `dev` 分支进行
- 测试通过后合并到 `main`

## 重要注意事项

- `pubilc/` 目录名称是故意保留的拼写错误，**不要重命名**，PyInstaller spec 文件和所有代码均依赖此名称
- `eat.exe` 是游戏配套工具，应用运行时需存在于目标文件夹中
- `.spr` 文件复制到 `sprite/`，`.tbt` 文件复制到 `icon/`
- 无自动化测试，通过手动运行 EXE 验证功能
