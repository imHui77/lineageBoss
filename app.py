import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import sys


class BossSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss Selector")

        # 使用 sys._MEIPASS 处理打包后的路径问题
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # will set the sys.frozen attribute and the app folder can be found in sys._MEIPASS.
            self.boss_dir = os.path.join(sys._MEIPASS, "Boss")
        else:
            # If the application is run as a script, the app folder will be found in the current directory.
            self.boss_dir = os.path.join(os.getcwd(), "Boss")

        self.bosses = [d for d in os.listdir(self.boss_dir) if os.path.isdir(os.path.join(self.boss_dir, d))]

        self.selected_bosses = {boss: tk.BooleanVar() for boss in self.bosses}
        self.target_dir = None

        # 選擇資料夾狀態
        self.folders_selected = False

        tk.Label(self.root, text="選擇要出現光柱的BOSS").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=10)

        initial_width = 400
        initial_height = 600

        content_frame = tk.Frame(self.root)
        content_frame.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

        checkbutton_frame = tk.Frame(content_frame)
        checkbutton_frame.pack(anchor=tk.W, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # BOSS 按鈕
        for index, boss in enumerate(self.bosses):
            cb = tk.Checkbutton(checkbutton_frame, text=boss, variable=self.selected_bosses[boss], onvalue=1,
                                offvalue=0)
            cb.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)

        # 檢查是否有
        self.check_eat_exe_label = tk.Label(self.root, text="尚未檢查目標資料夾", fg="red")
        self.check_eat_exe_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        self.target_dir_label = tk.Label(self.root, text="尚未選擇天堂資料夾", fg="red")
        self.target_dir_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW, pady=10)

        tk.Button(button_frame, text="選擇目標資料夾", command=self.choose_target_folder).grid(row=2, column=0, padx=10,
                                                                                               pady=10)
        # 視窗左上方放置一個全選的按鈕
        tk.Button(button_frame, text="全選", command=lambda event=True: self.select_all(event)).grid(row=1, column=1,
                                                                                                     padx=10, pady=10)

        # 視窗右上方放置一個取消全選的按鈕
        tk.Button(button_frame, text="取消全選", command=lambda event=False: self.select_all(event)).grid(row=1,
                                                                                                          column=2,
                                                                                                          padx=10,
                                                                                                          pady=10)

        tk.Label(button_frame, text="製作人: 九兒").grid(row=2, column=3, padx=10, pady=10, sticky=tk.W)

        tk.Button(button_frame, text="開始複製", command=self.copy_selected).grid(row=2, column=4, padx=10, pady=10)

        # 進度條
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=6, column=0, columnspan=4, pady=10)

        self.root.update_idletasks()

        # 動態調整視窗寬度和高度
        total_rows = (len(self.bosses) + 3) // 4  # 每行4個，計算總行數
        new_height = max(initial_height, total_rows * 30 + 150)  # 估算每行高度並添加額外空間
        new_width = max(initial_width, self.root.winfo_reqwidth() + 20)  # 估算所需寬度並添加額外空間

        self.root.geometry(
            f"{new_width}x{new_height}+{int((self.root.winfo_screenwidth() - new_width) / 2)}+{int((self.root.winfo_screenheight() - new_height) / 2)}")

    def choose_target_folder(self):
        self.target_dir = filedialog.askdirectory(title="選擇目標資料夾")
        if self.target_dir:
            self.target_dir_label.config(text=f"目標資料夾: {self.target_dir}", fg="green")
            # 檢查目標資料夾中是否存在 eat.exe 文件
            if os.path.isfile(os.path.join(self.target_dir, 'eat.exe')):
                self.check_eat_exe_label.config(text="已找到吃檔程式", fg="green")
            else:
                self.check_eat_exe_label.config(text="未找到吃檔程式(天堂路徑錯誤?)", fg="red")
                return False
        else:
            self.target_dir_label.config(text="尚未選擇天堂資料夾", fg="red")
            self.check_eat_exe_label.config(text="尚未檢查天堂資料夾", fg="red")
            return False

        self.folders_selected = True

    def copy_selected(self):
        if not self.target_dir:
            messagebox.showwarning("Warning", "請先選擇要出現光柱的BOSS！")
            return

        selected_bosses = [boss for boss, var in self.selected_bosses.items() if var.get()]
        total_files = 0
        for boss in selected_bosses:
            src = os.path.join(self.boss_dir, boss, "sprite")
            if os.path.exists(src):
                total_files += len([item for item in os.listdir(src) if item.endswith('.spr')])

        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        for boss in selected_bosses:
            src = os.path.join(self.boss_dir, boss, "sprite")
            if os.path.exists(src):
                for item in os.listdir(src):
                    if item.endswith('.spr'):
                        s = os.path.join(src, item)
                        d = os.path.join(self.target_dir + '\\sprite', item)
                        shutil.copy2(s, d)
                        self.progress["value"] += 1
                        self.root.update_idletasks()

        messagebox.showinfo("Success", "Selected Bosses copied successfully!")

        # 确保 target_dir 和 eat.exe 路径正确
        if os.path.exists(os.path.join(self.target_dir, 'eat.exe')):
            exe_path = os.path.join(self.target_dir, 'eat.exe')
            print(exe_path)
            subprocess.run([exe_path])

    def select_all(self, event=True):
        for boss, var in self.selected_bosses.items():
            var.set(event)


if __name__ == "__main__":
    root = tk.Tk()
    app = BossSelectorApp(root)
    root.mainloop()
