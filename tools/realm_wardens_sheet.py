#!/usr/bin/env python3
"""Compose contact sheets of generated Realm Wardens concepts for quick review."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "docs", "realm-wardens", "manifest.json")
STATE = os.path.join(ROOT, "docs", "realm-wardens", "state.json")
OUT = os.path.join(ROOT, "docs", "realm-wardens")
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

CELL = 220
PAD = 6
LABEL_H = 22
COLS = 6


def main():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    groups = {}
    for a in man["assets"]:
        path = st.get(f"concept:{a['id']}", {}).get("path")
        if not path:
            continue
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue
        groups.setdefault(a["group"], []).append((a["id"], full))
    try:
        font = ImageFont.truetype(FONT_PATH, 15)
    except Exception:
        font = ImageFont.load_default()
    for group, items in groups.items():
        rows = (len(items) + COLS - 1) // COLS
        w = COLS * (CELL + PAD) + PAD
        h = rows * (CELL + LABEL_H + PAD) + PAD
        sheet = Image.new("RGB", (w, h), (24, 24, 28))
        draw = ImageDraw.Draw(sheet)
        for i, (aid, full) in enumerate(items):
            r, c = divmod(i, COLS)
            x = PAD + c * (CELL + PAD)
            y = PAD + r * (CELL + LABEL_H + PAD)
            try:
                im = Image.open(full).convert("RGB")
                im.thumbnail((CELL, CELL), Image.LANCZOS)
                sheet.paste(im, (x + (CELL - im.width) // 2, y))
            except Exception:
                pass
            draw.text((x + 2, y + CELL + 3), aid, fill=(230, 230, 235), font=font)
        out = os.path.join(OUT, f"sheet_{group}.png")
        sheet.save(out)
        print(f"{group}: {len(items)} -> {out}")


if __name__ == "__main__":
    main()
