mod commands;
mod converter;
mod settings;

use settings::Settings;
use std::sync::Mutex;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let settings = Settings::load(&app.handle());
            app.manage(Mutex::new(settings));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::convert_files,
            commands::get_settings,
            commands::set_settings,
            commands::select_output_dir,
            commands::save_markdown,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
