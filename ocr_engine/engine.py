import easyocr

from ocr_engine.config import *


# OCR ENGINE

class OCREngine:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

            cls._instance.reader = easyocr.Reader(

                LANGUAGE,

                gpu=USE_GPU

            )

        return cls._instance


# Global Engine

ocr_engine = OCREngine()