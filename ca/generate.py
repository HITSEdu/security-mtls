from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta


ca_key_path = "ca/cert/ca.key"
ca_crt_path = "ca/cert/ca.crt"


def saveFile(fileName: str, data):
    with open(fileName, "wb") as f:
        f.write(data)


def generate_ca():
    
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyCompany"),
        x509.NameAttribute(NameOID.COMMON_NAME, "My Local CA"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(
                ca=True,
                path_length=None,
            ),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    saveFile(ca_key_path, ca_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),  # для теста
    ))
    saveFile(ca_crt_path, cert.public_bytes(serialization.Encoding.PEM))

    print(f"CA generated: {ca_crt_path}, {ca_key_path}")
    return cert, ca_key


if __name__ == "__main__":
    #! Создаём CA один раз при инициализации инфраструктуры
    ca_cert, ca_key = generate_ca()

    # После этого можно использовать их в твоей существующей функции:
    # cert, key = generate_server_keys_and_cert(ca_cert, ca_key, hostname="myserver.example.com")