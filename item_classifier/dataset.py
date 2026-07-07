from torchvision.datasets import ImageFolder
import albumentations as A
import numpy as np
import torch

from PIL import Image

from config import *


class AlbumentationTransform:

    def __init__(self, training=True):

        if training:

            self.transform = A.Compose([

                A.Resize(
                    IMAGE_SIZE,
                    IMAGE_SIZE
                ),

                A.RandomBrightnessContrast(
                    brightness_limit=BRIGHTNESS,
                    contrast_limit=CONTRAST,
                    p=0.8,
                ),

                A.RandomGamma(
                    gamma_limit=(95,105),
                    p=0.5,
                ),

                A.GaussianBlur(
                    blur_limit=(3,5),
                    p=0.2,
                ),

                A.GaussNoise(
                    std_range=(0.005,0.02),
                    p=0.2,
                ),

                A.ImageCompression(
                    quality_range=(80,100),
                    p=0.3,
                ),

                A.Normalize(
                    mean=MEAN,
                    std=STD,
                )

            ])

        else:

            self.transform = A.Compose([

                A.Resize(
                    IMAGE_SIZE,
                    IMAGE_SIZE
                ),

                A.Normalize(
                    mean=MEAN,
                    std=STD,
                )

            ])

    def __call__(self, img):

        img = np.array(img.convert("RGB"))

        img = self.transform(image=img)["image"]

        img = torch.from_numpy(
            img.transpose(2,0,1)
        ).float()

        return img


def create_dataset(training=True):

    transform = AlbumentationTransform(training)

    dataset = ImageFolder(
        root=DATASET_DIR,
        transform=transform
    )

    return dataset