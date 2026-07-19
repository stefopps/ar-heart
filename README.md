# MeWorld AR — Hello Cube (baseline)

Clean starting point for incremental AR work.

**What works on `master`:** Stemkoski smoothed-controls **hello cube** + local model swap loader (`.glb` / `.gltf`) + Hiro marker flyer + AR.js stack.

**Current version:** `v=27` — immediate cube on boot (model loads async, no blocking)

**Previous work (crimson racer, GLB, touch UI, docs):** preserved on branch [`archive/v10-crimson-racer`](https://github.com/stefopps/ar-heart/tree/archive/v10-crimson-racer) — nothing deleted from git history.

## Live

https://stefopps.github.io/ar-heart/?v=27

## Local

```
python serve.py
```

Or HTTPS for phone camera:

```
python server_https.py
```

Open flyer: `flyer.html`  
AR page: `index.html`

## Keep / grow from here

| Path | Role |
|------|------|
| `index.html` | AR hello cube (Stemkoski hierarchy) |
| `flyer.html` | Printable Hiro marker + QR codes |
| `hiro-marker.png` / `hiro_marker.png` | Marker image for flyer |
| `data/hiro.patt` + `data/camera_para.dat` | ARToolkit pattern + camera |
| `js/three.js` | three.js **r86** (matches Stemkoski) |
| `jsartoolkit5/` | ARToolkit runtime |
| `threex/` | Marker + smoothed controls |
| `serve.py` | HTTP dev server + `/api/settings` + `/api/upload-model` |
| `server_https.py` | HTTPS dev server (extends serve.py, needed for phone camera) |
| `settings.json` | Disk-persisted lights, orientation, modelUrl, modelLabel |
| `models/uploads/` | Uploaded GLB files saved here for persistence |

## Swap the cube for a local model

1. **Tap "Load local model"** on the AR page and pick any `.glb` / `.gltf` from your phone/PC — uploads to `models/uploads/` and persists.
2. **Or** put a file in `models/` and set at the top of `index.html`:
   ```js
   var MODEL_URL = 'models/your-file.glb';
   ```
3. **Double-click any slider** to reset it to its default value.
4. **Click cube faces** (desktop preview) to set the model's up-axis.
5. **Drag the CSS axis cube** to rotate and click any face.
6. **Reset to cube** with the button on the page.

## Features (v=27)

- **Floating resizable preview** — drag, resize, collapse on desktop
- **Webcam toggle** — enable/disable AR camera feed
- **CSS axis cube** — click/tap faces to set model up-axis (no 3rd WebGL context)
- **Slider double-click reset** — any slider resets to default on double-click
- **Live settings -> AR** — light changes apply to both preview and AR simultaneously
- **Green marker pad** — semi-transparent green circle on Hiro marker (always visible when locked)
- **Drive animation** — loaded model glides from point A to B across the marker, turns around, and loops. Toggle "Drive: ON/OFF" in the swap bar; Speed + Distance sliders in the preview panel.
- **Disk persistence** — settings saved to `settings.json` via `/api/settings`
- **Model upload** — local files POST to `/api/upload-model` for persistent serving
- **Immediate boot** — orange cube renders instantly, model loads async in background

## Critical architecture rules (READ BEFORE EDITING index.html)

index.html is a **single-file JavaScript application** — one syntax error kills the entire app with zero visible errors (WebGL canvas just stays black). The most frequent failure:

### #1 KILLER: Missing closing brace in `initialize()`

When the boot was restructured to call `showCube()` synchronously before `loadSettingsAsync()`, the closing `}` of `initialize()` was accidentally deleted. This put every function from `clearContent()` onward *inside* `initialize()`, making them unreachable. Result: black screen, no cube, nothing renders.

**Prevention:**
- After ANY edit to `initialize()`: verify the brace count matches — `function initialize() {` MUST have exactly one `}` at the end of its body, BEFORE `clearContent()`.
- `clearContent()` should be at the top level, NOT nested inside `initialize()`.

### #2 KILLER: Third WebGL context

Desktop browsers typically allow 6-16 WebGL contexts. Phones (especially iOS Safari) allow far fewer. We already have 2 contexts (AR renderer + Preview renderer). Adding a third (orientCubeRenderer) caused context loss -> black preview. The fix: CSS 3D cube instead of WebGL.

**Prevention:** Never add a third `THREE.WebGLRenderer`. If you need another 3D view, use CSS transforms or canvas 2D.

### #3 KILLER: `isPhoneUI()` blocking preview on desktop

Aggressive media queries (`hover: none` and `pointer: coarse`) sometimes matched on headless browsers or hidpi displays, skipping `initPreview()` entirely.

**Prevention:** `shouldInitPreview()` explicitly checks `window.innerWidth > 900` — not just media query. `initPreview()` is ALWAYS called regardless of phone/desktop.

### #4 KILLER: Calling Three.js API that doesn't exist in r86

`THREE.Quaternion.identity()` does NOT exist in the bundled Three.js r86. Calling it throws `qUp.identity is not a function` at page load — a `PAGE_ERROR` (uncaught in Promise) that crashes `initialize()` silently. Everything after the crash line never runs: no `showCube()`, no `loadSettingsAsync()`, no model. The page looks alive (canvases exist, WebGL works) but the status bar gets stuck at whatever last set.

**Prevention:** Never use `.identity()` on Three.js math objects in this project. Use `.set(0,0,0,1)` for quaternions, `.set(1,1,1)` for vectors, etc. Check the Three.js r86 source (`js/three.js`) before using any modern API.

**Also:** `loadModelFromUrl` now uses browser `fetch` (not Three.js `FileLoader` XHR) for downloading GLB files. `FileLoader` silently hangs when WebGL context is lost; `fetch` survives context loss independently.

## Incremental rule

Build one feature at a time on top of this cube. When you need old racer files:

```
git checkout archive/v10-crimson-racer -- models/ path/you/want
```

## Credits

- [stemkoski/AR-Examples](https://github.com/stemkoski/AR-Examples) — smoothed-controls hello cube  
- [jeromeetienne/AR.js](https://github.com/jeromeetienne/AR.js) / [AR-js-org/AR.js](https://github.com/AR-js-org/AR.js)
