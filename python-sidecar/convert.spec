# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import site

site_packages = site.getsitepackages()[0]
user_site = site.getusersitepackages()

# Check venv site-packages first, then user site
venv_site = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'lib', 'python3.14', 'site-packages')
if not os.path.isdir(venv_site):
    for sp in site.getsitepackages():
        if os.path.isdir(os.path.join(sp, 'markitdown')):
            venv_site = sp
            break

# Find magika package directory
magika_dir = None
for path in sys.path + [venv_site]:
    candidate = os.path.join(path, 'magika')
    if os.path.isdir(candidate):
        magika_dir = candidate
        break

# Find markitdown package directory for data files
markitdown_dir = None
for path in sys.path + [venv_site]:
    candidate = os.path.join(path, 'markitdown')
    if os.path.isdir(candidate):
        markitdown_dir = candidate
        break

datas = []
if magika_dir:
    datas.append((magika_dir, 'magika'))

a = Analysis(
    ['convert.py'],
    pathex=[venv_site],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'markitdown',
        'markitdown.converters',
        'markitdown.converters._audio_converter',
        'markitdown.converters._bing_serp_converter',
        'markitdown.converters._csv_converter',
        'markitdown.converters._doc_intel_converter',
        'markitdown.converters._docx_converter',
        'markitdown.converters._epub_converter',
        'markitdown.converters._exiftool',
        'markitdown.converters._html_converter',
        'markitdown.converters._image_converter',
        'markitdown.converters._ipynb_converter',
        'markitdown.converters._llm_caption',
        'markitdown.converters._markdownify',
        'markitdown.converters._outlook_msg_converter',
        'markitdown.converters._pdf_converter',
        'markitdown.converters._plain_text_converter',
        'markitdown.converters._pptx_converter',
        'markitdown.converters._rss_converter',
        'markitdown.converters._transcribe_audio',
        'markitdown.converters._wikipedia_converter',
        'markitdown.converters._xlsx_converter',
        'markitdown.converters._youtube_converter',
        'markitdown.converters._zip_converter',
        'pdfminer',
        'pdfminer.high_level',
        'pdfplumber',
        'mammoth',
        'pandas',
        'openpyxl',
        'xlrd',
        'python_pptx',
        'markdownify',
        'olefile',
        'pydub',
        'speech_recognition',
        'PIL',
        'PIL.Image',
        'bs4',
        'lxml',
        'lxml.etree',
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
