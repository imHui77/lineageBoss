#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use lineage_boss_visualization::app;

fn main() -> eframe::Result {
    let native_options = eframe::NativeOptions {
        viewport: eframe::egui::ViewportBuilder::default()
            .with_inner_size([760.0, 560.0])
            .with_min_inner_size([520.0, 420.0]),
        ..Default::default()
    };

    eframe::run_native(
        "天堂 明顯化",
        native_options,
        Box::new(|cc| Ok(Box::new(app::LineageBossApp::new(cc)))),
    )
}
