# MarkIt-Desktop

A modern cross-platform desktop GUI for [MarkItDown](https://github.com/microsoft/markitdown), the file-to-Markdown converter by Microsoft.

Convert PDFs, Word documents, Excel spreadsheets, PowerPoint presentations, HTML, images, audio, EPUBs, and more to clean Markdown — all through a clean, intuitive interface.

## Features

- **Drag & drop** — Drop files or folders directly into the app
- **Live preview** — See the converted Markdown instantly, rendered as HTML
- **Batch conversion** — Convert multiple files at once with a single click
- **Raw Markdown view** — Toggle between rendered preview and raw Markdown
- **Auto-save** — Optionally save converted Markdown to a directory automatically
- **Clipboard support** — Copy converted Markdown to clipboard
- **Dark & Light themes** — Switch with `Ctrl+T`
- **Cross-platform** — Linux, Windows, and macOS

## Supported Formats

| Category | Formats |
|----------|---------|
| Documents | `.pdf`, `.docx`, `.doc` |
| Spreadsheets | `.xlsx`, `.xls`, `.csv` |
| Presentations | `.pptx`, `.ppt` |
| Web | `.html`, `.htm`, `.xml`, `.rss` |
| Data | `.json`, `.ipynb` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg` |
| E-books | `.epub` |
| Email | `.msg` |
| Archives | `.zip` |
| Text | `.txt`, `.md` |

## Installation

### pip (any OS with Python 3.10+)

```bash
pip install markitdown-gui
markitdown-gui
```

### Linux

| Format | Command |
|--------|---------|
| **AppImage** | Download from [Releases](https://github.com/microsoft/markitdown/releases), `chmod +x` and run |
| **Debian/Ubuntu** | `sudo dpkg -i markitdown-gui_*.deb` |
| **Fedora/RHEL** | `sudo rpm -i markitdown-gui-*.rpm` |
| **Arch (AUR)** | `yay -S markitdown-gui` |

### Windows

Download the `.exe` from [Releases](https://github.com/microsoft/markitdown/releases) and run — no installation required.

### macOS

Download the `.dmg` from [Releases](https://github.com/microsoft/markitdown/releases) and drag to Applications.

## Building from Source

```bash
git clone https://github.com/microsoft/markitdown.git
cd markitdown
pip install -e "markitdown[all]"

cd ../markitdown-gui
pip install -e .
markitdown-gui
```

### Standalone Binary

```bash
pip install pyinstaller
pyinstaller build/pyinstaller.spec
```

## Tech Stack

- **[PySide6](https://wiki.qt.io/Qt_for_Python)** — Qt for Python, providing native look on all platforms
- **[MarkItDown](https://github.com/microsoft/markitdown)** — File-to-Markdown conversion engine
- **[Markdown](https://python-markdown.github.io/)** — Markdown to HTML renderer for preview

## License

MIT — see [LICENSE](LICENSE) for details.
