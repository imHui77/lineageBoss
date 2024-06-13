import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk


def create_notebook(app):
    notebook = ttk.Notebook(app.root)
    notebook.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW)

    boss_frame = tk.Frame(notebook)
    notebook.add(boss_frame, text="BOSS")

    skill_frame = tk.Frame(notebook)
    notebook.add(skill_frame, text="技能")

    app.image_label = tk.Label(app.root)
    app.image_label.grid(row=2, column=8, columnspan=4, pady=10)

    create_checkbuttons(boss_frame, app.bosses, app.selected_bosses, app.update_image)
    create_checkbuttons(skill_frame, app.skills, app.selected_skills, app.update_image)


def create_checkbuttons(frame, items, selected_items, update_func):
    for index, item in enumerate(items):
        cb = tk.Checkbutton(
            frame,
            text=item,
            variable=selected_items[item],
            onvalue=1,
            offvalue=0,
            command=lambda i=item: update_func(i)
        )
        cb.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky=tk.W)


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


def update_image(app, name):
    img_path = os.path.join(app.img_dir, name, name + ".gif")
    if os.path.exists(img_path):
        image = Image.open(img_path)
        image = image.resize((200, 300), Image.ANTIALIAS)
        app.photo = ImageTk.PhotoImage(image)
        app.image_label.config(image=app.photo)
    else:
        app.image_label.config(image='')
