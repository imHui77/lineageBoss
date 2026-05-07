use std::{
    fs::File,
    io::BufReader,
    path::{Path, PathBuf},
    time::{Duration, Instant},
};

use eframe::egui;
use image::{AnimationDecoder, ImageReader, codecs::gif::GifDecoder};

pub struct PreviewState {
    pub item_name: String,
    pub paths: Vec<PathBuf>,
    pub index: usize,
    frames: Vec<PreviewFrame>,
    frame_index: usize,
    last_tick: Instant,
    loaded_path: Option<PathBuf>,
    error: Option<String>,
}

struct PreviewFrame {
    texture: egui::TextureHandle,
    delay: Duration,
    size: egui::Vec2,
}

impl PreviewState {
    pub fn new(item_name: String, paths: Vec<PathBuf>) -> Self {
        Self {
            item_name,
            paths,
            index: 0,
            frames: Vec::new(),
            frame_index: 0,
            last_tick: Instant::now(),
            loaded_path: None,
            error: None,
        }
    }

    pub fn show(&mut self, ctx: &egui::Context, open: &mut bool) {
        let viewport_id = egui::ViewportId::from_hash_of(("preview", &self.item_name));
        let title = format!("{} - 圖片預覽", self.item_name);

        let mut should_close = false;

        ctx.show_viewport_immediate(
            viewport_id,
            egui::ViewportBuilder::default()
                .with_title(&title)
                .with_inner_size([560.0, 460.0])
                .with_min_inner_size([320.0, 240.0]),
            |ctx, _class| {
                egui::CentralPanel::default().show(ctx, |ui| {
                    if self.paths.is_empty() {
                        ui.label("未找到圖片檔案");
                        return;
                    }

                    self.ensure_loaded(ctx);

                    ui.horizontal(|ui| {
                        if ui
                            .add_enabled(self.paths.len() > 1, egui::Button::new("上一張"))
                            .clicked()
                        {
                            self.previous();
                        }

                        ui.label(format!(
                            "第 {} 張 / 共 {} 張",
                            self.index + 1,
                            self.paths.len()
                        ));

                        if ui
                            .add_enabled(self.paths.len() > 1, egui::Button::new("下一張"))
                            .clicked()
                        {
                            self.next();
                        }
                    });

                    ui.separator();

                    if let Some(error) = &self.error {
                        ui.colored_label(egui::Color32::RED, error);
                        return;
                    }

                    if self.frames.is_empty() {
                        ui.label("載入中...");
                        return;
                    }

                    self.advance_animation(ctx);
                    let frame = &self.frames[self.frame_index];
                    let available = ui.available_size();
                    let display_size = fit_size(frame.size, available);
                    ui.add(egui::Image::new((frame.texture.id(), display_size)));
                });

                if ctx.input(|i| i.viewport().close_requested()) {
                    should_close = true;
                }
            },
        );

        if should_close {
            *open = false;
        }
    }

    fn previous(&mut self) {
        if self.paths.is_empty() {
            return;
        }
        self.index = if self.index == 0 {
            self.paths.len() - 1
        } else {
            self.index - 1
        };
        self.loaded_path = None;
    }

    fn next(&mut self) {
        if self.paths.is_empty() {
            return;
        }
        self.index = (self.index + 1) % self.paths.len();
        self.loaded_path = None;
    }

    fn ensure_loaded(&mut self, ctx: &egui::Context) {
        let path = self.paths.get(self.index).cloned();
        if path.is_none() || self.loaded_path == path {
            return;
        }

        let path = path.unwrap();
        self.frames.clear();
        self.frame_index = 0;
        self.error = None;
        self.last_tick = Instant::now();

        let result = if is_gif(&path) {
            load_gif(ctx, &path)
        } else {
            load_static_image(ctx, &path)
        };

        match result {
            Ok(frames) => self.frames = frames,
            Err(err) => self.error = Some(format!("無法載入圖片: {err}")),
        }

        self.loaded_path = Some(path);
    }

    fn advance_animation(&mut self, ctx: &egui::Context) {
        if self.frames.len() <= 1 {
            return;
        }

        let delay = self.frames[self.frame_index].delay;
        if self.last_tick.elapsed() >= delay {
            self.frame_index = (self.frame_index + 1) % self.frames.len();
            self.last_tick = Instant::now();
        }

        ctx.request_repaint_after(delay);
    }
}

fn load_static_image(ctx: &egui::Context, path: &Path) -> Result<Vec<PreviewFrame>, String> {
    let image = ImageReader::open(path)
        .map_err(|err| err.to_string())?
        .decode()
        .map_err(|err| err.to_string())?
        .to_rgba8();

    Ok(vec![frame_from_rgba(
        ctx,
        path,
        0,
        image,
        Duration::from_millis(100),
    )])
}

fn load_gif(ctx: &egui::Context, path: &Path) -> Result<Vec<PreviewFrame>, String> {
    let file = File::open(path).map_err(|err| err.to_string())?;
    let decoder = GifDecoder::new(BufReader::new(file)).map_err(|err| err.to_string())?;
    let frames = decoder
        .into_frames()
        .collect_frames()
        .map_err(|err| err.to_string())?;

    let mut result = Vec::new();
    for (index, frame) in frames.into_iter().enumerate() {
        let delay = frame.delay();
        let (num, den) = delay.numer_denom_ms();
        let millis = if den == 0 { 100 } else { (num / den).max(20) };
        result.push(frame_from_rgba(
            ctx,
            path,
            index,
            frame.into_buffer(),
            Duration::from_millis(u64::from(millis)),
        ));
    }

    if result.is_empty() {
        return Err("GIF 沒有可顯示的影格".to_owned());
    }

    Ok(result)
}

fn frame_from_rgba(
    ctx: &egui::Context,
    path: &Path,
    index: usize,
    image: image::RgbaImage,
    delay: Duration,
) -> PreviewFrame {
    let size = [image.width() as usize, image.height() as usize];
    let color_image = egui::ColorImage::from_rgba_unmultiplied(size, image.as_raw());
    let texture = ctx.load_texture(
        format!("{}#{index}", path.display()),
        color_image,
        egui::TextureOptions::LINEAR,
    );

    PreviewFrame {
        size: egui::vec2(size[0] as f32, size[1] as f32),
        texture,
        delay,
    }
}

fn fit_size(size: egui::Vec2, max_size: egui::Vec2) -> egui::Vec2 {
    if size.x <= 0.0 || size.y <= 0.0 {
        return egui::vec2(1.0, 1.0);
    }

    let scale = (max_size.x / size.x).min(max_size.y / size.y).min(1.0);
    egui::vec2(size.x * scale, size.y * scale)
}

fn is_gif(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case("gif"))
}
