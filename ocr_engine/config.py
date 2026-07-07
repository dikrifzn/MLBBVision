from pathlib import Path
import torch


# PATH

ROOT_DIR = Path(__file__).parent


# DEVICE

USE_GPU = torch.cuda.is_available()


# OCR

LANGUAGE = ["en"]

ALLOWLIST = {
    "gold": "0123456789",
    "level": "0123456789",
    "score": "0123456789",
    "duration": "0123456789:",
    "kda": "0123456789/ ",
    "name": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._- "
}


# PREPROCESS

UPSCALE_GOLD = 3

UPSCALE_LEVEL = 4

UPSCALE_SCORE = 5

UPSCALE_KDA = 4

UPSCALE_NAME = 3

UPSCALE_DURATION = 4


CLAHE_CLIP = 2.0

CLAHE_GRID = (8, 8)


# DEBUG

DEBUG = False

DEBUG_DIR = ROOT_DIR / "debug"

DEBUG_DIR.mkdir(
    exist_ok=True
)