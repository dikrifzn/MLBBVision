import json
from pathlib import Path

import cv2


class CropEngine:

    def __init__(self, coordinate_file):

        coordinate_file = Path(coordinate_file)

        if not coordinate_file.exists():
            raise FileNotFoundError(coordinate_file)

        with open(
            coordinate_file,
            "r",
            encoding="utf8"
        ) as f:

            self.layout = json.load(f)

        if "variables" not in self.layout:
            raise KeyError("variables not found in coordinates.json")

        self.variables = self.layout["variables"]

    # Extract Semua ROI

    def extract(self, image):

        if image is None:
            raise ValueError("Image is None")

        crops = {}

        height, width = image.shape[:2]

        for name, roi in self.variables.items():

            x = int(roi["x"])
            y = int(roi["y"])
            w = int(roi["w"])
            h = int(roi["h"])

            x = max(0, x)
            y = max(0, y)

            x2 = min(width, x + w)
            y2 = min(height, y + h)

            crop = image[
                y:y2,
                x:x2
            ].copy()

            crops[name] = crop

        return crops

    # Extract Satu ROI

    def extract_one(self, image, name):

        if image is None:
            raise ValueError("Image is None")

        if name not in self.variables:
            raise KeyError(name)

        roi = self.variables[name]

        x = int(roi["x"])
        y = int(roi["y"])
        w = int(roi["w"])
        h = int(roi["h"])

        height, width = image.shape[:2]

        x = max(0, x)
        y = max(0, y)

        x2 = min(width, x + w)
        y2 = min(height, y + h)

        return image[
            y:y2,
            x:x2
        ].copy()

    # Save Semua Crop

    def save_all(
        self,
        image,
        output_dir
    ):

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        crops = self.extract(image)

        for name, crop in crops.items():

            cv2.imwrite(
                str(output_dir / f"{name}.png"),
                crop
            )

        return len(crops)

    # Get ROI

    def get_roi(self, name):

        if name not in self.variables:
            raise KeyError(name)

        return self.variables[name]

    # Get Semua Nama ROI

    def get_names(self):

        return list(self.variables.keys())

    # Total ROI

    def __len__(self):

        return len(self.variables)

    # Print Info

    def info(self):

        print("=" * 60)
        print("Crop Engine")
        print("=" * 60)

        print("Total ROI :", len(self))

        print("=" * 60)

        for name in self.variables.keys():
            print(name)

        print("=" * 60)

# TES

if __name__ == "__main__":

    engine = CropEngine(
        "../layout_editor/coordinates.json"
    )

    engine.info()

    image = cv2.imread(
        "../test/sample.png"
    )

    if image is None:
        raise FileNotFoundError(
            "../test/sample.png"
        )

    crops = engine.extract(image)

    print()

    print("=" * 60)
    print("Testing Crop")
    print("=" * 60)

    print("Total Crop :", len(crops))

    print()

    for name, crop in list(crops.items())[:10]:

        print(
            f"{name:<30}",
            crop.shape
        )

    print()

    total = engine.save_all(
        image,
        "../output"
    )

    print("=" * 60)
    print(f"Saved {total} images to output/")
    print("=" * 60)