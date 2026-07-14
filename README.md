# Duck or Cat

A binary image classifier that tells ducks apart from cats, built from three independent components sharing `data/` and `models/` at the repo root:

```
duck-or-cat/
├── scraper/    # Scrapy project — fetches labeled images from the Pexels API
├── notebook/   # Jupyter notebook — trains & evaluates a ResNet18 classifier
├── webapp/     # Flask app — serves the trained model behind a web UI
├── data/raw/   # <label>/*.jpg images produced by the scraper
└── models/     # model.pt + classes.json produced by the notebook
```

## 1. Scraper — build the dataset

Get a free API key at https://www.pexels.com/api/, then:

```bash
cd scraper
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then paste your PEXELS_API_KEY into .env
scrapy crawl pexels -a labels=cat,duck -a images_per_label=500
```

Images land in `data/raw/cat/` and `data/raw/duck/`.

## 2. Notebook — train the model

```bash
cd notebook
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook train_model.ipynb
```

Run all cells. This trains a transfer-learned ResNet18 on `data/raw/`, evaluates it
on a held-out test split, and writes `models/model.pt` + `models/classes.json`.

## 3. Webapp — serve the model

```bash
cd webapp
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit http://127.0.0.1:5000, upload a photo, and get a duck/cat prediction with confidence.

## Notes

- Each component has its own `requirements.txt` and is meant to be run in its own
  virtual environment — they only share the `data/` and `models/` folders on disk.
- Re-running the notebook overwrites `models/model.pt`; re-run the webapp (or just
  refresh, since it loads the model once at startup) to pick up a new version.
