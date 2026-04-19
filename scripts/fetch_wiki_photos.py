#!/usr/bin/env python3
"""Holt passende Wikipedia-Bilder für POIs aller Länder.

Strategie:
1. Kandidaten = POIs ohne Eintrag in photos_<CC>.json (nach Cleanup).
2. Für jeden Kandidaten mehrere Query-Varianten bauen (Name + Region / Name / Name + Location).
3. Wikipedia REST summary API hitten; lead image filtern.
4. Duplicate-Guard: dieselbe URL max 2× akzeptieren — sonst gilt sie als generisch.
5. Sprachpriorität pro Land (z. B. JP → ja+de+en, IT → it+de+en).
6. Respektvoll: korrektes User-Agent, parallel, batched.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import ssl
import argparse
import concurrent.futures
from collections import Counter

UA = (
    'JahresguidePhotoRefresher/1.0 '
    '(https://jahresguide.app; contact miroslav.mikulic@gmail.com) Python/3'
)

# Sprachpriorität pro Länder-Code: welche Wikipedias werden (in dieser
# Reihenfolge) abgefragt. "de" und "en" sind immer Fallback.
LANG_PRIO = {
    'CH': ['de', 'fr', 'it', 'en'],
    'FR': ['fr', 'de', 'en'],
    'DE': ['de', 'en'],
    'AT': ['de', 'en'],
    'IT': ['it', 'de', 'en'],
    'ES': ['es', 'de', 'en'],
    'PT': ['pt', 'de', 'en'],
    'GR': ['el', 'de', 'en'],
    'NL': ['nl', 'de', 'en'],
    'BE': ['nl', 'fr', 'de', 'en'],
    'LU': ['fr', 'de', 'lb', 'en'],
    'CZ': ['cs', 'de', 'en'],
    'SK': ['sk', 'de', 'en'],
    'PL': ['pl', 'de', 'en'],
    'HR': ['hr', 'de', 'en'],
    'SI': ['sl', 'de', 'en'],
    'BA': ['bs', 'hr', 'sr', 'de', 'en'],
    'NO': ['no', 'nb', 'de', 'en'],
    'SE': ['sv', 'de', 'en'],
    'FI': ['fi', 'de', 'en'],
    'IS': ['is', 'de', 'en'],
    'FO': ['fo', 'da', 'de', 'en'],
    'CY': ['el', 'de', 'en'],
    'JP': ['ja', 'de', 'en'],
    'QA': ['ar', 'de', 'en'],
    'AE': ['ar', 'de', 'en'],
    'CA_ON': ['en', 'fr', 'de'],
    'CA_OST': ['en', 'fr', 'de'],
    'CA_WEST': ['en', 'fr', 'de'],
    'CA_ZEN': ['en', 'fr', 'de'],
}

# Bekannte Generika: Bilder die zu viele Male im alten Datensatz auftauchten.
# Greift als letzter Filter direkt an der URL.
GENERIC_FILENAMES = {
    'bern_luftaufnahme', 'altstadt_zurich_2015', 'lugano_from_sighignola',
    'appenzell_2022', 'interlaken_aer', 'santis_mountain_by_sunset',
    'schaffhausen_mit_munot', '2009_08_24_06262_lucerne',
    'basel_-_munsterpfalz1', '1_zermatt_evening_2022',
    'blick_auf_die_winterthurer_altstadt', 'luftbild_davos2',
    'thun_be', 'solothurn_2023',
    'la_tour_eiffel_vue_de_la_tour_saint-jacques',
    'bordeaux_place_de_la_bourse_de_nuit',
    'place_stanislas_et_ses_grilles', 'subefountain_reims_france',
    'grande_place_bourse_du_travail_et_beffroi_lille_2',
    'rouen_37903223574', 'montpellier_place_de_la_comedie',
    'place_de_la_comedie_2377437375', 'montage_toulouse_3',
    'mont-saint-michel_vu_du_ciel',
    'switzerland_apr_2023_14_08_21_426000',
    'sphinx_et_jungfrau',
}

BAD_PATTERNS = re.compile(
    r'(karte|wappen|flag|coat_of_arms|logo|locator|positionskarte|'
    r'relief_|verwaltung|blank|icon|symbol|blason|escudo|stemma|banner|'
    r'coat-of-arms)',
    re.I,
)

SSL_CTX = ssl.create_default_context()


def normalize_filename(url):
    m = re.search(r'/commons/(?:thumb/)?(?:[^/]+/){0,2}([^/]+?)(?:/\d+px-|$)', url)
    if not m:
        return ''
    fn = urllib.parse.unquote(m.group(1))
    fn = re.sub(r'\.(jpg|jpeg|png|svg|tiff?)$', '', fn, flags=re.I)
    return fn.lower()


def is_bad_image(url):
    lc = url.lower()
    if BAD_PATTERNS.search(lc):
        return True
    if lc.endswith('.svg') or '.svg/' in lc:
        return True
    if lc.endswith('.tif') or '.tif/' in lc:
        return True
    fn = normalize_filename(url)
    if fn in GENERIC_FILENAMES:
        return True
    return False


def extract_photo(data):
    if not data:
        return None
    if data.get('type') == 'disambiguation':
        return None
    thumb = data.get('thumbnail', {}).get('source') or ''
    original = data.get('originalimage', {}).get('source') or ''
    src = thumb or original
    if not src:
        return None
    if is_bad_image(src):
        return None
    src = re.sub(r'/\d+px-', '/400px-', src)
    return src


SUFFIX_STOP = {
    'dorf', 'altstadt', 'schloss', 'kirche', 'kathedrale', 'munster',
    'münster', 'stadt', 'zentrum', 'wanderung', 'bergbahn', 'zahnradbahn',
    'bahn', 'staudamm', 'stausee', 'see', 'pass', 'schlucht',
    'wasserfalle', 'wasserfälle', 'wasserfall', 'gletscher', 'park',
    'garten', 'museum', 'ausstellung', 'konzert', 'festival', 'rundweg',
    'promenade', 'aussichtspunkt', 'platz', 'brucke', 'brücke', 'tal',
    'berg', 'alp', 'hutte', 'hütte', 'höhle', 'hohle', 'kloster',
    'chateau', 'eglise', 'abbaye', 'fontaine', 'musee', 'place',
    'quartier', 'pont', 'cathedrale', 'basilique', 'palais', 'jardin',
    'mountain', 'village', 'gorge', 'lake', 'valley', 'falls',
    'ort', 'skigebiet', 'paradies', 'world', 'erlebnis',
    'erlebniswelt', 'fahrt', 'schifffahrt',
    'castello', 'chiesa', 'duomo', 'piazza', 'basilica', 'palazzo',
    'museo', 'monte', 'lago', 'cascata', 'grotta',
    'castillo', 'iglesia', 'catedral', 'plaza', 'palacio',
    'mosteiro', 'igreja', 'mosteiro', 'praca',
    'kasteel', 'kerk', 'paleis',
    'hrad', 'kostel', 'zamek', 'zamok',
    'tempel', 'temple', 'shrine', 'jinja', 'tera',
}

STOP_WORDS_GLOBAL = {
    'der', 'die', 'das', 'und', 'von', 'in', 'im', 'zu', 'am', 'auf',
    'la', 'le', 'les', 'du', 'de', 'des', 'sur', 'et', 'aux', 'à',
    'mit', 'st', 'sankt', 'saint', 'of', 'the', 'and', 'il', 'lo',
    'gli', 'alla', 'nel', 'dello', 'della', 'da', 'dei', 'delle',
    'el', 'los', 'las', 'na', 've', 'za', 'do', 'al', 'den', 'het',
    'een', 'van',
}


def _meaningful_words(name):
    words = [w for w in name.split() if w and w.lower() not in STOP_WORDS_GLOBAL]
    return words


def build_queries(poi):
    name = poi['name'].replace('–', '-').replace('—', '-').strip()
    name_u = name.replace(' ', '_')
    name_hyphen = name.replace(' ', '-')
    loc = poi.get('location', '').replace(' ', '_')
    reg = poi.get('region', '').replace(' ', '_')

    words = _meaningful_words(name)
    head = words[0] if words else name
    core_candidates = [w for w in words if w.lower() not in SUFFIX_STOP]
    core = core_candidates[-1] if core_candidates else head

    queries = []
    if reg and len(reg) <= 4:
        queries.append(f'{name_u}_{reg}')
    queries.append(name_u)
    queries.append(name_hyphen)
    if core and loc and core.lower() not in loc.lower():
        queries.append(f'{core}_({loc})')
    if core and reg and len(reg) <= 4:
        queries.append(f'{core}_{reg}')
    if loc and loc != name_u:
        queries.append(f'{name_u}_({loc})')
        queries.append(f'{loc}_{name_u}')
    if core and core != name_u:
        queries.append(core)
    if head and head != core and head != name_u:
        queries.append(head)

    seen = set()
    return [q for q in queries if q and not (q in seen or seen.add(q))]


def wiki_search(lang, query, limit=3, timeout=6):
    """Fallback: Wikipedia-Volltextsuche, gibt Titel zurück."""
    url = (
        f'https://{lang}.wikipedia.org/w/api.php?action=query&format=json'
        f'&list=search&srsearch={urllib.parse.quote(query)}&srlimit={limit}'
    )
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            data = json.loads(r.read().decode('utf-8'))
            return [hit['title'].replace(' ', '_') for hit in data.get('query', {}).get('search', [])]
    except Exception:
        return []


def fetch_summary(lang, title, timeout=8):
    url = f'https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            if r.status == 200:
                return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError:
        pass
    except Exception:
        pass
    return None


def _check_summary_match(poi, data, min_overlap=1):
    """Verifiziert dass der Wikipedia-Artikel tatsächlich zum POI passt."""
    if not data:
        return False
    title = (data.get('title') or '').lower()
    extract = (data.get('extract') or '').lower()
    desc = (data.get('description') or '').lower()
    text = f'{title} {desc} {extract[:400]}'
    poi_words = {w.lower() for w in _meaningful_words(poi['name']) if len(w) >= 4}
    for w in _meaningful_words(poi.get('location', '')):
        if len(w) >= 4:
            poi_words.add(w.lower())
    if not poi_words:
        return True
    hits = sum(1 for w in poi_words if w in text)
    return hits >= min_overlap


def find_photo(poi, used_urls, langs):
    """Gibt URL zurück oder None."""
    queries = build_queries(poi)
    tried_titles = set()

    def _try(lang, title):
        key = f'{lang}:{title.lower()}'
        if key in tried_titles:
            return None
        tried_titles.add(key)
        data = fetch_summary(lang, title)
        if not data:
            return None
        if not _check_summary_match(poi, data):
            return None
        photo = extract_photo(data)
        if photo and used_urls[photo] < 2:
            return photo
        return None

    # Pro Sprache alle Query-Varianten durchgehen
    for lang in langs:
        for q in queries:
            found = _try(lang, q)
            if found:
                return found

    # Volltextsuche als Fallback (nur primäre Sprache + EN)
    fallback_langs = [langs[0]]
    if 'en' not in fallback_langs:
        fallback_langs.append('en')
    for lang in fallback_langs:
        search_q = poi['name']
        if poi.get('location') and poi['location'].lower() not in poi['name'].lower():
            search_q += ' ' + poi['location']
        titles = wiki_search(lang, search_q, limit=3)
        for t in titles:
            found = _try(lang, t)
            if found:
                return found
    return None


def process_batch(pois, used_urls, langs, max_workers=12):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_poi = {ex.submit(find_photo, p, used_urls, langs): p for p in pois}
        for fut in concurrent.futures.as_completed(future_to_poi):
            poi = future_to_poi[fut]
            try:
                url = fut.result()
            except Exception:
                url = None
            if url:
                results[str(poi['id'])] = url
                used_urls[url] += 1
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('country', help='Länder-Code, z. B. DE, IT, JP')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--only-worthy', action='store_true',
                    help='Nur sehenswuerdigkeit/kultur/weihnachten anfragen')
    args = ap.parse_args()

    cc = args.country
    langs = LANG_PRIO.get(cc, ['de', 'en'])
    pois_file = f'/sessions/elegant-great-turing/pois_{cc}.json'
    photos_file = f'/sessions/elegant-great-turing/mnt/Jahresguide/photos_{cc}.json'

    with open(pois_file) as f:
        pois = json.load(f)

    # Lade existierende photos_*.json falls vorhanden
    try:
        with open(photos_file) as f:
            photos = json.load(f)
    except FileNotFoundError:
        photos = {}

    existing_ids = {int(k) for k in photos.keys()}
    used_urls = Counter(photos.values())

    candidates = [p for p in pois if p['id'] not in existing_ids]

    # Wikipedia-würdige Kategorien priorisieren
    priority = {
        'sehenswuerdigkeit': 0, 'kultur': 1, 'weihnachten': 2,
        'festival': 3, 'volksfest': 4, 'familie': 5, 'sport': 6,
    }
    if args.only_worthy:
        candidates = [p for p in candidates if p['category'] in
                      ('sehenswuerdigkeit', 'kultur', 'weihnachten')]
    candidates.sort(key=lambda p: priority.get(p['category'], 10))

    if args.offset:
        candidates = candidates[args.offset:]
    if args.limit:
        candidates = candidates[:args.limit]

    print(f'[{cc}] {len(candidates)} POIs werden geprüft (Sprachen: {",".join(langs)})',
          flush=True)

    block = 50
    total_added = 0
    t0 = time.time()
    for i in range(0, len(candidates), block):
        chunk = candidates[i:i + block]
        new = process_batch(chunk, used_urls, langs, max_workers=args.workers)
        if new:
            photos.update(new)
            total_added += len(new)
            with open(photos_file, 'w', encoding='utf-8') as f:
                json.dump(photos, f, ensure_ascii=False, separators=(',', ':'))
        elapsed = time.time() - t0
        total_blocks = (len(candidates) + block - 1) // block
        print(f'  [{cc}] Block {i//block + 1}/{total_blocks}: '
              f'+{len(new)} (gesamt +{total_added}), {elapsed:.0f}s', flush=True)

    print(f'[{cc}] Fertig: +{total_added} Bilder, {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
