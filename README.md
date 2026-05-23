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
- **Dark & Light themes** — Switch with a click
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

### Linux

| Format | Command |
|--------|---------|
| **AppImage** | Download from [Releases](https://github.com/microsoft/markitdown/releases), `chmod +x` and run |
| **Debian/Ubuntu** | `sudo dpkg -i markit-desktop_*.deb` |
| **Fedora/RHEL** | `sudo rpm -i markit-desktop-*.rpm` |
| **Arch (AUR)** | `yay -S markit-desktop` |

### Windows

Download the `.exe` installer from [Releases](https://github.com/microsoft/markitdown/releases) and run.

### macOS

Download the `.dmg` from [Releases](https://github.com/microsoft/markitdown/releases) and drag to Applications.

## Building from Source

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://www.rust-lang.org/tools/install) (v1.70+)
- [Python](https://www.python.org/) (v3.10+)
- [Tauri system dependencies](https://v2.tauri.app/start/prerequisites/)

### Steps

```bash
git clone https://github.com/microsoft/markitdown.git
cd markitdown-gui

# Install frontend dependencies
npm install

# Build the Python sidecar
./build-sidecar.sh

# Run in development mode
npm run tauri dev

# Build production binary
npm run tauri build
```

## Tech Stack

- **[Tauri v2](https://v2.tauri.app/)** — Cross-platform desktop app framework
- **[Svelte 5](https://svelte.dev/)** — Frontend framework
- **[Tailwind CSS v4](https://tailwindcss.com/)** — Utility-first CSS
- **[MarkItDown](https://github.com/microsoft/markitdown)** — File-to-Markdown conversion engine
- **[marked](https://marked.js.org/)** — Markdown to HTML renderer
- **[highlight.js](https://highlightjs.org/)** — Syntax highlighting

## License

MIT — see [LICENSE](LICENSE) for details.
