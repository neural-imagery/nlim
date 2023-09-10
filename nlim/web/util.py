import os
from pathlib import Path

import pandas as pd
import requests

from nlim.web.constants import METADATA_PATH, UPLOADS_DIR


def save_uploaded_file(data: bytes, filename: str):
    # Save the uploaded file to the uploads directory
    with open(os.path.join(UPLOADS_DIR, filename), "wb") as f:
        f.write(data)


def save_metadata(data_filename: str, metadata: str):
    metadata_df = pd.DataFrame({"File": [data_filename], "Metadata": [metadata]})
    metadata_df.to_csv(
        METADATA_PATH,
        mode="a",
        header=not os.path.exists(METADATA_PATH),
        index=False,
    )


def post_fnirs_data_metadata(file_path: str, metadata: str):
    file_as_path: Path = Path(file_path)
    filename: str = file_as_path.name
    requests.post(
        "http://35.186.191.80/dataset/add",
        data={"metadata": metadata},
        files={"fnirs_data": (filename, file_as_path.read_bytes())},
    )
