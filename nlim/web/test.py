import requests

requests.post(
    "http://localhost:5000/dataset/add",
    data={"metadata": "foo.txt test"},
    files={"fnirs_data": ("foo.txt", open("foo.txt", "rb"))},
)
