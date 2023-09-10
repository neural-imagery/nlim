from pathlib import Path

UPLOADS_DIR = Path.home() / "datasets"
METADATA_PATH = UPLOADS_DIR / "metadata.csv"

UPLOADS_DIR = str(UPLOADS_DIR)
METADATA_PATH = str(METADATA_PATH)
