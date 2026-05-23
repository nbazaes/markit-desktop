#!/usr/bin/env bash
set -euo pipefail

APP_NAME="markitdown-gui"
VERSION="${VERSION:-0.1.0}"
RELEASE="${RELEASE:-1}"
ARCH="$(uname -m)"

echo "Building .rpm package for ${ARCH}..."

BUILD_DIR="$(mktemp -d)"
RPMBUILD="${BUILD_DIR}/rpmbuild"

mkdir -p "${RPMBUILD}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

SPECS_DIR="${RPMBUILD}/SPECS"

cat > "${SPECS_DIR}/${APP_NAME}.spec" << SPEC
Name:           ${APP_NAME}
Version:        ${VERSION}
Release:        ${RELEASE}
Summary:        Modern GUI for MarkItDown file-to-Markdown converter
License:        MIT
URL:            https://github.com/microsoft/markitdown
BuildArch:      noarch

Requires:       python3 >= 3.10
Requires:       python3-pyside6

%description
A cross-platform desktop application for converting various file formats
to Markdown using the MarkItDown library.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/${APP_NAME}
mkdir -p %{buildroot}/usr/share/applications

cp -r src/markitdown_gui %{buildroot}/usr/share/${APP_NAME}/

cat > %{buildroot}/usr/bin/markitdown-gui << 'WRAPPER'
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/${APP_NAME}:\${PYTHONPATH:-}"
exec python3 /usr/share/${APP_NAME}/__main__.py "\$@"
WRAPPER
chmod +x %{buildroot}/usr/bin/markitdown-gui

cat > %{buildroot}/usr/share/applications/markitdown-gui.desktop << 'DESKTOP'
[Desktop Entry]
Name=MarkItDown GUI
Exec=/usr/bin/markitdown-gui %F
Icon=markitdown-gui
Type=Application
Categories=Utility;TextTools;
DESKTOP

%files
/usr/bin/markitdown-gui
/usr/share/${APP_NAME}/
/usr/share/applications/markitdown-gui.desktop

%post
update-desktop-database &> /dev/null || true

%postun
update-desktop-database &> /dev/null || true
SPEC

cp -r "$(dirname "$0")/../../../src" "${BUILD_DIR}/"

rpmbuild -ba "${SPECS_DIR}/${APP_NAME}.spec" --define "_topdir ${RPMBUILD}"

cp "${RPMBUILD}/RPMS/noarch/${APP_NAME}-${VERSION}-${RELEASE}.noarch.rpm" .

echo "RPM package built: ${APP_NAME}-${VERSION}-${RELEASE}.noarch.rpm"
