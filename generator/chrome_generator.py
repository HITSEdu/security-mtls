from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from pathlib import Path


def create_p12_for_chrome():
    with open("cert/client/client-cert.pem", "rb") as f:
        client_cert = x509.load_pem_x509_certificate(f.read())
    
    with open("cert/client/client-key.pem", "rb") as f:
        client_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    
    with open("cert/ca/ca-cert.pem", "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    
    p12 = pkcs12.serialize_key_and_certificates(
        name=b"Client Certificate",
        key=client_key,
        cert=client_cert,
        cas=[ca_cert],
        encryption_algorithm=serialization.BestAvailableEncryption(b"1234")
    )
    
    output_path = Path("cert/client/client-browser.p12")
    with open(output_path, "wb") as f:
        f.write(p12)
    
    print(f"PKCS#12 файл создан: {output_path}")
    print("Пароль для импорта: 1234")


if __name__ == "__main__":
    create_p12_for_chrome()
