import os

import pandas as pd
import streamlit as st

from nlim.web.constants import METADATA_PATH, UPLOADS_DIR
from nlim.web.util import save_metadata, save_uploaded_file

# Directory to save uploaded files


def main():
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Sidebar - File Upload
    uploaded_file = st.file_uploader("Upload .nirs File")

    if uploaded_file is not None:
        save_uploaded_file(uploaded_file.getbuffer(), uploaded_file.name)
        st.success("File uploaded successfully!")

    # Sidebar - Metadata
    metadata = st.text_area("Enter Metadata")

    if st.button("Save Metadata"):
        save_metadata(uploaded_file.name, metadata=metadata)
        st.success("Metadata saved successfully!")

    # Main content - Display Uploaded Files and Metadata
    st.header("Uploaded NIRS Files")

    uploaded_files = os.listdir(UPLOADS_DIR)
    with st.expander(label="Filenames"):
        for file in uploaded_files:
            st.write(file)

    st.header("Cross-Dataset Metadata")

    if not os.path.exists(METADATA_PATH):
        st.error("No datasets present!")
    else:
        metadata_df = pd.read_csv(METADATA_PATH)
        st.write(metadata_df)

        st.header("Download")
        selected_file = st.selectbox(
            "Select a dataset to download:", metadata_df["File"].unique()
        )
        file_path = os.path.join(UPLOADS_DIR, selected_file)
        st.download_button(
            label="Download Selected Dataset",
            data=open(file_path, "rb"),
            key=selected_file,
            file_name=selected_file,
        )

        st.header("Delete Dataset")
        selected_file = st.selectbox(
            "Select a dataset to delete:", metadata_df["File"].unique()
        )
        file_path = os.path.join(UPLOADS_DIR, selected_file)
        if st.checkbox("Check to enable delete button"):
            if st.button("Delete dataset"):
                os.remove(file_path)
                metadata_df = pd.read_csv(METADATA_PATH)
                metadata_df = metadata_df[metadata_df["File"] != selected_file]
                if len(metadata_df) == 0:
                    os.remove(METADATA_PATH)
                else:
                    metadata_df.to_csv(
                        METADATA_PATH,
                        mode="w",
                        header=not os.path.exists(METADATA_PATH),
                        index=False,
                    )
                st.success("Deleted and updated metadata")


main()
