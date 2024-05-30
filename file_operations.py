import os
import shutil


def check_eat_exe(app):
    if os.path.isfile(os.path.join(app.target_dir, 'eat.exe')):
        app.check_eat_exe_label.config(text="已找到吃檔程式", fg="green")
    else:
        app.check_eat_exe_label.config(text="未找到吃檔程式(天堂路徑錯誤?)", fg="red")
        return False


def copy_files_to_sprite(app, selected_bosses, selected_skills):
    total_files = 0
    for boss in selected_bosses:
        src = os.path.join(app.boss_dir, boss, "sprite")
        if os.path.exists(src):
            total_files += len([item for item in os.listdir(src) if item.endswith('.spr')])

    for skill in selected_skills:
        src = os.path.join(app.skills_dir, skill, "sprite")
        if os.path.exists(src):
            total_files += len([item for item in os.listdir(src) if item.endswith('.spr')])

    for d in selected_bosses + selected_skills:
        src = os.path.join(app.boss_dir if d in selected_bosses else app.skills_dir, d, "sprite")
        if os.path.exists(src):
            for item in os.listdir(src):
                if item.endswith('.spr'):
                    s = os.path.join(src, item)
                    d = os.path.join(app.target_dir + '\\sprite', item)
                    shutil.copy2(s, d)
                    app.progress["value"] += 1
                    app.root.update_idletasks()
    return total_files
