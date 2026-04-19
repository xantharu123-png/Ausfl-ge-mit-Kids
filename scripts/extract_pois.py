#!/usr/bin/env python3
"""Extrahiert POI-Daten aus den map_*.html-Dateien in pois_<CC>.json.

Das JS-Objektformat ist {id:1,name:"X",...} — also kein valides JSON.
Wir zerlegen es Zeile für Zeile in der `const allPOIs = [...]`-Region.
"""

import json
import re
from pathlib import Path

ROOT = Path('/sessions/elegant-great-turing/mnt/Jahresguide')
OUT = Path('/sessions/elegant-great-turing')

# (Dateiname, Ländercode)
FILES = [
    ('map_belgien.html', 'BE'),
    ('map_bosnien.html', 'BA'),
    ('map_deutschland.html', 'DE'),
    ('map_faeroeer.html', 'FO'),
    ('map_finnland.html', 'FI'),
    ('map_griechenland.html', 'GR'),
    ('map_island.html', 'IS'),
    ('map_italien.html', 'IT'),
    ('map_japan.html', 'JP'),
    ('map_kanada_ontario.html', 'CA_ON'),
    ('map_kanada_ost.html', 'CA_OST'),
    ('map_kanada_west.html', 'CA_WEST'),
    ('map_kanada_zentral.html', 'CA_ZEN'),
    ('map_katar.html', 'QA'),
    ('map_kroatien.html', 'HR'),
    ('map_luxemburg.html', 'LU'),
    ('map_niederlande.html', 'NL'),
    ('map_norwegen.html', 'NO'),
    ('map_oesterreich.html', 'AT'),
    ('map_polen.html', 'PL'),
    ('map_portugal.html', 'PT'),
    ('map_schweden.html', 'SE'),
    ('map_slowakei.html', 'SK'),
    ('map_slowenien.html', 'SI'),
    ('map_spanien.html', 'ES'),
    ('map_tschechien.html', 'CZ'),
    ('map_vae.html', 'AE'),
    ('map_zypern.html', 'CY'),
]

# Feld-Extraktoren
FIELD_STR = re.compile(r'(\w+):\s*"((?:[^"\\]|\\.)*)"')
FIELD_NUM = re.compile(r'(\w+):\s*(-?\d+(?:\.\d+)?)')


def parse_poi_line(line):
    """Parst eine einzelne Zeile im Format {id:N,name:"X",...}"""
    if '{id:' not in line:
        return None
    m = re.search(r'\{(id:[^}]*)\}', line)
    if not m:
        return None
    body = m.group(1)
    poi = {}
    for k, v in FIELD_STR.findall(body):
        poi[k] = v.replace('\\"', '"')
    for k, v in FIELD_NUM.findall(body):
        if k in poi:
            continue
        poi[k] = float(v) if '.' in v else int(v)
    return poi if 'id' in poi and 'name' in poi else None


def extract(html_path):
    content = html_path.read_text(encoding='utf-8')
    # Region: allPOIs = [ ... ]
    m = re.search(r'const\s+allPOIs\s*=\s*\[(.*?)\n\];', content, re.S)
    if not m:
        # Fallback: var / let
        m = re.search(r'(?:var|let|const)\s+allPOIs\s*=\s*\[(.*?)\];', content, re.S)
    if not m:
        return []
    body = m.group(1)
    pois = []
    for line in body.split('\n'):
        poi = parse_poi_line(line)
        if poi:
            pois.append(poi)
    return pois


def main():
    total = 0
    for fname, cc in FILES:
        path = ROOT / fname
        if not path.exists():
            print(f'MISSING: {fname}')
            continue
        pois = extract(path)
        out = OUT / f'pois_{cc}.json'
        with out.open('w', encoding='utf-8') as f:
            json.dump(pois, f, ensure_ascii=False, indent=2)
        print(f'{cc:6s}: {len(pois):4d} POIs aus {fname}')
        total += len(pois)
    print(f'\nGesamt: {total} POIs')


if __name__ == '__main__':
    main()
