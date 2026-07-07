import json
import argparse

import cv2
import torch
import albumentations as A

from .config import *
from .model import ItemClassifier

# Transform

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

# Load Class Mapping

with open(CLASS_MAPPING, "r", encoding="utf8") as f:
    classes = json.load(f)

num_classes = len(classes)

# Load Model

model = ItemClassifier(num_classes)

checkpoint = torch.load(
    BEST_MODEL,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model"]
)

model.to(DEVICE)
model.eval()

# Predict OpenCV Image

def predict_image(image):

    if image is None:
        raise ValueError("Image is None")

    # BGRA
    if len(image.shape) == 3 and image.shape[2] == 4:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2RGB
        )

    # BGR
    else:

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

    image = transform(
        image=image
    )["image"]

    image = torch.from_numpy(
        image.transpose(2, 0, 1)
    ).float()

    image = image.unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        output = model(image)

        probability = torch.softmax(
            output,
            dim=1
        )

        confidence, pred = torch.max(
            probability,
            dim=1
        )

    item = classes[pred.item()]

    return {
        "item": item,
        "confidence": float(confidence.item())
    }

# Predict File

def predict(image_path):

    image = cv2.imread(
        image_path,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        raise FileNotFoundError(image_path)

    result = predict_image(image)

    print("=" * 60)
    print("Prediction")
    print("=" * 60)
    print("Item       :", result["item"])
    print(
        "Confidence :",
        f"{result['confidence']*100:.2f}%"
    )
    print("=" * 60)

    return result

# Main

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "image",
        help="Image Path"
    )

    args = parser.parse_args()

    predict(args.image)