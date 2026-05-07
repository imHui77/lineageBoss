# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python/Tkinter 桌面应用，用于天堂游戏资源（精灵/图标）的批量可视化与复制。使用 PyInstaller onedir 模式打包为 Windows 应用文件夹。

## 构建与打包

使用 Pipenv 管理依赖：

```bash
pipenv install
```

**一键打包（推荐）**：双击 `build.bat`，自动清理旧构建、编译、复制资源到 dist、混淆资源夹名称。
- `build.bat` — 仅编译 + 混淆 dist 资源
- `build.bat release` — 编译 + 混淆 + 打包发布用 zip（`dist/LineageBossVisualization-YYYYMMDD.zip`）

**手动打包**：

```bash
cargo build --release
xcopy /e /i /y pubilc dist\LineageBossVisualization\pubilc
target\release\obfuscate.exe dist\LineageBossVisualization\pubilc --apply
```

输出位置：`dist/LineageBossVisualization/`
- `LineageBossVisualization.exe`（GUI，~5MB）
- `pubilc/`（资源夹名已混淆为 SHA-256 短雜湊；含 AES-256-GCM 加密的 `manifest.bin` 对照表）

**资源夹混淆**：开发时 `pubilc/` 保留中文原名（`Boss/奧塔/...`）；`build.bat` 复制到 dist 时自动重命名为 hash（`6a6ac.../5fb75.../...`）并写入加密 `manifest.bin`。GUI 启动时用嵌入 exe 的 AES key 解密 manifest，UI 显示中文名称。原始 `pubilc/` 永远不会被修改。

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

- `pubilc/` 目录名称是故意保留的拼写错误，**不要重命名**，所有代码均依赖此名称
- `eat.exe` 是游戏配套工具，应用运行时需存在于目标文件夹中
- `.spr` 文件复制到 `sprite/`，`.tbt` 文件复制到 `icon/`
- 测试：`cargo test`（单元测试）+ 手动运行 EXE 验证 GUI
- 混淆工具：`target/release/obfuscate.exe <目录> [--apply] [--reverse]`，预设 dry-run，需明确 `--apply` 才修改磁盘；`--reverse` 可依 manifest 还原原始名称
