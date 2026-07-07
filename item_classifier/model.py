import torch
import torch.nn as nn

from torchvision.models import (
    efficientnet_v2_s,
    EfficientNet_V2_S_Weights
)


class ItemClassifier(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()

        # Load pretrained EfficientNetV2-S
        self.backbone = efficientnet_v2_s(
            weights=EfficientNet_V2_S_Weights.DEFAULT
        )

        # Ambil jumlah input classifier bawaan
        in_features = self.backbone.classifier[1].in_features

        # Ganti classifier
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


if __name__ == "__main__":

    from dataset import create_dataset

    print("=" * 60)
    print("Loading Dataset")
    print("=" * 60)

    dataset = create_dataset(
        training=False
    )

    num_classes = len(dataset.classes)

    print(f"Classes : {num_classes}")

    model = ItemClassifier(num_classes)

    model.eval()

    x = torch.randn(
        2,
        3,
        224,
        224
    )

    with torch.no_grad():
        y = model(x)

    print("=" * 60)
    print("Input :", x.shape)
    print("Output:", y.shape)
    print("=" * 60)

    print("Model Test Passed")