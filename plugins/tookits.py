import requests
def fileToUrl(file_path):
    url = "https://file.io"
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files)
    data = response.json()
    return data.get("link")