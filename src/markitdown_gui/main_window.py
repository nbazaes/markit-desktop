import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QLabel,
    QToolButton, QFileDialog, QProgressBar, QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QAction, QKeySequence

from markitdown_gui.settings import Settings
from markitdown_gui.file_panel import FilePanel
from markitdown_gui.preview_panel import PreviewPanel
from markitdown_gui.converter import ConversionPool, ConversionTask, ConversionResult


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.conversion_pool = ConversionPool()
        self._conversion_results: dict[str, str] = {}
        self._converting_count = 0
        self._total_to_convert = 0

        self._setup_ui()
        self._load_settings()
        self._apply_theme()

    def _setup_ui(self):
        self.setWindowTitle("MarkItDown GUI")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        self._create_menu_bar()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Files...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(lambda: self.file_panel._browse_files())
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")

        copy_action = QAction("&Copy Markdown", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy_markdown)
        edit_menu.addAction(copy_action)

        view_menu = menubar.addMenu("&View")

        theme_action = QAction("Toggle &Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)

        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        self.convert_btn = QToolButton()
        self.convert_btn.setText("⚡ Convert All")
        self.convert_btn.setObjectName("primary")
        self.convert_btn.setToolTip("Convert all files to Markdown")
        self.convert_btn.clicked.connect(self._convert_all)
        toolbar.addWidget(self.convert_btn)

        toolbar.addSeparator()

        self.copy_btn = QToolButton()
        self.copy_btn.setText("📋 Copy")
        self.copy_btn.setToolTip("Copy current markdown to clipboard")
        self.copy_btn.clicked.connect(self._copy_markdown)
        self.copy_btn.setEnabled(False)
        toolbar.addWidget(self.copy_btn)

        self.save_btn = QToolButton()
        self.save_btn.setText("💾 Save")
        self.save_btn.setToolTip("Save markdown to file")
        self.save_btn.clicked.connect(self._save_markdown)
        self.save_btn.setEnabled(False)
        toolbar.addWidget(self.save_btn)

        toolbar.addSeparator()

        self.clear_btn = QToolButton()
        self.clear_btn.setText("🗑️ Clear")
        self.clear_btn.setToolTip("Clear all files")
        self.clear_btn.clicked.connect(self._clear_all)
        self.clear_btn.setEnabled(False)
        toolbar.addWidget(self.clear_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        output_widget = QWidget()
        output_layout = QHBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(8)

        output_label = QLabel("Output:")
        output_label.setStyleSheet("color: #6c6c80; font-size: 12px;")
        output_layout.addWidget(output_label)

        self.output_btn = QToolButton()
        self.output_btn.setText("Select folder...")
        self.output_btn.setToolTip("Select output directory")
        self.output_btn.clicked.connect(self._select_output_dir)
        output_layout.addWidget(self.output_btn)

        self.output_path_label = QLabel("")
        self.output_path_label.setStyleSheet(
            "color: #4ecca3; font-size: 12px; font-family: monospace;"
        )
        output_layout.addWidget(self.output_path_label)

        toolbar.addWidget(output_widget)

    def _create_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        self.file_panel = FilePanel()
        self.file_panel.files_added.connect(self._on_files_added)
        self.file_panel.file_selected.connect(self._on_file_selected)
        self.file_panel.files_removed.connect(self._on_files_removed)
        splitter.addWidget(self.file_panel)

        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)

        splitter.setSizes([320, 880])

        layout.addWidget(splitter)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c6c80;")
        self.status_bar.addPermanentWidget(self.status_label, 1)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #6c6c80; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _load_settings(self):
        geom = self.settings.window_geometry
        if geom:
            self.restoreGeometry(QByteArray(geom))

        output_dir = self.settings.output_directory
        if output_dir and os.path.isdir(output_dir):
            self._set_output_directory(output_dir)

        if not self.settings.dark_mode:
            self._apply_light_theme()

    def _save_settings(self):
        self.settings.window_geometry = bytes(self.saveGeometry())

    def _apply_theme(self):
        import os
        style_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def _apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #f5f5f5; color: #1a1a1a; }
            QToolBar { background-color: #ffffff; border-bottom: 1px solid #e0e0e0; }
            QToolButton, QPushButton {
                background-color: #ffffff; color: #1a1a1a;
                border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px 16px;
            }
            QToolButton:hover, QPushButton:hover { background-color: #f0f0f0; }
            QPushButton#primary { background-color: #e94560; border-color: #e94560; color: white; }
            QPushButton#primary:hover { background-color: #ff6b81; }
            QListWidget { background-color: #ffffff; border: none; }
            QListWidget::item:hover { background-color: #f0f0f0; }
            QListWidget::item:selected { background-color: #e8e8e8; border: 1px solid #e94560; }
            QTextBrowser { background-color: #ffffff; border: none; padding: 16px; }
            QStatusBar { background-color: #ffffff; border-top: 1px solid #e0e0e0; }
            QProgressBar { background-color: #e0e0e0; border: none; border-radius: 2px; height: 4px; }
            QProgressBar::chunk { background-color: #e94560; border-radius: 2px; }
            QMenuBar { background-color: #ffffff; color: #1a1a1a; border-bottom: 1px solid #e0e0e0; }
            QMenu { background-color: #ffffff; color: #1a1a1a; border: 1px solid #e0e0e0; }
            QTabBar::tab { background-color: #f0f0f0; color: #666; }
            QTabBar::tab:selected { background-color: #ffffff; color: #1a1a1a; }
        """)

    def _toggle_theme(self):
        self.settings.dark_mode = not self.settings.dark_mode
        if self.settings.dark_mode:
            self._apply_theme()
        else:
            self._apply_light_theme()

    def _select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.settings.last_directory
        )
        if directory:
            self._set_output_directory(directory)

    def _set_output_directory(self, directory: str):
        self.settings.output_directory = directory
        self.settings.last_directory = directory
        self.output_path_label.setText(directory)

    def _on_files_added(self, files: list[str]):
        self.convert_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self._update_status()

    def _on_files_removed(self, files: list[str]):
        for f in files:
            self._conversion_results.pop(f, None)
        if not self.file_panel.get_file_paths():
            self.convert_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.preview_panel.clear()
        self._update_status()

    def _on_file_selected(self, file_path: str):
        if file_path in self._conversion_results:
            self.preview_panel.set_markdown(self._conversion_results[file_path])
            self.copy_btn.setEnabled(True)
            self.save_btn.setEnabled(True)

    def _convert_all(self):
        files = self.file_panel.get_file_paths()
        if not files:
            return

        output_dir = self.settings.output_directory
        self._total_to_convert = len(files)
        self._converting_count = 0

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(self._total_to_convert)
        self.progress_bar.setValue(0)
        self.convert_btn.setEnabled(False)

        for file_path in files:
            if file_path in self._conversion_results:
                self._on_conversion_finished(ConversionResult(
                    file_path=file_path,
                    markdown=self._conversion_results[file_path],
                ))
                continue

            self.file_panel.set_status(file_path, "converting")

            task = ConversionTask(
                file_path=file_path,
                output_directory=output_dir,
                use_ocr=self.settings.use_ocr,
                extract_images=self.settings.extract_images,
            )

            self.conversion_pool.convert(task,
                started=lambda p, fp=file_path: self.file_panel.set_status(fp, "converting"),
                finished=self._on_conversion_finished,
            )

    def _on_conversion_finished(self, result: ConversionResult):
        self._converting_count += 1
        self.progress_bar.setValue(self._converting_count)

        if result.error:
            self.file_panel.set_status(result.file_path, "error")
        else:
            self._conversion_results[result.file_path] = result.markdown
            self.file_panel.set_status(result.file_path, "converted")

            if result.output_path:
                self.status_label.setText(f"Saved: {result.output_path}")

        if self._converting_count >= self._total_to_convert:
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            self._update_status()

            if result.markdown:
                self.preview_panel.set_markdown(result.markdown)
                self.copy_btn.setEnabled(True)
                self.save_btn.setEnabled(True)

    def _copy_markdown(self):
        md = self.preview_panel.get_markdown()
        if md:
            clipboard = self.application().clipboard()
            clipboard.setText(md)
            self.status_label.setText("Copied to clipboard")

    def _save_markdown(self):
        md = self.preview_panel.get_markdown()
        if not md:
            return

        default_name = "output.md"
        files = self.file_panel.get_file_paths()
        if files:
            default_name = Path(files[0]).stem + ".md"

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Markdown", default_name, "Markdown Files (*.md);;All Files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            self.status_label.setText(f"Saved: {path}")

    def _clear_all(self):
        self.file_panel.clear_all()
        self.preview_panel.clear()
        self._conversion_results.clear()
        self.convert_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText("Ready")

    def _update_status(self):
        total = len(self.file_panel.get_file_paths())
        converted = len(self._conversion_results)
        if total > 0:
            self.progress_label.setText(f"{converted} of {total} converted")
        else:
            self.progress_label.setText("")

    def _show_about(self):
        QMessageBox.about(
            self,
            "About MarkItDown GUI",
            "<h3>MarkItDown GUI</h3>"
            "<p>A modern cross-platform GUI for converting files to Markdown.</p>"
            "<p>Built with PySide6 (Qt for Python).</p>"
            "<p>Powered by <a href='https://github.com/microsoft/markitdown'>MarkItDown</a>.</p>",
        )

    def closeEvent(self, event):
        self.conversion_pool.cancel_all()
        self._save_settings()
        super().closeEvent(event)
