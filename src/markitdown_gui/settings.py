from PySide6.QtCore import QSettings


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = QSettings("MarkItDown", "MarkItDownGUI")
        return cls._instance

    @property
    def _s(self):
        return self._settings

    @property
    def output_directory(self) -> str:
        return self._s.value("output_directory", "", str)

    @output_directory.setter
    def output_directory(self, value: str):
        self._s.setValue("output_directory", value)

    @property
    def dark_mode(self) -> bool:
        return self._s.value("dark_mode", True, type=bool)

    @dark_mode.setter
    def dark_mode(self, value: bool):
        self._s.setValue("dark_mode", value)

    @property
    def last_directory(self) -> str:
        return self._s.value("last_directory", "", str)

    @last_directory.setter
    def last_directory(self, value: str):
        self._s.setValue("last_directory", value)

    @property
    def window_geometry(self) -> bytes:
        return self._s.value("window_geometry", b"")

    @window_geometry.setter
    def window_geometry(self, value: bytes):
        self._s.setValue("window_geometry", value)

    @property
    def use_ocr(self) -> bool:
        return self._s.value("use_ocr", False, type=bool)

    @use_ocr.setter
    def use_ocr(self, value: bool):
        self._s.setValue("use_ocr", value)

    @property
    def extract_images(self) -> bool:
        return self._s.value("extract_images", True, type=bool)

    @extract_images.setter
    def extract_images(self, value: bool):
        self._s.setValue("extract_images", value)
