from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from pathlib import Path
import ipaddress

CA_DIR = Path("cert/ca")
SERVER_DIR = Path("cert/server")
CLIENT_DIR = Path("cert/client")

for dir_path in [CA_DIR, SERVER_DIR, CLIENT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def saveFile(fileName: Path, data: bytes):
    with open(fileName, "wb") as f:
        f.write(data)


class MTLSGenerator:
    def __init__(self):
        self.ca_cert = None
        self.ca_key = None
        
        
    def generate_ca(self):    
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "K"),
            x509.NameAttribute(NameOID.COMMON_NAME, "K"),
        ])
        
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=0),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=False,
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
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("*.localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1")),
                ]),
                critical=False,
            )
            .sign(ca_key, hashes.SHA256())
        )
        
        saveFile(CA_DIR / "ca-key.pem", ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        
        saveFile(CA_DIR / "ca-cert.pem", ca_cert.public_bytes(
            serialization.Encoding.PEM
        ))
        
        self.ca_cert = ca_cert
        self.ca_key = ca_key
        
        print("CA сертификат и ключ созданы")
        return ca_cert, ca_key
    
    
    def generate_server_cert(self, server_domain="localhost"):        
        if not self.ca_cert or not self.ca_key:
            raise ValueError("Сначала нужно сгенерировать CA!")
        
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Hits"),
            x509.NameAttribute(NameOID.COMMON_NAME, server_domain),
        ])
        
        server_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
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
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(server_domain),
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .sign(self.ca_key, hashes.SHA256())
        )
        
        saveFile(SERVER_DIR / "server-key.pem", server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        
        saveFile(SERVER_DIR / "server-cert.pem", server_cert.public_bytes(
            serialization.Encoding.PEM
        ))
        
        print("Серверный сертификат создан и подписан CA")
        return server_cert, server_key
    
    
    def generate_client_cert(self, client_name="client"):
        if not self.ca_cert or not self.ca_key:
            raise ValueError("Сначала нужно сгенерировать CA!")
        
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tomsk"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "HitsOff"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Klient"),
            x509.NameAttribute(NameOID.COMMON_NAME, client_name),
        ])
        
        client_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_cert.subject)
            .public_key(client_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
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
                    x509.DNSName(client_name),
                    x509.RFC822Name(f"{client_name}@example.com")
                ]),
                critical=False,
            )
            .sign(self.ca_key, hashes.SHA256())
        )
        
        saveFile(CLIENT_DIR / f"{client_name}-key.pem", client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        
        saveFile(CLIENT_DIR / f"{client_name}-cert.pem", client_cert.public_bytes(
            serialization.Encoding.PEM
        ))
        
        print(f"Клиентский сертификат для {client_name} создан и подписан CA")
        return client_cert, client_key


if __name__ == "__main__":
    generator = MTLSGenerator()
    ca_cert, ca_key = generator.generate_ca()
    server_cert, server_key = generator.generate_server_cert("localhost")
    client_cert, client_key = generator.generate_client_cert("client")
