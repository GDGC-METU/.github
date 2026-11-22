"""Fine-tune MobileNetV3-Small using images sorted into class folders."""
import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets

from .classifier import LABELS, build_model, image_transform


def train(data_dir: Path, output: Path, epochs: int = 8, batch_size: int = 16):
    dataset = datasets.ImageFolder(data_dir, transform=image_transform())
    if tuple(dataset.classes) != LABELS:
        raise ValueError(
            f"Expected class folders {LABELS}; found {dataset.classes}. "
            "Use exactly metal, paper, and plastic."
        )
    if len(dataset) < 6:
        raise ValueError("Add more labeled images before training (at least 2 per class).")
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    model = build_model(pretrained=True)
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for images, targets in loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(images), targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs} - loss {total_loss / len(loader):.4f}")
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"labels": list(LABELS), "state_dict": model.cpu().state_dict()}, output)
    print(f"Saved model to {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/train"))
    parser.add_argument("--output", type=Path, default=Path("models/waste_sorter.pth"))
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    train(args.data, args.output, args.epochs, args.batch_size)


if __name__ == "__main__":
    main()
