import json
import torch


def save_class_mapping(classes, filename):
    """
    Simpan daftar nama class.
    """

    with open(filename, "w", encoding="utf8") as f:
        json.dump(
            classes,
            f,
            indent=4,
            ensure_ascii=False
        )


def load_class_mapping(filename):
    """
    Load daftar class.
    """

    with open(filename, "r", encoding="utf8") as f:
        return json.load(f)


def save_checkpoint(
    model,
    optimizer,
    epoch,
    filename,
    accuracy=None,
    loss=None
):
    """
    Simpan checkpoint model.
    """

    checkpoint = {
        "epoch": epoch,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "accuracy": accuracy,
        "loss": loss,
    }

    torch.save(checkpoint, filename)


def load_checkpoint(
    filename,
    model,
    optimizer=None,
    device="cpu"
):
    """
    Load checkpoint model.
    """

    checkpoint = torch.load(
        filename,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["model"]
    )

    if optimizer is not None:
        optimizer.load_state_dict(
            checkpoint["optimizer"]
        )

    return checkpoint