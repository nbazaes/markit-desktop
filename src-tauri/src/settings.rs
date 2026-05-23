use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub output_directory: Option<String>,
    pub dark_mode: bool,
    pub use_ocr: bool,
    pub extract_images: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            output_directory: None,
            dark_mode: true,
            use_ocr: false,
            extract_images: true,
        }
    }
}

impl Settings {
    fn config_path(app: &AppHandle) -> Result<PathBuf, String> {
        let app_data_dir = app
            .path()
            .app_config_dir()
            .map_err(|e| format!("Failed to get config directory: {}", e))?;

        Ok(app_data_dir.join("settings.json"))
    }

    pub fn load(app: &AppHandle) -> Self {
        let config_path = match Self::config_path(app) {
            Ok(path) => path,
            Err(e) => {
                eprintln!("Failed to get config path: {}", e);
                return Self::default();
            }
        };

        if !config_path.exists() {
            return Self::default();
        }

        let content = match fs::read_to_string(&config_path) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("Failed to read settings file: {}", e);
                return Self::default();
            }
        };

        match serde_json::from_str(&content) {
            Ok(settings) => settings,
            Err(e) => {
                eprintln!("Failed to parse settings: {}", e);
                Self::default()
            }
        }
    }

    pub fn save(&self, app: &AppHandle) -> Result<(), String> {
        let config_path = Self::config_path(app)?;

        if let Some(parent) = config_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create config directory: {}", e))?;
        }

        let content = serde_json::to_string_pretty(self)
            .map_err(|e| format!("Failed to serialize settings: {}", e))?;

        fs::write(&config_path, content)
            .map_err(|e| format!("Failed to write settings file: {}", e))?;

        Ok(())
    }
}
