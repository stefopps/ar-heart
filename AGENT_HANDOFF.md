# AGENT HANDOFF — AR Heart / Racer (MeWorld)

**Last agent:** Cursor (claude-sonnet-4)
**Date:** 2026-07-18 ~08:30 UTC
**Status:** DEPLOYED — v=7 r94 production upgrade live on GitHub Pages

---

## Before You Do ANYTHING

READ the Quick Launch checklist in `README.md`. The flyer launches FIRST. The dev server launches SECOND. Open the viewer THIRD. Do not skip or reorder.

---

## What We Built / Fixed This Session

### 1. Root Cause: Silent Infinite Spinner (FIXED — v=5)

**The problem:** The original `GLTFLoader.js` was a **glTF 1.0** loader (uses `technique`/`program`/`shader` materials, `KHR_materials_common`, binary header `version: 1`). Meshy AI and Houdini export **glTF 2.0** GLB files (PBR `pbrMetallicRoughness` materials). The 1.0 loader silently failed inside internal Promises with no `.catch` — no error ever surfaced, spinner spun forever, zero console output.

**The fix (v=5):** Replaced `js/GLTFLoader.js` with the three.js r94 glTF-2.0-capable rewrite (Don McCurdy).

### 2. Production Upgrade (v=7 — THIS SESSION)

**Three.js core upgraded from r86 → r94:**
- `js/three.js` — REVISION '94', matched trio with GLTFLoader and OrbitControls
- `js/GLTFLoader.js` — glTF 2.0 PBR (`pbrMetallicRoughness`, `KHR_materials_pbrSpecularGlossiness`)
- `js/OrbitControls.js` — matched r94, for preview.html

**Defensive loading pattern — no more silent failures:**
- 20s hard timeout on every `loader.load()` call
- Sync `try/catch` around `loader.load()` — catches things the Promise chain drops
- Empty geometry check (zero bounding box detection)
- HTTP status in error messages when available
- Reload button when loading fails

**Backup files left in `js/`:**
- `three.js.r86.bak` — original r86 core, restore if AR.js marker tracking breaks
- `GLTFLoader.js.old.bak` — previous loader (likely also glTF 2.0 but from earlier fix)

### 3. Model Swap: Crimson Racer → Retopology (v=6)
- Model at `models/retopology.glb` (320KB, converted from Houdini OBJ)
- All UI labels updated: "Retopology", "Houdini 22", "OBJ → GLB"
- The old 17.7MB Meshy model is still in models/ if needed

### 4. Cache-Busting Pipeline
**The problem:** GitHub Pages CDN (Fastly) serves `max-age=300`. iOS Safari caches aggressively. Every push takes up to 5 min to propagate. The phone won't show changes immediately.
**The fix:** Three layers:
1. **GLB loader** — `loader.load('...glb?v=' + Date.now())` — fresh URL every page load
2. **QR code** — regenerates with `?v=N` query param on every deploy
3. **Deploy stamp** — `<!-- v=N -->` comment in `index.html` for version verification

**When swapping models, ALWAYS:**
- Bump the `v=` number
- Regenerate `qr-iphone.png` with the new URL
- Wait 5 min before testing on phone
- Test in a private/incognito tab first

### 5. Orange Theme
- All UI elements use `#ff6600` orange (borders, text, buttons, spinner, accent glows)
- Hiro marker tinted orange via CSS filter
- If you see green, you're looking at a cached old version

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | AR viewer (phone scans QR, points at marker, 3D model appears) — hardened with 20s timeout |
| `flyer.html` | Desktop/print: QR code + Hiro marker side by side |
| `preview.html` | 3D viewer (no AR, no camera): orbit/zoom/pan the model — hardened with timeout + reload button |
| `models/retopology.glb` | Current model (320KB, Houdini OBJ → GLB) |
| `models/Meshy_AI_Crimson_Polygon_Racer_0717124504_texture.glb` | Old model (17.7MB, Meshy AI) |
| `js/three.js` | Three.js r94 — DO NOT DOWNGRADE without understanding glTF loader impact |
| `js/GLTFLoader.js` | Three.js r94 glTF 2.0 loader (pbrMetallicRoughness) |
| `js/OrbitControls.js` | Three.js r94 orbit controls |
| `js/three.js.r86.bak` | Original r86 backup — restore only if AR.js marker tracking breaks |
| `js/GLTFLoader.js.old.bak` | Previous loader backup |
| `data/hiro.patt` | ARToolkit Hiro marker pattern |
| `data/camera_para.dat` | ARToolkit camera parameters |
| `qr-iphone.png` | QR code pointing to Pages URL with v=7 param |
| `AGENT_HANDOFF.md` | This file — read me first |
| `README.md` | Quick launch checklist |

---

## Deploy Flow (Every Model Swap)

```powershell
Set-Location "C:\Users\steve\Augmented Reality\ar-heart"

# 1. Edit index.html (model path, UI labels, deploy stamp comment)
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

## Common Mistakes (Do Not Repeat)

- **"Phone still shows old model"** — you didn't push, or you didn't wait 5 min for CDN, or the phone is using a cached tab. Use a new `?v=` URL in a private tab.
- **"Model never shows up, no console errors"** — The GLTFLoader may be a glTF 1.0 loader trying to parse a glTF 2.0 file. Check the loader file: if it references `technique`/`KHR_materials_common`, it's 1.0. glTF 2.0 loaders reference `pbrMetallicRoughness`/`KHR_materials_pbr`. Three.js r86 only shipped with a 1.0 loader. **We're now on r94 — this should never happen again.**
- **"Timeout error after 20s"** — The new hardened loader shows a timeout message if the model doesn't load. Check the browser console (F12) for the real error. If it says HTTP 404, the model path is wrong. If it's a CORS error, the server isn't configured correctly.
- **"AR marker tracking broke"** — If this happens after an upgrade, the three.js core version may not be compatible with the AR.js/threex stack. Restore `js/three.js.r86.bak` → `js/three.js` and update AGENT_HANDOFF.md with what broke.
- **"QR code still goes to old version"** — Regenerate `qr-iphone.png` with bumped `v=N`. The QR encodes the URL with the version string.
- **"Marker doesn't track"** — Works only on phone (needs camera + WebRTC). Desktop `preview.html` is for inspection only.

---

## Home URLs

- **Local dev:** `https://localhost:8443` (with server running)
- **GitHub Pages:** `https://stefopps.github.io/ar-heart?v=7` (current)
- **Repo:** `https://github.com/stefopps/ar-heart`
- **Flyer:** `file:///C:/Users/steve/Augmented%20Reality/ar-heart/flyer.html`
- **Preview:** `file:///C:/Users/steve/Augmented%20Reality/ar-heart/preview.html`

---

## Secrets / Credentials

No API keys, no secrets. Static HTML + JS. GitHub Pages deploys from `master` branch root.
