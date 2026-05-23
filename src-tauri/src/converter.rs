use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};
use tauri::{AppHandle, Emitter};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversionInput {
    pub files: Vec<String>,
    pub output_dir: Option<String>,
    pub use_ocr: bool,
    pub extract_images: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversionResult {
    pub file: String,
    pub markdown: String,
    pub error: Option<String>,
    pub output_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "event")]
pub enum SidecarEvent {
    #[serde(rename = "started")]
    Started {
        file: String,
        index: usize,
        total: usize,
    },
    #[serde(rename = "finished")]
    Finished {
        file: String,
        index: usize,
        markdown: String,
        output_path: String,
    },
    #[serde(rename = "error")]
    Error {
        file: Option<String>,
        index: Option<usize>,
        error: String,
    },
    #[serde(rename = "warning")]
    Warning {
        file: String,
        index: usize,
        warning: String,
    },
    #[serde(rename = "complete")]
    Complete {
        total: usize,
        success: usize,
        failed: usize,
    },
}

#[derive(Debug, Clone, Serialize)]
pub struct ConversionProgress {
    pub event_type: String,
    pub file: Option<String>,
    pub index: Option<usize>,
    pub total: Option<usize>,
    pub markdown: Option<String>,
    pub output_path: Option<String>,
    pub error: Option<String>,
    pub success: Option<usize>,
    pub failed: Option<usize>,
}

pub async fn run_conversion(
    app: AppHandle,
    input: ConversionInput,
) -> Result<Vec<ConversionResult>, String> {
    let input_json = serde_json::to_string(&input)
        .map_err(|e| format!("Failed to serialize input: {}", e))?;

    let sidecar_path = app
        .path()
        .resource_dir()
        .map_err(|e| format!("Failed to get resource directory: {}", e))?
        .join("sidecars")
        .join("markit-convert");

    if !sidecar_path.exists() {
        return Err(format!(
            "Sidecar not found at {:?}. Please build it first with: cd python-sidecar && pyinstaller convert.spec",
            sidecar_path
        ));
    }

    let mut child = Command::new(&sidecar_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin
            .write_all(input_json.as_bytes())
            .map_err(|e| format!("Failed to write to sidecar stdin: {}", e))?;
    }

    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "Failed to capture sidecar stdout".to_string())?;

    let reader = BufReader::new(stdout);
    let mut results = Vec::new();

    for line in reader.lines() {
        let line = line.map_err(|e| format!("Failed to read sidecar output: {}", e))?;

        if line.trim().is_empty() {
            continue;
        }

        let event: SidecarEvent = match serde_json::from_str(&line) {
            Ok(e) => e,
            Err(e) => {
                eprintln!("Failed to parse sidecar event: {} - Line: {}", e, line);
                continue;
            }
        };

        let progress = match &event {
            SidecarEvent::Started {
                file,
                index,
                total,
            } => ConversionProgress {
                event_type: "started".to_string(),
                file: Some(file.clone()),
                index: Some(*index),
                total: Some(*total),
                markdown: None,
                output_path: None,
                error: None,
                success: None,
                failed: None,
            },
            SidecarEvent::Finished {
                file,
                index,
                markdown,
                output_path,
            } => {
                results.push(ConversionResult {
                    file: file.clone(),
                    markdown: markdown.clone(),
                    error: None,
                    output_path: if output_path.is_empty() {
                        None
                    } else {
                        Some(output_path.clone())
                    },
                });

                ConversionProgress {
                    event_type: "finished".to_string(),
                    file: Some(file.clone()),
                    index: Some(*index),
                    total: None,
                    markdown: Some(markdown.clone()),
                    output_path: Some(output_path.clone()),
                    error: None,
                    success: None,
                    failed: None,
                }
            }
            SidecarEvent::Error {
                file,
                index,
                error,
            } => {
                if let Some(file_path) = file {
                    results.push(ConversionResult {
                        file: file_path.clone(),
                        markdown: String::new(),
                        error: Some(error.clone()),
                        output_path: None,
                    });
                }

                ConversionProgress {
                    event_type: "error".to_string(),
                    file: file.clone(),
                    index: *index,
                    total: None,
                    markdown: None,
                    output_path: None,
                    error: Some(error.clone()),
                    success: None,
                    failed: None,
                }
            }
            SidecarEvent::Warning {
                file,
                index,
                warning,
            } => ConversionProgress {
                event_type: "warning".to_string(),
                file: Some(file.clone()),
                index: Some(*index),
                total: None,
                markdown: None,
                output_path: None,
                error: Some(warning.clone()),
                success: None,
                failed: None,
            },
            SidecarEvent::Complete {
                total,
                success,
                failed,
            } => ConversionProgress {
                event_type: "complete".to_string(),
                file: None,
                index: None,
                total: Some(*total),
                markdown: None,
                output_path: None,
                error: None,
                success: Some(*success),
                failed: Some(*failed),
            },
        };

        let _ = app.emit("conversion-progress", &progress);
    }

    let status = child
        .wait()
        .map_err(|e| format!("Failed to wait for sidecar: {}", e))?;

    if !status.success() {
        let stderr = child
            .stderr
            .take()
            .map(|mut s| {
                let mut output = String::new();
                let _ = std::io::Read::read_to_string(&mut s, &mut output);
                output
            })
            .unwrap_or_default();

        return Err(format!(
            "Sidecar exited with status: {}. Stderr: {}",
            status, stderr
        ));
    }

    Ok(results)
}
