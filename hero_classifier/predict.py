import json
import argparse

import cv2
import numpy as np
import torch
import albumentations as A

from config import *
from model import HeroClassifier


# ==========================================
# Transform
# ==========================================

transform = A.Compose([
    A.Resize(
        IMAGE_SIZE,
        IMAGE_SIZE
    ),

    A.Normalize(
        mean=MEAN,
        std=STD
    )
])


# ==========================================
# Load Class
# ==========================================

with open(CLASS_MAPPING, "r", encoding="utf8") as f:
    classes = json.load(f)

num_classes = len(classes)


# ==========================================
# Load Model
# ==========================================

model = HeroClassifier(num_classes)

checkpoint = torch.load(
    BEST_MODEL,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model"]
)

model.to(DEVICE)

model.eval()


# ==========================================
# Predict
# ==========================================

def predict(image_path):

    image = cv2.imread(
        image_path,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        raise FileNotFoundError(image_path)

    if len(image.shape) == 3 and image.shape[2] == 4:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2RGB
        )

    else:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

    image = transform(
        image=image
    )["image"]

    image = torch.from_numpy(
        image.transpose(2,0,1)
    ).float()

    image = image.unsqueeze(0)

    image = image.to(DEVICE)

    with torch.no_grad():

        output = model(image)

        prob = torch.softmax(
            output,
            dim=1
        )

        confidence, pred = torch.max(
            prob,
            dim=1
        )

    hero = classes[pred.item()]

    print("="*60)
    print("Prediction")
    print("="*60)
    print("Hero       :", hero)
    print("Confidence :", f"{confidence.item()*100:.2f}%")
    print("="*60)


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "image",
        help="Image Path"
    )

    args = parser.parse_args()

    predict(args.image)