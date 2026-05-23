# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

src_dir = Path(__file__).parent.parent / "src"

a = Analysis(
    [str(src_dir / "markitdown_gui" / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(src_dir / "markitdown_gui" / "resources" / "styles.qss"), "markitdown_gui/resources"),
    ],
    hiddenimports=[
        "markitdown",
        "markitdown.converters",
        "markitdown.converters._pdf_converter",
        "markitdown.converters._docx_converter",
        "markitdown.converters._xlsx_converter",
        "markitdown.converters._pptx_converter",
        "markitdown.converters._html_converter",
        "markitdown.converters._csv_converter",
        "markitdown.converters._image_converter",
        "markitdown.converters._audio_converter",
        "markitdown.converters._epub_converter",
        "markitdown.converters._ipynb_converter",
        "markitdown.converters._outlook_msg_converter",
        "markitdown.converters._rss_converter",
        "markitdown.converters._zip_converter",
        "markitdown.converters._plain_text_converter",
        "markdown",
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite",
        "pygments",
        "pygments.styles",
        "pygments.lexers",
        "PySide6",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="markitdown-gui",
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
