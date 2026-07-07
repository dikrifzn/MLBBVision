from pathlib import Path
import json

import cv2

from crop_engine.crop_engine import CropEngine

from pipeline.postgame import PostGamePipeline

from hero_classifier.predict import predict_image as hero_predict
from item_classifier.predict import predict_image as item_predict


# PATHS

ROOT_DIR = Path(__file__).resolve().parent

SCREENSHOT = ROOT_DIR / "test" / "sample.png"

COORDINATES = ROOT_DIR / "layout_editor" / "coordinates.json"

OUTPUT_DIR = ROOT_DIR / "output" / "json"

OUTPUT_FILE = OUTPUT_DIR / "postgame.json"


# MAIN

def main():

    print("=" * 60)
    print("MLBBVision")
    print("=" * 60)

    image = cv2.imread(

        str(SCREENSHOT),

        cv2.IMREAD_UNCHANGED

    )

    if image is None:
        raise FileNotFoundError(SCREENSHOT)

    crop_engine = CropEngine(COORDINATES)

    # crop_engine.save_all(

    #     image,

    #     ROOT_DIR / "output" / "crop"

    # )
    pipeline = PostGamePipeline(

        crop_engine=crop_engine,

        hero_predict=hero_predict,

        item_predict=item_predict,

    )

    result = pipeline.run(image)

    # SAVE JSON

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True

    )

    with open(

        OUTPUT_FILE,

        "w",

        encoding="utf8"

    ) as f:

        json.dump(

            result,

            f,

            indent=4,

            ensure_ascii=False

        )

    print()

    print("=" * 60)

    print("RESULT")

    print("=" * 60)

    print(f"Total ROI   : {len(crop_engine)}")

    print(f"JSON Saved  : {OUTPUT_FILE}")

    print("=" * 60)

    print()

    print(

        json.dumps(

            result,

            indent=4,

            ensure_ascii=False

        )

    )


# ENTRY

if __name__ == "__main__":

    main()