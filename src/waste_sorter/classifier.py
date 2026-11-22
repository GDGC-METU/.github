"""Model loading and prediction helpers."""
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms

# torchvision.datasets.ImageFolder assigns indices from alphabetically sorted
# folder names. Keep this tuple in that same order so a saved model's outputs
# always map to the intended material.
LABELS = ("metal", "paper", "plastic")
IMAGE_SIZE = 224


def build_model(num_classes: int = 3, pretrained: bool = False):
    weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = models.mobilenet_v3_small(weights=weights)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, num_classes)
    return model


def image_transform():
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ])


class WasteClassifier:
    def __init__(self, model_path: str | Path, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        saved = torch.load(model_path, map_location=self.device, weights_only=True)
        self.labels = tuple(saved["labels"])
        if self.labels != LABELS:
            raise ValueError(f"Expected labels {LABELS}, got {self.labels}")
        self.model = build_model(len(self.labels))
        self.model.load_state_dict(saved["state_dict"])
        self.model.to(self.device).eval()
        self.transform = image_transform()

    @torch.inference_mode()
    def predict(self, image: Image.Image) -> tuple[str, float]:
        tensor = self.transform(image.convert("RGB")).unsqueeze(0).to(self.device)
        probabilities = self.model(tensor).softmax(dim=1)[0]
        index = int(probabilities.argmax().item())
        return self.labels[index], float(probabilities[index].item())


def classify_with_threshold(classifier: WasteClassifier, image: Image.Image, threshold: float):
    label, confidence = classifier.predict(image)
    return (label if confidence >= threshold else "unknown", confidence)
