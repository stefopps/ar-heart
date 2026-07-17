# AR Viewer — MeWorld

WebAR viewer that displays 3D models when you point your phone camera at a Hiro marker.
Built with Three.js + ARToolkit, deployed via GitHub Pages.

**Current model:** Crimson Polygon Racer (Meshy AI, GLTF 2.0, 17.7MB GLB)

## Quick Launch — Agent Checklist (Must Follow)

Every agent must do this in order. Skip nothing. The flyer always launches first.

1. **Open the flyer** (QR code + Hiro marker side by side):
```powershell
Start-Process "file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html"
```

2. **Start the dev server** on port 8443:
```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"
python -c "import http.server; h=http.server.SimpleHTTPRequestHandler; h.extensions_map['.js']='application/javascript'; h.extensions_map['.dat']='application/octet-stream'; h.extensions_map['.patt']='application/octet-stream'; h.extensions_map['.wasm']='application/wasm'; s=http.server.HTTPServer(('0.0.0.0',8443),h); print('AR on http://localhost:8443'); s.serve_forever()"
```

3. **Open the AR viewer** in the browser:
```powershell
Start-Process "http://localhost:8443"
```

### Live URL (GitHub Pages)

```
https://stefopps.github.io/ar-heart
```

After any model change, you MUST push to `master` — Pages serves from `master` branch root. If the user says "it still shows the old model", you forgot to push.

## How to Swap the 3D Model

The model is loaded in `index.html` via GLTFLoader (~line 183). To swap:

1. **Drop the new .glb file** into `models/`
2. **Edit `index.html`** — change the `loader.load()` path and update the UI labels (title, badge, info panel)
3. **Stage, commit, push:**
```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"
# Bump the cache version on every deploy (prevents stale CDN/phone cache)
python -q -c "import qrcode; qr = qrcode.QRCode(box_size=10, border=4); qr.add_data('https://stefopps.github.io/ar-heart?v=N'); qr.make(fit=True); img = qr.make_image(fill_color='black', back_color='white'); img.save('qr-iphone.png'); print('QR regenerated')"
git add index.html README.md models/ js/ qr-iphone.png flyer.html
git commit -m "swap model: <description>, v=N cache-bust"
git push origin master
```
4. **Wait 5 minutes** — GitHub Pages CDN (Fastly) has a `max-age=300` TTL. Testing immediately will serve stale.
5. **Verify** — open `https://stefopps.github.io/ar-heart?v=N` with the new version number. If the UI doesn't match, check the deploy comment at the top of the page source.

### Where to Edit in index.html

| What | Line/Area |
|------|-----------|
| **Deploy stamp** | `<!-- deploy:... -->` comment at line 2 — update timestamp on every push |
| Page title | `<title>` in `<head>` |
| Loading text | `<p>MeWorld AR ___</p>` in `#loading` div |
| Top badge | `<div class="value">___</div>` |
| Info panel | `<h3>___</h3>` and the rows inside `#info` |
| Model path | `loader.load('models/___?v=' + Date.now())` ~line 192 |
| Status text | `s.textContent = '___ detected'` in markerFound |

### GLTFLoader

The project uses Three.js r86 (2017). The GLTFLoader compatible with r86 is at `js/GLTFLoader.js`. If you need to re-download:
```powershell
curl.exe -s -o "js\GLTFLoader.js" "https://cdn.jsdelivr.net/npm/three@0.86.0/examples/js/loaders/GLTFLoader.js"
```

## Quick Start (User)

1. **Open the flyer** on desktop (`flyer.html`) — QR code + Hiro marker side by side
2. **Scan the QR code** with your phone (or open `https://stefopps.github.io/ar-heart`)
3. **Allow camera** access when prompted
4. **Point your phone camera** at the Hiro marker on the flyer
5. The 3D model appears above the marker — move the flyer to rotate/zoom

## How It Works

### Tech Stack

| Layer | Technology |
|-------|-----------|
| AR Tracking | ARToolkit (WebAssembly) via `jsartoolkit5` |
| 3D Rendering | Three.js |
| Marker | Hiro pattern (standard AR marker, `data/hiro.patt`) |
| Camera | WebRTC `getUserMedia` via `THREEx.ArToolkitSource` |
| Hosting | GitHub Pages (static, no build step) |
| Local dev | Python HTTP server on port 8443 |

### 3D Model

The current model is loaded from a GLB file via `THREE.GLTFLoader`. It replaces the original procedural anatomical heart.

**Model:** `models/Meshy_AI_Crimson_Polygon_Racer_0717124504_texture.glb` (17.7MB, GLTF 2.0)

The model is auto-scaled to fit a 0.8-unit bounding box and centered at Y=0.3 on the marker.

### Marker Tracking

The Hiro marker is tracked using ARToolkit's pattern matching:

```
Camera → ARToolkit pattern detection → 6DOF pose → Three.js scene transform
```

When the marker is detected:
- The 3D model appears in space, positioned relative to the marker
- The info panel slides in (model info)
- The status bar shows "[Model] detected"

When the marker is lost:
- The model disappears
- The info panel slides out
- Instructions reappear

### Controls

The model moves entirely through physical marker tracking:

- **Move the flyer** → rotate/translate
- **Move closer** → zoom in (marker appears larger in camera)
- **No on-screen controls, keyboard, or GUI are active**

## Deployment

### GitHub Pages (Production)

```
Repo:   github.com/stefopps/ar-heart
Branch: master (root)
URL:    https://stefopps.github.io/ar-heart
```

GitHub Pages is configured in the repo settings. Every push to `master` automatically deploys.

### Local Development

Run a Python HTTP server (needed because HTTPS is required for camera access on iOS):

```bash
python server.py  # serves on port 8443 with SSL certs for camera permissions
```

Or with the standard library:

```bash
python -c "import http.server; h=http.server.SimpleHTTPRequestHandler; h.extensions_map['.js']='application/javascript'; h.extensions_map['.dat']='application/octet-stream'; s=http.server.HTTPServer(('0.0.0.0',8443),h); print(':8443'); s.serve_forever()"
```

If testing from a phone on the same Wi-Fi, open **Windows Firewall** for port 8443 (admin CMD):

```
netsh advfirewall firewall add rule name="AR_Heart_8443" dir=in action=allow protocol=TCP localport=8443
```

### QR Code Generation

The QR code (`qr-iphone.png`) points to the GitHub Pages URL. To regenerate:

```python
import qrcode
qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data("https://stefopps.github.io/ar-heart")
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qr-iphone.png")
```

### Hiro Marker

The marker image (`hiro-marker.png`) is the standard ARToolkit Hiro pattern. The pattern data is in `data/hiro.patt`. To download from CDN:

```
https://raw.githubusercontent.com/AR-js-org/AR.js/master/data/images/hiro.png
```

## Recovery Notes

### July 17, 2026 — Model Swap

Replaced the procedural anatomical heart with the Crimson Polygon Racer GLB:

1. Downloaded `GLTFLoader.js` compatible with Three.js r86 from jsDelivr CDN
2. Copied the racer GLB (17.7MB) into `models/`
3. Stripped out `createHeart()`, `startBPM()`, and the beating animation from `index.html`
4. Added GLB loading with auto-scale via `THREE.Box3().setFromObject()`
5. Updated all UI labels (title, badge, info panel, status text)
6. Pushed to `master` — GitHub Pages deploys automatically

**Lesson:** Local `index.html` file changes don't matter for the phone — the phone scans the GitHub Pages URL. Always push after changes.

### July 16, 2026 — Recovery After Reset

The project was originally built on July 6, 2026. On July 16, after a laptop reset, it was re-cloned and the following issues were fixed:

1. **Missing assets** — `hiro-marker.png` and `qr-iphone.png` were not in the repo (cleaned in an earlier commit). Re-generated both.
2. **QR code URL** — Originally pointed to a local IP (`192.168.1.157:8443`). Updated to GitHub Pages URL so it works from any phone without firewall configuration.
3. **GitHub Pages confirmation** — Verified Pages is enabled deploying from `master` branch root.
4. **Marker overlay** — Added an overlay to `index.html` showing the Hiro marker on first load so users know what to point at.
5. **Firewall rule** — Added Windows Firewall exception for port 8443 for local dev testing.

## UI Panels

### Info Panel (right side, slides in)

Displays current model metadata. Edit these values in `index.html` when changing models.

### Status Bar (bottom center)

- "Point camera at the Hiro marker on your flyer" (tracking)
- "[Model] detected — tracking" with green pulse animation (found)

### Marker Overlay (first load)

Shows the Hiro marker image with a "Got it" dismiss button. Dark semi-transparent overlay.

## Active Features

- [x] Hiro pattern marker tracking (ARToolkit)
- [x] GLTF 2.0 model loading via GLTFLoader (Three.js r86)
- [x] Auto-scale model to fit bounding box
- [x] Info panel
- [x] Status bar with tracking state
- [x] Loading screen
- [x] Printable flyer with QR code + marker
- [x] GitHub Pages deployment
- [x] Local dev server on port 8443

## Libraries Present But Not Wired

These files are in the repo and loaded in `index.html` but not activated:

| File | What It Does | 
|------|-------------|
| `js/keyboard.js` | Keyboard input handling |
| `js/dat.gui.min.js` | GUI control panel (sliders, color pickers) |
| `js/OBJLoader.js` + `js/MTLLoader.js` | Load external 3D model files |
| `js/stats.min.js` | FPS performance monitor |
| `threex/threex-arsmoothedcontrols.js` | Smoothed marker tracking (lerp/slerp) |

### Future Feature Ideas

- **dat.GUI panel** — sliders for BPM speed, heart scale, color, opacity
- **OBJ model loading** — swap the procedural heart for a detailed anatomical OBJ
- **Smooth tracking** — instantiate `ArSmoothedControls` to reduce jitter
- **Keyboard controls** — arrow keys to rotate, +/- to zoom
- **Multiple markers** — different views (cross-section, external, labeled)
- **Touch/drag gestures** — rotate with one finger, pinch to zoom
- **Audio** — heartbeat sound synchronized to animation

## Git History

```
50e0543  flyer assets: Hiro marker + QR code pointing to GitHub Pages  (Jul 16, 2026)
f2af3de  Update QR and flyer for Pages URL                            (Jul 6, 2026)
c2448c2  Clean: remove dev artifacts                                  (Jul 6, 2026)
9bffd5c  AR heart demo -- stemkoski pattern                           (Jul 6, 2026)
```

## Credits

- **Code base**: [stemkoski/AR-Examples](https://github.com/stemkoski/AR-Examples) (Lee Stemkoski)
- **Inspiration**: [@thesunkenblimp](https://www.instagram.com/p/DZ5zg9cRSk6)
- **MeWorld AR** by Steve (`stefopps`)
