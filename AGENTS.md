# AGENTS.md — MarkIt-Desktop

## Project overview

A cross-platform **desktop GUI** (Tauri v2 / Svelte 5 / Rust) that wraps Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) file-to-Markdown converter via a Python sidecar process.

## Package naming

- App name: `MarkIt-Desktop`
- npm package: `markit-desktop`
- Tauri identifier: `com.markitdesktop.app`

## Dev commands

```bash
# Install frontend dependencies
npm install

# Build the Python sidecar (required before running)
./build-sidecar.sh

# Run in development mode (hot reload for frontend + Rust)
npm run tauri dev

# Type-check frontend
npm run check

# Check Rust compilation
cd src-tauri && cargo check

# Build production binary
npm run tauri build
```

## Architecture

```
markitdown-gui/
├── src/                        # Svelte 5 frontend
│   ├── App.svelte              # Main layout
│   ├── main.ts                 # Entry point
│   ├── app.css                 # Tailwind CSS v4 + theme tokens
│   └── lib/
│       ├── components/         # UI components
│       │   ├── Toolbar.svelte
│       │   ├── FilePanel.svelte
│       │   ├── PreviewPanel.svelte
│       │   └── StatusBar.svelte
│       └── stores/             # Svelte stores (state management)
│           ├── files.ts
│           ├── conversion.ts
│           └── settings.ts
├── src-tauri/                  # Rust backend
│   ├── src/
│   │   ├── main.rs             # Entry point
│   │   ├── lib.rs              # App setup, command registration
│   │   ├── commands.rs         # IPC commands
│   │   ├── converter.rs        # Sidecar process management
│   │   └── settings.rs         # JSON config persistence
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   ├── capabilities/           # Tauri permissions
│   └── sidecars/               # Platform-specific Python binaries
├── python-sidecar/             # Python conversion sidecar
│   ├── convert.py              # CLI wrapper: stdin JSON → stdout JSON
│   ├── convert.spec            # PyInstaller spec
│   └── requirements.txt
├── build-sidecar.sh            # Sidecar build script
├── package.json
├── vite.config.ts
├── tsconfig.json
└── svelte.config.js
```

### Key design points

- **Frontend**: Svelte 5 with TypeScript, Tailwind CSS v4 for styling. State managed via Svelte stores (`$lib/stores/`).
- **Backend**: Rust (Tauri v2). Handles sidecar process management, settings persistence, file dialogs, and IPC.
- **Sidecar**: Python binary built with PyInstaller. Communicates via stdin/stdout using line-delimited JSON events.
- **IPC**: Frontend calls Rust commands via `@tauri-apps/api/core` `invoke()`. Rust emits events via `app.emit()` for progress updates.
- **Settings**: JSON file stored in app config directory (`~/.config/markit-desktop/settings.json` on Linux).
- **Themes**: Dark (default) and light themes via CSS custom properties. Toggle with button in toolbar.
- **The `markitdown/` subdirectory** is a nested git repository (the MarkItDown library), not a submodule. It is untracked in the parent repo.

### IPC commands (Rust → Frontend)

| Command | Description |
|---------|-------------|
| `convert_files` | Start batch conversion via sidecar |
| `get_settings` | Load app settings |
| `set_settings` | Save app settings |
| `select_output_dir` | Open native folder picker |
| `save_markdown` | Open native save dialog and write file |

### Events (Rust → Frontend)

| Event | Description |
|-------|-------------|
| `conversion-progress` | Progress updates during conversion (started/finished/error/complete) |

## Build & CI

- Frontend build: Vite (`npm run build`)
- Rust build: Cargo via Tauri CLI (`npm run tauri build`)
- Sidecar build: PyInstaller (`./build-sidecar.sh`)
- CI (`release.yml`): triggered on `v*` tags. Builds sidecar per platform, then Tauri bundles for all targets.
- Sidecar binaries are **not** committed — they are built by CI and copied into `src-tauri/sidecars/` before Tauri build.

## No tests or linters

This repo has no test suite, no pre-commit hooks, and no lint/formatter/typecheck config. Use `npm run check` for TypeScript and `cargo check` for Rust.
