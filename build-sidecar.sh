#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIDECAR_DIR="${SCRIPT_DIR}/python-sidecar"
OUTPUT_DIR="${SCRIPT_DIR}/src-tauri/sidecars"
VENV_DIR="${SCRIPT_DIR}/.venv"

echo "Building Python sidecar..."

cd "${SIDECAR_DIR}"

# Use venv pip if available, otherwise system pip
if [ -f "${VENV_DIR}/bin/pip" ]; then
    PIP="${VENV_DIR}/bin/pip"
    PYTHON="${VENV_DIR}/bin/python"
elif command -v pip &> /dev/null; then
    PIP="pip"
    PYTHON="python3"
else
    echo "Error: pip not found"
    exit 1
fi

echo "Installing dependencies..."
${PIP} install -r requirements.txt

echo "Building with PyInstaller..."
${PYTHON} -m PyInstaller convert.spec --clean

mkdir -p "${OUTPUT_DIR}"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux)  TARGET_OS="unknown-linux-gnu" ;;
    Darwin) TARGET_OS="apple-darwin" ;;
    MINGW*|MSYS*|CYGWIN*) TARGET_OS="pc-windows-msvc" ;;
    *) echo "Unsupported OS: ${OS}"; exit 1 ;;
esac

case "${ARCH}" in
    x86_64|amd64) TARGET_ARCH="x86_64" ;;
    aarch64|arm64) TARGET_ARCH="aarch64" ;;
    *) echo "Unsupported architecture: ${ARCH}"; exit 1 ;;
esac

TARGET_TRIPLE="${TARGET_ARCH}-${TARGET_OS}"

if [[ "${OS}" == "MINGW"* ]] || [[ "${OS}" == "MSYS"* ]] || [[ "${OS}" == "CYGWIN"* ]]; then
    BINARY_NAME="markit-convert.exe"
    OUTPUT_NAME="markit-convert-${TARGET_TRIPLE}.exe"
else
    BINARY_NAME="markit-convert"
    OUTPUT_NAME="markit-convert-${TARGET_TRIPLE}"
fi

cp "dist/${BINARY_NAME}" "${OUTPUT_DIR}/${OUTPUT_NAME}"
chmod +x "${OUTPUT_DIR}/${OUTPUT_NAME}"

echo "Sidecar built: ${OUTPUT_DIR}/${OUTPUT_NAME}"
