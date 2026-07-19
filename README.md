# MeWorld AR — Hello Cube (baseline)

Clean starting point for incremental AR work.

**What works on `master`:** Stemkoski smoothed-controls **hello cube** + Hiro marker flyer + the minimum AR.js stack.

**Previous work (crimson racer, GLB, touch UI, docs):** preserved on branch [`archive/v10-crimson-racer`](https://github.com/stefopps/ar-heart/tree/archive/v10-crimson-racer) — nothing deleted from git history.

## Live

https://stefopps.github.io/ar-heart/?v=11

## Local

```
python server.py
```

Or HTTPS for phone camera:

```
python server_https.py
```

(`server_https.py` lives on the archive branch; copy it over if needed, or use the local copy if present.)

Open flyer: `flyer.html`  
AR page: `index.html`

## Keep / grow from here

| Path | Role |
|------|------|
| `index.html` | AR hello cube (Stemkoski hierarchy) |
| `flyer.html` | Printable Hiro marker + QR |
| `hiro-marker.png` / `hiro_marker.png` | Marker image for flyer |
| `data/hiro.patt` + `data/camera_para.dat` | ARToolkit pattern + camera |
| `js/three.js` | three.js **r86** (matches Stemkoski) |
| `jsartoolkit5/` | ARToolkit runtime |
| `threex/` | Marker + smoothed controls |

## Incremental rule

Build one feature at a time on top of this cube. When you need old racer files:

```
git checkout archive/v10-crimson-racer -- models/ path/you/want
```

## Credits

- [stemkoski/AR-Examples](https://github.com/stemkoski/AR-Examples) — smoothed-controls hello cube  
- [jeromeetienne/AR.js](https://github.com/jeromeetienne/AR.js) / [AR-js-org/AR.js](https://github.com/AR-js-org/AR.js)
