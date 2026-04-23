import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from file_operations import get_public_dir

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


def get_images(app, item_name, first_only=False):
    """返回項目資料夾中的圖片路徑列表；first_only=True 時找到第一個即返回。"""
    public_dir = get_public_dir(app.root_dir)
    for category_name, items in app.categories.items():
        if item_name not in items:
            continue
        category_path = os.path.join(public_dir, category_name, item_name)
        if not os.path.exists(category_path):
            continue
        results = []
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if os.path.splitext(file.lower())[1] in IMAGE_EXTENSIONS:
                    if first_only:
                        return [os.path.join(root, file)]
                    results.append(os.path.join(root, file))
        return results
    return []


def _create_scrollable_tab(notebook, tab_title, text, label_kwargs=None):
    frame = tk.Frame(notebook)
    notebook.add(frame, text=tab_title)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    kwargs = {"font": ("Arial", 11), "justify": tk.LEFT, "wraplength": 500, "anchor": "nw"}
    if label_kwargs:
        kwargs.update(label_kwargs)

    tk.Label(scrollable_frame, text=text, **kwargs).pack(
        padx=20, pady=20, fill=tk.BOTH, expand=True
    )

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def create_notebook(app):
    notebook = ttk.Notebook(app.root)
    notebook.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

    for category_name, items in app.categories.items():
        frame = tk.Frame(notebook)
        notebook.add(frame, text=category_name)
        create_checkbuttons(frame, items, app.selected_items[category_name], app)

    _create_scrollable_tab(
        notebook,
        "使用說明",
        """
使用說明

• 運行該程式後需自行吃檔

• 選擇項目後點擊「開始」按鈕進行處理

• 點擊項目旁的 [S] 按鈕可預覽圖片

• 支援多種圖片格式：PNG、JPG、GIF、BMP、WEBP

• GIF 檔案會自動播放動畫效果
    """,
    )

    _create_scrollable_tab(
        notebook,
        "免責聲明",
        """
免責聲明

本程式中部分圖片及功能係引用自第三方資源，相關版權及權利歸原作者所有。

對於第三方資源的正確性、完整性或合法性，本程式不作任何保證。

使用本程式所造成之任何損害或法律責任，本程式開發者不負任何責任。

使用者應自行確認並遵守相關版權及法律規定。
    """,
        label_kwargs={"fg": "red"},
    )


def create_checkbuttons(frame, items, selected_items, app_instance):
    for index, item in enumerate(items):
        item_frame = tk.Frame(frame)
        item_frame.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)

        cb = tk.Checkbutton(
            item_frame,
            text=item,
            variable=selected_items[item],
            onvalue=1,
            offvalue=0,
        )
        cb.grid(row=0, column=0, sticky=tk.W)

        if item in app_instance.items_with_images:
            show_btn = tk.Button(
                item_frame,
                text="[S]",
                font=("Arial", 8),
                fg="blue",
                bd=0,
                padx=2,
                pady=0,
                command=lambda i=item: show_image_popup(app_instance, i),
            )
            show_btn.grid(row=0, column=1, sticky=tk.W)


def create_buttons(app):
    button_frame = tk.Frame(app.root)
    button_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW, pady=10)

    tk.Button(button_frame, text="選擇目標資料夾", command=app.choose_target_folder).grid(
        row=2, column=0, padx=10, pady=10
    )
    tk.Label(button_frame, text="製作人: 九兒").grid(row=2, column=3, padx=10, pady=10, sticky=tk.W)
    tk.Button(button_frame, text="開始", command=app.copy_selected).grid(
        row=2, column=4, padx=10, pady=10
    )


def show_image_popup(app, item_name):
    try:
        if app.preview_window:
            try:
                if app.preview_window.winfo_exists():
                    app.preview_window.destroy()
            except tk.TclError:
                pass
            app.preview_window = None

        image_paths = get_images(app, item_name)

        if not image_paths:
            messagebox.showinfo("提示", f"在 {item_name} 中未找到圖片檔案")
            return

        popup = tk.Toplevel(app.root)
        popup.title(f"{item_name} - 圖片預覽")
        popup.resizable(True, True)
        app.preview_window = popup

        main_frame = tk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        image_label = tk.Label(main_frame, bg="white", relief="sunken", bd=2)
        image_label.pack(pady=5, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        current_image_index = [0]
        current_gif_frames = []
        current_gif_index = [0]
        animation_job = [None]

        def stop_animation():
            if animation_job[0]:
                popup.after_cancel(animation_job[0])
                animation_job[0] = None

        def animate_gif():
            if current_gif_frames and len(current_gif_frames) > 1:
                try:
                    frame = current_gif_frames[current_gif_index[0]]
                    image_label.config(image=frame)
                    current_gif_index[0] = (current_gif_index[0] + 1) % len(current_gif_frames)
                    animation_job[0] = popup.after(100, animate_gif)
                except Exception:
                    pass

        def _calc_display_size(original_width, original_height):
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            max_width = min(original_width + 100, int(screen_width * 0.6))
            max_height = min(original_height + 150, int(screen_height * 0.8))
            scale_x = (max_width - 100) / original_width if original_width > (max_width - 100) else 1
            scale_y = (max_height - 150) / original_height if original_height > (max_height - 150) else 1
            scale = min(scale_x, scale_y, 1)
            return max_width, max_height, scale

        def load_image(index):
            if not (0 <= index < len(image_paths)):
                return
            try:
                stop_animation()
                current_gif_frames.clear()

                image_path = image_paths[index]
                info_label.config(text=f"第 {index + 1} 張 / 共 {len(image_paths)} 張")

                img = Image.open(image_path)
                max_width, max_height, scale = _calc_display_size(*img.size)
                popup.geometry(f"{max_width}x{max_height}")

                file_ext = os.path.splitext(image_path.lower())[1]
                if file_ext == ".gif":
                    frames = []
                    try:
                        while True:
                            frame = img.copy()
                            if scale < 1:
                                w = int(img.size[0] * scale)
                                h = int(img.size[1] * scale)
                                frame = frame.resize((w, h), Image.Resampling.LANCZOS)
                            frames.append(ImageTk.PhotoImage(frame))
                            img.seek(img.tell() + 1)
                    except EOFError:
                        pass

                    if frames:
                        current_gif_frames.extend(frames)
                        current_gif_index[0] = 0
                        image_label.config(image=frames[0])
                        if len(frames) > 1:
                            animate_gif()
                else:
                    if scale < 1:
                        w = int(img.size[0] * scale)
                        h = int(img.size[1] * scale)
                        img = img.resize((w, h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_label.config(image=photo)
                    image_label.image = photo

            except Exception as e:
                image_label.config(image="", text=f"無法載入圖片: {str(e)}")
                print(f"圖片載入錯誤: {e}")

        def prev_image():
            if len(image_paths) > 1:
                current_image_index[0] = (current_image_index[0] - 1) % len(image_paths)
                load_image(current_image_index[0])

        def next_image():
            if len(image_paths) > 1:
                current_image_index[0] = (current_image_index[0] + 1) % len(image_paths)
                load_image(current_image_index[0])

        def on_popup_close():
            stop_animation()
            if app.preview_window == popup:
                app.preview_window = None
            popup.destroy()

        button_frame = tk.Frame(control_frame)
        button_frame.pack(side=tk.TOP, pady=5)

        if len(image_paths) > 1:
            tk.Button(button_frame, text="◀ 上一張", command=prev_image).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="下一張 ▶", command=next_image).pack(side=tk.RIGHT, padx=5)

        info_label = tk.Label(control_frame, text="", font=("Arial", 10))
        info_label.pack(pady=5)

        tk.Button(button_frame, text="關閉", command=on_popup_close).pack(side=tk.BOTTOM, pady=5)

        popup.protocol("WM_DELETE_WINDOW", on_popup_close)
        load_image(0)

        popup.transient(app.root)
        popup.focus_set()
        popup.update_idletasks()
        app.root.update_idletasks()

        main_x = app.root.winfo_x()
        main_y = app.root.winfo_y()
        main_width = app.root.winfo_width()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()

        x = main_x + main_width + 10
        y = main_y
        if x + popup_width > popup.winfo_screenwidth():
            x = popup.winfo_screenwidth() - popup_width - 10

        popup.geometry(f"+{x}+{y}")

    except Exception as e:
        messagebox.showerror("錯誤", f"打開圖片預覽視窗時發生錯誤: {str(e)}")
        print(f"彈出視窗錯誤: {e}")
