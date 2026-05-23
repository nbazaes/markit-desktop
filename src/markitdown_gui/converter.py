import os
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool

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


class ConversionWorker(QObject):
    started = Signal(str)
    finished = Signal(ConversionResult)
    progress = Signal(str, int, int)

    def __init__(self):
        super().__init__()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self, task: ConversionTask):
        if self._cancelled:
            return

        file_path = task.file_path
        self.started.emit(file_path)

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

            self.finished.emit(ConversionResult(
                file_path=file_path,
                markdown=markdown,
                output_path=output_path,
            ))

        except Exception as e:
            self.finished.emit(ConversionResult(
                file_path=file_path,
                error=str(e),
            ))


class ConversionPool:
    def __init__(self):
        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(4)
        self._workers: dict[str, ConversionWorker] = {}

    def convert(self, task: ConversionTask, callbacks: dict):
        worker = ConversionWorker()

        if "started" in callbacks:
            worker.started.connect(callbacks["started"])
        if "finished" in callbacks:
            worker.finished.connect(callbacks["finished"])

        self._workers[task.file_path] = worker

        runnable = _WorkerRunnable(worker, task)
        self._pool.start(runnable)

    def cancel(self, file_path: str):
        if file_path in self._workers:
            self._workers[file_path].cancel()
            del self._workers[file_path]

    def cancel_all(self):
        for worker in self._workers.values():
            worker.cancel()
        self._workers.clear()


class _WorkerRunnable(QRunnable):
    def __init__(self, worker: ConversionWorker, task: ConversionTask):
        super().__init__()
        self.worker = worker
        self.task = task
        self.setAutoDelete(True)

    def run(self):
        self.worker.run(self.task)
