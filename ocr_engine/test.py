from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse
from pathlib import Path

import cv2

from ocr_engine.preprocess import (
    preprocess_gold,
    preprocess_level,
    preprocess_score,
    preprocess_duration,
    preprocess_kda,
    preprocess_name,
)

from ocr_engine.predict import predict_text

from ocr_engine.parser import (
    parse_gold,
    parse_level,
    parse_score,
    parse_duration,
    parse_kda,
    parse_name,
)

from ocr_engine.config import (
    DEBUG,
    DEBUG_DIR
)


# PREPROCESS SELECTOR

PREPROCESS = {

    "gold": preprocess_gold,

    "level": preprocess_level,

    "score": preprocess_score,

    "duration": preprocess_duration,

    "kda": preprocess_kda,

    "name": preprocess_name,

}


# PARSER SELECTOR

PARSER = {

    "gold": parse_gold,

    "level": parse_level,

    "score": parse_score,

    "duration": parse_duration,

    "kda": parse_kda,

    "name": parse_name,

}

# TEST

def run(image_path, mode):

    image = cv2.imread(

        str(image_path),

        cv2.IMREAD_UNCHANGED

    )

    if image is None:

        raise FileNotFoundError(image_path)

    image = PREPROCESS[mode](image)

    if DEBUG:

        save_path = DEBUG_DIR / f"{mode}.png"

        cv2.imwrite(

            str(save_path),

            image

        )

    result = predict_text(

        image,

        mode

    )

    value = PARSER[mode](

        result["text"]

    )

    print()

    print("=" * 60)

    print("MODE        :", mode)

    print("RAW TEXT    :", result["text"])

    print("PARSED      :", value)

    print("CONFIDENCE  :", f"{result['confidence']*100:.2f}%")

    print("=" * 60)

    cv2.imshow(

        "Preprocess",

        image

    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()


# MAIN

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(

        "image",

        help="Image Path"

    )

    parser.add_argument(

        "--mode",

        default="gold",

        choices=[

            "gold",

            "level",

            "score",

            "duration",

            "kda",

            "name"

        ]

    )

    args = parser.parse_args()

    run(

        args.image,

        args.mode

    )