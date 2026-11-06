"""Extrait des sprites séparés d'une planche générée sur fond vert, et fabrique un aperçu de formation.

Usage :
    python3 -I extraire_sprites.py PLANCHE.png DOSSIER_SORTIE [--prefixe nom] [--hauteur 34] [--formation]

- Retire le fond vert (#00FF00) avec un bord doux et supprime le reflet vert.
- Découpe chaque sprite séparé par du vert (aucune ligne droite à travers un sujet).
- N'étire jamais l'image : les sprites gardent leur résolution d'origine.
- Avec --formation, assemble un aperçu (formation serrée et lâche) à la hauteur donnée, variantes mélangées et retournées en miroir.
"""
import argparse
import os
import random

import numpy as np
from PIL import Image


def detourer(chemin):
    im = np.asarray(Image.open(chemin).convert("RGB")).astype(np.float32)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    alpha = np.clip(1 - ((g - np.maximum(r, b)) - 30) / 50, 0, 1)
    g2 = np.minimum(g, np.maximum(r, b) * 1.03)
    rgba = np.dstack([r, g2, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA"), alpha > 0.5


def plages(profil, seuil, ecart_min):
    actif = profil > seuil
    out, debut = [], None
    for i, v in enumerate(actif):
        if v and debut is None:
            debut = i
        if not v and debut is not None:
            if out and debut - out[-1][1] < ecart_min:
                out[-1] = (out[-1][0], i)
            else:
                out.append((debut, i))
            debut = None
    if debut is not None:
        out.append((debut, len(actif)))
    return [o for o in out if o[1] - o[0] > 20]


def extraire(chemin):
    img, masque = detourer(chemin)
    sprites = []
    for y0, y1 in plages(masque.sum(1), 2, 15):
        for x0, x1 in plages(masque[y0:y1].sum(0), 1, 12):
            yy, xx = np.where(masque[y0:y1, x0:x1])
            sprites.append(img.crop((x0 + xx.min() - 2, y0 + yy.min() - 2,
                                     x0 + xx.max() + 3, y0 + yy.max() + 3)))
    return sprites


def formation(sprites, hauteur, colonnes, rangs, dx, dy, alea, graine=3):
    random.seed(graine)
    variantes = [s.resize((max(1, round(s.width * hauteur / s.height)), hauteur), Image.LANCZOS) for s in sprites]
    variantes += [v.transpose(Image.FLIP_LEFT_RIGHT) for v in variantes]
    fond = Image.new("RGBA", (colonnes * dx + 60, rangs * dy + 60), (95, 125, 62, 255))
    for j in range(rangs):
        for i in range(colonnes):
            v = random.choice(variantes)
            fond.alpha_composite(v, (30 + i * dx + random.randint(-alea, alea), 30 + j * dy + random.randint(-alea, alea)))
    return fond


def main():
    p = argparse.ArgumentParser()
    p.add_argument("planche")
    p.add_argument("sortie")
    p.add_argument("--prefixe", default="sprite")
    p.add_argument("--hauteur", type=int, default=34)
    p.add_argument("--formation", action="store_true")
    a = p.parse_args()
    os.makedirs(a.sortie, exist_ok=True)
    sprites = extraire(a.planche)
    for i, s in enumerate(sprites, 1):
        s.save(os.path.join(a.sortie, f"{a.prefixe}_{i:02d}.png"))
    print(f"{len(sprites)} sprites extraits :", [s.size for s in sprites])
    if a.formation and sprites:
        h = a.hauteur
        serre = formation(sprites, h, 10, 5, int(h * 0.47), int(h * 0.76), 1)
        lache = formation(sprites, h, 10, 5, int(h * 0.7), int(h * 1.06), 3)
        apercu = Image.new("RGBA", (serre.width + lache.width + 30, max(serre.height, lache.height)), (95, 125, 62, 255))
        apercu.alpha_composite(serre, (0, 0))
        apercu.alpha_composite(lache, (serre.width + 30, 0))
        apercu = apercu.convert("RGB").resize((apercu.width * 2, apercu.height * 2), Image.NEAREST)
        chemin = os.path.join(a.sortie, f"{a.prefixe}_formation.png")
        apercu.save(chemin)
        print("Aperçu de formation :", chemin)


if __name__ == "__main__":
    main()
