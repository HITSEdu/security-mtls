import requests
from pathlib import Path
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_CERT = Path("cert/client/client-cert.pem")
CLIENT_KEY = Path("cert/client/client-key.pem")
CA_CERT = Path("cert/ca/ca-cert.pem")


def test_connection():
    try:
        response = requests.get(
            "https://localhost:8443/hello/World",
            verify=str(CA_CERT),
            cert=(str(CLIENT_CERT), str(CLIENT_KEY)),
            timeout=10
        )
        print(f"Успех! Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        return response
    except Exception as e:
        print(f"SSL ошибка: {e}")


if __name__ == "__main__":
    test_connection()