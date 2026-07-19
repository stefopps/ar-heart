"""HTTPS wrapper around serve.ARRequestHandler (camera on iOS needs HTTPS)."""
import os
import ssl
import sys
import http.server

from serve import ARRequestHandler, ROOT, SETTINGS_PATH, ensure_defaults

cert_file = os.path.join(ROOT, "cert.pem")
key_file = os.path.join(ROOT, "key.pem")

if not os.path.exists(cert_file) or not os.path.exists(key_file):
    print("[cert] Generating self-signed SSL certificate (valid 365 days)...")
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "192.168.1.157")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("192.168.1.157")]), critical=False)
        .sign(key, hashes.SHA256(), default_backend())
    )
    with open(key_file, "wb") as f:
        f.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("[cert] Generated cert.pem + key.pem")

ensure_defaults()
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(cert_file, key_file)


class ThreadingHTTPSServer(http.server.ThreadingHTTPServer):
    """TLS handshake happens per-connection in the worker thread, not on the
    main accept loop. A phone stalling on the cert warning (or a half-open
    connection) can no longer freeze the whole server."""
    daemon_threads = True
    allow_reuse_address = True

    def get_request(self):
        # Accept the raw TCP socket and wrap it WITHOUT handshaking here
        sock, addr = self.socket.accept()
        sock.settimeout(30)  # so a dead client's handshake/read can't hang forever
        ssock = ctx.wrap_socket(sock, server_side=True, do_handshake_on_connect=False)
        return ssock, addr

    def finish_request(self, request, client_address):
        # Runs in the per-request daemon thread — do the handshake here
        try:
            request.do_handshake()
        except (ssl.SSLError, OSError):
            return  # bad/stalled handshake: drop just this connection
        super().finish_request(request, client_address)


httpd = ThreadingHTTPSServer(("0.0.0.0", port), ARRequestHandler)

print(f"[HTTPS] https://192.168.1.157:{port}/index.html")
print(f"[HTTPS] settings -> {SETTINGS_PATH}")
print("[HTTPS] On phone: accept cert warning, then allow camera")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n[HTTPS] Server stopped.")
