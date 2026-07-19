# AGENTS.md — ar-heart (MeWorld AR)

Single-file Three.js + AR.js app. One JS error = black screen, zero visible feedback. Be paranoid.

## File map

| File | Role | Risk |
|------|------|------|
| `index.html` | THE app. All HTML + CSS + JS in one file. ~1750 lines. | HIGH — one syntax error breaks everything |
| `serve.py` | HTTP dev server, `/api/settings`, `/api/upload-model` | LOW |
| `server_https.py` | HTTPS wrapper for serve.py | LOW |
| `settings.json` | Persisted lights, orientation, modelUrl | LOW |
| `flyer.html` | Printable Hiro marker + QR codes | LOW |
| `README.md` | Human docs + architecture rules | LOW |

## Critical invariants (DO NOT BREAK)

1. **`initialize()` must close before `clearContent()`.** `clearContent` is a top-level function. If it's nested inside `initialize()`, the whole script is dead.
2. **Only 2 WebGL contexts max.** AR renderer + Preview renderer. No third `THREE.WebGLRenderer`. Use CSS 3D for extras.
3. **`initPreview()` must always run.** Never gate it behind `isPhoneUI()`. `shouldInitPreview()` uses `innerWidth > 900`.
4. **`showCube()` must be callable from the top level.** Must not depend on async boot order.
5. **Version comment `<!-- v=XX: ... -->` goes near top of HTML source, incrementing on any meaningful change.**

## Post-edit verification checklist (RUN EVERY TIME after editing index.html)

After ANY edit to `index.html`, run these checks. Do not close your turn until verified.

### 1. Brace sanity — `initialize()` is closed
```
grep -n "function initialize\|function clearContent" index.html
```
- `clearContent` must appear on a HIGHER line number than `initialize`.
- Between them: exactly one `}` at the indentation depth that closes `initialize`.
- Quick verify: the line IMMEDIATELY before `function clearContent()` should be `}` (column 0).

### 2. `showCube` is at top level (not nested)
```
grep -n "function showCube" index.html
```
- Must not be inside any other function. Check surrounding context — it should follow a `}` at column 0.

### 3. WebGL context count = 2
```
grep -c "THREE.WebGLRenderer" index.html
```
- Must return exactly `2` (AR renderer + preview renderer). If 3+, REJECT.

### 3b. Three.js r86 API compatibility (NEW)
```
grep "\.identity()" index.html
grep "\.copy()" index.html | head -5
grep "THREE\.Quaternion" index.html
```
- Three.js r86 is OLD. `THREE.Quaternion.identity()` does NOT exist, use `.set(0,0,0,1)`.
- `.copy()` exists on r86 Quaternion, Vector3, etc. (fine).
- Any modern Three.js API must be verified against `js/three.js` before use.

### 4. Flyer version matches
```
grep "badge" flyer.html
```
- Version number should match the current `v=XX` in `index.html` version comment.

### 5. Server restart (if changing APIs)
```
# If serve.py or server_https.py changed:
python -c "import py_compile; py_compile.compile('serve.py', doraise=True)"
python -c "import py_compile; py_compile.compile('server_https.py', doraise=True)"
```

### 6. Visual smoke test
- Open `http://127.0.0.1:8080/index.html?v=XX` in browser.
- Confirm: orange cube visible in preview panel.
- Confirm: status bar text updates (not empty).
- Confirm: no console errors (F12).
- Confirm: webcam toggle works (not stuck).
- Confirm: floating preview drag/resize works.

## Common failure patterns (LEARNED THE HARD WAY)

| Symptom | Root cause | Check |
|---------|-----------|-------|
| Black preview + black AR | `initialize()` never closes → all functions undefined | Check brace count |
| Preview black but AR works | Third WebGL context killed preview canvas | `grep -c WebGLRenderer`, must be 2 |
| Preview never initializes | `isPhoneUI()` returned true on desktop | Check `shouldInitPreview()` |
| Model never loads on phone | `fetch` vs `FileLoader` path difference | Try FileLoader fallback first, then fetch+parse |
| Settings lost on reload | API miss → never hit `loadSettingsFromLocalStorage` | `loadSettings()` runs sync at boot now |

## Version history (recent)

| v | What changed |
|---|-------------|
| v=29 | CRITICAL: fixed qUp.identity() crash (not in r86). Rewrote GLB load to use fetch (survives WebGL context loss). |
| v=27-28 | CRITICAL: restructured boot — loadSettings() + initPreview() + showCube() run synchronously. loadSettingsAsync() is fire-and-forget. |
| v=26 | Honest status messages — label ≠ loaded until GLB is actually placed |
| v=25 | fetch+parse GLB for iOS reliability |
| v=24 | Always show cube on marker first, then swap GLB |
| v=23 | Persist settings to settings.json via /api/settings |
| v=22 | Live settings → AR, marker pad, lock status |
| v=21 | Double-click slider reset |
| v=20 | Drag-rotate CSS axis cube |
| v=17-19 | CSS cube, preview hardening, webcam error handling |
| v=15 | Floating resizable preview, webcam toggle |

## Agent handoff protocol

When handing off between sessions:
1. State current `v=XX` version.
2. List any unverified checklist items.
3. Note the last file edited and what changed.
4. If `initialize()` was touched, state explicitly whether brace count was verified.
