import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from ui_elements import create_notebook, create_buttons, update_image
from file_operations import check_eat_exe, copy_files_to_sprite
import subprocess


class BossSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天堂 明顯化")

        self.img_dir = os.path.join(os.getcwd(), "img")
        self.boss_dir = os.path.join(sys._MEIPASS, "Boss") if getattr(sys, 'frozen', False) else os.path.join(
            os.getcwd(), "Boss")
        self.skills_dir = os.path.join(sys._MEIPASS, "skills") if getattr(sys, 'frozen', False) else os.path.join(
            os.getcwd(), "skills")

        self.bosses = [d for d in os.listdir(self.boss_dir) if os.path.isdir(os.path.join(self.boss_dir, d))]
        self.skills = [d for d in os.listdir(self.skills_dir) if os.path.isdir(os.path.join(self.skills_dir, d))]

        self.selected_bosses = {boss: tk.BooleanVar() for boss in self.bosses}
        self.selected_skills = {skill: tk.BooleanVar() for skill in self.skills}
        self.target_dir = None
        self.folders_selected = False

        create_notebook(self)
        create_buttons(self)

        self.check_eat_exe_label = tk.Label(self.root, text="尚未檢查目標資料夾", fg="red")
        self.check_eat_exe_label.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        self.target_dir_label = tk.Label(self.root, text="尚未選擇天堂資料夾", fg="red")
        self.target_dir_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=10, pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=6, column=0, columnspan=4, pady=10)

        self.root.update_idletasks()
        self.adjust_window_size()

    def choose_target_folder(self):
        self.target_dir = filedialog.askdirectory(title="選擇天堂資料夾")
        if self.target_dir:
            self.target_dir_label.config(text=f"天堂資料夾: {self.target_dir}", fg="green")
            check_eat_exe(self)
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

        total_files = copy_files_to_sprite(self, selected_bosses, selected_skills)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        messagebox.showinfo("Success", "Selected Bosses copied successfully!")

        # 執行eat.exe
        if os.path.exists(os.path.join(self.target_dir, 'eat.exe')):
            exe_path = os.path.join(self.target_dir, 'eat.exe')
            subprocess.run([exe_path])

    def select_all(self, event=True):
        for var in self.selected_bosses.values():
            var.set(event)
        for var in self.selected_skills.values():
            var.set(event)

    def adjust_window_size(self):
        initial_width = 400
        initial_height = 500
        total_rows = (len(self.bosses) + 3) // 4
        new_height = max(initial_height, total_rows * 30 + 150)
        new_width = max(initial_width, self.root.winfo_reqwidth() + 20)

        self.root.geometry(
            f"{new_width}x{new_height}+{int((self.root.winfo_screenwidth() - new_width) / 2)}+{int((self.root.winfo_screenheight() - new_height) / 2)}")

    def update_image(self, name):
        update_image(self, name)
