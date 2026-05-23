#!/usr/bin/env bash
set -euo pipefail

APP_NAME="markitdown-gui"
VERSION="${VERSION:-0.1.0}"
ARCH="$(dpkg --print-architecture 2>/dev/null || echo amd64)"

echo "Building .deb package for ${ARCH}..."

BUILD_DIR="$(mktemp -d)"
PKG_DIR="${BUILD_DIR}/${APP_NAME}-${VERSION}"

mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}/usr/bin"
mkdir -p "${PKG_DIR}/usr/share/${APP_NAME}"
mkdir -p "${PKG_DIR}/usr/share/applications"
mkdir -p "${PKG_DIR}/usr/share/doc/${APP_NAME}"

cat > "${PKG_DIR}/DEBIAN/control" << CONTROL
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-pyside6.qtcore, python3-pyside6.qtgui, python3-pyside6.qtwidgets
Maintainer: MarkItDown Contributors
Description: Modern GUI for MarkItDown file-to-Markdown converter
 A cross-platform desktop application for converting various file formats
 to Markdown using the MarkItDown library.
CONTROL

python3 -m pip install --target "${PKG_DIR}/usr/share/${APP_NAME}" -e .

cat > "${PKG_DIR}/usr/bin/markitdown-gui" << WRAPPER
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/${APP_NAME}:\${PYTHONPATH:-}"
exec python3 /usr/share/${APP_NAME}/markitdown_gui/__main__.py "\$@"
WRAPPER
chmod +x "${PKG_DIR}/usr/bin/markitdown-gui"

cat > "${PKG_DIR}/usr/share/applications/markitdown-gui.desktop" << DESKTOP
[Desktop Entry]
Name=MarkItDown GUI
Exec=/usr/bin/markitdown-gui %F
Icon=markitdown-gui
Type=Application
Categories=Utility;TextTools;
DESKTOP

dpkg-deb --build "${PKG_DIR}" "${APP_NAME}_${VERSION}_${ARCH}.deb"

echo "Debian package built: ${APP_NAME}_${VERSION}_${ARCH}.deb"
