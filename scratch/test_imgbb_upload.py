import requests
import io

def test():
    # Use a dummy API key or no key to see what happens
    api_key = "dummy"
    
    filename = "test.txt"
    file_stream = io.BytesIO(b"Hello world!")
    content_type = "text/plain"
    
    try:
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={'key': api_key},
            files={'image': (filename, file_stream, content_type)}
        )
        print("Status code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test()
