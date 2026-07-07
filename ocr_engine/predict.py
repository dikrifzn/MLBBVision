import cv2

from ocr_engine.engine import ocr_engine
from ocr_engine.config import ALLOWLIST


# OCR

def predict_text(
    image,
    mode="name"
):
    """
    Universal OCR

    Parameters
    ----------
    image : numpy.ndarray

    mode :
        gold
        level
        score
        duration
        kda
        name

    Returns
    -------
    {
        "text":"",
        "confidence":0.0
    }
    """

    if image is None:

        return {

            "text": "",

            "confidence": 0.0

        }

    # Gray → RGB

    if len(image.shape) == 2:

        image = cv2.cvtColor(

            image,

            cv2.COLOR_GRAY2RGB

        )

    elif image.shape[2] == 4:

        image = cv2.cvtColor(

            image,

            cv2.COLOR_BGRA2RGB

        )

    else:

        image = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2RGB

        )

    # OCR

    result = ocr_engine.reader.readtext(

        image,

        detail=1,

        paragraph=False,

        decoder="greedy",

        allowlist=ALLOWLIST.get(mode)

    )

    if len(result) == 0:

        return {

            "text": "",

            "confidence": 0.0

        }

    texts = []

    scores = []

    for _, text, confidence in result:

        texts.append(text)

        scores.append(confidence)

    return {

        "text": " ".join(texts).strip(),

        "confidence": max(scores)

    }