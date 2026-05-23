# MIGRATION.md — PySide6 → Tauri

## Overview

Full migration of **MarkIt-Desktop** from PySide6/Qt (Python) to **Tauri v2** (Rust backend + Svelte 5 web frontend). The `markitdown` conversion library remains Python but runs as a **sidecar process** bundled with the app.

## Tech stack

| Layer | Before | After |
|-------|--------|-------|
| Frontend | PySide6 (Qt widgets) | Svelte 5 + TypeScript |
| Styling | QSS stylesheet | Tailwind CSS v4 |
| Backend | Python (`converter.py`, `settings.py`) | Rust (Tauri commands) |
| Conversion | `markitdown` library (inline) | Python sidecar (PyInstaller binary) |
| Settings | `QSettings` (Qt registry) | JSON file (`~/.config/markit-desktop/`) |
| Build | hatchling + PyInstaller + shell scripts | Vite + Tauri CLI bundler |
| Packages | Manual AppImage/deb/rpm scripts | Tauri bundler (native) |
| MD render | `markdown` + `Pygments` (Python) | `marked` + `highlight.js` (JS) |

## Project structure (target)

```
markitdown-gui/
├── src-tauri/                  # Rust backend
│   ├── src/
│   │   ├── main.rs             # Tauri entry point
│   │   ├── lib.rs              # App setup, plugin registration, command registration
│   │   ├── commands.rs         # IPC commands
│   │   ├── converter.rs        # Sidecar process management
│   │   └── settings.rs         # JSON config persistence
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/
│   │   └── default.json        # Permission capabilities
│   ├── icons/
│   └── sidecars/               # Platform-specific Python binaries (built by CI)
├── src/                        # Svelte frontend
│   ├── App.svelte              # Main layout
│   ├── main.ts                 # Entry point
│   ├── app.css                 # Tailwind imports + custom theme tokens
│   ├── lib/
│   │   ├── components/
│   │   │   ├── FilePanel.svelte
│   │   │   ├── PreviewPanel.svelte
│   │   │   ├── Toolbar.svelte
│   │   │   ├── StatusBar.svelte
│   │   │   └── FileItem.svelte
│   │   ├── stores/
│   │   │   ├── files.svelte.ts        # File list state (Svelte 5 runes)
│   │   │   ├── conversion.svelte.ts   # Conversion progress/results
│   │   │   └── settings.svelte.ts     # App settings + theme
│   │   └── utils/
│   │       └── format.ts       # File size formatting, etc.
│   └── vite-env.d.ts
├── python-sidecar/
│   ├── convert.py              # CLI wrapper: stdin JSON → stdout JSON
│   ├── requirements.txt        # markitdown[all] + pyinstaller
│   └── convert.spec            # PyInstaller spec
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tsconfig.json
├── AGENTS.md
├── MIGRATION.md                # This file
├── README.md
├── LICENSE
└── .github/workflows/release.yml
```

## Files to delete

- `src/markit_desktop/` — entire Python package (replaced by `src/` + `src-tauri/`)
- `build/` — old PyInstaller spec + packaging scripts (Tauri bundler replaces them)
- `pyproject.toml` — Python project metadata (no longer a Python package)
- `requirements.txt` (root) — moved into `python-sidecar/`

## Files to keep

- `markitdown/` — nested git repo of the library (untracked in parent)
- `.git/` — version history
- `.github/` — update `release.yml` for Tauri CI
- `AGENTS.md` — update for new architecture
- `README.md` — update install/build instructions
- `LICENSE` — unchanged

---

## Phase 1 — Project scaffolding

Remove old files and initialize the Tauri + Svelte + Vite project.

### Steps

1. **Remove old Python source**:
   ```bash
   rm -rf src/markit_desktop/
   rm -rf build/
   rm -f pyproject.toml requirements.txt
   ```

2. **Initialize Tauri v2 + Svelte 5 + TypeScript**:
   ```bash
   npm create tauri-app@latest . -- --template svelte-ts --manager npm
   ```
   Accept defaults, select Svelte + TypeScript template.

3. **Install frontend dependencies**:
   ```bash
   npm install
   npm install -D tailwindcss @tailwindcss/vite
   npm install @tauri-apps/api @tauri-apps/plugin-dialog @tauri-apps/plugin-shell @tauri-apps/plugin-fs marked highlight.js
   ```

4. **Configure Tailwind** — create `src/app.css`:
   ```css
   @import "tailwindcss";
   @plugin "@tailwindcss/typography";

   @theme {
     --color-bg-deep: #1e1e24;
     --color-bg-surface: #26262e;
     --color-bg-raised: #343440;
     --color-border: #3a3a46;
     --color-border-hover: #4a4a56;
     --color-accent: #c7924b;
     --color-accent-hover: #d4a85c;
     --color-accent-pressed: #a6763b;
     --color-accent-dim: #5a4620;
     --color-text-primary: #e8e4d9;
     --color-text-secondary: #b0aca5;
     --color-text-muted: #87878d;
     --color-text-dim: #5a5a64;
     --color-success: #6aab73;
     --color-error: #c95f5f;
     --color-warning: #c7924b;

     --font-mono: "SF Mono", "Consolas", "Monaco", monospace;
   }
   ```

5. **Configure Vite** with `@tailwindcss/vite` plugin in `vite.config.ts`:
   ```ts
   import { defineConfig } from "vite";
   import tailwindcss from "@tailwindcss/vite";

   const host = process.env.TAURI_DEV_HOST;

   export default defineConfig({
     plugins: [tailwindcss()],
     clearScreen: false,
     server: {
       host: host || false,
       port: 1420,
       strictPort: true,
       hmr: host ? { protocol: "ws", host, port: 1421 } : undefined,
     },
   });
   ```

6. **Configure `tauri.conf.json`**:
   ```json
   {
     "productName": "MarkIt-Desktop",
     "version": "0.2.0",
     "identifier": "com.markitdesktop.app",
     "build": {
       "frontendDist": "../dist",
       "devUrl": "http://localhost:1420",
       "beforeDevCommand": "npm run dev",
       "beforeBuildCommand": "npm run build"
     },
     "app": {
       "windows": [{
         "title": "MarkIt-Desktop",
         "width": 1280,
         "height": 780,
         "minWidth": 1020,
         "minHeight": 660,
         "resizable": true,
         "dragDropEnabled": true
       }]
     },
     "bundle": {
       "active": true,
       "targets": ["appimage", "deb", "rpm", "nsis", "dmg"],
       "icon": ["icons/32x32.png", "icons/128x128.png", "icons/128x128@2x.png", "icons/icon.icns", "icons/icon.ico"],
       "externalBin": ["sidecars/markit-convert"]
     },
     "plugins": {
       "dialog": {},
       "shell": {
         "sidecar": true,
         "scope": [{ "name": "sidecars/markit-convert", "sidecar": true }]
       }
     }
   }
   ```

7. **Verify**: `npm run tauri dev` should open a blank window.

---

## Phase 2 — Python sidecar

Create a standalone Python CLI binary that Tauri spawns as a subprocess. Communication via stdin/stdout (line-delimited JSON).

### `python-sidecar/convert.py`

```python
#!/usr/bin/env python3
"""MarkIt-Desktop conversion sidecar. Reads JSON from stdin, writes JSON to stdout."""

import sys
import json
import os
from pathlib import Path
from markitdown import MarkItDown

def main():
    input_data = json.load(sys.stdin)
    files = input_data.get("files", [])
    output_dir = input_data.get("output_dir", "")
    use_ocr = input_data.get("use_ocr", False)

    md = MarkItDown()
    results = []

    for file_path in files:
        result = {"file": file_path, "markdown": "", "error": None, "output_path": None}
        try:
            # Emit progress event
            print(json.dumps({"event": "started", "file": file_path}), flush=True)

            converted = md.convert(file_path)
            markdown = converted.text_content

            result["markdown"] = markdown

            # Auto-save if output directory specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                source_name = Path(file_path).stem
                output_path = os.path.join(output_dir, f"{source_name}.md")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown)
                result["output_path"] = output_path

        except Exception as e:
            result["error"] = str(e)

        results.append(result)

    print(json.dumps({"event": "finished", "results": results}), flush=True)

if __name__ == "__main__":
    main()
```

### `python-sidecar/requirements.txt`

```
markitdown[all]>=0.1.0
pyinstaller>=6.0.0
```

### `python-sidecar/convert.spec`

PyInstaller spec for single-file binary:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['convert.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'markitdown',
        'markitdown.converters',
        'markitdown.converters._pdf_converter',
        'markitdown.converters._docx_converter',
        'markitdown.converters._xlsx_converter',
        'markitdown.converters._pptx_converter',
        'markitdown.converters._html_converter',
        'markitdown.converters._csv_converter',
        'markitdown.converters._image_converter',
        'markitdown.converters._audio_converter',
        'markitdown.converters._epub_converter',
        'markitdown.converters._ipynb_converter',
        'markitdown.converters._outlook_msg_converter',
        'markitdown.converters._rss_converter',
        'markitdown.converters._zip_converter',
        'markitdown.converters._plain_text_converter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='markit-convert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### Build command

```bash
cd python-sidecar
pip install -r requirements.txt
pyinstaller convert.spec
cp dist/markit-convert ../src-tauri/sidecars/markit-convert-$(uname -s)-$(uname -m)
```

### How Tauri uses the sidecar

In Rust (`converter.rs`):

```rust
use tauri_plugin_shell::ShellExt;

async fn run_conversion(app: &tauri::AppHandle, input: &str) -> Result<String, String> {
    let sidecar = app.shell()
        .sidecar("markit-convert")
        .map_err(|e| e.to_string())?;

    let output = sidecar
        .args(["--stdin"])
        .write(input.as_bytes());

    // Parse streaming JSON events from stdout
    // emit Tauri events for each line
}
```

---

## Phase 3 — Rust backend

### Dependencies (`Cargo.toml`)

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon"] }
tauri-plugin-dialog = "2"
tauri-plugin-shell = "2"
tauri-plugin-fs = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
dirs = "5"
tokio = { version = "1", features = ["full"] }
```

### `lib.rs` — App setup

```rust
mod commands;
mod converter;
mod settings;

use tauri::Manager;

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            let settings = settings::Settings::load(app.handle())?;
            app.manage(std::sync::Mutex::new(settings));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::convert_files,
            commands::save_markdown,
            commands::get_settings,
            commands::set_settings,
            commands::select_output_dir,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### `commands.rs` — IPC commands

```rust
use crate::converter;
use crate::settings::Settings;
use std::sync::Mutex;
use tauri::{AppHandle, Manager, State};

#[derive(serde::Serialize, serde::Deserialize)]
pub struct ConversionResult {
    pub file: String,
    pub markdown: String,
    pub error: Option<String>,
    pub output_path: Option<String>,
}

#[tauri::command]
pub async fn convert_files(
    files: Vec<String>,
    output_dir: Option<String>,
    app: AppHandle,
) -> Result<Vec<ConversionResult>, String> {
    converter::run(app, files, output_dir).await
}

#[tauri::command]
pub async fn save_markdown(
    content: String,
    default_name: String,
) -> Result<Option<String>, String> {
    // Use tauri-plugin-dialog save dialog, write to file
    todo!()
}

#[tauri::command]
pub fn get_settings(state: State<'_, Mutex<Settings>>) -> Settings {
    state.lock().unwrap().clone()
}

#[tauri::command]
pub fn set_settings(new_settings: Settings, state: State<'_, Mutex<Settings>>, app: AppHandle) {
    let mut settings = state.lock().unwrap();
    *settings = new_settings;
    let _ = settings.save(&app);
}

#[tauri::command]
pub async fn select_output_dir(app: AppHandle) -> Result<Option<String>, String> {
    let path = app.dialog()
        .file()
        .blocking_pick_folder();
    // ... return selected path
    todo!()
}
```

### `converter.rs` — Sidecar management

```rust
use tauri::{AppHandle, Emitter};
use tauri_plugin_shell::ShellExt;
use serde_json::Value;
use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};

#[derive(Clone, serde::Serialize)]
struct ConversionEvent {
    event: String,
    file: Option<String>,
    results: Option<Vec<super::commands::ConversionResult>>,
}

pub async fn run(
    app: AppHandle,
    files: Vec<String>,
    output_dir: Option<String>,
) -> Result<Vec<super::commands::ConversionResult>, String> {
    // Build JSON input for sidecar
    let input = serde_json::json!({
        "files": files,
        "output_dir": output_dir.unwrap_or_default(),
    });

    // Spawn sidecar process
    let sidecar_command = app.shell()
        .sidecar("markit-convert")
        .map_err(|e| e.to_string())?;

    let (mut rx, mut child) = sidecar_command.spawn().map_err(|e| e.to_string())?;

    // Write input to sidecar's stdin
    child.write(input.to_string().as_bytes()).map_err(|e| e.to_string())?;

    // Read line-delimited JSON events from stdout
    let reader = BufReader::new(rx.stdout.take().unwrap());
    let mut results = Vec::new();

    for line in reader.lines() {
        let line = line.map_err(|e| e.to_string())?;
        let event: Value = serde_json::from_str(&line).map_err(|e| e.to_string())?;

        match event["event"].as_str() {
            Some("started") => {
                let file = event["file"].as_str().unwrap_or("").to_string();
                let _ = app.emit("conversion-started", file);
            }
            Some("finished") => {
                let conversion_results: Vec<super::commands::ConversionResult> =
                    serde_json::from_value(event["results"].clone()).map_err(|e| e.to_string())?;
                results = conversion_results;
                let _ = app.emit("conversion-finished", &results);
            }
            _ => {}
        }
    }

    child.wait().map_err(|e| e.to_string())?;

    Ok(results)
}
```

### `settings.rs` — Config persistence

```rust
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub output_directory: String,
    pub dark_mode: bool,
    pub use_ocr: bool,
    pub extract_images: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            output_directory: String::new(),
            dark_mode: true,
            use_ocr: false,
            extract_images: true,
        }
    }
}

impl Settings {
    fn config_path() -> PathBuf {
        let base = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
        base.join("markit-desktop").join("settings.json")
    }

    pub fn load(app: &tauri::AppHandle) -> Result<Self, Box<dyn std::error::Error>> {
        let path = Self::config_path();
        if path.exists() {
            let content = std::fs::read_to_string(&path)?;
            Ok(serde_json::from_str(&content)?)
        } else {
            Ok(Self::default())
        }
    }

    pub fn save(&self, app: &tauri::AppHandle) -> Result<(), Box<dyn std::error::Error>> {
        let path = Self::config_path();
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(&path, serde_json::to_string_pretty(self)?)?;
        Ok(())
    }
}
```

---

## Phase 4 — Svelte frontend

### Layout concept

```
┌─────────────────────────────────────────────────────────┐
│  [▸ Convert All]  │  [Copy] [Save]  ──  [Clear] │ Output│
├────────────────────┬────────────────────────────────────┤
│  FILES    +        │  [Preview]  [Source]                │
│                    │                                    │
│  ┌──────────────┐  │  ┌──────────────────────────────┐  │
│  │ PDF report   │  │  │ # My Document                │  │
│  │ 2.4 MB   ✓   │  │  │                              │  │
│  ├──────────────┤  │  │ Lorem ipsum dolor sit amet,  │  │
│  │ XLSX data    │  │  │ consectetur adipiscing elit. │  │
│  │ 1.2 MB   ⟳   │  │  │                              │  │
│  ├──────────────┤  │  │ > A blockquote               │  │
│  │ DOCX letter   │  │  │                              │  │
│  │ 512 KB   ○   │  │  │ ```python                    │  │
│  └──────────────┘  │  │ print("hello")                │  │
│                    │  │ ```                           │  │
│                    │  └──────────────────────────────┘  │
├────────────────────┴────────────────────────────────────┤
│  Ready             3 files · 2/3 converted   ████████░░ │
└─────────────────────────────────────────────────────────┘
```

### Component tree

```
App.svelte
├── Toolbar.svelte
│   ├── Convert All (primary button)
│   ├── Copy (secondary)
│   ├── Save (secondary)
│   ├── Clear (danger)
│   └── Output dir picker
├── FilePanel.svelte
│   ├── Header ("FILES" + count badge + add button)
│   ├── Drag-drop zone
│   └── FileItem.svelte (×N)
│       ├── Extension badge (color-coded)
│       ├── Filename + size
│       └── Status indicator
├── PreviewPanel.svelte
│   ├── Tab: Preview (rendered HTML)
│   └── Tab: Source (raw markdown)
└── StatusBar.svelte
    ├── Status text
    ├── File count / conversion count
    └── Progress bar
```

### `App.svelte` (main layout)

```svelte
<script lang="ts">
  import Toolbar from "./lib/components/Toolbar.svelte";
  import FilePanel from "./lib/components/FilePanel.svelte";
  import PreviewPanel from "./lib/components/PreviewPanel.svelte";
  import StatusBar from "./lib/components/StatusBar.svelte";
  import { settings } from "./lib/stores/settings.svelte";
  import { onMount } from "svelte";

  let darkMode = $state(true);

  onMount(async () => {
    await settings.load();
    darkMode = settings.darkMode;
  });

  $effect(() => {
    document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
    settings.darkMode = darkMode;
    settings.save();
  });
</script>

<div class="flex flex-col h-screen bg-bg-deep text-text-primary overflow-hidden">
  <Toolbar {darkMode} onToggle={() => darkMode = !darkMode} />
  <div class="flex flex-1 overflow-hidden">
    <FilePanel class="w-80 border-r border-border flex-shrink-0" />
    <PreviewPanel class="flex-1" />
  </div>
  <StatusBar class="h-8 border-t border-border bg-bg-surface" />
</div>
```

### `Toolbar.svelte`

```svelte
<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { open } from "@tauri-apps/plugin-dialog";
  import { files, clearFiles } from "../stores/files.svelte";
  import { conversion, startConversion } from "../stores/conversion.svelte";
  import { settings } from "../stores/settings.svelte";
  import { getCurrentMarkdown } from "../stores/preview.svelte";

  async function convertAll() {
    if (files.count === 0) return;
    await startConversion(files.paths, settings.outputDir);
  }

  async function copyMarkdown() {
    const md = getCurrentMarkdown();
    if (md) await navigator.clipboard.writeText(md);
  }

  async function saveMarkdown() {
    const md = getCurrentMarkdown();
    if (!md) return;
    await invoke("save_markdown", { content: md, defaultName: "output.md" });
  }

  async function pickOutputDir() {
    const dir = await open({ directory: true, multiple: false });
    if (dir) {
      settings.outputDir = dir;
      settings.save();
    }
  }
</script>

<div class="flex items-center gap-3 px-4 py-2.5 bg-bg-surface border-b border-border">
  <button
    class="px-5 py-1.5 rounded-lg bg-accent text-white font-semibold text-sm
           hover:bg-accent-hover active:bg-accent-pressed disabled:opacity-40
           disabled:cursor-not-allowed transition-colors"
    onclick={convertAll}
    disabled={files.count === 0 || conversion.isRunning}>
    Convert All
  </button>

  <div class="w-px h-6 bg-border"></div>

  <button class="toolbar-btn" onclick={copyMarkdown} disabled={!getCurrentMarkdown()}>Copy</button>
  <button class="toolbar-btn" onclick={saveMarkdown} disabled={!getCurrentMarkdown()}>Save</button>

  <div class="flex-1"></div>

  <button class="toolbar-btn text-error hover:text-red-400" onclick={clearFiles}>Clear</button>

  <div class="w-px h-6 bg-border"></div>

  <button class="toolbar-btn text-text-muted text-xs" onclick={pickOutputDir}>
    {settings.outputDir ? settings.outputDir.split('/').pop() : "Output folder..."}
  </button>
</div>

<style>
  .toolbar-btn {
    @apply px-3.5 py-1.5 rounded-lg text-sm font-medium text-text-secondary
           hover:bg-bg-raised hover:text-text-primary active:bg-bg-surface
           disabled:opacity-30 disabled:cursor-not-allowed transition-colors
           border border-transparent;
  }
</style>
```

### `FilePanel.svelte`

```svelte
<script lang="ts">
  import { open } from "@tauri-apps/plugin-dialog";
  import { files } from "../stores/files.svelte";
  import FileItem from "./FileItem.svelte";

  let dropActive = $state(false);

  async function browseFiles() {
    const selected = await open({
      multiple: true,
      filters: [{ name: "All Supported", extensions: ["pdf","docx","doc","xlsx","xls","csv","pptx","ppt","html","htm","xml","json","txt","md","epub","jpg","jpeg","png","gif","bmp","tiff","tif","mp3","wav","m4a","flac","ogg","msg","ipynb","zip","rss"] }]
    });
    if (selected) files.addFiles(Array.isArray(selected) ? selected : [selected]);
  }

  function handleDrop(e: DragEvent) {
    dropActive = false;
    // Tauri exposes dropped file paths via the event's data
    // For HTML5 drag-drop fallback: use e.dataTransfer?.files
    // Tauri v2: use onDragDropEvent from @tauri-apps/api/window
  }
</script>

<div class="flex flex-col h-full bg-bg-deep">
  <div class="flex items-center justify-between px-4 py-3 bg-bg-surface border-b border-border">
    <span class="text-xs font-semibold text-text-muted tracking-wider">FILES</span>
    <div class="flex items-center gap-2">
      {#if files.count > 0}
        <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-bg-raised text-text-muted">
          {files.count}
        </span>
      {/if}
      <button
        class="w-7 h-7 flex items-center justify-center rounded-lg border border-border
               text-text-muted hover:bg-bg-raised hover:text-text-primary transition-colors text-lg font-bold"
        onclick={browseFiles}>+</button>
    </div>
  </div>

  <div
    class="flex-1 overflow-y-auto"
    class:drop-zone-active={dropActive}
    ondragover={(e) => { e.preventDefault(); dropActive = true; }}
    ondragleave={() => dropActive = false}
    ondrop={handleDrop}>

    {#if files.list.length === 0}
      <div class="flex items-center justify-center h-full text-text-dim text-sm text-center px-6 leading-relaxed">
        Drop files or folders here<br>or click + to browse
      </div>
    {:else}
      <div class="py-1">
        {#each files.list as file (file.path)}
          <FileItem {file} onremove={() => files.removeFile(file.path)} />
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .drop-zone-active {
    @apply bg-accent-dim/20 border-2 border-dashed border-accent rounded-lg m-2;
  }
</style>
```

### `PreviewPanel.svelte`

```svelte
<script lang="ts">
  import { marked } from "marked";
  import hljs from "highlight.js";
  import { preview } from "../stores/preview.svelte";

  let activeTab = $state<"preview" | "source">("preview");

  // Configure marked with highlight.js
  marked.setOptions({
    highlight: (code, lang) => {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    }
  });

  let renderedHtml = $derived(preview.markdown ? marked.parse(preview.markdown) : "");
</script>

<div class="flex flex-col h-full bg-bg-deep">
  <div class="flex bg-bg-surface border-b border-border px-1 pt-2">
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors"
      class:text-text-primary={activeTab === "preview"}
      class:text-text-muted={activeTab !== "preview"}
      class:bg-bg-deep={activeTab === "preview"}
      class:hover:bg-bg-raised={activeTab !== "preview"}
      onclick={() => activeTab = "preview"}>Preview</button>
    <button
      class="px-5 py-2 rounded-t-lg text-sm font-medium transition-colors"
      class:text-text-primary={activeTab === "source"}
      class:text-text-muted={activeTab !== "source"}
      class:bg-bg-deep={activeTab === "source"}
      class:hover:bg-bg-raised={activeTab !== "source"}
      onclick={() => activeTab = "source"}>Source</button>
  </div>

  <div class="flex-1 overflow-auto">
    {#if activeTab === "preview"}
      <div class="prose prose-invert max-w-3xl mx-auto p-8">
        {@html renderedHtml}
      </div>
    {:else}
      <pre class="p-6 text-sm font-mono text-text-secondary whitespace-pre-wrap break-words">{preview.markdown}</pre>
    {/if}
  </div>
</div>
```

### `FileItem.svelte`

```svelte
<script lang="ts">
  import type { FileEntry } from "../stores/files.svelte";

  let { file, onremove }: { file: FileEntry; onremove: () => void } = $props();

  const EXT_COLORS: Record<string, string> = {
    pdf: "bg-error", docx: "bg-blue-600", doc: "bg-blue-600",
    xlsx: "bg-success", xls: "bg-success", csv: "bg-success",
    pptx: "bg-orange-600", ppt: "bg-orange-600",
    html: "bg-accent", htm: "bg-accent",
    jpg: "bg-purple-600", jpeg: "bg-purple-600", png: "bg-purple-600", gif: "bg-purple-600",
    mp3: "bg-teal-600", wav: "bg-teal-600", zip: "bg-gray-600",
  };

  let extColor = $derived(EXT_COLORS[file.ext.toLowerCase()] ?? "bg-gray-600");

  function statusIcon(status: string) {
    switch (status) {
      case "converted": return { text: "✓", cls: "text-success" };
      case "converting": return { text: "⟳", cls: "text-warning animate-spin" };
      case "error": return { text: "✗", cls: "text-error" };
      default: return { text: "", cls: "text-text-dim" };
    }
  }

  let status = $derived(statusIcon(file.status));
</script>

<div
  class="flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg cursor-pointer
         hover:bg-bg-surface active:bg-bg-raised transition-colors group"
  role="listitem"
  tabindex="0"
>
  <div class="{extColor} w-9 h-9 rounded-lg flex items-center justify-center text-white text-[10px] font-bold uppercase flex-shrink-0">
    {file.ext}
  </div>
  <div class="flex-1 min-w-0">
    <div class="text-sm font-medium text-text-primary truncate">{file.name}</div>
    <div class="text-xs text-text-muted">{file.sizeFormatted}</div>
  </div>
  <div class="text-sm font-semibold w-5 text-center {status.cls}">{status.text}</div>
  <!-- Dropdown for remove? -->
  <button class="hidden group-hover:block text-text-dim hover:text-error ml-1" onclick={onremove} title="Remove">×</button>
</div>
```

### `StatusBar.svelte`

```svelte
<script lang="ts">
  import { conversion } from "../stores/conversion.svelte";
  import { files } from "../stores/files.svelte";

  let progressPct = $derived(
    conversion.total > 0 ? (conversion.current / conversion.total) * 100 : 0
  );
</script>

<div class="flex items-center gap-4 px-4 h-full text-xs text-text-muted">
  <span>{conversion.isRunning ? "Converting..." : "Ready"}</span>

  {#if files.count > 0}
    <span>{files.count} file{files.count !== 1 ? "s" : ""}</span>
    {#if conversion.total > 0}
      <span>· {conversion.completed} / {conversion.total} converted</span>
    {/if}
  {/if}

  <div class="flex-1"></div>

  {#if conversion.isRunning}
    <div class="w-40 h-1.5 bg-bg-raised rounded-full overflow-hidden">
      <div class="h-full bg-accent rounded-full transition-all duration-300" style="width: {progressPct}%"></div>
    </div>
  {/if}
</div>
```

### Stores

**`files.svelte.ts`**
```typescript
import { invoke } from "@tauri-apps/api/core";

export type Status = "pending" | "converting" | "converted" | "error";

export interface FileEntry {
  path: string;
  name: string;
  ext: string;
  size: number;
  sizeFormatted: string;
  status: Status;
}

const SUPPORTED = new Set(["pdf","docx","doc","xlsx","xls","csv","pptx","ppt","html","htm",
  "xml","json","txt","md","epub","jpg","jpeg","png","gif","bmp","tiff","tif",
  "mp3","wav","m4a","flac","ogg","msg","ipynb","zip","rss"]);

function formatSize(bytes: number): string {
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  for (const unit of units) {
    if (size < 1024) return unit === "B" ? `${size} ${unit}` : `${size.toFixed(1)} ${unit}`;
    size /= 1024;
  }
  return `${size.toFixed(1)} TB`;
}

function createFilesStore() {
  let list = $state<FileEntry[]>([]);

  return {
    get list() { return list; },
    get count() { return list.length; },
    get paths() { return list.map(f => f.path); },

    addFiles(paths: string[]) {
      const existing = new Set(list.map(f => f.path));
      for (const p of paths) {
        if (existing.has(p)) continue;
        const parts = p.split(/[/\\]/);
        const name = parts[parts.length - 1] ?? p;
        const ext = (name.split(".").pop() ?? "").toLowerCase();
        if (SUPPORTED.has(ext) || !ext) {
          list.push({ path: p, name, ext, size: 0, sizeFormatted: "", status: "pending" });
          // Get file size asynchronously
          this.refreshSize(p);
        }
      }
    },

    async refreshSize(path: string) {
      // Use Tauri FS plugin or fetch API
      const entry = list.find(f => f.path === path);
      if (!entry) return;
      // For now, placeholder:
      entry.size = 0;
      entry.sizeFormatted = "?";
    },

    removeFile(path: string) {
      list = list.filter(f => f.path !== path);
    },

    clearFiles() {
      list = [];
    },

    updateStatus(path: string, status: Status) {
      const entry = list.find(f => f.path === path);
      if (entry) entry.status = status;
    }
  };
}

export const files = createFilesStore();
```

**`conversion.svelte.ts`**
```typescript
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { files } from "./files.svelte";
import { preview } from "./preview.svelte";

function createConversionStore() {
  let isRunning = $state(false);
  let current = $state(0);
  let total = $state(0);
  let completed = $state(0);
  let results = $state<Map<string, string>>(new Map());

  listen("conversion-started", (event: any) => {
    files.updateStatus(event.payload, "converting");
    current++;
  });

  listen("conversion-finished", (event: any) => {
    const data = event.payload as Array<{ file: string; markdown: string; error?: string; output_path?: string }>;
    for (const r of data) {
      if (r.error) {
        files.updateStatus(r.file, "error");
      } else {
        files.updateStatus(r.file, "converted");
        results.set(r.file, r.markdown);
      }
      completed++;
    }
    current = total;
    isRunning = false;
  });

  return {
    get isRunning() { return isRunning; },
    get current() { return current; },
    get total() { return total; },
    get completed() { return completed; },
    get completedCount() { return completed; },

    async startConversion(filePaths: string[], outputDir: string) {
      isRunning = true;
      current = 0;
      completed = 0;
      total = filePaths.length;
      results.clear();

      try {
        await invoke("convert_files", { files: filePaths, outputDir: outputDir || null });
      } catch (e) {
        console.error("Conversion failed:", e);
        isRunning = false;
      }
    },

    getResult(path: string): string | undefined {
      return results.get(path);
    }
  };
}

export const conversion = createConversionStore();
```

**`settings.svelte.ts`**
```typescript
import { invoke } from "@tauri-apps/api/core";

interface AppSettings {
  output_directory: string;
  dark_mode: boolean;
  use_ocr: boolean;
  extract_images: boolean;
}

function createSettingsStore() {
  let data = $state<AppSettings>({
    output_directory: "",
    dark_mode: true,
    use_ocr: false,
    extract_images: true,
  });

  return {
    get outputDir() { return data.output_directory; },
    set outputDir(v: string) { data.output_directory = v; },
    get darkMode() { return data.dark_mode; },
    set darkMode(v: boolean) { data.dark_mode = v; },

    async load() {
      try {
        data = await invoke<AppSettings>("get_settings");
      } catch {
        // Use defaults
      }
    },

    async save() {
      await invoke("set_settings", { newSettings: data });
    }
  };
}

export const settings = createSettingsStore();
```

---

## Phase 5 — Build & CI

### Build commands

```bash
# Development
npm run tauri dev

# Production build (all platforms)
npm run tauri build

# Linux-only
npm run tauri build -- --target x86_64-unknown-linux-gnu

# Sidecar build (per platform, before tauri build)
cd python-sidecar
pip install -r requirements.txt
pyinstaller convert.spec
cp dist/markit-convert ../src-tauri/sidecars/markit-convert-$(uname -s)-$(uname -m)
```

### `.github/workflows/release.yml`

```yaml
name: Build & Release

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  build-sidecar:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
            suffix: Linux-x86_64
          - os: windows-latest
            target: x86_64-pc-windows-msvc
            suffix: Windows-x86_64
          - os: macos-latest
            target: x86_64-apple-darwin
            suffix: Darwin-x86_64
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: |
          cd python-sidecar
          pip install -r requirements.txt
          pyinstaller convert.spec
          mkdir -p ../src-tauri/sidecars
          cp dist/markit-convert* ../src-tauri/sidecars/markit-convert-${{ matrix.suffix }}
      - uses: actions/upload-artifact@v4
        with:
          name: sidecar-${{ matrix.suffix }}
          path: src-tauri/sidecars/markit-convert-${{ matrix.suffix }}

  build-tauri:
    needs: build-sidecar
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
          - os: windows-latest
            target: x86_64-pc-windows-msvc
          - os: macos-latest
            target: x86_64-apple-darwin
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: sidecar-* }
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: "v__VERSION__"
          releaseBody: "See the assets to download."
          releaseDraft: false
          prerelease: false
```

---

## Phase 6 — Cleanup & docs

1. **Update `AGENTS.md`** — reflect Tauri/Svelte architecture, new dev commands
2. **Update `README.md`** — new install instructions (no more `pip install`; provide download links), build-from-source using Tauri
3. **Remove stale files** — any remaining Python build artifacts

---

## Light theme

Define CSS custom properties for light theme using `data-theme="light"`:

```css
[data-theme="light"] {
  --color-bg-deep: #fafaf7;
  --color-bg-surface: #f5f5f0;
  --color-bg-raised: #e8e8e0;
  --color-border: #e0e0d8;
  --color-border-hover: #c0c0b8;
  --color-accent: #a6763b;
  --color-accent-hover: #c7924b;
  --color-text-primary: #2d2d2a;
  --color-text-secondary: #5a5a52;
  --color-text-muted: #878780;
  --color-text-dim: #a0a098;
}
```

Toggle via `Ctrl+T` keyboard shortcut (Tauri global shortcut), or a button in toolbar.

---

## Supported file extensions (color mapping)

| Extension | Color |
|-----------|-------|
| .pdf | Red |
| .docx, .doc | Blue |
| .xlsx, .xls, .csv | Green |
| .pptx, .ppt | Orange |
| .html, .htm | Amber |
| .jpg, .jpeg, .png, .gif, .bmp, .tiff, .tif | Purple |
| .mp3, .wav, .m4a, .flac, .ogg | Teal |
| .zip | Gray |
| Other | Dark gray |

---

## Key implementation notes

1. **Tauri v2 event system**: Use `app.emit()` in Rust to push events to frontend. Use `listen()` in Svelte to receive. Events are the bridge for sidecar progress reporting.

2. **Drag and drop**: Tauri v2 supports drag-drop natively via the window's `onDragDropEvent`. The frontend receives the file paths directly (no HTML5 data-transfer workarounds needed).

3. **File dialogs**: Use `@tauri-apps/plugin-dialog` for open/save directory dialogs. These are native OS dialogs, not HTML file inputs.

4. **Clipboard**: Use `navigator.clipboard.writeText()` in the frontend for copy-to-clipboard. Works in Tauri's webview.

5. **Svelte 5 runes**: Use `$state`, `$derived`, `$effect` instead of Svelte 4 stores. Run `$state` inside module-level functions (like `createFilesStore()`) for shared reactive state.

6. **Sidecar naming**: The sidecar binary must follow the naming convention `{name}-{targetTriple}` (e.g., `markit-convert-x86_64-unknown-linux-gnu`). Tauri's `shell` plugin resolves the correct platform binary automatically.

7. **Sidecar size concern**: The Python sidecar adds ~60-100MB to the bundle. This can be reduced by:
   - Using a minimal Python distribution (e.g., `python-build-standalone`)
   - Only including required converters (slim install)
   - Eventually migrating popular converters to Rust

8. **Markdown CSS**: Use Tailwind's `@plugin "@tailwindcss/typography"` for the default prose styles. Override with custom theme colors for headings, code blocks, etc.

9. **Splitter resize**: Implement with CSS `resize: horizontal` on the FilePanel, or a simple draggable handle between the two panels.
