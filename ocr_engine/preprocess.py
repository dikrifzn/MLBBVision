import cv2
import numpy as np

from ocr_engine.config import (
    CLAHE_CLIP,
    CLAHE_GRID,
    UPSCALE_GOLD,
    UPSCALE_LEVEL,
    UPSCALE_SCORE,
    UPSCALE_KDA,
    UPSCALE_NAME,
    UPSCALE_DURATION,
)

# BASIC

def gray(image):

    if image is None:
        return None

    if len(image.shape) == 2:
        return image

    if image.shape[2] == 4:

        return cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2GRAY
        )

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


def resize(image, scale):

    return cv2.resize(

        image,

        None,

        fx=scale,

        fy=scale,

        interpolation=cv2.INTER_CUBIC

    )


def clahe(image):

    c = cv2.createCLAHE(

        clipLimit=CLAHE_CLIP,

        tileGridSize=CLAHE_GRID

    )

    return c.apply(image)


def otsu(image):

    _, image = cv2.threshold(

        image,

        0,

        255,

        cv2.THRESH_BINARY + cv2.THRESH_OTSU

    )

    return image


def adaptive(image):

    return cv2.adaptiveThreshold(

        image,

        255,

        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

        cv2.THRESH_BINARY,

        31,

        11

    )


def denoise(image):

    return cv2.fastNlMeansDenoising(

        image,

        None,

        10,

        7,

        21

    )


# GOLD

def preprocess_gold(image):

    image = gray(image)

    image = denoise(image)

    image = clahe(image)

    image = resize(
        image,
        UPSCALE_GOLD
    )

    image = otsu(image)

    return image


# LEVEL

def preprocess_level(image):

    image = gray(image)

    image = resize(

        image,

        UPSCALE_LEVEL

    )

    image = otsu(image)

    return image


# SCORE

def preprocess_score(image):

    image = gray(image)

    image = resize(

        image,

        UPSCALE_SCORE

    )

    image = otsu(image)

    return image


# KDA

def preprocess_kda(image):

    image = gray(image)

    image = clahe(image)

    image = resize(

        image,

        UPSCALE_KDA

    )

    # image = adaptive(image)

    return image


# PLAYER NAME

def preprocess_name(image):

    image = gray(image)

    image = clahe(image)

    image = resize(

        image,

        UPSCALE_NAME

    )

    return image


# GAME DURATION

def preprocess_duration(image):

    image = gray(image)

    image = resize(

        image,

        UPSCALE_DURATION

    )

    image = otsu(image)

    return image