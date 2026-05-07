# 天堂BOSS明顯化 - Rust 編譯指南

## 環境需求
- Rust 1.94+
- Cargo
- Windows 10+（目標平台）

## 安裝 Rust

請使用 rustup 安裝：

```powershell
winget install Rustlang.Rustup
```

安裝後確認版本：

```bash
rustc --version
cargo --version
```

## 開發指令

### 格式化
```bash
cargo fmt
```

### 測試
```bash
cargo test
```

### 本機執行
```bash
cargo run
```

## 編譯成 exe

### 基本編譯
```bash
cargo build --release
```

輸出位置：

```text
target/release/lineage_boss_visualization.exe
```

### 使用 build.bat

`build.bat` 會清理舊輸出、執行 release 編譯，並把 exe 複製到：

```text
dist/LineageBossVisualization/LineageBossVisualization.exe
```

執行：

```bat
build.bat
```

同時建立 zip：

```bat
build.bat release
```

## 資源資料夾

Rust 版不再使用 PyInstaller 打包資源。請將 `pubilc/` 或 `public/` 放在 exe 同一層：

```text
dist/
└── LineageBossVisualization/
    ├── LineageBossVisualization.exe
    └── pubilc/
        ├── BOSS/
        ├── skills/
        └── other/
```

程式啟動時會優先找 `pubilc/`，找不到時改找 `public/`。

## 支援的檔案類型

1. Sprite 檔案 `.spr`
   - 來源：`項目/sprite/`
   - 目標：天堂遊戲的 `sprite/`

2. Icon 檔案 `.tbt`
   - 來源：`項目/icon/`
   - 目標：天堂遊戲的 `icon/`

3. 預覽圖片
   - PNG、JPG、JPEG、GIF、BMP、WEBP

## 清理

```bash
cargo clean
```

或刪除：
- `target/`
- `dist/`
