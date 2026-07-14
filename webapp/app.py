import json
import os

import torch
import torch.nn.functional as F
from flask import Flask, render_template, request
from PIL import Image
from torchvision import models, transforms

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model.pt")
CLASSES_PATH = os.path.join(MODELS_DIR, "classes.json")
IMG_SIZE = 224

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(CLASSES_PATH) as f:
    idx_to_class = {int(k): v for k, v in json.load(f).items()}

model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, len(idx_to_class))
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
                image = Image.open(uploaded.stream)
                ranked = predict(image)
                result = {
                    "label": ranked[0][0],
                    "confidence": ranked[0][1],
                    "ranked": ranked,
                }
            except Exception:
                error = "Could not read that file as an image."

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
