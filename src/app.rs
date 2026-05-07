use std::path::PathBuf;
use std::sync::Arc;

use eframe::egui;

use crate::{
    file_ops::{self, Category},
    preview::PreviewState,
};

fn install_cjk_font(ctx: &egui::Context) {
    let candidates = [
        r"C:\Windows\Fonts\msjh.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
    ];

    let Some(bytes) = candidates.iter().find_map(|p| std::fs::read(p).ok()) else {
        return;
    };

    let mut fonts = egui::FontDefinitions::default();
    let mut data = egui::FontData::from_owned(bytes);
    data.index = 0;
    fonts.font_data.insert("cjk".to_owned(), Arc::new(data));

    fonts
        .families
        .entry(egui::FontFamily::Proportional)
        .or_default()
        .insert(0, "cjk".to_owned());
    fonts
        .families
        .entry(egui::FontFamily::Monospace)
        .or_default()
        .push("cjk".to_owned());

    ctx.set_fonts(fonts);
}

pub struct LineageBossApp {
    root_dir: PathBuf,
    categories: Vec<Category>,
    active_tab: Tab,
    target_dir: Option<PathBuf>,
    status: StatusMessage,
    copied: usize,
    total: usize,
    preview: Option<PreviewState>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Tab {
    Category(usize),
    Help,
    Disclaimer,
}

#[derive(Default)]
struct StatusMessage {
    text: String,
    is_error: bool,
}

impl LineageBossApp {
    pub fn new(cc: &eframe::CreationContext<'_>) -> Self {
        install_cjk_font(&cc.egui_ctx);

        let root_dir = file_ops::default_resource_root();
        let categories = file_ops::scan_categories(&root_dir);
        let active_tab = if categories.is_empty() {
            Tab::Help
        } else {
            Tab::Category(0)
        };

        let status = if categories.is_empty() {
            StatusMessage::error(format!(
                "找不到 public/pubilc 資料夾或沒有可用項目：{}",
                file_ops::get_public_dir(&root_dir).display()
            ))
        } else {
            StatusMessage::ok("尚未選擇天堂資料夾")
        };

        Self {
            root_dir,
            categories,
            active_tab,
            target_dir: None,
            status,
            copied: 0,
            total: 0,
            preview: None,
        }
    }
}

impl eframe::App for LineageBossApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("top_bar").show(ctx, |ui| {
            ui.horizontal_wrapped(|ui| {
                ui.heading("天堂 明顯化");
                ui.separator();
                ui.label(format!("資源目錄：{}", self.root_dir.display()));
            });
        });

        egui::TopBottomPanel::bottom("bottom_bar").show(ctx, |ui| {
            ui.horizontal_wrapped(|ui| {
                if ui.button("選擇目標資料夾").clicked()
                    && let Some(path) = rfd::FileDialog::new().pick_folder()
                {
                    self.target_dir = Some(path);
                    self.update_target_status();
                }

                if ui.button("全選").clicked() {
                    self.set_all(true);
                }

                if ui.button("取消全選").clicked() {
                    self.set_all(false);
                }

                if ui.button("開始").clicked() {
                    self.copy_selected();
                }

                ui.separator();
                ui.label("製作人: 九兒");
            });

            ui.add(
                egui::ProgressBar::new(self.progress())
                    .desired_width(f32::INFINITY)
                    .text(format!("{} / {}", self.copied, self.total)),
            );

            let color = if self.status.is_error {
                egui::Color32::from_rgb(190, 48, 48)
            } else {
                egui::Color32::from_rgb(32, 130, 72)
            };
            ui.colored_label(color, &self.status.text);

            if let Some(target_dir) = &self.target_dir {
                ui.label(format!("天堂資料夾: {}", target_dir.display()));
            }
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            self.show_tabs(ui);
            ui.separator();

            match self.active_tab {
                Tab::Category(index) => self.show_category(ui, index),
                Tab::Help => show_help(ui),
                Tab::Disclaimer => show_disclaimer(ui),
            }
        });

        if let Some(preview) = &mut self.preview {
            let mut open = true;
            preview.show(ctx, &mut open);
            if !open {
                self.preview = None;
            }
        }
    }
}

impl LineageBossApp {
    fn show_tabs(&mut self, ui: &mut egui::Ui) {
        ui.horizontal_wrapped(|ui| {
            for category_index in 0..self.categories.len() {
                let selected = self.active_tab == Tab::Category(category_index);
                if ui
                    .selectable_label(selected, &self.categories[category_index].display_name)
                    .clicked()
                {
                    self.active_tab = Tab::Category(category_index);
                }
            }

            if ui
                .selectable_label(self.active_tab == Tab::Help, "使用說明")
                .clicked()
            {
                self.active_tab = Tab::Help;
            }
            if ui
                .selectable_label(self.active_tab == Tab::Disclaimer, "免責聲明")
                .clicked()
            {
                self.active_tab = Tab::Disclaimer;
            }
        });
    }

    fn show_category(&mut self, ui: &mut egui::Ui, index: usize) {
        let Some(category) = self.categories.get_mut(index) else {
            return;
        };

        let category_disk = category.disk_name.clone();
        let mut preview_request = None;
        egui::ScrollArea::vertical().show(ui, |ui| {
            egui::Grid::new(format!("category_grid_{index}"))
                .num_columns(4)
                .spacing([18.0, 8.0])
                .show(ui, |ui| {
                    for (item_index, item) in category.items.iter_mut().enumerate() {
                        ui.horizontal(|ui| {
                            ui.checkbox(&mut item.checked, &item.display_name);
                            if item.has_images && ui.small_button("[S]").clicked() {
                                preview_request = Some((
                                    item.display_name.clone(),
                                    item.disk_name.clone(),
                                    category_disk.clone(),
                                ));
                            }
                        });

                        if item_index % 4 == 3 {
                            ui.end_row();
                        }
                    }
                });
        });

        if let Some((display, item_disk, category_disk)) = preview_request {
            self.open_preview(display, item_disk, category_disk);
        }
    }

    fn open_preview(&mut self, display: String, item_disk: String, category_disk: String) {
        let paths = file_ops::image_paths_for_item(&self.root_dir, &category_disk, &item_disk);
        if paths.is_empty() {
            self.status = StatusMessage::error(format!("在 {display} 中未找到圖片檔案"));
            return;
        }

        self.preview = Some(PreviewState::new(display, paths));
    }

    fn set_all(&mut self, checked: bool) {
        for category in &mut self.categories {
            for item in &mut category.items {
                item.checked = checked;
            }
        }
    }

    fn selected_items(&self) -> Vec<(String, Vec<String>)> {
        self.categories
            .iter()
            .filter_map(|category| {
                let items = category
                    .items
                    .iter()
                    .filter(|item| item.checked)
                    .map(|item| item.disk_name.clone())
                    .collect::<Vec<_>>();

                if items.is_empty() {
                    None
                } else {
                    Some((category.disk_name.clone(), items))
                }
            })
            .collect()
    }

    fn copy_selected(&mut self) {
        let Some(target_dir) = &self.target_dir else {
            self.status = StatusMessage::error("請先選擇天堂資料夾！");
            return;
        };

        let selected = self.selected_items();
        if selected.is_empty() {
            self.status = StatusMessage::error("請先選擇要出現光柱的項目！");
            return;
        }

        let report = file_ops::copy_selected(&self.root_dir, target_dir, &selected);
        self.total = report.total;
        self.copied = report.copied;

        if report.errors.is_empty() {
            self.status = StatusMessage::ok(format!("已完成複製，共 {} 個檔案。", report.copied));
        } else {
            self.status = StatusMessage::error(format!(
                "已複製 {} / {} 個檔案，另有 {} 個錯誤。",
                report.copied,
                report.total,
                report.errors.len()
            ));
        }

        if file_ops::check_eat_exe(target_dir)
            && let Err(err) = file_ops::run_eat_exe(target_dir)
        {
            self.status = StatusMessage::error(format!("檔案已複製，但 eat.exe 執行失敗: {err}"));
        }
    }

    fn update_target_status(&mut self) {
        let Some(target_dir) = &self.target_dir else {
            self.status = StatusMessage::error("尚未選擇天堂資料夾");
            return;
        };

        if file_ops::check_eat_exe(target_dir) {
            self.status = StatusMessage::ok("已找到吃檔程式");
        } else {
            self.status = StatusMessage::error("未找到吃檔程式(天堂路徑錯誤?)");
        }
    }

    fn progress(&self) -> f32 {
        if self.total == 0 {
            0.0
        } else {
            self.copied as f32 / self.total as f32
        }
    }
}

impl StatusMessage {
    fn ok(text: impl Into<String>) -> Self {
        Self {
            text: text.into(),
            is_error: false,
        }
    }

    fn error(text: impl Into<String>) -> Self {
        Self {
            text: text.into(),
            is_error: true,
        }
    }
}

fn show_help(ui: &mut egui::Ui) {
    egui::ScrollArea::vertical().show(ui, |ui| {
        ui.heading("使用說明");
        ui.add_space(8.0);
        ui.label("• 運行該程式後需自行吃檔");
        ui.label("• 選擇項目後點擊「開始」按鈕進行處理");
        ui.label("• 點擊項目旁的 [S] 按鈕可預覽圖片");
        ui.label("• 支援多種圖片格式：PNG、JPG、GIF、BMP、WEBP");
        ui.label("• GIF 檔案會自動播放動畫效果");
    });
}

fn show_disclaimer(ui: &mut egui::Ui) {
    egui::ScrollArea::vertical().show(ui, |ui| {
        ui.colored_label(egui::Color32::RED, "免責聲明");
        ui.add_space(8.0);
        ui.label("本程式中部分圖片及功能係引用自第三方資源，相關版權及權利歸原作者所有。");
        ui.label("對於第三方資源的正確性、完整性或合法性，本程式不作任何保證。");
        ui.label("使用本程式所造成之任何損害或法律責任，本程式開發者不負任何責任。");
        ui.label("使用者應自行確認並遵守相關版權及法律規定。");
    });
}
