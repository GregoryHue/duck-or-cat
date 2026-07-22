import base64
import io
import json
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from flask import Flask, render_template, request
from PIL import Image
from torchvision import transforms

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model.pt")
CLASSES_PATH = os.path.join(MODELS_DIR, "classes.json")
IMG_SIZE = 224

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(CLASSES_PATH) as f:
    idx_to_class = {int(k): v for k, v in json.load(f).items()}


class DuckOrCatCNN(nn.Module):
    """Must stay identical to the architecture in notebook/train_model.ipynb —
    this loads the state_dict that notebook trains and exports."""

    def __init__(self, num_classes=2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


model = DuckOrCatCNN(num_classes=len(idx_to_class))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def predict(image: Image.Image):
    tensor = transform(image.convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = F.softmax(model(tensor), dim=1).squeeze(0)
    ranked = sorted(
        ((idx_to_class[i], probs[i].item()) for i in range(len(idx_to_class))),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return ranked


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        uploaded = request.files.get("photo")
        if not uploaded or uploaded.filename == "":
            error = "Please choose an image to upload."
        else:
            try:
                image_bytes = uploaded.read()
                image = Image.open(io.BytesIO(image_bytes))
                ranked = predict(image)
                mime = Image.MIME.get(image.format, "image/jpeg")
                image_data_uri = f"data:{mime};base64,{base64.b64encode(image_bytes).decode()}"
                result = {
                    "label": ranked[0][0],
                    "confidence": ranked[0][1],
                    "ranked": ranked,
                    "image_data_uri": image_data_uri,
                }
            except Exception:
                error = "Could not read that file as an image."

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
