# AGENT HANDOFF — AR Heart / Racer (MeWorld)

**Last agent:** Cursor (claude-sonnet-4)
**Date:** 2026-07-18 01:15 UTC
**Status:** DEPLOYED — Orange theme v=4 live on GitHub Pages

---

## Before You Do ANYTHING

READ the Quick Launch checklist in `README.md`. The flyer launches FIRST. The dev server launches SECOND. Open the viewer THIRD. Do not skip or reorder.

---

## What We Built / Fixed This Session

### 1. Model Swap: Procedural Heart → Crimson Polygon Racer GLB
- Stripped `createHeart()`, `startBPM()`, heartbeat animation from `index.html`
- Added `GLTFLoader.js` (Three.js r86 compatible) at `js/GLTFLoader.js`
- Model lives at `models/Meshy_AI_Crimson_Polygon_Racer_0717124504_texture.glb` (17.7MB)
- `preview.html` — 3D viewer with orbit controls, no AR needed. Open locally to inspect model before phone test.

### 2. Cache-Busting Pipeline (v=4)
**The problem:** GitHub Pages CDN (Fastly) serves `max-age=300`. iOS Safari caches aggressively. Every push takes up to 5 min to propagate. The phone won't show changes immediately.
**The fix:** Three layers of cache busting:
1. **GLB loader** — `loader.load('...glb?v=' + Date.now())` — fresh URL every page load
2. **QR code** — regenerates with `?v=N` query param on every deploy
3. **Deploy stamp** — `<!-- deploy:... -->` comment at line 2 of `index.html` for version verification

**When swapping models, ALWAYS:**
- Bump the `v=` number
- Regenerate `qr-iphone.png` with the new URL
- Wait 5 min before testing on phone
- Test in a private/incognito tab first

### 3. Orange Theme (v=4 Visual Indicator)
- All `#00e5a0` (green) replaced with `#ff6600` (orange) in `index.html`
- Hiro marker image tinted orange in flyer and AR overlay
- "v4" badge on flyer marker box
- If you see green, you're looking at a cached old version

### 4. Agent Checklist Added to README
- Step-by-step launch commands
- How to swap models (with table of which lines to edit)
- CDN wait warning
- GLTFLoader download command for r86

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | AR viewer (phone scans QR, points at marker, 3D model appears) |
| `flyer.html` | Desktop/print: QR code + Hiro marker side by side |
| `preview.html` | 3D viewer (no AR, no camera): orbit/zoom/pan the model |
| `server.py` | HTTPS dev server (needs openssl — not used, use Python http.server instead) |
| `models/` | GLB + FBX models and PBR textures |
| `js/GLTFLoader.js` | Three.js r86 GLTF 2.0 loader |
| `js/OrbitControls.js` | Three.js r86 orbit controls (preview viewer) |
| `js/three.js` | Three.js r86 (2017) — DO NOT UPGRADE without updating GLTFLoader |
| `data/hiro.patt` | ARToolkit Hiro marker pattern |
| `qr-iphone.png` | QR code pointing to Pages URL with v= param |

---

## Deploy Flow (Every Model Swap)

```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"

# 1. Edit index.html (model path, UI labels, deploy stamp)
# 2. Regenerate QR (N = next version number)
python -q -c "import qrcode; qr = qrcode.QRCode(box_size=10, border=4); qr.add_data('https://stefopps.github.io/ar-heart?v=N'); qr.make(fit=True); img = qr.make_image(fill_color='black', back_color='white'); img.save('qr-iphone.png'); print('QR v=N done')"

# 3. Commit and push
git add index.html README.md flyer.html qr-iphone.png models/ js/
git commit -m "swap model: <name>, v=N cache-bust"
git push origin master

# 4. WAIT 5 MINUTES for Fastly CDN to purge
# 5. Test: https://stefopps.github.io/ar-heart?v=N (private tab)
```

---

## Common Mistakes (Do Not Repeat)

- **"Phone still shows the heart"** — you didn't push, or you didn't wait 5 min for CDN, or the phone is using a cached tab. Use a new `?v=` URL in a private tab.
- **"server.py doesn't work"** — OpenSSL not installed. Use the one-liner `python -c "import http.server;..."` from README instead.
- **"GLTFLoader error"** — Three.js is r86. GLTFLoader must match. Use the one at `js/GLTFLoader.js` or download from `https://cdn.jsdelivr.net/npm/three@0.86.0/examples/js/loaders/GLTFLoader.js`
- **"QR code still goes to old version"** — Regenerate `qr-iphone.png` with bumped `v=N`. The QR encodes the URL with the version string.
- **"Marker doesn't track"** — Works only on phone (needs camera + WebRTC). The `flyer.html` marker must be visible to the camera. Desktop `preview.html` is for inspection only.

---

## Home URLs

- **Local dev:** `http://localhost:8443` (with server running)
- **GitHub Pages:** `https://stefopps.github.io/ar-heart?v=4` (current)
- **Repo:** `https://github.com/stefopps/ar-heart`
- **Flyer:** `file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html`
- **Preview:** `file:///C:/Users/steve/Augmented%20Reality/ar-heart/preview.html`

---

## Secrets / Credentials

No API keys, no secrets. Static HTML + JS. GitHub Pages deploys from `master` branch root.
