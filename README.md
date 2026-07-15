# Duck or Cat

A binary image classifier that tells ducks apart from cats, built from three independent components

- 1. A web-scrapping component to build a dataset
- 2. A notebook component to build, train and test a model on the dataset
- 3. A webapp to serve the model and classify pictures in real condition 

```
duck-or-cat/
├── scraper/    # Scrapy project — fetches labeled images from the Pexels API
├── notebook/   # Jupyter notebook — trains & evaluates a ResNet18 classifier
├── webapp/     # Flask app + Dockerfile — serves the trained model
├── data/raw/   # <label>/*.jpg images produced by the scraper
├── models/     # model.pt (Git LFS) + classes.json produced by the notebook
└── .github/    # workflow that builds the webapp image and publishes it to GHCR
```

## Trying out the project



You can test this project by checking out the deployement on Render (https://duck-or-cat-latest.onrender.com/) or running a Docker command:

```
docker pull ghcr.io/gregoryhue/duck-or-cat:latest
docker run -d -p 5000:5000 ghcr.io/gregoryhue/duck-or-cat:latest
```

## Building the project

### 1. Scraper — build the dataset

Get a free API key at https://www.pexels.com/api/, then:

```bash
cd scraper
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then paste your PEXELS_API_KEY into .env
scrapy crawl pexels -a labels=cat,duck -a images_per_label=500
```

Images land in `data/raw/cat/` and `data/raw/duck/`.

### 2. Notebook — train the model

```bash
cd notebook
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook train_model.ipynb
```

Run all cells. This trains a transfer-learned ResNet18 on `data/raw/`, evaluates it
on a held-out test split, and writes `models/model.pt` + `models/classes.json`.

### 3. Webapp — serve the model

```bash
cd webapp
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Or with Docker, from the repo root (build context needs to see both `webapp/` and `models/`):

```bash
docker build -f webapp/Dockerfile -t duck-or-cat-webapp .
docker run -d -p 5000:5000 --name duck-or-cat-webapp duck-or-cat-webapp
```

Either way, visit http://127.0.0.1:5000, upload a photo, and get a duck/cat
prediction with confidence, alongside a preview of the photo you uploaded.