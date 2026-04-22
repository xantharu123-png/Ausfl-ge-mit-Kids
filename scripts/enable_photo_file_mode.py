#!/usr/bin/env python3
"""Make POI photo baselines work even when maps are opened via file://.

This script does three things for every country map and the CH index map:
1. Generates `photos_<CC>.js` from the existing `photos_<CC>.json`.
2. Injects that JS file before the main inline script.
3. Replaces the baseline loader so it prefers the JS baseline and falls back
   to JSON `fetch(...)` when served over HTTP(S).

It also bumps `_photoCacheVersion` to force clients to drop stale bad caches.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

HTML_TO_CC = {
    "index.html": "CH",
    "map_belgien.html": "BE",
    "map_bosnien.html": "BA",
    "map_deutschland.html": "DE",
    "map_faeroeer.html": "FO",
    "map_finnland.html": "FI",
    "map_frankreich.html": "FR",
    "map_griechenland.html": "GR",
    "map_island.html": "IS",
    "map_italien.html": "IT",
    "map_japan.html": "JP",
    "map_kanada_ontario.html": "CA_ON",
    "map_kanada_ost.html": "CA_OST",
    "map_kanada_west.html": "CA_WEST",
    "map_kanada_zentral.html": "CA_ZEN",
    "map_katar.html": "QA",
    "map_kroatien.html": "HR",
    "map_luxemburg.html": "LU",
    "map_niederlande.html": "NL",
    "map_norwegen.html": "NO",
    "map_oesterreich.html": "AT",
    "map_polen.html": "PL",
    "map_portugal.html": "PT",
    "map_schweden.html": "SE",
    "map_slowakei.html": "SK",
    "map_slowenien.html": "SI",
    "map_spanien.html": "ES",
    "map_tschechien.html": "CZ",
    "map_vae.html": "AE",
    "map_zypern.html": "CY",
}

MAIN_SCRIPT_RE = re.compile(
    r'(<script src="https://unpkg\.com/leaflet\.markercluster@1\.5\.3/dist/leaflet\.markercluster\.js"></script>\s*)<script>'
)

LOADER_RE = re.compile(
    r"""
        [ \t]*//\s+Baseline-Fotos\s+aus\s+JSON\s+laden\s+\(vorab\s+von\s+Wikipedia\s+geholt\)\s*
        \(function\s+loadBaselinePhotos\(\)\s*\{
        .*?
        \}\)\(\);
        \s*
    """,
    re.DOTALL | re.VERBOSE,
)

VERSION_RE = re.compile(r"(const _photoCacheVersion\s*=\s*)(\d+)")

LOADER_TEMPLATE = """        // Baseline-Fotos aus JS oder JSON laden (funktioniert auch bei file://)
        (function loadBaselinePhotos() {{
            function applyBaseline(data) {{
                if (!data || typeof data !== 'object') return;
                var loaded = 0;
                Object.keys(data).forEach(function(k) {{
                    var prev = _photoCache[k];
                    if (prev !== data[k]) {{
                        _photoCache[k] = data[k];
                        loaded++;
                    }}
                }});
                if (loaded > 0) {{
                    try {{ localStorage.setItem('photoCache{storage_cc}', JSON.stringify(_photoCache)); }} catch(e) {{}}
                    console.log('[Photos] ' + loaded + ' Baseline-Fotos geladen');
                    document.querySelectorAll('img[data-poi-photo]').forEach(function(img) {{
                        var pid = img.getAttribute('data-poi-photo');
                        if (_photoCache[pid] && img.src !== _photoCache[pid]) {{
                            img.src = _photoCache[pid];
                        }}
                    }});
                }}
            }}

            var globalPhotos = (window.__PHOTO_BASELINE__ && window.__PHOTO_BASELINE__['{cc}']) || null;
            if (globalPhotos && typeof globalPhotos === 'object') {{
                applyBaseline(globalPhotos);
                return;
            }}

            fetch('photos_{cc}.json')
                .then(function(r) {{ return r.ok ? r.json() : null; }})
                .then(applyBaseline)
                .catch(function(err) {{
                    console.warn('[Photos] Baseline konnte nicht geladen werden:', err);
                }});
        }})();
"""


def generate_js_baseline(cc: str) -> None:
    json_path = ROOT / f"photos_{cc}.json"
    js_path = ROOT / f"photos_{cc}.js"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js_path.write_text(
        "window.__PHOTO_BASELINE__ = window.__PHOTO_BASELINE__ || {};\n"
        f"window.__PHOTO_BASELINE__['{cc}'] = {payload};\n",
        encoding="utf-8",
    )


def patch_html(html_name: str, cc: str) -> str:
    path = ROOT / html_name
    content = path.read_text(encoding="utf-8")
    original = content

    script_tag = f'<script src="photos_{cc}.js"></script>\n'
    if script_tag not in content:
        content, count = MAIN_SCRIPT_RE.subn(rf"\1{script_tag}<script>", content, count=1)
        if count == 0:
            return f"FAIL script-insert: {html_name}"

    already_patched = f"window.__PHOTO_BASELINE__ && window.__PHOTO_BASELINE__['{cc}']" in content
    if not already_patched:
        loader_block = LOADER_TEMPLATE.format(cc=cc, storage_cc=cc)
        content, count = LOADER_RE.subn(loader_block + "\n        ", content, count=1)
        if count == 0:
            return f"FAIL loader-replace: {html_name}"

    def bump_version(match: re.Match[str]) -> str:
        return match.group(1) + "6"

    content, count = VERSION_RE.subn(bump_version, content, count=1)
    if count == 0:
        return f"FAIL version-bump: {html_name}"

    if content != original:
        path.write_text(content, encoding="utf-8")
        return f"OK: {html_name}"
    return f"SKIP: {html_name}"


def main() -> None:
    for html_name, cc in HTML_TO_CC.items():
        generate_js_baseline(cc)
        print(patch_html(html_name, cc))


if __name__ == "__main__":
    main()
