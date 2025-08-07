import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from ui_elements import create_notebook, create_buttons
from file_operations import check_eat_exe, copy_files_to_sprite
import subprocess


class BossSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天堂 明顯化")

        self.img_dir = os.path.join(os.getcwd(), "img")
        
        # 動態掃描資料夾邏輯
        self.root_dir = sys._MEIPASS if getattr(sys, 'frozen', False) else os.getcwd()
        self.categories = self.scan_categories()
        
        # 動態創建選擇變數
        self.selected_items = {}
        for category_name, items in self.categories.items():
            self.selected_items[category_name] = {item: tk.BooleanVar() for item in items}
        
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

    def scan_categories(self):
        """動態掃描 pubilc 資料夾下的所有類別資料夾"""
        categories = {}
        
        # 掃描 pubilc 資料夾下的所有子資料夾
        public_dir = os.path.join(self.root_dir, "pubilc")  # 使用你的資料夾名稱
        if not os.path.exists(public_dir):
            # 如果 pubilc 不存在，嘗試 public
            public_dir = os.path.join(self.root_dir, "public")
        
        if os.path.exists(public_dir):
            try:
                for item in os.listdir(public_dir):
                    item_path = os.path.join(public_dir, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        # 掃描該類別資料夾下的所有子項目
                        try:
                            subitems = [d for d in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, d))]
                            if subitems:  # 只有當有子項目時才加入
                                categories[item] = subitems
                        except PermissionError:
                            continue
            except PermissionError:
                pass
        
        return categories

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
            messagebox.showwarning("Warning", "請先選擇天堂資料夾！")
            return

        # 收集所有選中的項目
        all_selected = {}
        for category_name, items in self.selected_items.items():
            selected = [item for item, var in items.items() if var.get()]
            if selected:
                all_selected[category_name] = selected

        if not all_selected:
            messagebox.showwarning("Warning", "請先選擇要出現光柱的項目！")
            return

        total_files = copy_files_to_sprite(self, all_selected)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        messagebox.showinfo("Success", "Selected items copied successfully!")

        # 執行eat.exe
        if os.path.exists(os.path.join(self.target_dir, 'eat.exe')):
            exe_path = os.path.join(self.target_dir, 'eat.exe')
            subprocess.run([exe_path])

    def select_all(self, event=True):
        for category_items in self.selected_items.values():
            for var in category_items.values():
                var.set(event)

    def adjust_window_size(self):
        initial_width = 400
        initial_height = 500
        # 計算所有類別中最大的項目數量
        max_items = max(len(items) for items in self.categories.values()) if self.categories else 0
        total_rows = (max_items + 3) // 4
        new_height = max(initial_height, total_rows * 30 + 150)
        new_width = max(initial_width, self.root.winfo_reqwidth() + 20)

        self.root.geometry(
            f"{new_width}x{new_height}+{int((self.root.winfo_screenwidth() - new_width) / 2)}+{int((self.root.winfo_screenheight() - new_height) / 2)}")

