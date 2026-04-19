#!/usr/bin/env python3
"""Fügt in jeder map_*.html einen loadBaselinePhotos()-IIFE ein,
der photos_<CC>.json lädt und in _photoCache mergt.

Wird nach dem Version-Check (`Object.keys(_photoCache).forEach(k => delete _photoCache[k]);`)
eingefügt, damit die Baseline den gerade geleerten Cache wieder befüllt.
Idempotent: wenn bereits vorhanden, wird übersprungen.
"""
import re
from pathlib import Path

ROOT = Path('/sessions/elegant-great-turing/mnt/Jahresguide')

# Zuordnung map_*.html → (Ländercode, localStorage-Suffix)
FILES = {
    'map_belgien.html': 'BE',
    'map_bosnien.html': 'BA',
    'map_deutschland.html': 'DE',
    'map_faeroeer.html': 'FO',
    'map_finnland.html': 'FI',
    'map_griechenland.html': 'GR',
    'map_island.html': 'IS',
    'map_italien.html': 'IT',
    'map_japan.html': 'JP',
    'map_kanada_ontario.html': 'CA_ON',
    'map_kanada_ost.html': 'CA_OST',
    'map_kanada_west.html': 'CA_WEST',
    'map_kanada_zentral.html': 'CA_ZEN',
    'map_katar.html': 'QA',
    'map_kroatien.html': 'HR',
    'map_luxemburg.html': 'LU',
    'map_niederlande.html': 'NL',
    'map_norwegen.html': 'NO',
    'map_oesterreich.html': 'AT',
    'map_polen.html': 'PL',
    'map_portugal.html': 'PT',
    'map_schweden.html': 'SE',
    'map_slowakei.html': 'SK',
    'map_slowenien.html': 'SI',
    'map_spanien.html': 'ES',
    'map_tschechien.html': 'CZ',
    'map_vae.html': 'AE',
    'map_zypern.html': 'CY',
}

MARKER_RE = re.compile(
    r"(Object\.keys\(_photoCache\)\.forEach\(k => delete _photoCache\[k\]\);\s*\n\s*\})",
)

TEMPLATE = """
        // Baseline-Fotos aus JSON laden (vorab von Wikipedia geholt)
        (function loadBaselinePhotos() {{
            fetch('photos_{cc}.json').then(function(r) {{ return r.ok ? r.json() : null; }}).then(function(data) {{
                if (!data || typeof data !== 'object') return;
                var loaded = 0;
                Object.keys(data).forEach(function(k) {{
                    if (!_photoCache[k]) {{ _photoCache[k] = data[k]; loaded++; }}
                }});
                if (loaded > 0) {{
                    try {{ localStorage.setItem('photoCache{cc}', JSON.stringify(_photoCache)); }} catch(e) {{}}
                    console.log('[Photos] ' + loaded + ' Baseline-Fotos geladen');
                    document.querySelectorAll('img[data-poi-photo]').forEach(function(img) {{
                        var pid = img.getAttribute('data-poi-photo');
                        if (_photoCache[pid] && img.src.indexOf('unsplash.com') > -1) {{ img.src = _photoCache[pid]; }}
                    }});
                }}
            }}).catch(function() {{}});
        }})();
"""


def patch(path, cc):
    content = path.read_text(encoding='utf-8')
    if f"fetch('photos_{cc}.json')" in content:
        return f'SKIP (bereits drin): {path.name}'

    insertion = TEMPLATE.format(cc=cc).strip('\n')
    new_content, n = MARKER_RE.subn(
        lambda m: m.group(1) + '\n\n        ' + insertion + '\n',
        content,
        count=1,
    )
    if n == 0:
        return f'FAIL (Marker nicht gefunden): {path.name}'
    path.write_text(new_content, encoding='utf-8')
    return f'OK: {path.name} (photos_{cc}.json-Loader eingefügt)'


def main():
    for fname, cc in FILES.items():
        path = ROOT / fname
        if not path.exists():
            print(f'MISSING: {fname}')
            continue
        print(patch(path, cc))


if __name__ == '__main__':
    main()
