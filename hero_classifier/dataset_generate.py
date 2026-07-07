from pathlib import Path
from PIL import Image
import numpy as np
import albumentations as A

# CONFIG

INPUT_DIR = Path("dataset_original")
OUTPUT_DIR = Path("dataset")

OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLES_PER_HERO = 50

# AUGMENTATION

transform = A.Compose([

    A.RandomBrightnessContrast(
        brightness_limit=0.12,
        contrast_limit=0.12,
        p=0.8,
    ),

    A.RandomGamma(
        gamma_limit=(95, 105),
        p=0.5,
    ),

    A.GaussianBlur(
        blur_limit=(3, 5),
        p=0.15,
    ),

    A.GaussNoise(
        std_range=(0.005, 0.02),
        p=0.2,
    ),

    A.ImageCompression(
        quality_range=(80, 100),
        p=0.5,
    ),

    A.Sharpen(
        p=0.2,
    ),

])

print("=" * 60)
print("Generating Hero Dataset")
print("=" * 60)

total = 0

files = sorted(INPUT_DIR.glob("*"))

for file in files:

    if file.suffix.lower() not in [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]:
        continue

    hero_name = file.stem

    hero_dir = OUTPUT_DIR / hero_name

    hero_dir.mkdir(parents=True, exist_ok=True)

    # LOAD RGBA

    img = Image.open(file).convert("RGBA")

    rgba = np.array(img)

    rgb = rgba[:, :, :3]

    alpha = rgba[:, :, 3]

    # SAVE ORIGINAL

    Image.fromarray(rgba).save(
        hero_dir / "0000.png"
    )

    # GENERATE

    for i in range(1, SAMPLES_PER_HERO + 1):

        aug = transform(image=rgb)["image"]

        result = np.dstack((aug, alpha))

        Image.fromarray(result).save(
            hero_dir / f"{i:04}.png"
        )

        total += 1

    print(f"{hero_name:<20} -> {SAMPLES_PER_HERO+1}")

print("=" * 60)
print("Finished")
print("Hero :", len(files))
print("Generated :", total)
print("=" * 60)