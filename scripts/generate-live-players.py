#!/usr/bin/env python3
"""Генерирует «живых» PvP-игроков: аватары + энергия + MMR.

Запуск из docs/:
  python3 scripts/generate-live-players.py

Пишет:
  assets/live/player-XX.jpg
  assets/live-players.json
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "live"
JSON_PATH = ROOT / "assets" / "live-players.json"

NAMES = [
    "mira_roll", "sasha_cut", "dima_byte", "lina_glow", "artem_drop",
    "kate_wave", "ivan_clip", "yana_pulse", "igor_lab", "tina_mini",
    "pasha_frame", "olesya_neon", "mark_zero", "alina_hype", "kostya_reel",
    "vera_soft", "nikita_rush", "dasha_loop", "roma_spark", "nasty_beat",
]

STYLES = [
    "Рилс-шторм", "Мем-атака", "Чил-вайб", "Хайп-дроп", "Ночной стрим",
    "Кринж-баттл", "Флекс-режим", "Софт-контент", "Байт-челлендж", "Топ-клип",
]

SKINS = [
    (255, 224, 196), (255, 213, 170), (240, 190, 150), (210, 160, 120),
    (180, 130, 95), (140, 95, 70), (95, 70, 55),
]
HAIRS = [
    (30, 30, 35), (60, 40, 25), (120, 70, 30), (200, 160, 80),
    (40, 80, 140), (160, 60, 120), (20, 20, 20), (230, 90, 60),
]
BG_A = [
    (37, 99, 235), (190, 24, 93), (5, 150, 105), (124, 58, 237),
    (217, 119, 6), (8, 145, 178), (220, 38, 38), (67, 56, 202),
]
BG_B = [
    (15, 23, 42), (30, 10, 40), (6, 30, 25), (20, 10, 50),
    (40, 25, 8), (8, 30, 45), (40, 10, 15), (15, 15, 45),
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_avatar(seed: int, initials: str, size: int = 256) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (size, size))
    px = img.load()
    c1 = BG_A[seed % len(BG_A)]
    c2 = BG_B[(seed * 3) % len(BG_B)]
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            n = 0.08 * math.sin((x + seed) * 0.05) * math.cos((y - seed) * 0.04)
            px[x, y] = lerp(c1, c2, min(1, max(0, t + n)))

    draw = ImageDraw.Draw(img)
    skin = SKINS[seed % len(SKINS)]
    hair = HAIRS[(seed * 5) % len(HAIRS)]
    cx, cy = size // 2, size // 2 + 8
    # shoulders
    draw.ellipse([cx - 90, cy + 40, cx + 90, size + 40], fill=lerp(c1, (20, 20, 30), 0.4))
    # head
    draw.ellipse([cx - 58, cy - 70, cx + 58, cy + 50], fill=skin)
    # hair
    draw.ellipse([cx - 62, cy - 88, cx + 62, cy - 10], fill=hair)
    if seed % 2 == 0:
        draw.rectangle([cx - 62, cy - 40, cx + 62, cy - 8], fill=hair)
    # eyes
    eye_y = cy - 18
    draw.ellipse([cx - 28, eye_y, cx - 12, eye_y + 12], fill=(30, 30, 35))
    draw.ellipse([cx + 12, eye_y, cx + 28, eye_y + 12], fill=(30, 30, 35))
    draw.ellipse([cx - 24, eye_y + 2, cx - 18, eye_y + 8], fill=(240, 240, 255))
    draw.ellipse([cx + 16, eye_y + 2, cx + 22, eye_y + 8], fill=(240, 240, 255))
    # smile
    draw.arc([cx - 18, cy + 5, cx + 18, cy + 28], 20, 160, fill=(160, 80, 80), width=3)
    # ring
    draw.ellipse([6, 6, size - 7, size - 7], outline=(255, 255, 255), width=5)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    # initials badge
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    text = initials[:2].upper()
    bb = bd.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = size - tw - 22, size - th - 18
    bd.rounded_rectangle([bx - 10, by - 6, bx + tw + 10, by + th + 6], radius=12, fill=(15, 23, 42, 200))
    bd.text((bx, by), text, fill=(248, 250, 252, 255), font=font)
    img = Image.alpha_composite(img.convert("RGBA"), badge).convert("RGB")
    return img


def build_players(n: int = 16, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    names = NAMES[:]
    rng.shuffle(names)
    players = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(n):
        name = names[i % len(names)]
        if i >= len(names):
            name = f"{name}_{i}"
        handle = f"@{name}"
        initials = "".join(ch for ch in name if ch.isalpha())[:2] or "PL"
        photo_name = f"player-{i:02d}.jpg"
        avatar = make_avatar(seed + i * 97, initials)
        avatar.save(OUT_DIR / photo_name, "JPEG", quality=78, optimize=True)

        energy_max = rng.choice([3, 3, 4, 5])
        energy = rng.randint(0, energy_max)
        mmr = int(rng.gauss(1050, 180))
        mmr = max(700, min(1800, mmr))
        best = max(28, int(mmr / 10 + rng.randint(-15, 40)))
        subs = max(12, int((mmr - 600) * rng.uniform(0.4, 2.2)))
        players.append({
            "id": f"live_{i:02d}",
            "name": handle,
            "avatar": "😎",
            "photo": f"assets/live/{photo_name}",
            "style": rng.choice(STYLES),
            "subs": subs,
            "best": best,
            "mmr": mmr,
            "energy": energy,
            "energyMax": energy_max,
            "energyAt": 0,
            "live": True,
            "online": energy > 0 or rng.random() > 0.25,
        })
    return players


def main():
    players = build_players(16, seed=20260713)
    payload = {
        "version": 1,
        "generatedAt": "2026-07-13",
        "energyRegenMs": 90000,
        "players": players,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(players)} players → {JSON_PATH}")
    print(f"Avatars → {OUT_DIR}")


if __name__ == "__main__":
    main()
