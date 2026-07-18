# AGENT HANDOFF — AR Heart / Racer (MeWorld)

**Last agent:** Cursor (claude-sonnet-4)
**Date:** 2026-07-18 ~08:30 UTC
**Status:** DEPLOYED — v=8 r98 production stack live on GitHub Pages

---

## Before You Do ANYTHING

READ the Quick Launch checklist in `README.md`. The flyer launches FIRST. The dev server launches SECOND. Open the viewer THIRD. Do not skip or reorder.

---

## What's Live Right Now

### Stack (v=8, working)
| Component | Version | Source |
|-----------|---------|--------|
| `js/three.js` | **r98** | jsDelivr CDN (`three@0.98.0/build/three.js`) |
| `js/GLTFLoader.js` | **r98** (matched) | jsDelivr CDN (`three@0.98.0/examples/js/loaders/GLTFLoader.js`) |
| `js/OrbitControls.js` | **r98** (matched) | jsDelivr CDN (`three@0.98.0/examples/js/controls/OrbitControls.js`) |
| Model | Crimson Polygon Racer | Meshy AI, 17.7MB GLB, glTF 2.0 PBR |
| AR tracking | `jsartoolkit5` + `threex` | Original stemkoski stack (untouched) |

### Why r98?
The r86 core only shipped with a glTF 1.0 loader. r94 added glTF 2.0 but didn't export `LoaderUtils`/`AnimationUtils` in the built file — the GLTFLoader crashed with "Cannot read properties of undefined (reading 'extractUrlBase')". **r98** is the first version where the built three.js exports all utilities its own GLTFLoader needs, with zero polyfills.

### The Journey
```
r86 → silent infinite spinner (glTF 1.0 loader can't parse 2.0 GLBs)
  ↓
r94 → missing LoaderUtils/AnimationUtils/BufferGeometryUtils (loaded but no polyfill = crash)
  ↓
r98 → works out of the box. matched trio. no hacks.
```

### Defensive Loading (in both index.html + preview.html)
- **45s hard timeout** — if `onLoad` never fires, user sees "Timed out" instead of infinite spinner
- **Sync `try/catch`** around `loader.load()` — catches exceptions the internal Promise chain drops
- **Empty geometry check** — zero bounding box → "empty model" error
- **HTTP status** in error messages when available
- **`file://` detection** — tells user to use `http://localhost:8443/preview.html` instead of double-clicking
- **Reload button** in preview.html when load fails

### Controls (preview.html)
- `rotateSpeed: 0.3` (was 1.0 — 70% slower, no more twitch)
- `zoomSpeed: 0.8` (was 1.0)
- `dampingFactor: 0.15` (was 0.08 — more inertia)
- `minDistance: 0.5`, `maxDistance: 15`

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | AR viewer — hardened with 45s timeout, try/catch, empty-geometry check |
| `flyer.html` | Desktop/print: QR code + Hiro marker side by side |
| `preview.html` | 3D viewer — orbit controls, hardened loader, reload button, `file://` warning |
| `models/Meshy_AI_Crimson_Polygon_Racer_0717124504_texture.glb` | Current model (17.7MB, Meshy AI PBR) |
| `models/retopology.glb` | Test model (331KB, Houdini OBJ → GLB) |
| `js/three.js` | Three.js r98 — DO NOT DOWNGRADE |
| `js/GLTFLoader.js` | r98 glTF 2.0 loader (`pbrMetallicRoughness`) |
| `js/OrbitControls.js` | r98 orbit controls |
| `js/three.js.r86.bak` | Original r86 — restore only if AR.js tracking breaks |
| `js/GLTFLoader.js.old.bak` | Previous loader (r94 era, needs polyfills) |
| `data/hiro.patt` | ARToolkit Hiro marker pattern |
| `data/camera_para.dat` | ARToolkit camera parameters |
| `qr-iphone.png` | QR code → `https://stefopps.github.io/ar-heart/?v=8` |
| `AGENT_HANDOFF.md` | This file |
| `README.md` | Quick launch checklist |

---

## Cache-Busting Pipeline

GitHub Pages CDN (Fastly) serves `max-age=300`. iOS Safari caches aggressively.

Three layers:
1. **GLB loader** — `loader.load('...glb?v=' + Date.now())` — fresh URL every page load
2. **QR code** — regenerates with `?v=N` query param on every deploy
3. **Deploy stamp** — `<!-- v=N -->` comment in `index.html`

**When swapping models, ALWAYS:**
- Bump the `v=` number
- Regenerate `qr-iphone.png` with the new URL
- Wait 5 min before testing on phone
- Test in a private/incognito tab first

---

## Deploy Flow (Every Model Swap)

```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"

# 1. Edit index.html (model path, UI labels, deploy stamp)
# 2. Regenerate QR (N = next version number)
python -c "import qrcode; qr = qrcode.QRCode(box_size=10, border=4); qr.add_data('https://stefopps.github.io/ar-heart/?v=N'); qr.make(fit=True); img = qr.make_image(fill_color='#ff6600', back_color='#0a0a0f'); img.save('qr-iphone.png'); print('QR v=N done')"

# 3. Commit and push
git add index.html preview.html qr-iphone.png models/
git commit -m "swap model: <name>, v=N cache-bust"
git push origin master

# 4. WAIT 5 MINUTES for Fastly CDN to purge
# 5. Test: https://stefopps.github.io/ar-heart?v=N (private tab)
```

---

## Local Dev Server

```powershell
cd "C:\Users\steve\Augmented Reality\ar-heart"
python -m http.server 8443
```

Then open: `http://localhost:8443/preview.html`

**Do NOT double-click `preview.html`** — the `file://` protocol blocks XHR to local assets. Always use the server.

---

## Common Mistakes (Do Not Repeat)

- **"Phone still shows old model"** — didn't push, or didn't wait 5 min for CDN, or phone cache. Private tab with fresh `?v=N`.
- **"Model never shows up, no errors"** — glTF 1.0 loader vs 2.0 file. Check: `pbrMetallicRoughness` = 2.0 (good), `technique`/`KHR_materials_common` = 1.0 (broken). We're on r98 — this shouldn't happen again.
- **"Cannot read properties of undefined (reading 'extractUrlBase')"** — three.js core is too old for the GLTFLoader. Upgrade to r98+ or add polyfills for `LoaderUtils`/`AnimationUtils`/`BufferGeometryUtils`.
- **"CORS error: file:// blocked"** — opened `preview.html` by double-clicking. Always use `http://localhost:8443/preview.html`.
- **"AR marker tracking broke"** — restore `js/three.js.r86.bak` → `js/three.js` and update this doc.
- **"QR goes to old version"** — regenerate `qr-iphone.png` with new `v=N`.
- **"Marker doesn't track"** — phone only (needs camera + WebRTC). `preview.html` is inspection only.

---

## Home URLs

- **Local dev:** `http://localhost:8443/preview.html`
- **GitHub Pages:** `https://stefopps.github.io/ar-heart?v=8` (current)
- **Repo:** `https://github.com/stefopps/ar-heart`
- **Flyer:** `file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html`

---

## Secrets / Credentials

No API keys, no secrets. Static HTML + JS. GitHub Pages deploys from `master` branch root.
