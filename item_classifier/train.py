import time
import json

import torch
import torch.nn as nn

from tqdm import tqdm

from config import *
from dataloader import create_dataloader
from model import HeroClassifier
from utils import save_checkpoint
from utils import save_class_mapping


def train():

    print("=" * 60)
    print("Loading Dataset")
    print("=" * 60)

    dataset, train_loader = create_dataloader(
        training=True
    )

    save_class_mapping(
        dataset.classes,
        CLASS_MAPPING
    )

    num_classes = len(dataset.classes)

    print(f"Classes      : {num_classes}")
    print(f"Images       : {len(dataset)}")
    print(f"Device       : {DEVICE}")

    print("=" * 60)
    print("Building Model")
    print("=" * 60)

    model = HeroClassifier(num_classes)

    model = model.to(DEVICE)

    total_params = sum(
        p.numel()
        for p in model.parameters()
    )

    print(f"Parameters : {total_params:,}")

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS
    )

    best_acc = 0.0

    print("=" * 60)
    print("Start Training")
    print("=" * 60)

    for epoch in range(EPOCHS):

        epoch_start = time.time()

        model.train()

        running_loss = 0.0

        running_correct = 0

        running_total = 0

        progress = tqdm(
            train_loader,
            desc=f"Epoch {epoch+1}/{EPOCHS}",
            ncols=120
        )
        for images, labels in progress:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(outputs, labels)

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

            _, predicted = torch.max(outputs, dim=1)

            running_total += labels.size(0)

            running_correct += (
                predicted == labels
            ).sum().item()

            avg_loss = running_loss / max(1, progress.n + 1)

            avg_acc = (
                100.0
                * running_correct
                / running_total
            )

            progress.set_postfix(
                loss=f"{avg_loss:.4f}",
                acc=f"{avg_acc:.2f}%"
            )

        scheduler.step()

        epoch_loss = running_loss / len(train_loader)

        epoch_acc = (
            100.0
            * running_correct
            / running_total
        )

        epoch_time = time.time() - epoch_start

        print()

        print("=" * 60)
        print(f"Epoch        : {epoch+1}/{EPOCHS}")
        print(f"Loss         : {epoch_loss:.4f}")
        print(f"Accuracy     : {epoch_acc:.2f}%")
        print(f"LearningRate : {optimizer.param_groups[0]['lr']:.7f}")
        print(f"Time         : {epoch_time:.1f} sec")
        print("=" * 60)
        if epoch_acc > best_acc:

            best_acc = epoch_acc

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=epoch + 1,
                filename=BEST_MODEL,
            )

            print(f"✅ Best Model Saved ({best_acc:.2f}%)")

        save_checkpoint(
            model=model,
            optimizer=optimizer,
            epoch=epoch + 1,
            filename=LAST_MODEL,
        )

        print("💾 Last Model Saved")
        print()

    print("=" * 60)
    print("Training Finished")
    print("=" * 60)

    print(f"Best Accuracy : {best_acc:.2f}%")
    print(f"Best Model    : {BEST_MODEL}")
    print(f"Last Model    : {LAST_MODEL}")


if __name__ == "__main__":

    start = time.time()

    train()

    end = time.time()

    print("=" * 60)
    print(f"Total Training Time : {(end-start)/60:.2f} Minutes")
    print("=" * 60)