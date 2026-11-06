"""
Riduce le immagini di placeholder/ PRIMA della build web (solo nella copia
usata da GitHub Actions: le immagini originali nel repository non cambiano).
Nel gioco le immagini sono mostrate piccole: foto enormi rallentano il
caricamento e possono esaurire la memoria del browser.
"""
import os
import sys

from PIL import Image

ROOT = sys.argv[1] if len(sys.argv) > 1 else "placeholder"
MAX_SIDE = {"avatars": 512, "background": 1920, "level2_trascinamento": 1920}
DEFAULT_MAX = 800   # foto degli animali
EXTS = (".jpg", ".jpeg", ".png", ".webp")

before = after = 0
for dirpath, _, files in os.walk(ROOT):
    for name in files:
        if not name.lower().endswith(EXTS):
            continue
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        top = rel.split("/")[0]
        # sfondi del livello 2 (file direttamente nella cartella) piu' grandi
        is_scene = top == "level2_trascinamento" and rel.count("/") == 1
        limit = MAX_SIDE.get(top, DEFAULT_MAX) if (top != "level2_trascinamento" or is_scene) else DEFAULT_MAX
        before += os.path.getsize(path)
        with Image.open(path) as im:
            im.load()
            if max(im.size) > limit:
                im.thumbnail((limit, limit), Image.LANCZOS)
            if name.lower().endswith((".jpg", ".jpeg")):
                im.convert("RGB").save(path, quality=85, optimize=True)
            elif name.lower().endswith(".png"):
                im.save(path, optimize=True)
            else:
                im.save(path, quality=85)
        after += os.path.getsize(path)
print(f"Immagini: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")
