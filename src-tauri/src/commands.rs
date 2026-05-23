use crate::converter::{run_conversion, ConversionInput, ConversionResult};
use crate::settings::Settings;
use std::sync::Mutex;
use tauri::{AppHandle, State};

#[tauri::command]
pub async fn convert_files(
    app: AppHandle,
    files: Vec<String>,
    output_dir: Option<String>,
    use_ocr: bool,
    extract_images: bool,
) -> Result<Vec<ConversionResult>, String> {
    let input = ConversionInput {
        files,
        output_dir,
        use_ocr,
        extract_images,
    };

    run_conversion(app, input).await
}

#[tauri::command]
pub fn get_settings(settings: State<'_, Mutex<Settings>>) -> Result<Settings, String> {
    let settings = settings
        .lock()
        .map_err(|e| format!("Failed to lock settings: {}", e))?;
    Ok(settings.clone())
}

#[tauri::command]
pub fn set_settings(
    app: AppHandle,
    settings: State<'_, Mutex<Settings>>,
    new_settings: Settings,
) -> Result<(), String> {
    let mut current = settings
        .lock()
        .map_err(|e| format!("Failed to lock settings: {}", e))?;

    *current = new_settings.clone();
    drop(current);

    new_settings.save(&app)?;
    Ok(())
}

#[tauri::command]
pub async fn select_output_dir(app: AppHandle) -> Result<Option<String>, String> {
    use tauri_plugin_dialog::DialogExt;

    let folder = app
        .dialog()
        .file()
        .set_title("Select Output Directory")
        .blocking_pick_folder();

    Ok(folder.map(|p| p.to_string()))
}

#[tauri::command]
pub async fn save_markdown(app: AppHandle, content: String, default_name: String) -> Result<Option<String>, String> {
    use tauri_plugin_dialog::DialogExt;
    use std::fs;

    let file = app
        .dialog()
        .file()
        .set_title("Save Markdown")
        .set_file_name(&default_name)
        .add_filter("Markdown", &["md"])
        .blocking_save_file();

    if let Some(path) = file {
        let path_str = path.to_string();
        fs::write(&path_str, content)
            .map_err(|e| format!("Failed to write file: {}", e))?;
        Ok(Some(path_str))
    } else {
        Ok(None)
    }
}
