"""
MeWorld AR local server — static files + settings.json write + model upload.

HTTP:  python serve.py
HTTPS: python server_https.py  (imports this handler)
"""
from __future__ import annotations

import http.server
import json
import os
import re
import ssl
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT / "settings.json"
UPLOAD_DIR = ROOT / "models" / "uploads"


def ensure_defaults():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(
            json.dumps(
                {
                    "ambient": "1.20",
                    "key": "1.80",
                    "fill": "0.60",
                    "orbit": "40",
                    "height": "5.0",
                    "upAxis": "+Y",
                    "orientYaw": "0",
                    "orientPitch": "0",
                    "orientRoll": "0",
                    "modelUrl": "models/retopology.glb",
                    "modelLabel": "retopology.glb",
                    "webcamEnabled": True,
                    "version": 23,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def safe_filename(name: str) -> str:
    name = os.path.basename(unquote(name or "model.glb"))
    name = re.sub(r"[^\w.\-]+", "_", name)
    if not name.lower().endswith((".glb", ".gltf")):
        name += ".glb"
    return name or "model.glb"


class ARRequestHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **getattr(http.server.SimpleHTTPRequestHandler, "extensions_map", {}),
        ".js": "application/javascript",
        ".dat": "application/octet-stream",
        ".patt": "application/octet-stream",
        ".wasm": "application/wasm",
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".json": "application/json",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, code: int, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n > 0 else b""

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/settings":
            ensure_defaults()
            try:
                data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            except Exception as e:
                return self._send_json(500, {"ok": False, "error": str(e)})
            return self._send_json(200, data)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/api/settings", "/settings.json"):
            raw = self._read_body()
            try:
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("settings must be a JSON object")
            except Exception as e:
                return self._send_json(400, {"ok": False, "error": f"invalid json: {e}"})
            ensure_defaults()
            SETTINGS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(f"[settings] wrote {SETTINGS_PATH}")
            return self._send_json(200, {"ok": True, "path": "settings.json"})

        if parsed.path == "/api/upload-model":
            raw = self._read_body()
            if len(raw) < 4:
                return self._send_json(400, {"ok": False, "error": "empty body"})
            magic = raw[:4]
            name = safe_filename(self.headers.get("X-Filename") or "model.glb")
            if name.lower().endswith(".glb") and magic != b"glTF":
                return self._send_json(
                    400,
                    {"ok": False, "error": f'Not a glTF binary (header {magic!r})'},
                )
            ensure_defaults()
            dest = UPLOAD_DIR / name
            # avoid overwrite collisions
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                i = 2
                while True:
                    cand = UPLOAD_DIR / f"{stem}_{i}{suffix}"
                    if not cand.exists():
                        dest = cand
                        break
                    i += 1
            dest.write_bytes(raw)
            rel = f"models/uploads/{dest.name}"
            print(f"[upload] saved {rel} ({len(raw)} bytes)")
            return self._send_json(200, {"ok": True, "url": rel, "label": dest.name})

        self.send_error(404, "Unknown API route")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def run_http(port: int = 8080):
    ensure_defaults()
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), ARRequestHandler)
    print(f"[HTTP] http://127.0.0.1:{port}/index.html")
    print(f"[HTTP] settings -> {SETTINGS_PATH}")
    print("[HTTP] POST /api/settings  ·  POST /api/upload-model")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[HTTP] stopped.")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_http(p)
