import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QToolButton,
    QFileDialog, QFrame,
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon


SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".pptx", ".ppt", ".html", ".htm", ".xml", ".json",
    ".txt", ".md", ".epub", ".jpg", ".jpeg", ".png",
    ".gif", ".bmp", ".tiff", ".tif", ".mp3", ".wav",
    ".m4a", ".flac", ".ogg", ".msg", ".ipynb", ".zip",
    ".rss", ".url",
}

EXTENSION_COLORS = {
    ".pdf": "#e74c3c",
    ".docx": "#2980b9",
    ".doc": "#2980b9",
    ".xlsx": "#27ae60",
    ".xls": "#27ae60",
    ".csv": "#27ae60",
    ".pptx": "#e67e22",
    ".ppt": "#e67e22",
    ".html": "#f39c12",
    ".htm": "#f39c12",
    ".jpg": "#9b59b6",
    ".jpeg": "#9b59b6",
    ".png": "#9b59b6",
    ".gif": "#9b59b6",
    ".mp3": "#1abc9c",
    ".wav": "#1abc9c",
    ".zip": "#34495e",
}


class FilePanel(QWidget):
    files_added = Signal(list)
    file_selected = Signal(str)
    files_removed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_paths: list[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = self._create_header()
        layout.addWidget(header)

        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self._on_drag_enter
        self.file_list.dragMoveEvent = self._on_drag_move
        self.file_list.dropEvent = self._on_drop
        self.file_list.currentItemChanged.connect(self._on_selection_changed)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.file_list)

    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setProperty("class", "panel-header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("FILES")
        title.setStyleSheet("font-weight: 600; font-size: 12px; color: #a0a0b0; letter-spacing: 0.5px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.count_label = QLabel("0")
        self.count_label.setStyleSheet(
            "background: #e94560; color: white; padding: 2px 8px; "
            "border-radius: 10px; font-size: 11px; font-weight: 600;"
        )
        header_layout.addWidget(self.count_label)

        self.add_button = QToolButton()
        self.add_button.setText("+")
        self.add_button.setToolTip("Add files")
        self.add_button.setFixedSize(28, 28)
        self.add_button.clicked.connect(self._browse_files)
        header_layout.addWidget(self.add_button)

        return header

    def _browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Convert",
            "",
            "All Supported Files (*.pdf *.docx *.doc *.xlsx *.xls *.csv *.pptx *.ppt *.html *.htm *.xml *.json *.txt *.md *.epub *.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.mp3 *.wav *.m4a *.flac *.ogg *.msg *.ipynb *.zip *.rss);;All Files (*)",
        )
        if files:
            self.add_files(files)

    def add_files(self, file_paths: list[str]):
        valid_paths = []
        for path in file_paths:
            path = os.path.abspath(path)
            if os.path.isfile(path) and path not in self._file_paths:
                ext = Path(path).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS or not ext:
                    valid_paths.append(path)
                    self._add_file_item(path)

        if valid_paths:
            self._file_paths.extend(valid_paths)
            self._update_count()
            self.files_added.emit(valid_paths)

    def _add_file_item(self, file_path: str):
        name = Path(file_path).name
        ext = Path(file_path).suffix.lower()
        size = os.path.getsize(file_path)

        item = QListWidgetItem()
        item.setData(Qt.UserRole, file_path)
        item.setSizeHint(QSize(0, 52))

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        icon_label = QLabel(ext.upper().replace(".", ""))
        icon_label.setFixedSize(36, 36)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(
            f"background: {EXTENSION_COLORS.get(ext, '#34495e')}; "
            f"border-radius: 6px; color: white; font-size: 10px; "
            f"font-weight: 700;"
        )
        layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        name_label.setWordWrap(False)
        info_layout.addWidget(name_label)

        size_label = QLabel(self._format_size(size))
        size_label.setStyleSheet("font-size: 11px; color: #6c6c80;")
        info_layout.addWidget(size_label)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        status_label = QLabel("○")
        status_label.setObjectName("file_status")
        status_label.setStyleSheet(
            "color: #6c6c80; font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(status_label)

        item.setSizeHint(widget.sizeHint())
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, widget)

    def _format_size(self, size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _update_count(self):
        self.count_label.setText(str(len(self._file_paths)))

    def _on_drag_enter(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _on_drag_move(self, event):
        event.acceptProposedAction()

    def _on_drop(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                for root, _, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(root, f)
                        ext = Path(fp).suffix.lower()
                        if ext in SUPPORTED_EXTENSIONS:
                            files.append(fp)
        if files:
            self.add_files(files)
            event.acceptProposedAction()

    def _on_selection_changed(self, current, previous):
        if current:
            path = current.data(Qt.UserRole)
            self.file_selected.emit(path)

    def _show_context_menu(self, pos):
        item = self.file_list.itemAt(pos)
        if not item:
            return

        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)

        remove_action = menu.addAction("Remove")
        remove_action.triggered.connect(lambda: self._remove_item(item))

        clear_all_action = menu.addAction("Clear All")
        clear_all_action.triggered.connect(self.clear_all)

        menu.exec(self.file_list.mapToGlobal(pos))

    def _remove_item(self, item):
        path = item.data(Qt.UserRole)
        row = self.file_list.row(item)
        self.file_list.takeItem(row)
        if path in self._file_paths:
            self._file_paths.remove(path)
            self._update_count()
            self.files_removed.emit([path])

    def clear_all(self):
        removed = list(self._file_paths)
        self.file_list.clear()
        self._file_paths.clear()
        self._update_count()
        if removed:
            self.files_removed.emit(removed)

    def get_file_paths(self) -> list[str]:
        return list(self._file_paths)

    def set_status(self, file_path: str, status: str):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.data(Qt.UserRole) == file_path:
                widget = self.file_list.itemWidget(item)
                if widget:
                    status_label = widget.findChild(QLabel, "file_status")
                    if status_label:
                        if status == "converted":
                            status_label.setText("✓")
                            status_label.setStyleSheet(
                                "color: #4ecca3; font-size: 14px; font-weight: 600;"
                            )
                        elif status == "error":
                            status_label.setText("✗")
                            status_label.setStyleSheet(
                                "color: #e94560; font-size: 14px; font-weight: 600;"
                            )
                        elif status == "converting":
                            status_label.setText("⟳")
                            status_label.setStyleSheet(
                                "color: #f9a825; font-size: 14px; font-weight: 600;"
                            )
                break
