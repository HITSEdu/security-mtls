from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta


client_key_path = "client/cert/client.key"
client_crt_path = "client/cert/client.crt"


def saveFile(fileName: str, data):
    with open(fileName, "wb") as f:
        f.write(data)


def generate_client_signature_cert(ca_cert=None, ca_key=None, use_ca=True):
    client_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyCompany"),
        x509.NameAttribute(NameOID.COMMON_NAME, "client"),
    ])

    if use_ca and ca_cert and ca_key:
        issuer = ca_cert.subject
        serial = x509.random_serial_number()
    else:
        issuer = subject
        serial = x509.random_serial_number()
        ca_key = client_key

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(client_key.public_key())
        .serial_number(serial)
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("client"),
                x509.RFC822Name("client@example.com")
            ]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    saveFile(client_crt_path, cert.public_bytes(serialization.Encoding.PEM))
    saveFile(client_key_path, client_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ))

    print(f"Client signature cert saved: {client_key_path}, {client_crt_path}")
    return cert, client_key


cert, key = generate_client_signature_cert(use_ca=False)
