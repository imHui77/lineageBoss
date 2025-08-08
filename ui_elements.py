import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

# 全域變數追蹤目前開啟的預覽視窗
current_preview_window = None


def create_notebook(app):
    notebook = ttk.Notebook(app.root)
    notebook.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

    # 動態創建頁籤
    for category_name, items in app.categories.items():
        frame = tk.Frame(notebook)
        notebook.add(frame, text=category_name)
        create_checkbuttons(frame, items, app.selected_items[category_name], app)
    
    # 創建說明頁籤
    create_info_tab(notebook)
    
    # 創建免責聲明頁籤
    create_disclaimer_tab(notebook)


def create_checkbuttons(frame, items, selected_items, app_instance):
    for index, item in enumerate(items):
        # 創建一個框架來放置checkbox和[S]按鈕
        item_frame = tk.Frame(frame)
        item_frame.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)
        
        cb = tk.Checkbutton(
            item_frame,
            text=item,
            variable=selected_items[item],
            onvalue=1,
            offvalue=0
        )
        cb.grid(row=0, column=0, sticky=tk.W)
        
        # 檢查該項目是否有圖片，如果有就顯示[S]按鈕
        if has_images_in_project(app_instance, item):
            show_btn = tk.Button(
                item_frame,
                text="[S]",
                font=("Arial", 8),
                fg="blue",
                bd=0,
                padx=2,
                pady=0,
                command=lambda i=item: show_image_popup(app_instance, i)
            )
            show_btn.grid(row=0, column=1, sticky=tk.W)


def create_buttons(app):
    button_frame = tk.Frame(app.root)
    button_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW, pady=10)

    tk.Button(button_frame, text="選擇目標資料夾", command=app.choose_target_folder).grid(row=2, column=0, padx=10,
                                                                                          pady=10)
    # tk.Button(button_frame, text="全選", command=lambda event=True: app.select_all(event)).grid(row=1, column=1,
    #                                                                                             padx=10, pady=10)
    # tk.Button(button_frame, text="取消全選", command=lambda event=False: app.select_all(event)).grid(row=1, column=2,
    #                                                                                                  padx=10, pady=10)
    tk.Label(button_frame, text="製作人: 九兒").grid(row=2, column=3, padx=10, pady=10, sticky=tk.W)
    tk.Button(button_frame, text="開始", command=app.copy_selected).grid(row=2, column=4, padx=10, pady=10)


def create_info_tab(notebook):
    """創建說明頁籤"""
    info_frame = tk.Frame(notebook)
    notebook.add(info_frame, text="使用說明")
    
    # 創建滾動區域
    canvas = tk.Canvas(info_frame)
    scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # 說明內容
    info_text = """
使用說明

• 運行該程式後需自行吃檔

• 選擇項目後點擊「開始」按鈕進行處理

• 點擊項目旁的 [S] 按鈕可預覽圖片

• 支援多種圖片格式：PNG、JPG、GIF、BMP、WEBP

• GIF 檔案會自動播放動畫效果
    """
    
    info_label = tk.Label(scrollable_frame, text=info_text, 
                         font=("Arial", 11), justify=tk.LEFT, 
                         wraplength=500, anchor="nw")
    info_label.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def create_disclaimer_tab(notebook):
    """創建免責聲明頁籤"""
    disclaimer_frame = tk.Frame(notebook)
    notebook.add(disclaimer_frame, text="免責聲明")
    
    # 創建滾動區域
    canvas = tk.Canvas(disclaimer_frame)
    scrollbar = ttk.Scrollbar(disclaimer_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # 免責聲明內容
    disclaimer_text = """
免責聲明

本程式中部分圖片及功能係引用自第三方資源，相關版權及權利歸原作者所有。

對於第三方資源的正確性、完整性或合法性，本程式不作任何保證。

使用本程式所造成之任何損害或法律責任，本程式開發者不負任何責任。

使用者應自行確認並遵守相關版權及法律規定。
    """
    
    disclaimer_label = tk.Label(scrollable_frame, text=disclaimer_text, 
                               font=("Arial", 11), justify=tk.LEFT, 
                               wraplength=500, anchor="nw", fg="red")
    disclaimer_label.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def find_image_in_project_folder(app, item_name):
    """在項目資料夾中搜尋圖片檔案"""
    # 支援的圖片格式
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    # 搜尋所有類別資料夾
    for category_name, items in app.categories.items():
        if item_name in items:
            # 找到項目所在的類別資料夾
            category_path = os.path.join(app.root_dir, "pubilc", category_name, item_name)
            if not os.path.exists(category_path):
                category_path = os.path.join(app.root_dir, "public", category_name, item_name)
            
            if os.path.exists(category_path):
                # 遞迴搜尋該資料夾中的所有圖片檔案
                for root, dirs, files in os.walk(category_path):
                    for file in files:
                        file_lower = file.lower()
                        for ext in image_extensions:
                            if file_lower.endswith(ext):
                                return os.path.join(root, file)
    
    return None


def has_images_in_project(app, item_name):
    """檢查項目資料夾中是否有圖片檔案"""
    # 支援的圖片格式
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    # 搜尋所有類別資料夾
    for category_name, items in app.categories.items():
        if item_name in items:
            # 找到項目所在的類別資料夾
            category_path = os.path.join(app.root_dir, "pubilc", category_name, item_name)
            if not os.path.exists(category_path):
                category_path = os.path.join(app.root_dir, "public", category_name, item_name)
            
            if os.path.exists(category_path):
                # 遞迴搜尋該資料夾中是否有圖片檔案
                for root, dirs, files in os.walk(category_path):
                    for file in files:
                        file_lower = file.lower()
                        for ext in image_extensions:
                            if file_lower.endswith(ext):
                                return True
    
    return False


def get_all_images_in_project(app, item_name):
    """獲取項目資料夾中的所有圖片檔案路徑"""
    image_paths = []
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    
    # 搜尋所有類別資料夾
    for category_name, items in app.categories.items():
        if item_name in items:
            # 找到項目所在的類別資料夾
            category_path = os.path.join(app.root_dir, "pubilc", category_name, item_name)
            if not os.path.exists(category_path):
                category_path = os.path.join(app.root_dir, "public", category_name, item_name)
            
            if os.path.exists(category_path):
                # 遞迴搜尋該資料夾中的所有圖片檔案
                for root, dirs, files in os.walk(category_path):
                    for file in files:
                        file_lower = file.lower()
                        for ext in image_extensions:
                            if file_lower.endswith(ext):
                                image_paths.append(os.path.join(root, file))
    
    return image_paths


def show_image_popup(app, item_name):
    """顯示圖片彈出視窗"""
    global current_preview_window
    
    try:
        # 關閉前一個預覽視窗
        if current_preview_window:
            try:
                if current_preview_window.winfo_exists():
                    current_preview_window.destroy()
            except tk.TclError:
                # 視窗已經不存在
                pass
            current_preview_window = None
        
        image_paths = get_all_images_in_project(app, item_name)
        
        if not image_paths:
            messagebox.showinfo("提示", f"在 {item_name} 中未找到圖片檔案")
            return
        
        # 創建彈出視窗
        popup = tk.Toplevel(app.root)
        popup.title(f"{item_name} - 圖片預覽")
        popup.resizable(True, True)
        
        # 設定為目前的預覽視窗
        current_preview_window = popup
        
        # 創建主框架
        main_frame = tk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 創建圖片顯示區域
        image_label = tk.Label(main_frame, bg="white", relief="sunken", bd=2)
        image_label.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # 創建圖片列表和控制按鈕
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        current_image_index = [0]
        current_gif_frames = []
        current_gif_index = [0]
        animation_job = [None]
        
        def stop_animation():
            """停止GIF動畫"""
            if animation_job[0]:
                popup.after_cancel(animation_job[0])
                animation_job[0] = None
        
        def animate_gif():
            """播放GIF動畫"""
            if current_gif_frames and len(current_gif_frames) > 1:
                try:
                    frame = current_gif_frames[current_gif_index[0]]
                    image_label.config(image=frame)
                    current_gif_index[0] = (current_gif_index[0] + 1) % len(current_gif_frames)
                    animation_job[0] = popup.after(100, animate_gif)  # 100ms間隔
                except:
                    pass
        
        def load_image(index):
            """載入指定索引的圖片"""
            if 0 <= index < len(image_paths):
                try:
                    # 停止之前的動畫
                    stop_animation()
                    current_gif_frames.clear()
                    
                    image_path = image_paths[index]
                    filename = os.path.basename(image_path)
                    file_ext = filename.lower().split('.')[-1]
                    
                    # 更新圖片信息（只顯示順序）
                    info_label.config(text=f"第 {index + 1} 張 / 共 {len(image_paths)} 張")
                    
                    # 先載入圖片獲取原始尺寸
                    if file_ext == 'gif':
                        # 處理GIF檔案
                        gif_image = Image.open(image_path)
                        original_width, original_height = gif_image.size
                        frames = []
                        
                        # 計算合適的顯示尺寸
                        screen_width = popup.winfo_screenwidth()
                        screen_height = popup.winfo_screenheight()
                        max_width = min(original_width + 100, int(screen_width * 0.6))
                        max_height = min(original_height + 150, int(screen_height * 0.8))
                        
                        # 計算圖片縮放比例
                        scale_x = (max_width - 100) / original_width if original_width > (max_width - 100) else 1
                        scale_y = (max_height - 150) / original_height if original_height > (max_height - 150) else 1
                        scale = min(scale_x, scale_y, 1)  # 不放大，只縮小
                        
                        display_width = int(original_width * scale)
                        display_height = int(original_height * scale)
                        
                        try:
                            while True:
                                # 調整每一幀的大小
                                frame = gif_image.copy()
                                if scale < 1:
                                    frame = frame.resize((display_width, display_height), Image.Resampling.LANCZOS)
                                photo_frame = ImageTk.PhotoImage(frame)
                                frames.append(photo_frame)
                                gif_image.seek(gif_image.tell() + 1)
                        except EOFError:
                            pass  # 到達GIF結尾
                        
                        if frames:
                            current_gif_frames.extend(frames)
                            current_gif_index[0] = 0
                            image_label.config(image=frames[0])
                            
                            # 調整視窗大小
                            popup.geometry(f"{max_width}x{max_height}")
                            
                            if len(frames) > 1:
                                animate_gif()
                    else:
                        # 處理靜態圖片
                        image = Image.open(image_path)
                        original_width, original_height = image.size
                        
                        # 計算合適的視窗尺寸
                        screen_width = popup.winfo_screenwidth()
                        screen_height = popup.winfo_screenheight()
                        max_width = min(original_width + 100, int(screen_width * 0.6))
                        max_height = min(original_height + 150, int(screen_height * 0.8))
                        
                        # 計算圖片縮放比例
                        scale_x = (max_width - 100) / original_width if original_width > (max_width - 100) else 1
                        scale_y = (max_height - 150) / original_height if original_height > (max_height - 150) else 1
                        scale = min(scale_x, scale_y, 1)  # 不放大，只縮小
                        
                        if scale < 1:
                            display_width = int(original_width * scale)
                            display_height = int(original_height * scale)
                            image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                        
                        photo = ImageTk.PhotoImage(image)
                        image_label.config(image=photo)
                        image_label.image = photo  # 保持引用
                        
                        # 調整視窗大小
                        popup.geometry(f"{max_width}x{max_height}")
                        
                except Exception as e:
                    image_label.config(image='', text=f"無法載入圖片: {str(e)}")
                    print(f"圖片載入錯誤: {e}")  # 用於調試
        
        def prev_image():
            if image_paths and len(image_paths) > 1:
                current_image_index[0] = (current_image_index[0] - 1) % len(image_paths)
                load_image(current_image_index[0])
        
        def next_image():
            if image_paths and len(image_paths) > 1:
                current_image_index[0] = (current_image_index[0] + 1) % len(image_paths)
                load_image(current_image_index[0])
        
        def on_popup_close():
            """視窗關閉時的清理操作"""
            global current_preview_window
            stop_animation()
            if current_preview_window == popup:
                current_preview_window = None
            popup.destroy()
        
        # 創建控制按鈕
        button_frame = tk.Frame(control_frame)
        button_frame.pack(side=tk.TOP, pady=5)
        
        if len(image_paths) > 1:
            tk.Button(button_frame, text="◀ 上一張", command=prev_image).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="下一張 ▶", command=next_image).pack(side=tk.RIGHT, padx=5)
        
        # 圖片信息標籤
        info_label = tk.Label(control_frame, text="", font=("Arial", 10))
        info_label.pack(pady=5)
        
        # 關閉按鈕
        tk.Button(button_frame, text="關閉", command=on_popup_close).pack(side=tk.BOTTOM, pady=5)
        
        # 設置關閉事件
        popup.protocol("WM_DELETE_WINDOW", on_popup_close)
        
        # 載入第一張圖片以確定視窗尺寸
        load_image(0)
        
        # 讓彈出視窗置於最上層
        popup.transient(app.root)
        popup.focus_set()
        
        # 設定視窗位置在主視窗靠右
        popup.update_idletasks()
        app.root.update_idletasks()
        
        # 獲取主視窗的位置和大小
        main_x = app.root.winfo_x()
        main_y = app.root.winfo_y()
        main_width = app.root.winfo_width()
        main_height = app.root.winfo_height()
        
        # 獲取預覽視窗的大小
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        
        # 計算預覽視窗位置（主視窗右側）
        x = main_x + main_width + 10  # 主視窗右側，留10px間距
        y = main_y  # 與主視窗頂部對齊
        
        # 確保視窗不會超出螢幕右邊
        screen_width = popup.winfo_screenwidth()
        if x + popup_width > screen_width:
            x = screen_width - popup_width - 10
        
        popup.geometry(f"+{x}+{y}")
        
    except Exception as e:
        messagebox.showerror("錯誤", f"打開圖片預覽視窗時發生錯誤: {str(e)}")
        print(f"彈出視窗錯誤: {e}")  # 用於調試
