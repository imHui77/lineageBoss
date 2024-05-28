import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import sys
from PIL import Image, ImageTk


class BossSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Boss Selector")

        self.img_dir = os.path.join(os.getcwd(), "img")

        if getattr(sys, 'frozen', False):
            self.boss_dir = os.path.join(sys._MEIPASS, "Boss")
        else:
            self.boss_dir = os.path.join(os.getcwd(), "Boss")

        # skills
        if getattr(sys, 'frozen', False):
            self.skills_dir = os.path.join(sys._MEIPASS, "skills")
        else:
            self.skills_dir = os.path.join(os.getcwd(), "skills")

        self.bosses = [d for d in os.listdir(self.boss_dir) if os.path.isdir(os.path.join(self.boss_dir, d))]
        self.skills = [d for d in os.listdir(self.skills_dir) if os.path.isdir(os.path.join(self.skills_dir, d))]

        self.selected_bosses = {boss: tk.BooleanVar() for boss in self.bosses}
        self.selected_skills = {skill: tk.BooleanVar() for skill in self.skills}
        self.target_dir = None


        # 選擇資料夾狀態
        self.folders_selected = False

        tk.Label(self.root, text="選擇要出現光柱的BOSS").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=10)

        initial_width = 800
        initial_height = 600

        # 創建 Notebook
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

        # 創建 BOSS 分頁
        boss_frame = tk.Frame(notebook)
        notebook.add(boss_frame, text="BOSS")

        # 創建技能分頁
        skill_frame = tk.Frame(notebook)
        notebook.add(skill_frame, text="技能")

        # 技能圖片顯示區域
        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=2, column=8, columnspan=4, pady=10)

        # BOSS 按鈕
        for index, boss in enumerate(self.bosses):
            cb = tk.Checkbutton(boss_frame, text=boss, variable=self.selected_bosses[boss], onvalue=1, offvalue=0,
                                command=lambda b=boss: self.update_image(b))
            cb.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)

        # 技能按鈕
        for index, skill in enumerate(self.skills):
            cb = tk.Checkbutton(skill_frame, text=skill, variable=self.selected_skills[skill], onvalue=1, offvalue=0,
                                command=lambda s=skill: self.update_image(s))
            cb.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)

        # 檢查是否有 eat.exe 文件
        self.check_eat_exe_label = tk.Label(self.root, text="尚未檢查目標資料夾", fg="red")
        self.check_eat_exe_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        self.target_dir_label = tk.Label(self.root, text="尚未選擇天堂資料夾", fg="red")
        self.target_dir_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW, pady=10)

        tk.Button(button_frame, text="選擇目標資料夾", command=self.choose_target_folder).grid(row=2, column=0, padx=10, pady=10)

        # 視窗左上方放置一個全選的按鈕
        tk.Button(button_frame, text="全選", command=lambda event=True: self.select_all(event)).grid(row=1, column=1, padx=10, pady=10)

        # 視窗右上方放置一個取消全選的按鈕
        tk.Button(button_frame, text="取消全選", command=lambda event=False: self.select_all(event)).grid(row=1, column=2, padx=10, pady=10)

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
        selected_skills = [skill for skill, var in self.selected_skills.items() if var.get()]
        total_files = 0
        for boss in selected_bosses:
            src = os.path.join(self.boss_dir, boss, "sprite")
            if os.path.exists(src):
                total_files += len([item for item in os.listdir(src) if item.endswith('.spr')])

        for skill in selected_skills:
            src = os.path.join(self.skills_dir, skill, "sprite")
            if os.path.exists(src):
                total_files += len([item for item in os.listdir(src) if item.endswith('.spr')])

        self.progress["maximum"] = total_files
        self.progress["value"] = 0
        self.copy_file_to_sprite(self.boss_dir, selected_bosses)
        self.copy_file_to_sprite(self.skills_dir, selected_skills)
        messagebox.showinfo("Success", "Selected Bosses copied successfully!")

        # 執行eat.exe
        # if os.path.exists(os.path.join(self.target_dir, 'eat.exe')):
        #     exe_path = os.path.join(self.target_dir, 'eat.exe')
        #     subprocess.run([exe_path])

    def select_all(self, event=True):
        for boss, var in self.selected_bosses.items():
            var.set(event)
        for skill, var in self.selected_skills.items():
            var.set(event)

    def copy_file_to_sprite(self, dir, selecteds):
        for d in selecteds:
            src = os.path.join(dir, d, "sprite")
            if os.path.exists(src):
                for item in os.listdir(src):
                    if item.endswith('.spr'):
                        s = os.path.join(src, item)
                        d = os.path.join(self.target_dir + '\\sprite', item)
                        shutil.copy2(s, d)
                        self.progress["value"] += 1
                        self.root.update_idletasks()

    def update_image(self, name):
        img_path = os.path.join(self.img_dir, name, name + ".gif")
        if os.path.exists(img_path):
            image = Image.open(img_path)
            image = image.resize((200, 300), Image.ANTIALIAS)  # 調整圖片大小
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.photo)
        else:
            self.image_label.config(image='')

if __name__ == "__main__":
    root = tk.Tk()
    app = BossSelectorApp(root)
    root.mainloop()
