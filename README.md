# AR Viewer — MeWorld

WebAR viewer that displays 3D models when you point your phone camera at a Hiro marker.
Built with Three.js r98 + ARToolkit, deployed via GitHub Pages.

**Current model:** Crimson Polygon Racer (Meshy AI, glTF 2.0 PBR, 17.7MB GLB)

## Quick Launch — Agent Checklist (Must Follow)

Every agent must do this in order. Skip nothing. The flyer always launches first.

1. **Start the dev server** on port 8443:
```powershell
cd "C:\Users\steve\Augmented Reality\ar-heart"
python -m http.server 8443
```

2. **Open the flyer** (QR code + Hiro marker side by side):
```powershell
Start-Process "file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html"
```

3. **Open the preview viewer** in the browser:
```powershell
Start-Process "http://localhost:8443/preview.html"
```

Do NOT double-click `preview.html` — the `file://` protocol blocks local asset loading.

### Live URL (GitHub Pages)
```
https://stefopps.github.io/ar-heart?v=8
```
After any change, push to `master` and wait 5 minutes for Fastly CDN to propagate.

## Model Swap Pipeline

1. **Drop the new .glb file** into `models/`
2. **Edit `index.html`** and `preview.html` — change `MODEL_URL` and UI labels
3. **Regenerate QR** with new version number:
```powershell
python -c "import qrcode; qr = qrcode.QRCode(box_size=10, border=4); qr.add_data('https://stefopps.github.io/ar-heart/?v=N'); qr.make(fit=True); img = qr.make_image(fill_color='#ff6600', back_color='#0a0a0f'); img.save('qr-iphone.png')"
```
4. **Commit and push:**
```powershell
git add index.html preview.html qr-iphone.png models/
git commit -m "swap model: <name>, v=N cache-bust"
git push origin master
```
5. **Wait 5 minutes** for CDN purge
6. **Test** in private tab: `https://stefopps.github.io/ar-heart?v=N`

### Where to Edit

| What | File | Variable/Location |
|------|------|-------------------|
| Model path | `index.html`, `preview.html` | `var MODEL_URL = 'models/___'` |
| Page title | `index.html` | `<title>` in `<head>` |
| Loading text | `index.html` | `<p>` in `#loading` div |
| Top badges | `index.html` | `<div class="value">` |
| Info panel | `index.html` | `<h3>` and rows in `#info` |
| Status text | `index.html` | `s.textContent` in markerFound |

## Tech Stack

| Layer | Version |
|-------|---------|
| **Three.js** | r98 (jsDelivr CDN) |
| **GLTFLoader** | r98 matched — glTF 2.0 PBR (`pbrMetallicRoughness`) |
| **OrbitControls** | r98 matched — preview viewer |
| **AR Tracking** | `jsartoolkit5` + `threex` (stemkoski, version-locked, untouched) |
| **Marker** | Hiro pattern (`data/hiro.patt`) |
| **Hosting** | GitHub Pages (static, no build step) |
| **Local dev** | Python `http.server` on port 8443 |

### Why r98?

- **r86** only shipped a glTF **1.0** loader — silently fails on glTF 2.0 files (infinite spinner, no errors)
- **r94** has a glTF 2.0 loader but the built file doesn't export `LoaderUtils`/`AnimationUtils` — GLTFLoader crashes
- **r98** is the first release where three.js exports all utilities its own GLTFLoader needs — zero polyfills

### Backups

- `js/three.js.r86.bak` — original r86 core. Restore ONLY if AR.js marker tracking breaks after an upgrade.
- `js/GLTFLoader.js.old.bak` — previous loader (r94 era, needs polyfills).

## Defensive Loading

Both `index.html` and `preview.html` have hardened model loading:
- **45s timeout** — no more infinite spinners
- **`try/catch`** around `loader.load()` — catches sync exceptions
- **Empty geometry check** — zero bounding box → "empty model" error
- **HTTP status** in error messages
- **`file://` detection** — tells user to use the dev server
- **Reload button** in preview.html

## How It Works

### Model Loading
The GLB is loaded via `THREE.GLTFLoader`, auto-scaled to fit a 0.8-unit bounding box, centered at Y=0.3 on the marker.

### Marker Tracking
```
Camera → ARToolkit pattern detection → 6DOF pose → Three.js scene transform
```
Phone-only (needs WebRTC `getUserMedia`). Desktop `preview.html` is for model inspection only.

### Controls (preview.html)
- **Drag** → orbit (rotateSpeed: 0.3)
- **Scroll** → zoom (zoomSpeed: 0.8)
- **Right-drag** → pan
- Damping: 0.15 (smooth inertia)

## Deploy (GitHub Pages)

```
Repo:   github.com/stefopps/ar-heart
Branch: master (root)
URL:    https://stefopps.github.io/ar-heart
```

## Credits

- **Code base**: [stemkoski/AR-Examples](https://github.com/stemkoski/AR-Examples)
- **Inspiration**: [@thesunkenblimp](https://www.instagram.com/p/DZ5zg9cRSk6)
- **MeWorld AR** by Steve (`stefopps`)
