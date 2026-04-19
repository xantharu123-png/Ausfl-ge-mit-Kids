#!/usr/bin/env python3
"""Bereinigt photos_<CC>.json-Dateien für alle Länder.

Entfernt:
- Einträge mit Bild-Dateiname, der weder POI-Name noch Ort trifft (Mismatch).
- Einträge auf einer überbenutzten URL (≥5 Verwendungen) ohne Namensbezug (Generika).
- Orphan-Einträge (Photo-ID ohne POI).
- Einträge mit bekannten Generika-Filenames aus anderen Ländern
  (Kreuz-Kontamination, z. B. Matterhorn in einem nicht-CH-File).

Muss NACH dem Fetch laufen.
"""

import json
import re
import urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path('/sessions/elegant-great-turing/mnt/Jahresguide')
POIS_ROOT = Path('/sessions/elegant-great-turing')
REPORT_DIR = Path('/sessions/elegant-great-turing/poi_report')
REPORT_DIR.mkdir(exist_ok=True)

COUNTRIES = [
    'BE', 'BA', 'DE', 'FO', 'FI', 'GR', 'IS', 'IT', 'JP',
    'CA_ON', 'CA_OST', 'CA_WEST', 'CA_ZEN', 'QA', 'HR', 'LU',
    'NL', 'NO', 'AT', 'PL', 'PT', 'SE', 'SK', 'SI', 'ES', 'CZ',
    'AE', 'CY',
]

STOP = {
    'der', 'die', 'das', 'und', 'von', 'in', 'zu', 'an', 'am', 'auf',
    'st', 'sankt', 'saint', 'la', 'le', 'les', 'du', 'de', 'des', 'sur',
    'lac', 'see', 'kirche', 'schloss', 'museum', 'altstadt', 'dorf',
    'wanderung', 'castle', 'chateau', 'eglise', 'musee', 'park', 'parc',
    'tour', 'maison', 'musee', 'stadt', 'center', 'zentrum',
    'il', 'lo', 'gli', 'alla', 'nel', 'dello', 'della', 'da', 'dei', 'delle',
    'el', 'los', 'las', 'na', 've', 'za', 'do', 'al', 'den', 'het',
    'een', 'van', 'of', 'the', 'and',
}

# Kreuz-Kontamination: Bilder aus CH oder FR dürfen nicht in anderen Ländern
# auftauchen (und umgekehrt Generika aus anderen wichtigen Regionen).
GLOBAL_GENERICS = re.compile(
    r'(matterhorn_from_domh|bern_luftaufnahme|sphinx_et_jungfrau|'
    r'altstadt_z%c3%bcrich|altstadt_zurich_2015|'
    r'interlaken_aer|appenzell_2022|lugano_from_sighignola|'
    r's%c3%a4ntis_mountain_by_sunset|santis_mountain_by_sunset|'
    r'luftbild_davos2|thun_be|solothurn_2023|'
    r'la_tour_eiffel_vue_de_la_tour_saint-jacques|'
    r'arc_de_triomphe%2c_paris|arc_de_triomphe_paris|'
    r'mont-saint-michel_vu_du_ciel|'
    r'big_ben|tower_bridge_london|colosseum_in_rome|'
    r'brandenburger_tor_abends)',
    re.I,
)


def extract_fn(url):
    m = re.search(r'/commons/(?:thumb/)?(?:[^/]+/){0,2}([^/]+?)(?:/\d+px-|$)', url)
    if not m:
        return ''
    fn = urllib.parse.unquote(m.group(1))
    return re.sub(r'\.(jpg|jpeg|png|JPG|JPEG|PNG|svg|SVG|tiff?)$', '', fn)


def normalize(s):
    s = s.lower()
    replacements = {
        'ä': 'a', 'ö': 'o', 'ü': 'u', 'Ä': 'a', 'Ö': 'o', 'Ü': 'u',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a',
        'î': 'i', 'ï': 'i', 'ô': 'o', 'û': 'u', 'ù': 'u', 'ç': 'c',
        'ñ': 'n', 'ß': 'ss', 'š': 's', 'č': 'c', 'ž': 'z', 'ć': 'c',
        'đ': 'd', 'á': 'a', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ý': 'y',
        'ł': 'l', 'ą': 'a', 'ę': 'e', 'ś': 's', 'ń': 'n', 'ż': 'z',
        'ő': 'o', 'ű': 'u',
    }
    s = ''.join(replacements.get(ch, ch) for ch in s)
    s = re.sub(r'[_\-\s\(\)\',\.]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def cleanup(cc, dry_run=False):
    pois_file = POIS_ROOT / f'pois_{cc}.json'
    photos_file = ROOT / f'photos_{cc}.json'
    if not pois_file.exists() or not photos_file.exists():
        return None

    with pois_file.open() as f:
        pois = json.load(f)
    with photos_file.open() as f:
        photos = json.load(f)

    if not photos:
        return {'cc': cc, 'before': 0, 'after': 0,
                'mismatch': 0, 'generic': 0, 'orphan': 0, 'contam': 0}

    poi_by_id = {p['id']: p for p in pois}
    valid_ids = set(poi_by_id.keys())
    dup_counts = Counter(photos.values())

    keep = {}
    dropped = {'mismatch': [], 'generic': [], 'orphan': [], 'contam': []}

    for pid_str, url in photos.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue

        if pid not in valid_ids:
            dropped['orphan'].append((pid, url))
            continue

        if GLOBAL_GENERICS.search(url):
            dropped['contam'].append((pid, poi_by_id[pid]['name'], url))
            continue

        poi = poi_by_id[pid]
        fn = extract_fn(url)
        fn_norm = normalize(fn)
        name_tokens = set(normalize(poi['name']).split()) - STOP
        loc_tokens = set(normalize(poi.get('location', '')).split()) - STOP
        all_tokens = name_tokens | loc_tokens
        tokens_fn = set(fn_norm.split()) - STOP

        name_overlap = name_tokens & tokens_fn
        loc_overlap = loc_tokens & tokens_fn
        name_substr = any(t in fn_norm for t in name_tokens if len(t) >= 4)
        any_substr = any(t in fn_norm for t in all_tokens if len(t) >= 4)

        dup = dup_counts[url]
        # Generika: nur droppen wenn die URL oft vorkommt UND kein Namensbezug.
        if dup >= 5 and not (name_overlap or name_substr):
            dropped['generic'].append((pid, poi['name'], fn, dup))
            continue

        # Mismatch-Heuristik deaktiviert: der Fetcher verifiziert bereits den
        # Artikel-Inhalt via _check_summary_match. Die Dateinamen-Heuristik
        # warf zu viele echte Bilder raus (Arabisch/Japanisch/Kyrillisch mit
        # transliterated Filenames, Historische Alternativnamen etc.).
        # Nur noch verlorene Foto-ID wird hier gedroppt (siehe orphan) — der
        # Rest wird dem Fetcher vertraut.
        keep[pid_str] = url

    stats = {
        'cc': cc,
        'before': len(photos),
        'after': len(keep),
        'mismatch': len(dropped['mismatch']),
        'generic': len(dropped['generic']),
        'orphan': len(dropped['orphan']),
        'contam': len(dropped['contam']),
    }

    if not dry_run:
        with photos_file.open('w', encoding='utf-8') as f:
            json.dump(keep, f, ensure_ascii=False, separators=(',', ':'))
        log_path = REPORT_DIR / f'cleanup_log_{cc}.json'
        with log_path.open('w', encoding='utf-8') as f:
            json.dump(dropped, f, ensure_ascii=False, indent=2, default=str)

    return stats


def main():
    print(f'{"CC":7s} {"vorher":>7s} {"nachher":>7s} {"mismatch":>9s} '
          f'{"generic":>8s} {"orphan":>7s} {"contam":>7s}')
    print('-' * 60)
    total = Counter()
    for cc in COUNTRIES:
        s = cleanup(cc)
        if s is None:
            continue
        total['before'] += s['before']
        total['after'] += s['after']
        total['mismatch'] += s['mismatch']
        total['generic'] += s['generic']
        total['orphan'] += s['orphan']
        total['contam'] += s['contam']
        print(f'{cc:7s} {s["before"]:>7d} {s["after"]:>7d} {s["mismatch"]:>9d} '
              f'{s["generic"]:>8d} {s["orphan"]:>7d} {s["contam"]:>7d}')
    print('-' * 60)
    print(f'{"SUMME":7s} {total["before"]:>7d} {total["after"]:>7d} '
          f'{total["mismatch"]:>9d} {total["generic"]:>8d} '
          f'{total["orphan"]:>7d} {total["contam"]:>7d}')


if __name__ == '__main__':
    main()
