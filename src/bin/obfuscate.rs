use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use lineage_boss_visualization::obfuscation::{
    CategoryEntry, MANIFEST_FILENAME, MANIFEST_VERSION, Manifest, hash_name, load_manifest,
    save_manifest,
};

fn main() -> ExitCode {
    let mut target: Option<PathBuf> = None;
    let mut apply = false;
    let mut reverse = false;

    for arg in env::args().skip(1) {
        match arg.as_str() {
            "--apply" => apply = true,
            "--reverse" => reverse = true,
            "-h" | "--help" => {
                print_help();
                return ExitCode::SUCCESS;
            }
            other if other.starts_with('-') => {
                eprintln!("未知參數: {other}");
                print_help();
                return ExitCode::FAILURE;
            }
            other => {
                if target.is_some() {
                    eprintln!("只能指定一個目標目錄");
                    return ExitCode::FAILURE;
                }
                target = Some(PathBuf::from(other));
            }
        }
    }

    let Some(target) = target else {
        eprintln!("缺少目標目錄參數");
        print_help();
        return ExitCode::FAILURE;
    };

    if !target.is_dir() {
        eprintln!("目標不是有效的目錄: {}", target.display());
        return ExitCode::FAILURE;
    }

    let mode_label = if reverse {
        "REVERSE (還原成原始名稱)"
    } else {
        "FORWARD (混淆成 hash 名稱)"
    };
    let action_label = if apply { "APPLY" } else { "DRY-RUN" };

    println!("== Lineage Boss 混淆工具 ==");
    println!("目標目錄 : {}", target.display());
    println!("方向     : {mode_label}");
    println!("動作     : {action_label}");
    println!();

    let result = if reverse {
        reverse_obfuscate(&target, apply)
    } else {
        forward_obfuscate(&target, apply)
    };

    match result {
        Ok(()) => {
            if !apply {
                println!();
                println!("這只是 DRY-RUN，沒有任何變更。要實際執行請加 --apply。");
            }
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("失敗: {err}");
            ExitCode::FAILURE
        }
    }
}

fn print_help() {
    println!("用法:");
    println!("  obfuscate <目錄> [--apply] [--reverse]");
    println!();
    println!("說明:");
    println!("  預設為 DRY-RUN（僅印出將要執行的動作）。");
    println!("  --apply       實際執行重命名與寫入 manifest.bin。");
    println!("  --reverse     反向：依現有 manifest.bin 還原為原始名稱。");
    println!();
    println!("範例:");
    println!(r"  obfuscate dist\LineageBossVisualization\pubilc");
    println!(r"  obfuscate dist\LineageBossVisualization\pubilc --apply");
    println!(r"  obfuscate dist\LineageBossVisualization\pubilc --apply --reverse");
}

fn forward_obfuscate(target: &Path, apply: bool) -> Result<(), String> {
    let manifest_file = target.join(MANIFEST_FILENAME);
    if manifest_file.exists() {
        return Err(format!(
            "目標已存在 manifest.bin（{}）。如要重新混淆請先用 --reverse。",
            manifest_file.display()
        ));
    }

    let mut manifest = Manifest {
        version: MANIFEST_VERSION,
        categories: BTreeMap::new(),
    };

    let mut category_renames: Vec<(PathBuf, PathBuf)> = Vec::new();
    let mut item_renames: Vec<(PathBuf, PathBuf)> = Vec::new();

    let category_entries = sorted_dir_entries(target)?;
    for category_path in &category_entries {
        let category_disk_original = file_name(category_path);
        let category_hash = hash_name(&category_disk_original);

        let mut item_map = BTreeMap::new();
        let item_entries = sorted_dir_entries(category_path)?;
        for item_path in &item_entries {
            let item_original = file_name(item_path);
            let item_hash = hash_name(&item_original);

            if item_map.contains_key(&item_hash) {
                return Err(format!(
                    "雜湊碰撞: {} 與既有項目衝突 (hash={item_hash})",
                    item_path.display()
                ));
            }

            item_map.insert(item_hash.clone(), item_original.clone());

            let new_item = category_path.join(&item_hash);
            item_renames.push((item_path.clone(), new_item));
        }

        if manifest.categories.contains_key(&category_hash) {
            return Err(format!(
                "雜湊碰撞: 分類 {} 與既有衝突 (hash={category_hash})",
                category_path.display()
            ));
        }

        manifest.categories.insert(
            category_hash.clone(),
            CategoryEntry {
                name: category_disk_original,
                items: item_map,
            },
        );

        let new_category = target.join(&category_hash);
        category_renames.push((category_path.clone(), new_category));
    }

    println!("[類別重命名] {} 個", category_renames.len());
    for (from, to) in &category_renames {
        println!("  {} -> {}", from.display(), file_name(to));
    }
    println!();
    println!("[項目重命名] {} 個", item_renames.len());
    for (from, to) in &item_renames {
        println!(
            "  {}/{} -> {}",
            file_name(from.parent().unwrap_or(Path::new(""))),
            file_name(from),
            file_name(to)
        );
    }

    if !apply {
        return Ok(());
    }

    println!();
    println!("[執行中]...");

    for (from, to) in &item_renames {
        fs::rename(from, to).map_err(|e| format!("rename {} 失敗: {e}", from.display()))?;
    }

    for (from, to) in &category_renames {
        fs::rename(from, to).map_err(|e| format!("rename {} 失敗: {e}", from.display()))?;
    }

    save_manifest(&manifest_file, &manifest)?;
    println!("已寫入 manifest: {}", manifest_file.display());
    println!("完成。");
    Ok(())
}

fn reverse_obfuscate(target: &Path, apply: bool) -> Result<(), String> {
    let manifest_file = target.join(MANIFEST_FILENAME);
    let manifest =
        load_manifest(&manifest_file).ok_or_else(|| "無法讀取或解密 manifest.bin".to_string())?;

    let mut category_renames: Vec<(PathBuf, PathBuf)> = Vec::new();
    let mut item_renames: Vec<(PathBuf, PathBuf)> = Vec::new();

    for (category_hash, entry) in &manifest.categories {
        let category_path = target.join(category_hash);
        if !category_path.is_dir() {
            return Err(format!(
                "manifest 指向的分類目錄不存在: {}",
                category_path.display()
            ));
        }

        for (item_hash, item_name) in &entry.items {
            let item_path = category_path.join(item_hash);
            if !item_path.is_dir() {
                return Err(format!(
                    "manifest 指向的項目目錄不存在: {}",
                    item_path.display()
                ));
            }
            let new_item = category_path.join(item_name);
            item_renames.push((item_path, new_item));
        }

        let new_category = target.join(&entry.name);
        category_renames.push((category_path, new_category));
    }

    println!("[項目還原] {} 個", item_renames.len());
    for (from, to) in &item_renames {
        println!(
            "  {}/{} -> {}",
            file_name(from.parent().unwrap_or(Path::new(""))),
            file_name(from),
            file_name(to)
        );
    }
    println!();
    println!("[類別還原] {} 個", category_renames.len());
    for (from, to) in &category_renames {
        println!("  {} -> {}", file_name(from), file_name(to));
    }

    if !apply {
        return Ok(());
    }

    println!();
    println!("[執行中]...");

    for (from, to) in &item_renames {
        fs::rename(from, to).map_err(|e| format!("rename {} 失敗: {e}", from.display()))?;
    }

    for (from, to) in &category_renames {
        fs::rename(from, to).map_err(|e| format!("rename {} 失敗: {e}", from.display()))?;
    }

    fs::remove_file(&manifest_file)
        .map_err(|e| format!("移除 manifest 失敗 {}: {e}", manifest_file.display()))?;
    println!("已移除 manifest 並還原原始名稱。");
    Ok(())
}

fn sorted_dir_entries(dir: &Path) -> Result<Vec<PathBuf>, String> {
    let mut entries: Vec<PathBuf> = fs::read_dir(dir)
        .map_err(|e| format!("讀取目錄失敗 {}: {e}", dir.display()))?
        .flatten()
        .map(|e| e.path())
        .filter(|path| {
            path.is_dir()
                && !path
                    .file_name()
                    .and_then(|n| n.to_str())
                    .is_some_and(|n| n.starts_with('.'))
        })
        .collect();
    entries.sort();
    Ok(entries)
}

fn file_name(path: &Path) -> String {
    path.file_name()
        .and_then(|n| n.to_str())
        .unwrap_or_default()
        .to_owned()
}
