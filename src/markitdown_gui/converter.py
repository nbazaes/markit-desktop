import os
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable

from PySide6.QtCore import QObject, QEvent, QCoreApplication

from markitdown import MarkItDown


@dataclass
class ConversionResult:
    file_path: str
    markdown: str = ""
    error: Optional[str] = None
    output_path: Optional[str] = None


@dataclass
class ConversionTask:
    file_path: str
    output_directory: str = ""
    use_ocr: bool = False
    extract_images: bool = True


_CallbackEventType = QEvent.Type(QEvent.registerEventType())

_handler: Optional[QObject] = None


def set_handler(obj: QObject):
    global _handler
    _handler = obj


class CallbackHandler(QObject):
    def event(self, e):
        if e.type() == _CallbackEventType:
            cb, *args = e.args, e.kwargs
            if isinstance(cb, tuple):
                cb, args = cb[0], cb[1:]
            cb(*args)
            return True
        return super().event(e)


class _CallbackEvent(QEvent):
    def __init__(self, callback, *args):
        super().__init__(_CallbackEventType)
        self.args = (callback, *args)
        self.kwargs = {}


class ConversionPool:
    def __init__(self):
        self._threads: dict[str, threading.Thread] = {}
        self._cancelled: set = set()
        self._lock = threading.Lock()

    def convert(self, task: ConversionTask, started: Callable = None, finished: Callable = None):
        def _run():
            file_path = task.file_path

            with self._lock:
                if file_path in self._cancelled:
                    return

            if started:
                self._post(started, file_path)

            try:
                md = MarkItDown()
                result = md.convert(file_path)
                markdown = result.text_content

                output_path = None
                if task.output_directory:
                    os.makedirs(task.output_directory, exist_ok=True)
                    source_name = Path(file_path).stem
                    output_path = os.path.join(task.output_directory, f"{source_name}.md")
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(markdown)

                conv_result = ConversionResult(
                    file_path=file_path,
                    markdown=markdown,
                    output_path=output_path,
                )

            except Exception as e:
                conv_result = ConversionResult(
                    file_path=file_path,
                    error=str(e),
                )

            if finished:
                self._post(finished, conv_result)

            with self._lock:
                self._threads.pop(file_path, None)

        t = threading.Thread(target=_run, daemon=True)
        with self._lock:
            self._threads[task.file_path] = t
        t.start()

    def _post(self, callback, *args):
        global _handler
        if _handler and QCoreApplication.instance():
            QCoreApplication.instance().postEvent(_handler, _CallbackEvent(callback, *args))

    def cancel(self, file_path: str):
        with self._lock:
            self._cancelled.add(file_path)

    def cancel_all(self):
        with self._lock:
            self._cancelled.update(self._threads.keys())
