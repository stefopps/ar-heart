"""AR Heart local dev server with self-signed SSL for camera permissions."""
import http.server, ssl, socket, os

PORT = 8443

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = http.server.SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map['.js'] = 'application/javascript'
    extensions_map['.dat'] = 'application/octet-stream'
    extensions_map['.patt'] = 'application/octet-stream'
    extensions_map['.wasm'] = 'application/wasm'

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {args[0]}")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Generate self-signed cert if missing
if not os.path.exists("cert.pem"):
    from subprocess import run
    run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", "key.pem",
         "-out", "cert.pem", "-days", "365", "-nodes",
         "-subj", "/CN=localhost"], check=True, shell=True)

with http.server.HTTPServer(("0.0.0.0", PORT), Handler) as httpd:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("cert.pem", "key.pem")
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"\n  AR Heart server running:")
    print(f"  Local:   https://localhost:{PORT}")
    print(f"  Network: https://{local_ip}:{PORT}")
    print(f"  Flyer:   https://localhost:{PORT}/flyer.html")
    print(f"\n  Open flyer.html on a second screen for QR code + marker side by side.\n")
    httpd.serve_forever()
