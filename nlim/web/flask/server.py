from flask import Flask, request

from nlim.web.util import save_metadata, save_uploaded_file

app = Flask(__name__)


@app.route("/dataset/add", methods=["POST"])
def create_dataset():
    if request.method == "POST":
        metadata = request.form["metadata"]
        fnirs_file = request.files["fnirs_data"]

        save_uploaded_file(data=fnirs_file.read(), filename=fnirs_file.filename)
        save_metadata(data_filename=fnirs_file.filename, metadata=metadata)

        return "Data received successfully"


if __name__ == "__main__":
    app.run(port=5000, debug=True, host="0.0.0.0")
