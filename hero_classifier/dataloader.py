from torch.utils.data import DataLoader

from dataset import create_dataset
from config import *


def create_dataloader(training=True):

    dataset = create_dataset(training)

    loader = DataLoader(

        dataset,

        batch_size=BATCH_SIZE,

        shuffle=training,

        num_workers=NUM_WORKERS,

        pin_memory=PIN_MEMORY,

        persistent_workers=NUM_WORKERS > 0,

    )

    return dataset, loader


if __name__ == "__main__":

    dataset, loader = create_dataloader()

    images, labels = next(iter(loader))

    print("="*60)
    print("Dataset Test")
    print("="*60)

    print(images.shape)

    print(labels.shape)

    print()

    print("Classes :", len(dataset.classes))

    print(dataset.classes[:10])