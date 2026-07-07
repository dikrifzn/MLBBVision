from pathlib import Path
import torch

# PATH

ROOT_DIR = Path(__file__).parent

DATASET_DIR = ROOT_DIR / "dataset"

CHECKPOINT_DIR = ROOT_DIR / "checkpoints"

LOG_DIR = ROOT_DIR / "logs"

CHECKPOINT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# DEVICE

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# IMAGE

IMAGE_SIZE = 224

# DATALOADER

BATCH_SIZE = 16

NUM_WORKERS = 0

PIN_MEMORY = DEVICE.type == "cuda"

# TRAINING

EPOCHS = 20

LEARNING_RATE = 1e-3

WEIGHT_DECAY = 1e-4

# NORMALIZATION

MEAN = (0.485, 0.456, 0.406)

STD = (0.229, 0.224, 0.225)

# AUGMENTATION

BRIGHTNESS = 0.12

CONTRAST = 0.12

BLUR = (3, 5)

NOISE = (0.005, 0.02)

JPEG = (80, 100)

# SAVE

BEST_MODEL = CHECKPOINT_DIR / "best_model.pth"

LAST_MODEL = CHECKPOINT_DIR / "last_model.pth"

CLASS_MAPPING = ROOT_DIR / "classes.json"