# AGENTS.md — MarkIt-Desktop

## Project overview

A cross-platform **desktop GUI** (PySide6 / Qt) that wraps Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) file-to-Markdown converter. This is **not a CLI tool** — the UI depends on a running Qt event loop.

## Package naming

- PyPI name / CLI command: `markit-desktop` (hyphen)
- Python import name: `markit_desktop` (underscore)
- Version source (hatchling dynamic): `src/markit_desktop/__about__.py`

## Dev commands

```bash
# Install in editable mode with all optional deps
pip install -e ".[full]"
# Or via requirements.txt (includes PyInstaller)
pip install -r requirements.txt

# Run the GUI
markit-desktop
# Or directly:
python -m markit_desktop

# Build standalone binary (PyInstaller)
pyinstaller build/pyinstaller.spec

# Build Linux packages (AppImage/deb/rpm)
bash build/packages/AppImage/build.sh
bash build/packages/deb/build.sh
bash build/packages/rpm/build.sh
```

## Architecture

```
src/markit_desktop/
├── __main__.py       # entry point: QApplication + MainWindow
├── __about__.py      # version (read by hatchling at build time)
├── main_window.py    # main UI: toolbar, splitter, conversion orchestration
├── file_panel.py     # left panel: file list, drag & drop
├── preview_panel.py  # right panel: rendered preview + raw markdown tabs
├── converter.py      # ConversionPool: threaded conversions, Qt event bridge
├── settings.py       # QSettings persistence (singleton)
└── resources/
    └── styles.qss    # dark theme stylesheet
```

Key design points:
- **Threading**: file conversions run in daemon threads (`ConversionPool`). Results are posted back to the Qt main thread via a custom `QEvent` bridge (`CallbackHandler`).
- **Settings**: uses `QSettings("MarkItDesktop", "MarkItDesktop")` for persistent config (window geometry, output dir, theme, OCR toggle).
- **Themes**: dark theme loaded from `resources/styles.qss`; light theme is inline CSS in `main_window.py`. Toggle with `Ctrl+T`.
- **The `markitdown/` subdirectory** is a nested git repository (the MarkItDown library), not a submodule. It is untracked in the parent repo.

## Build & CI

- Build backend: `hatchling`
- `build/` and `dist/` are gitignored **except** `build/packages/` and `build/pyinstaller.spec`
- CI (`release.yml`): triggered on `v*` tags. Builds AppImage, deb, rpm (Linux), .exe (Windows), .dmg (macOS)
- Hidden imports in `pyinstaller.spec` must be kept in sync with actual converter modules used

## No tests or linters

This repo has no test suite, no pre-commit hooks, and no lint/formatter/typecheck config. Add tooling before relying on it.
