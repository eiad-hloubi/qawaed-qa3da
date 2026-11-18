#!/usr/bin/env python3
"""Embed قعدة brand assets into a single-file HTML qa3da.

Replaces these placeholders inside the HTML (each is optional):
  /*QA3DA_FONTS*/      -> @font-face rules (woff2 as base64) for Lalezar + the family font
  <!--QA3DA_SPRITE-->  -> the brand SVG sprite (chairs + frame icons as <symbol>s)
  <!--QA3DA_LOGO-->    -> the regular official logo SVG (text uses Lalezar; fill via currentColor)

Usage:
  python3 embed_assets.py <in.html> <out.html> --family self|plan|play|lamma

The output works offline: no external font or image requests.
"""
import argparse
import base64
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent / "assets"
FAMILY_FONTS = {
    "plan": ("Readex Pro", "readex-pro", [400, 700]),
    "play": ("Changa", "changa", [400, 600, 800]),
    "self": ("Alexandria", "alexandria", [400, 800]),
    "lamma": ("Marhey", "marhey", [400, 700]),
}
# Unicode ranges as published by fontsource
RANGES = {
    "arabic": "U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC,U+102E0-102FB,U+10E60-10E7E,U+10EC2-10EC4,U+10EFC-10EFF,U+1EE00-1EEFF",
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
}


def face(family, slug, weight):
    out = []
    for sub in ("arabic", "latin"):
        f = HERE / "fonts" / f"{slug}-{sub}-{weight}-normal.woff2"
        if not f.exists():
            continue
        b64 = base64.b64encode(f.read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');unicode-range:{RANGES[sub]}}}"
        )
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--family", required=True, choices=FAMILY_FONTS)
    a = ap.parse_args()
    html = pathlib.Path(a.src).read_text(encoding="utf-8")
    fam, slug, weights = FAMILY_FONTS[a.family]
    fonts = [face("Lalezar", "lalezar", 400)] + [face(fam, slug, w) for w in weights]
    html = html.replace("/*QA3DA_FONTS*/", "\n".join(fonts))
    sprite = (HERE / "brand-sprite.svg").read_text(encoding="utf-8")
    html = html.replace("<!--QA3DA_SPRITE-->", sprite)
    logo = (HERE / "logo.svg").read_text(encoding="utf-8")
    logo = re.sub(r'\swidth="\d+"\sheight="\d+"', ' height="100%"', logo, count=1)
    logo = logo.replace('fill="#1C1A17">قـ', 'fill="currentColor">قـ')
    html = html.replace("<!--QA3DA_LOGO-->", logo)
    left = [p for p in ("/*QA3DA_FONTS*/", "<!--QA3DA_SPRITE-->", "<!--QA3DA_LOGO-->") if p in html]
    pathlib.Path(a.dst).write_text(html, encoding="utf-8")
    kb = len(html.encode()) // 1024
    print(f"wrote {a.dst} ({kb} KB), family font: {fam}" + (f"; unreplaced: {left}" if left else ""))


if __name__ == "__main__":
    sys.exit(main())
