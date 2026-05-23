import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from pygments.styles import get_style_by_name

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QTabWidget,
)
from PySide6.QtCore import Qt


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_markdown = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.preview_browser = QTextBrowser()
        self.preview_browser.setOpenExternalLinks(True)
        self.tabs.addTab(self.preview_browser, "Preview")

        self.raw_browser = QTextBrowser()
        self.raw_browser.setLineWrapMode(QTextBrowser.NoWrap)
        self.tabs.addTab(self.raw_browser, "Raw Markdown")

        layout.addWidget(self.tabs)

    def set_markdown(self, markdown: str):
        self._current_markdown = markdown
        self._update_preview()
        self._update_raw()

    def _update_preview(self):
        html = markdown.markdown(
            self._current_markdown,
            extensions=["tables", "fenced_code", "codehilite"],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "noclasses": True,
                    "style": "github-dark",
                }
            },
        )

        styled_html = f"""
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #eaeaea;
                padding: 16px;
            }}
            h1 {{
                font-size: 24px;
                border-bottom: 1px solid #2a2a4a;
                padding-bottom: 8px;
                margin-bottom: 16px;
            }}
            h2 {{
                font-size: 18px;
                color: #e94560;
                margin-top: 24px;
                margin-bottom: 12px;
            }}
            h3 {{
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 8px;
            }}
            p {{
                margin-bottom: 12px;
                color: #a0a0b0;
            }}
            code {{
                background: #16213e;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: "Consolas", "Monaco", monospace;
                font-size: 13px;
                color: #4ecca3;
            }}
            pre {{
                background: #16213e;
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            pre code {{
                background: none;
                padding: 0;
                color: #eaeaea;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 16px 0;
            }}
            th, td {{
                padding: 8px 12px;
                border: 1px solid #2a2a4a;
                text-align: left;
            }}
            th {{
                background: #1c2541;
                font-weight: 600;
            }}
            ul, ol {{
                padding-left: 24px;
            }}
            li {{
                margin-bottom: 6px;
                color: #a0a0b0;
            }}
            blockquote {{
                border-left: 3px solid #e94560;
                padding-left: 16px;
                margin-left: 0;
                color: #6c6c80;
            }}
            a {{
                color: #e94560;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            hr {{
                border: none;
                border-top: 1px solid #2a2a4a;
                margin: 24px 0;
            }}
            img {{
                max-width: 100%;
                border-radius: 6px;
            }}
        </style>
        {html}
        """
        self.preview_browser.setHtml(styled_html)

    def _update_raw(self):
        self.raw_browser.setPlainText(self._current_markdown)

    def clear(self):
        self._current_markdown = ""
        self.preview_browser.clear()
        self.raw_browser.clear()

    def get_markdown(self) -> str:
        return self._current_markdown
