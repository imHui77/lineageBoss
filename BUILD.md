# 天堂BOSS明顯化 - 編譯指南

## 環境需求
- Python 3.10+
- pipenv 或 pip
- Windows 10+ (目標平台)

## 安裝依賴套件

### 使用 pipenv (推薦)
```bash
pipenv install
pipenv shell
```

### 使用 pip
```bash
pip install pyinstaller pillow
```

## 編譯成 exe 檔案

### 基本編譯指令
```bash
python -m PyInstaller --onefile --windowed --add-data "pubilc;pubilc" --name "LineageBossVisualization" main.py
```

### 參數說明
- `--onefile`: 打包成單一exe檔案
- `--windowed`: 不顯示命令列視窗 (GUI應用程式)
- `--add-data "pubilc;pubilc"`: 包含pubilc資料夾（包含所有類別）到exe中
- `--name "LineageBossVisualization"`: 指定輸出檔案名稱

### 進階選項 (可選)
如果需要自訂圖示：
```bash
python -m PyInstaller --onefile --windowed --add-data "pubilc;pubilc" --add-data "img;img" --icon=img/BOSS.png --name "LineageBossVisualization" main.py
```

## 編譯流程

1. **準備環境**
   ```bash
   cd I:\GitHub\lineageBoss
   ```

2. **安裝 PyInstaller**
   ```bash
   python -m pip install pyinstaller
   ```

3. **執行編譯**
   ```bash
   python -m PyInstaller --onefile --windowed --add-data "pubilc;pubilc" --name "LineageBossVisualization" main.py
   ```

4. **檢查結果**
   編譯完成後，exe檔案會在 `dist/` 資料夾中：
   ```
   dist/LineageBossVisualization.exe
   ```

## 檔案結構說明

編譯時會包含以下資料夾：
- `pubilc/`: 包含所有類別的資料夾
  - `pubilc/BOSS/`: 包含所有BOSS的圖像檔案 (.spr格式)
  - `pubilc/skills/`: 包含所有技能的圖像檔案
  - `pubilc/other/`: 包含其他類別的圖像檔案
  - `pubilc/XX/`: 你新增的任何其他類別
- `img/`: 程式界面用的圖片資源 (可選)

## 支援的檔案類型

程式支援兩種類型的檔案複製：

1. **Sprite 檔案 (.spr)**
   - 來源：`項目/sprite/` 資料夾
   - 目標：天堂遊戲的 `sprite/` 資料夾
   - 用途：遊戲精靈圖像

2. **Icon 檔案 (.tbt)**
   - 來源：`項目/icon/` 資料夾  
   - 目標：天堂遊戲的 `icon/` 資料夾
   - 用途：遊戲圖示檔案

### 項目資料夾結構範例：
```
pubilc/
├── BOSS/
│   ├── 不死鳥/
│   │   └── sprite/          <- .spr 檔案
│   └── 伊弗/
│       └── sprite/          <- .spr 檔案
├── other/
│   └── 王族明顯化/
│       └── icon/            <- .tbt 檔案
└── skills/
    ├── 地屏-中文化/
    │   └── sprite/          <- .spr 檔案
    └── 汙水-中文化/
        └── sprite/          <- .spr 檔案
```

## 注意事項

1. **管理員權限**: PyInstaller可能會顯示不需要管理員權限的警告，這是正常的
2. **檔案大小**: 由於包含大量圖像資源，最終exe檔案會比較大
3. **Windows Defender**: 首次執行時可能被防毒軟體標記，這是正常現象
4. **相容性**: 編譯的exe檔案適用於Windows 10+系統

## 清理編譯檔案

編譯後會產生以下資料夾，可以安全刪除：
- `build/`: 編譯過程中的暫存檔案
- `*.spec`: PyInstaller規格檔案
- `__pycache__/`: Python快取檔案

```bash
# 清理指令 (可選)
rmdir /S build
del *.spec
```

## 疑難排解

### 編譯超時
如果編譯過程超時，可以嘗試：
1. 關閉防毒軟體暫時掃描
2. 使用較少的資源檔案進行測試
3. 增加timeout時間

### 執行時找不到檔案
確保所有資源檔案都正確包含在 `--add-data` 參數中

### 中文檔名問題
建議使用英文檔名避免編碼問題，如範例中的 `LineageBossVisualization`