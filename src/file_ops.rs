use std::{
    fs, io,
    path::{Path, PathBuf},
    process::Command,
};

pub const IMAGE_EXTENSIONS: &[&str] = &["png", "jpg", "jpeg", "gif", "bmp", "webp"];

#[derive(Clone, Debug)]
pub struct Category {
    pub name: String,
    pub items: Vec<Item>,
}

#[derive(Clone, Debug)]
pub struct Item {
    pub name: String,
    pub checked: bool,
    pub has_images: bool,
}

#[derive(Clone, Debug, Default)]
pub struct CopyReport {
    pub total: usize,
    pub copied: usize,
    pub errors: Vec<String>,
}

pub fn default_resource_root() -> PathBuf {
    let exe_parent = std::env::current_exe()
        .ok()
        .and_then(|path| path.parent().map(Path::to_path_buf));
    let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));

    if let Some(parent) = exe_parent
        && get_public_dir(&parent).exists()
    {
        return parent;
    }

    current_dir
}

pub fn get_public_dir(root_dir: &Path) -> PathBuf {
    let misspelled = root_dir.join("pubilc");
    if misspelled.exists() {
        misspelled
    } else {
        root_dir.join("public")
    }
}

pub fn scan_categories(root_dir: &Path) -> Vec<Category> {
    let public_dir = get_public_dir(root_dir);
    let mut categories = Vec::new();

    let Ok(entries) = fs::read_dir(public_dir) else {
        return categories;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() || is_hidden(&path) {
            continue;
        }

        let mut items = Vec::new();
        if let Ok(subentries) = fs::read_dir(&path) {
            for subentry in subentries.flatten() {
                let item_path = subentry.path();
                if item_path.is_dir() && !is_hidden(&item_path) {
                    items.push(Item {
                        name: file_name(&item_path),
                        checked: false,
                        has_images: contains_image(&item_path),
                    });
                }
            }
        }

        if !items.is_empty() {
            items.sort_by(|a, b| a.name.cmp(&b.name));
            categories.push(Category {
                name: file_name(&path),
                items,
            });
        }
    }

    categories.sort_by(|a, b| a.name.cmp(&b.name));
    categories
}

pub fn image_paths_for_item(
    root_dir: &Path,
    categories: &[Category],
    item_name: &str,
) -> Vec<PathBuf> {
    let public_dir = get_public_dir(root_dir);
    for category in categories {
        if !category.items.iter().any(|item| item.name == item_name) {
            continue;
        }

        let item_dir = public_dir.join(&category.name).join(item_name);
        let mut paths = Vec::new();
        collect_images(&item_dir, &mut paths);
        paths.sort();
        return paths;
    }

    Vec::new()
}

pub fn check_eat_exe(target_dir: &Path) -> bool {
    target_dir.join("eat.exe").is_file()
}

pub fn copy_selected(
    root_dir: &Path,
    target_dir: &Path,
    selections: &[(String, Vec<String>)],
) -> CopyReport {
    let public_dir = get_public_dir(root_dir);
    let mut report = CopyReport::default();

    for (category, items) in selections {
        for item in items {
            report.total +=
                count_matching_files(&public_dir.join(category).join(item).join("sprite"), "spr");
            report.total +=
                count_matching_files(&public_dir.join(category).join(item).join("icon"), "tbt");
        }
    }

    for (category, items) in selections {
        for item in items {
            copy_matching_files(
                &public_dir.join(category).join(item).join("sprite"),
                &target_dir.join("sprite"),
                "spr",
                &mut report,
            );
            copy_matching_files(
                &public_dir.join(category).join(item).join("icon"),
                &target_dir.join("icon"),
                "tbt",
                &mut report,
            );
        }
    }

    report
}

pub fn run_eat_exe(target_dir: &Path) -> io::Result<()> {
    Command::new(target_dir.join("eat.exe"))
        .current_dir(target_dir)
        .spawn()
        .map(|_| ())
}

fn copy_matching_files(src_dir: &Path, dst_dir: &Path, ext: &str, report: &mut CopyReport) {
    if !src_dir.exists() {
        return;
    }

    if let Err(err) = fs::create_dir_all(dst_dir) {
        report
            .errors
            .push(format!("無法建立目標資料夾 {}: {err}", dst_dir.display()));
        return;
    }

    let Ok(entries) = fs::read_dir(src_dir) else {
        report
            .errors
            .push(format!("無法讀取來源資料夾 {}", src_dir.display()));
        return;
    };

    for entry in entries.flatten() {
        let src = entry.path();
        if !src.is_file() || !has_extension(&src, ext) {
            continue;
        }

        let dst = dst_dir.join(src.file_name().unwrap_or_default());
        match fs::copy(&src, &dst) {
            Ok(_) => report.copied += 1,
            Err(err) => report.errors.push(format!(
                "複製失敗 {} -> {}: {err}",
                src.display(),
                dst.display()
            )),
        }
    }
}

fn count_matching_files(dir: &Path, ext: &str) -> usize {
    let Ok(entries) = fs::read_dir(dir) else {
        return 0;
    };

    entries
        .flatten()
        .map(|entry| entry.path())
        .filter(|path| path.is_file() && has_extension(path, ext))
        .count()
}

fn collect_images(dir: &Path, paths: &mut Vec<PathBuf>) {
    let Ok(entries) = fs::read_dir(dir) else {
        return;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            collect_images(&path, paths);
        } else if has_any_extension(&path, IMAGE_EXTENSIONS) {
            paths.push(path);
        }
    }
}

fn contains_image(dir: &Path) -> bool {
    let Ok(entries) = fs::read_dir(dir) else {
        return false;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() && contains_image(&path) {
            return true;
        }
        if has_any_extension(&path, IMAGE_EXTENSIONS) {
            return true;
        }
    }

    false
}

fn has_extension(path: &Path, expected: &str) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case(expected))
}

fn has_any_extension(path: &Path, extensions: &[&str]) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| {
            extensions
                .iter()
                .any(|expected| ext.eq_ignore_ascii_case(expected))
        })
}

fn file_name(path: &Path) -> String {
    path.file_name()
        .and_then(|name| name.to_str())
        .unwrap_or_default()
        .to_owned()
}

fn is_hidden(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.starts_with('.'))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn public_dir_prefers_legacy_misspelling() {
        let root = temp_root("public_dir_prefers_legacy_misspelling");
        fs::create_dir_all(root.join("pubilc")).unwrap();
        fs::create_dir_all(root.join("public")).unwrap();

        assert_eq!(get_public_dir(&root), root.join("pubilc"));

        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn scans_categories_and_marks_items_with_preview_images() {
        let root = temp_root("scans_categories");
        let item = root.join("public").join("BOSS").join("不死鳥");
        fs::create_dir_all(item.join("sprite")).unwrap();
        fs::write(item.join("preview.png"), []).unwrap();

        let categories = scan_categories(&root);

        assert_eq!(categories.len(), 1);
        assert_eq!(categories[0].name, "BOSS");
        assert_eq!(categories[0].items[0].name, "不死鳥");
        assert!(categories[0].items[0].has_images);

        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn copies_sprite_and_icon_files_to_target() {
        let root = temp_root("copies_sprite_and_icon_files_to_target");
        let item = root.join("public").join("BOSS").join("不死鳥");
        let target = root.join("target");
        fs::create_dir_all(item.join("sprite")).unwrap();
        fs::create_dir_all(item.join("icon")).unwrap();
        fs::write(item.join("sprite").join("boss.spr"), b"spr").unwrap();
        fs::write(item.join("icon").join("boss.tbt"), b"tbt").unwrap();
        fs::write(item.join("icon").join("ignore.txt"), b"txt").unwrap();

        let report = copy_selected(
            &root,
            &target,
            &[("BOSS".to_owned(), vec!["不死鳥".to_owned()])],
        );

        assert_eq!(report.total, 2);
        assert_eq!(report.copied, 2);
        assert!(target.join("sprite").join("boss.spr").is_file());
        assert!(target.join("icon").join("boss.tbt").is_file());
        assert!(!target.join("icon").join("ignore.txt").exists());

        fs::remove_dir_all(root).unwrap();
    }

    fn temp_root(name: &str) -> PathBuf {
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        std::env::temp_dir().join(format!("lineage_boss_{name}_{nanos}"))
    }
}
