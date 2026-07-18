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

## Smoke-Test / Screenshot Debugging (How We Verify Without Browser Console)

Since agents can't directly read the browser console or DOM, we use **desktop screenshots as a visual debugger**. Every error in this project was caught by iterating: serve → open → screenshot → inspect → fix → repeat.

### The Loop

```
1. Kill old servers   →  2. Start fresh python server
3. HTTP-verify files  →  4. Start-Process open in browser
5. Sleep (model size dependent)  →  6. CopyFromScreen capture desktop
7. Read the PNG back  →  8. Inspect: loaded? error text? spinner? blank?
9. If broken → fix code → go to 1
```

### Step-by-Step Commands

**1. Kill stale servers and restart:**
```powershell
# Kill any existing python servers on 8443
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8443 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue

# Start fresh
cd "C:\Users\steve\Augmented Reality\ar-heart"
python -m http.server 8443
```

**2. Verify files are serving (sanity check before opening browser):**
```powershell
$r = Invoke-WebRequest -Uri "http://localhost:8443/preview.html" -UseBasicParsing
"preview.html: HTTP $($r.StatusCode) ($($r.RawContentLength) bytes)"

$r2 = Invoke-WebRequest -Uri "http://localhost:8443/models/retopology.glb" -UseBasicParsing
"model: HTTP $($r2.StatusCode) ($([math]::Round($r2.RawContentLength/1KB,0)) KB)"
```
If HTTP != 200 here, the file path is wrong — fix it before opening the browser.

**3. Open browser, wait, screenshot:**
```powershell
# Wait time MUST account for model size:
#    <1MB model → 3-5 seconds
#    17MB model → 15-25 seconds (network + GLTF parsing)
Start-Process "http://localhost:8443/preview.html"
Start-Sleep -Seconds 22

Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bmp = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $screen.Bounds.Size)
$bmp.Save("_smoke_test.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
```

**4. Inspect the screenshot:**
```powershell
# Read back and visually check: is the model visible? is there an error overlay?
code _smoke_test.png
```

### What to Look For in the Screenshot

| Visual Sign | What It Means |
|-------------|---------------|
| Dark purple scene + grid floor + 3D model visible | Model loaded successfully |
| "Crimson Racer — orbit with mouse/touch" text at bottom | Confirmed: load succeeded (this text only appears after onLoad fires) |
| "Timed out loading model" error | GLTFLoader never fired onLoad — path wrong, glTF version mismatch, or file too big for the timeout |
| "Loader threw an exception: Cannot read properties..." | three.js version too old for the GLTFLoader — upgrade or polyfill |
| "Load error: HTTP 404" | Model path in MODEL_URL doesn't match the actual file |
| Spinner still spinning, no model | Loading still in progress — increase the wait time or check network |
| White/blank page | Server not running or html has a syntax error |
| "Failed to load" + Reload button visible | The catch/onError handler fired — check the error message text |
| "file://" mention in error | User double-clicked instead of using server URL |

### Real Bugs Caught with This Method

| Screenshot showed | Root Cause | Fix |
|-------------------|------------|-----|
| "file:// CORS blocked" error | Double-clicked preview.html instead of server URL | Added `file://` detection in error handler, doc warning |
| "Cannot read properties of undefined (extractUrlBase)" | r94 three.js doesn't export LoaderUtils | Upgraded to r98 (native exports) |
| Spinner after 10s, then 25s — no model | 17MB GLB only partially loaded at 10s | Increased timeout from 20s to 45s, added longer screenshot waits |
| Small wireframe visible — user said "I don't see a car" | Wrong model loaded (retopology.glb not Crimson Racer) | Swapped MODEL_URL back to Meshy AI GLB |
| Car loaded but "controls too fast, twitchy" | Default OrbitControls rotateSpeed=1.0 | Set rotateSpeed=0.3, dampingFactor=0.15 |

### Model Size → Screenshot Wait Time Guide

| Model Size | Min Wait | Reason |
|------------|----------|--------|
| <500KB | 3-5s | Instantly serves + parses |
| 1-5MB | 6-10s | Still fast over localhost |
| 10-20MB | 15-25s | Network transfer + GLTF JSON parsing + texture decode |
| 50MB+ | 30-45s | Needs the full 45s timeout window |

**Golden rule:** always take at least TWO screenshots — one at the minimum wait time, one after waiting longer. If both show the same error/state, it's a real bug, not a timing issue.

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
