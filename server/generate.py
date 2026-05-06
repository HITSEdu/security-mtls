from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta

server_key_path = "server/cert/server.key"
server_crt_path = "server/cert/server.crt"
ca_crt_path = "ca/cert/ca.crt"
ca_key_path = "ca/cert/ca.key"

def saveFile(fileName: str, data):
    with open(fileName, "wb") as f:
        f.write(data)


def generate_server_keys_and_cert(ca_cert, ca_key, hostname="localhost"):
    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyCompany"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName("www." + hostname),
            ]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    
    saveFile(server_crt_path, cert.public_bytes(serialization.Encoding.PEM))
    saveFile(server_key_path, server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),  # для теста
            ))

    print(f"Server keys and cert generated: {server_crt_path}, {server_key_path}")
    return cert, server_key


ca_cert = x509.load_pem_x509_certificate(open(ca_crt_path, "rb").read())
ca_key = serialization.load_pem_private_key(open(ca_key_path, "rb").read(), password=None)

cert, key = generate_server_keys_and_cert(ca_cert, ca_key, hostname="myserver.example.com")
