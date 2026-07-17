# AR Heart — MeWorld

WebAR anatomical heart that appears when you point your phone camera at a Hiro marker.
Built with Three.js + ARToolkit, deployed via GitHub Pages.

## Quick Launch (Desktop Flyer)

Open the flyer in a browser — it shows the QR code and Hiro marker side by side.
Display it on a second screen or print it, then scan the QR with your phone.

```
file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html
```

**Launch commands** (Cursor agent / PowerShell):

```powershell
Start-Process "file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html"
```

To also open the AR experience on desktop:

```powershell
Start-Process "C:\Users\steve\Augmented Reality\ar-heart\index.html"
```

### Dev Server (for phone access)

Start the local server on port 8443:

```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"
python -c "import http.server; h=http.server.SimpleHTTPRequestHandler; h.extensions_map['.js']='application/javascript'; h.extensions_map['.dat']='application/octet-stream'; h.extensions_map['.patt']='application/octet-stream'; h.extensions_map['.wasm']='application/wasm'; s=http.server.HTTPServer(('0.0.0.0',8443),h); print('AR Heart on http://localhost:8443'); s.serve_forever()"
```

## Quick Start (User)

1. **Open the flyer** on your desktop (`flyer.html`) — QR code + Hiro marker side by side
2. **Scan the QR code** with your phone (or open `https://stefopps.github.io/ar-heart`)
3. **Allow camera** access when prompted
4. **Point your phone camera** at the Hiro marker on the flyer
5. A 3D **beating anatomical heart** appears above the marker with a vitals panel (BPM, Rhythm, EF%)

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

### 3D Heart (Procedural — No OBJ Files)

The heart is built from Three.js geometric primitives:

- **3 ellipsoids** (scaled spheres) for the main heart muscle — layered with color variation (`#cc2244` base)
- **Aorta** — cylinder, red-tinted
- **Pulmonary artery** — cylinder, blue-tinted
- **SVC / IVC** — cylinders at top and bottom
- **Lighting** — directional key + fill + ambient, all attached to the marker root

**Beating animation**: The heart pulses via `Math.sin(Date.now() * 0.008)` — uniform scale oscillation at ~76 BPM. Only active when the marker is tracked.

### Marker Tracking

The Hiro marker is tracked using ARToolkit's pattern matching:

```
Camera → ARToolkit pattern detection → 6DOF pose → Three.js scene transform
```

When the marker is detected:
- The heart appears in 3D space, positioned relative to the marker
- The info panel slides in (BPM, Rhythm, EF%)
- The status bar shows "Heart detected"
- BPM display starts (cosmetic, fluctuates 60–76)

When the marker is lost:
- The heart disappears
- The info panel slides out
- Instructions reappear

### Controls

The heart moves entirely through physical marker tracking:

- **Move the flyer** → rotate/translate the heart
- **Move closer** → zoom in (marker appears larger in camera)
- **No on-screen controls, keyboard, or GUI are active** (though the libraries are loaded — see "Future Features" below)

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

## Recovery Notes (July 16, 2026)

The project was originally built on July 6, 2026. On July 16, after a laptop reset, it was re-cloned and the following issues were fixed:

1. **Missing assets** — `hiro-marker.png` and `qr-iphone.png` were not in the repo (cleaned in an earlier commit). Re-generated both.
2. **QR code URL** — Originally pointed to a local IP (`192.168.1.157:8443`). Updated to GitHub Pages URL so it works from any phone without firewall configuration.
3. **GitHub Pages confirmation** — Verified Pages is enabled deploying from `master` branch root.
4. **Marker overlay** — Added an overlay to `index.html` showing the Hiro marker on first load so users know what to point at.
5. **Firewall rule** — Added Windows Firewall exception for port 8443 for local dev testing.

## UI Panels

### Info Panel (right side, slides in)

| Field | Display |
|-------|---------|
| BPM | 68–76 (sinusoidal fluctuation, cosmetic) |
| Rhythm | Sinus |
| EF | 60% |

### Status Bar (bottom center)

- "Point camera at the Hiro marker on your printed flyer" (tracking)
- "Heart detected — tracking" with green pulse animation (found)

### Marker Overlay (first load)

Shows the Hiro marker image with a "Got it" dismiss button. Dark semi-transparent overlay.

## Active Features

- [x] Hiro pattern marker tracking (ARToolkit)
- [x] Procedural 3D anatomical heart (7 geometric parts)
- [x] Beating animation (sine-wave pulsing, ~76 BPM)
- [x] BPM display (cosmetic, 60–76 range)
- [x] Info panel (BPM, Rhythm, EF%)
- [x] Status bar with tracking state
- [x] Loading screen
- [x] Printable flyer with QR code + marker
- [x] GitHub Pages deployment
- [x] HTTPS local dev server

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
