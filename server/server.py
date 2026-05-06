from flask import Flask, render_template, request
import werkzeug.serving
import ssl
import OpenSSL


class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
    def make_environ(self):
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, x509_binary)
        environ['peercert'] = x509
        return environ


app = Flask(__name__)

app_key = 'certificates/server/server.key'
app_key_password = None
app_cert = 'certificates/server/server.pem'

ca_cert = 'certificates/ca/ca.pem'

ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert)

ssl_context.load_cert_chain(certfile=app_cert, keyfile=app_key, password=app_key_password)
ssl_context.verify_mode = ssl.CERT_REQUIRED

@app.route('/')
def hello_world():
    return { "hello": "world!" }


if __name__ == "__main__":
    app.run(ssl_context=ssl_context, request_handler=PeerCertWSGIRequestHandler)