import os
import shutil


def check_eat_exe(app):
    if os.path.isfile(os.path.join(app.target_dir, 'eat.exe')):
        app.check_eat_exe_label.config(text="已找到吃檔程式", fg="green")
    else:
        app.check_eat_exe_label.config(text="未找到吃檔程式(天堂路徑錯誤?)", fg="red")
        return False


def copy_files_to_sprite(app, all_selected):
    total_files = 0
    
    # 確定 public 資料夾路徑
    public_dir = os.path.join(app.root_dir, "pubilc")
    if not os.path.exists(public_dir):
        public_dir = os.path.join(app.root_dir, "public")
    
    # 計算總檔案數
    for category_name, selected_items in all_selected.items():
        category_dir = os.path.join(public_dir, category_name)
        for item in selected_items:
            # 計算 sprite 資料夾中的 .spr 檔案
            sprite_src = os.path.join(category_dir, item, "sprite")
            if os.path.exists(sprite_src):
                total_files += len([f for f in os.listdir(sprite_src) if f.lower().endswith('.spr')])
            
            # 計算 icon 資料夾中的 .tbt 檔案
            icon_src = os.path.join(category_dir, item, "icon")
            if os.path.exists(icon_src):
                total_files += len([f for f in os.listdir(icon_src) if f.lower().endswith('.tbt')])

    # 複製檔案
    for category_name, selected_items in all_selected.items():
        category_dir = os.path.join(public_dir, category_name)
        for item in selected_items:
            # 複製 sprite 資料夾中的 .spr 檔案
            sprite_src = os.path.join(category_dir, item, "sprite")
            if os.path.exists(sprite_src):
                sprite_dest_dir = os.path.join(str(app.target_dir), 'sprite')
                # 確保目標 sprite 資料夾存在
                os.makedirs(sprite_dest_dir, exist_ok=True)
                
                for file_item in os.listdir(sprite_src):
                    if file_item.lower().endswith('.spr'):
                        s = os.path.join(sprite_src, file_item)
                        d = os.path.join(sprite_dest_dir, file_item)
                        try:
                            shutil.copy2(s, d)
                            app.progress["value"] += 1
                            app.root.update_idletasks()
                        except Exception as e:
                            print(f"Error copying sprite {s} to {d}: {e}")
            
            # 複製 icon 資料夾中的 .tbt 檔案
            icon_src = os.path.join(category_dir, item, "icon")
            if os.path.exists(icon_src):
                icon_dest_dir = os.path.join(str(app.target_dir), 'icon')
                # 確保目標 icon 資料夾存在
                os.makedirs(icon_dest_dir, exist_ok=True)
                
                for file_item in os.listdir(icon_src):
                    if file_item.lower().endswith('.tbt'):
                        s = os.path.join(icon_src, file_item)
                        d = os.path.join(icon_dest_dir, file_item)
                        try:
                            shutil.copy2(s, d)
                            app.progress["value"] += 1
                            app.root.update_idletasks()
                        except Exception as e:
                            print(f"Error copying icon {s} to {d}: {e}")
    
    return total_files
