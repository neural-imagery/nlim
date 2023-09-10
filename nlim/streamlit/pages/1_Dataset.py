import os

import pandas as pd
import streamlit as st

# Directory to save uploaded files
UPLOADS_DIR = "uploads"


def save_uploaded_file(uploaded_file):
    # Save the uploaded file to the uploads directory
    with open(os.path.join(UPLOADS_DIR, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def main():
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Sidebar - File Upload
    uploaded_file = st.file_uploader("Upload .nirs File")

    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)
        st.success("File uploaded successfully!")

    # Sidebar - Metadata
    metadata = st.text_area("Enter Metadata")

    if st.button("Save Metadata"):
        metadata_df = pd.DataFrame(
            {"File": [uploaded_file.name], "Metadata": [metadata]}
        )
        metadata_df.to_csv(
            "metadata.csv",
            mode="a",
            header=not os.path.exists("metadata.csv"),
            index=False,
        )
        st.success("Metadata saved successfully!")

    # Main content - Display Uploaded Files and Metadata
    st.header("Uploaded NIRS Files")

    uploaded_files = os.listdir(UPLOADS_DIR)
    with st.expander(label="Filenames"):
        for file in uploaded_files:
            st.write(file)

    st.header("Cross-Dataset Metadata")

    if not os.path.exists("metadata.csv"):
        st.error("No datasets present!")
    else:
        metadata_df = pd.read_csv("metadata.csv")
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
                metadata_df = pd.read_csv("metadata.csv")
                metadata_df = metadata_df[metadata_df["File"] != selected_file]
                if len(metadata_df) == 0:
                    os.remove("metadata.csv")
                else:
                    metadata_df.to_csv(
                        "metadata.csv",
                        mode="w",
                        header=not os.path.exists("metadata.csv"),
                        index=False,
                    )
                st.success("Deleted and updated metadata")


main()
