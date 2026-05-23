#!/usr/bin/env bash
set -euo pipefail

APP_NAME="MarkItDown"
VERSION="${VERSION:-0.1.0}"
ARCH="$(uname -m)"

echo "Building AppImage for ${ARCH}..."

BUILD_DIR="$(mktemp -d)"
APPDIR="${BUILD_DIR}/AppDir"

mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

python -m pip install --target "${APPDIR}/usr/lib/python" -r requirements.txt
python -m pip install --target "${APPDIR}/usr/lib/python" -e .

cat > "${APPDIR}/usr/bin/markitdown-gui" << 'WRAPPER'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/../lib/python"
exec python3 "${SCRIPT_DIR}/../lib/python/markitdown_gui/__main__.py" "$@"
WRAPPER
chmod +x "${APPDIR}/usr/bin/markitdown-gui"

cat > "${APPDIR}/markitdown-gui.desktop" << DESKTOP
[Desktop Entry]
Name=${APP_NAME}
Exec=markitdown-gui %F
Icon=markitdown-gui
Type=Application
Categories=Utility;TextTools;
MimeType=text/plain;application/pdf;
DESKTOP

cat > "${APPDIR}/AppRun" << 'APPRUN'
#!/usr/bin/env bash
SELF="$(readlink -f "$0")"
HERE="$(dirname "$SELF")"
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/lib/python:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH:-}"
exec "${HERE}/usr/bin/markitdown-gui" "$@"
APPRUN
chmod +x "${APPDIR}/AppRun"

wget -q "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-${ARCH}.AppImage" -O linuxdeploy
chmod +x linuxdeploy

./linuxdeploy --appdir "${APPDIR}" \
    --output appimage \
    --desktop-file "${APPDIR}/markitdown-gui.desktop" \
    --icon-file "${APPDIR}/markitdown-gui.png" 2>/dev/null || true

OUTPUT="${APP_NAME}-${VERSION}-${ARCH}.AppImage"
mv "${APP_NAME}"*.AppImage "${OUTPUT}" 2>/dev/null || true

echo "AppImage built: ${OUTPUT}"
