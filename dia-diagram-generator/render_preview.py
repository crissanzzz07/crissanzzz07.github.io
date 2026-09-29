#!/usr/bin/env python3
"""Renderiza un .dia a PNG con Dia (headless) y recorta el margen blanco.
Requiere: dia, xvfb-run, Pillow.   Uso: render_preview.py in.dia out.png"""
import subprocess, sys
from PIL import Image, ImageChops
src, out = sys.argv[1:3]
subprocess.run(["xvfb-run", "-a", "dia", "--nosplash", "-t", "png", "-e", out, src], capture_output=True, check=True)
im = Image.open(out).convert("RGB")
box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
if box:
    m = 20
    im.crop((max(box[0]-m, 0), max(box[1]-m, 0), min(box[2]+m, im.width), min(box[3]+m, im.height))).save(out)
print(Image.open(out).size)
