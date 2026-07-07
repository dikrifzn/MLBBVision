import cv2

from crop_engine import CropEngine


engine = CropEngine("../layout_editor/coordinates.json")

image = cv2.imread("../test/sample.png")

crops = engine.extract(image)

print("=" * 60)
print("Total Crop :", len(crops))
print("=" * 60)

for name, crop in crops.items():

    print(
        f"{name:<30}",
        crop.shape
    )