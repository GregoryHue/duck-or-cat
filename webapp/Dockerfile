# Build context is the repo root (see .github/workflows/publish-webapp.yml)
# so this image only ever contains webapp/ and models/ — no scraper or notebook.
FROM python:3.12-slim

WORKDIR /app

COPY webapp/requirements.txt webapp/requirements.txt

# torch/torchvision default to CUDA wheels (multiple GB of nvidia-* packages)
# on Linux; this container has no GPU, so pull the CPU-only build first —
# the later requirements.txt install then sees them already satisfied.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision \
    && pip install --no-cache-dir -r webapp/requirements.txt

COPY webapp/ webapp/
COPY models/ models/

WORKDIR /app/webapp

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
