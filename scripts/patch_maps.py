#!/usr/bin/env python3
"""Härtet den Foto-Filter in allen map_*.html-Dateien.

- Bump: _photoCacheVersion 2 → 3 (zwingt Clients, gecachte Fotos neu zu holen).
- Blacklist mit Generika-Patterns (Stadtpanoramen, Luftaufnahmen fremder Städte,
  berühmte Landmarks die häufig als Disambiguations-Fallback auftauchen).
- Kreuz-Kontamination verhindern (z. B. Matterhorn darf nicht Bild eines
  POIs in Deutschland sein).
"""

import os
import re
from pathlib import Path

ROOT = Path('/sessions/elegant-great-turing/mnt/Jahresguide')

FILES = [
    'map_belgien.html', 'map_bosnien.html', 'map_deutschland.html',
    'map_faeroeer.html', 'map_finnland.html', 'map_griechenland.html',
    'map_island.html', 'map_italien.html', 'map_japan.html',
    'map_kanada_ontario.html', 'map_kanada_ost.html', 'map_kanada_west.html',
    'map_kanada_zentral.html', 'map_katar.html', 'map_kroatien.html',
    'map_luxemburg.html', 'map_niederlande.html', 'map_norwegen.html',
    'map_oesterreich.html', 'map_polen.html', 'map_portugal.html',
    'map_schweden.html', 'map_slowakei.html', 'map_slowenien.html',
    'map_spanien.html', 'map_tschechien.html', 'map_vae.html',
    'map_zypern.html',
]

# Globale Blacklist: berühmte Landmarks / Stadtpanoramen, die bei Disambig-
# Fallbacks unpassend auftauchen. Klein gehalten und konservativ.
GLOBAL_BLACKLIST = '''
        // Bekannte Generika/Fremd-Landmarks — nicht als POI-Foto cachen.
        var _GENERIC_IMAGE_BLACKLIST = [
            // Kreuz-Kontamination: berühmte Landmarks dürfen nicht Fremd-POIs zieren
            'matterhorn_from_domh', 'bern_luftaufnahme', 'sphinx_et_jungfrau',
            'la_tour_eiffel_vue_de_la_tour_saint-jacques',
            'arc_de_triomphe%2c_paris', 'arc_de_triomphe_paris',
            'big_ben', 'london_panorama', 'tower_bridge_london',
            'colosseum_in_rome', 'piazza_san_marco',
            'brandenburger_tor_abends',
            // Aerial-Overviews (zu oft Disambig-Fallback)
            'altstadt_z%c3%bcrich_2015', 'altstadt_zurich_2015',
            'interlaken_aer', 'appenzell_2022', 'lugano_from_sighignola',
            's%c3%a4ntis_mountain_by_sunset', 'santis_mountain_by_sunset',
            'thun_be', 'solothurn_2023', 'luftbild_davos2',
            'place_stanislas_et_ses_grilles',
            'bordeaux_place_de_la_bourse_de_nuit',
            'sub%c3%a9_fountain%2c_reims', 'sube_fountain_reims',
            'grande_place%2c_bourse_du_travail_et_beffroi_lille_2',
            'grande_place_bourse_du_travail_et_beffroi_lille_2',
            'rouen_%2837903223574%29', 'rouen_37903223574',
            'montpellier_place_de_la_com%c3%a9die', 'montpellier_place_de_la_comedie',
            'montage_toulouse_3', 'montage_toulouse_2',
            'mont-saint-michel_vu_du_ciel'
        ];
'''

OLD_VERSION_RE = re.compile(
    r"(const _photoCacheVersion\s*=\s*)2(\s*;)"
)

OLD_FILTER_RE = re.compile(
    r"function _isMapOrBadImage\(url\) \{\s*"
    r"var lc = url\.toLowerCase\(\);\s*"
    r"return /karte\|wappen\|flag\|coat_of_arms\|logo\|map\[_\.\]\|locator\|location_in\|positionskarte\|relief_\|verwaltung\|blank\|icon\|symbol\|blason\|escudo\|stemma\|banner/i\.test\(lc\)\s*"
    r"\|\| lc\.endsWith\('\.svg'\) \|\| lc\.indexOf\('\.svg/'\) > -1\s*"
    r"\|\| lc\.endsWith\('\.tif'\) \|\| lc\.indexOf\('\.tif/'\) > -1;\s*"
    r"\}"
)

NEW_FILTER = '''function _isMapOrBadImage(url) {
            var lc = url.toLowerCase();
            if (/karte|wappen|flag|coat_of_arms|logo|map[_.]|locator|location_in|positionskarte|relief_|verwaltung|blank|icon|symbol|blason|escudo|stemma|banner/i.test(lc)) return true;
            if (lc.endsWith('.svg') || lc.indexOf('.svg/') > -1) return true;
            if (lc.endsWith('.tif') || lc.indexOf('.tif/') > -1) return true;
            for (var i = 0; i < _GENERIC_IMAGE_BLACKLIST.length; i++) {
                if (lc.indexOf(_GENERIC_IMAGE_BLACKLIST[i]) > -1) return true;
            }
            return false;
        }'''


def patch(path):
    content = path.read_text(encoding='utf-8')
    orig = content

    # Version bump
    new_content, n1 = OLD_VERSION_RE.subn(r"\g<1>3\g<2>", content)
    if n1 == 0:
        return f'SKIP (kein Version-Treffer): {path.name}'
    content = new_content

    # Blacklist + neuer Filter: vor altem Filter einfügen
    new_content, n2 = OLD_FILTER_RE.subn(
        GLOBAL_BLACKLIST.strip() + '\n        ' + NEW_FILTER,
        content,
    )
    if n2 == 0:
        return f'SKIP (kein Filter-Treffer): {path.name}'
    content = new_content

    path.write_text(content, encoding='utf-8')
    return f'OK: {path.name} (version bumped, filter erweitert)'


def main():
    for f in FILES:
        path = ROOT / f
        if not path.exists():
            print(f'MISSING: {f}')
            continue
        print(patch(path))


if __name__ == '__main__':
    main()
