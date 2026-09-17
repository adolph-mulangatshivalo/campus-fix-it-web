import requests
import io

def test():
    file_stream = io.BytesIO(b"Hello world! This is a test image.")
    try:
        response = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': ('test.txt', file_stream, 'text/plain')}
        )
        print("Status code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test()
