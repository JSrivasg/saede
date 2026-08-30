#!/usr/bin/env python3
"""
Regenerate every image in assets/img/ from the originals.

    python3 tools/images.py

Point SOURCES at your master files and run it. Each entry says where the
original lives, what to crop away, and which widths to produce.

The crop boxes matter: several of these originals are phone screenshots, and
the app's own buttons sit ON the photograph, not just in a status bar above
it. Cropping to the visible photo edge is not enough — check the output.

Requires Pillow (already installed):  python3 -m pip install Pillow
"""
import os
import sys

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Pillow is needed: python3 -m pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
DL = os.path.expanduser("~/Downloads")

SOURCES = [
    {
        "name": "the front page water, wide crop for desktop",
        "src": os.path.join(DL, "IMG_4730.PNG"),
        # a band across the middle: clear of the app's buttons top and bottom
        "crop": (20, 172, 1300, 2090),
        "band": (0.30, 16 / 9),      # take a 16:9 band starting 30% down
        "out": "hero-water-wide-%d.jpg",
        "widths": [1600, 2200],
        "quality": 80,
        "sharpen": True,             # enlarged, so a light unsharp pass helps
    },
    {
        "name": "the front page water, tall crop for phones",
        "src": os.path.join(DL, "IMG_4730.PNG"),
        # tighter box: the first crop left Instagram's back arrow, menu and
        # search button in frame, because they float over the photo itself
        "crop": (22, 400, 1298, 1935),
        "out": "hero-water-%d.jpg",
        "widths": [800, 1280],
        "quality": 80,
    },
    {
        "name": "the duo on cream",
        "src": os.path.join(DL, "IMG_9641.PNG"),
        "out": "duo-cream-%d.jpg",
        "widths": [900, 1400, 2000],
        "quality": 82,
    },
    {
        "name": "the duo on silk",
        "src": os.path.join(DL, "A3C93E31-C06A-427A-9794-4B95A293BAD1.PNG"),
        "out": "duo-silk-%d.jpg",
        "widths": [900, 1400],
        "quality": 82,
    },
    {
        "name": "clouds, closing the story page",
        "src": os.path.join(DL, "CCDBE760-67A2-4916-97B8-C58044125B26.PNG"),
        "out": "clouds-%d.jpg",
        "widths": [1200],
        "quality": 78,
    },
]


def build(spec):
    if not os.path.exists(spec["src"]):
        print("  ! missing, skipped: %s" % spec["src"])
        return
    im = Image.open(spec["src"])
    if spec.get("crop"):
        im = im.crop(spec["crop"])
    if spec.get("band"):
        start, ratio = spec["band"]
        h = round(im.width / ratio)
        top = round(im.height * start)
        im = im.crop((0, top, im.width, min(top + h, im.height)))
    im = im.convert("RGB")

    for w in spec["widths"]:
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        if spec.get("sharpen") and w > im.width:
            r = r.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))
        path = os.path.join(OUT, spec["out"] % w)
        r.save(path, "JPEG", quality=spec.get("quality", 80),
               optimize=True, progressive=True)
        print("    %-30s %4dx%-4d %4d KB" % (
            os.path.basename(path), w, h, os.path.getsize(path) // 1024))


def main():
    os.makedirs(OUT, exist_ok=True)
    for spec in SOURCES:
        print("  " + spec["name"])
        build(spec)
    print("\nDone. Run python3 build.py to pick the new files up.")


if __name__ == "__main__":
    main()
