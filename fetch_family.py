#!/usr/bin/env python3
"""
Fetch family-friendly places from OpenStreetMap Overpass API and save as JSON files.
These JSON files are loaded by the HTML maps as pre-loaded family places.

Usage:
    python3 fetch_family.py
    python3 fetch_family.py --file map_italien.html
    python3 fetch_family.py --country CH

FREE - no API key needed! Uses OpenStreetMap Overpass API.
"""

import json, os, re, sys, time, glob
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests --quiet")
    import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Country bounding boxes [south, west, north, east]
COUNTRY_BOUNDS = {
    'CH': [45.82, 5.95, 47.81, 10.49],     # Schweiz
    'DE': [47.27, 5.87, 55.06, 15.04],      # Deutschland
    'AT': [46.37, 9.53, 49.02, 17.16],      # Österreich
    'IT': [36.65, 6.63, 47.09, 18.52],      # Italien
    'FR': [41.36, -5.14, 51.09, 9.56],      # Frankreich
    'ES': [36.00, -9.30, 43.79, 3.33],      # Spanien
    'PT': [36.96, -9.50, 42.15, -6.19],     # Portugal
    'NL': [50.75, 3.36, 53.47, 7.21],       # Niederlande
    'BE': [49.50, 2.54, 51.50, 6.41],       # Belgien
    'LU': [49.45, 5.73, 50.18, 6.53],       # Luxemburg
    'GR': [34.80, 19.37, 41.75, 29.65],     # Griechenland
    'HR': [42.39, 13.49, 46.55, 19.43],     # Kroatien
    'SI': [45.42, 13.38, 46.88, 16.61],     # Slowenien
    'CZ': [48.55, 12.09, 51.06, 18.86],     # Tschechien
    'SK': [47.73, 16.83, 49.60, 22.56],     # Slowakei
    'PL': [49.00, 14.12, 54.84, 24.15],     # Polen
    'NO': [57.96, 4.64, 71.19, 31.17],      # Norwegen
    'SE': [55.34, 11.11, 69.06, 24.17],     # Schweden
    'FI': [59.81, 20.55, 70.09, 31.59],     # Finnland
    'IS': [63.30, -24.53, 66.53, -13.50],   # Island
    'BA': [42.56, 15.72, 45.28, 19.62],     # Bosnien
    'CY': [34.57, 32.27, 35.71, 34.60],     # Zypern
    'QA': [24.47, 50.75, 26.15, 51.64],     # Katar
    'AE': [22.63, 51.50, 26.08, 56.38],     # VAE
    'JP': [24.40, 122.93, 45.52, 153.99],   # Japan
    'FO': [61.39, -7.42, 62.40, -6.26],     # Färöer
    # Kanada regions
    'CA_W': [48.30, -139.06, 60.00, -114.04],    # Kanada West
    'CA_Z': [48.99, -114.04, 60.00, -89.00],     # Kanada Zentral
    'CA_ON': [41.68, -95.15, 56.86, -74.34],     # Kanada Ontario
    'CA_O': [44.99, -79.76, 62.59, -52.62],      # Kanada Ost
}

# Map filenames to country codes
FILE_TO_COUNTRY = {}

def get_country_from_file(filepath):
    """Extract country code from HTML file's ratingCache key."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"localStorage\.getItem\('ratingCache(\w+)'\)", content)
    if match:
        return match.group(1)
    return None

def build_overpass_query(bounds, limit=2000):
    """Build Overpass query for family-friendly places."""
    south, west, north, east = bounds
    bbox = f"{south},{west},{north},{east}"

    return f"""[out:json][timeout:120];
(
  // Spielplätze
  node["leisure"="playground"]({bbox});
  way["leisure"="playground"]({bbox});
  // Schwimmbäder & Wasserspass
  node["leisure"="swimming_pool"]["access"!="private"]({bbox});
  way["leisure"="swimming_pool"]["access"!="private"]({bbox});
  node["leisure"="water_park"]({bbox});
  way["leisure"="water_park"]({bbox});
  // Zoos & Tierparks
  node["tourism"="zoo"]({bbox});
  way["tourism"="zoo"]({bbox});
  relation["tourism"="zoo"]({bbox});
  // Freizeitparks
  node["tourism"="theme_park"]({bbox});
  way["tourism"="theme_park"]({bbox});
  relation["tourism"="theme_park"]({bbox});
  // Indoor-Spielplätze
  node["leisure"="indoor_play"]({bbox});
  way["leisure"="indoor_play"]({bbox});
  node["indoor_play"="yes"]({bbox});
  // Wickelräume
  node["changing_table"="yes"]({bbox});
  node["diaper"="yes"]({bbox});
);
out center body {limit};"""


def parse_overpass_results(data):
    """Parse Overpass response into structured family places."""
    places = []
    seen = set()

    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name', '')

        # Get coordinates
        if element['type'] == 'node':
            lat = element.get('lat', 0)
            lon = element.get('lon', 0)
        else:
            center = element.get('center', {})
            lat = center.get('lat', 0)
            lon = center.get('lon', 0)

        if lat == 0 or lon == 0:
            continue

        # Determine type
        ftype = 'playground'
        if tags.get('tourism') == 'zoo':
            ftype = 'zoo'
        elif tags.get('tourism') == 'theme_park':
            ftype = 'theme_park'
        elif tags.get('leisure') == 'swimming_pool' or tags.get('leisure') == 'water_park':
            ftype = 'pool'
        elif tags.get('leisure') == 'indoor_play' or tags.get('indoor_play') == 'yes':
            ftype = 'indoor'
        elif tags.get('changing_table') == 'yes' or tags.get('diaper') == 'yes':
            ftype = 'changing'

        # Deduplicate by rounding coords
        key = f"{ftype}_{round(lat, 4)}_{round(lon, 4)}"
        if key in seen:
            continue
        seen.add(key)

        place = {
            'type': ftype,
            'lat': round(lat, 6),
            'lon': round(lon, 6),
        }
        if name:
            place['name'] = name
        if tags.get('opening_hours'):
            place['hours'] = tags['opening_hours']
        if tags.get('wheelchair') == 'yes':
            place['wheelchair'] = True
        if tags.get('fee') == 'no':
            place['free'] = True
        if tags.get('website'):
            place['url'] = tags['website']

        places.append(place)

    return places


def fetch_country(country_code, bounds, force=False):
    """Fetch family places for one country."""
    json_file = os.path.join(SCRIPT_DIR, f"family_{country_code}.json")

    if os.path.exists(json_file) and not force:
        with open(json_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f"  ✅ Bereits vorhanden: {json_file} ({len(existing)} Orte)")
        return

    query = build_overpass_query(bounds)

    print(f"  🔍 Lade Daten von Overpass API für {country_code}...")
    try:
        resp = requests.post(OVERPASS_URL, data={'data': query}, timeout=180)
        if resp.status_code == 429:
            print(f"  ⏳ Rate limit - warte 30s...")
            time.sleep(30)
            resp = requests.post(OVERPASS_URL, data={'data': query}, timeout=180)

        if resp.status_code != 200:
            print(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
            return

        data = resp.json()
        places = parse_overpass_results(data)

        # Sort by type for better readability
        places.sort(key=lambda p: p['type'])

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(places, f, ensure_ascii=False)

        # Count by type
        types = {}
        for p in places:
            types[p['type']] = types.get(p['type'], 0) + 1

        type_str = ', '.join(f"{k}: {v}" for k, v in sorted(types.items()))
        print(f"  💾 {json_file}: {len(places)} Orte ({type_str})")

    except requests.Timeout:
        print(f"  ❌ Timeout für {country_code}")
    except Exception as e:
        print(f"  ❌ Fehler: {e}")


def main():
    force = '--force' in sys.argv

    # Determine what to process
    target_file = None
    target_country = None
    for i, arg in enumerate(sys.argv):
        if arg == '--file' and i + 1 < len(sys.argv):
            target_file = sys.argv[i + 1]
        if arg == '--country' and i + 1 < len(sys.argv):
            target_country = sys.argv[i + 1]

    if target_country:
        if target_country not in COUNTRY_BOUNDS:
            print(f"❌ Unbekanntes Land: {target_country}")
            print(f"   Verfügbar: {', '.join(sorted(COUNTRY_BOUNDS.keys()))}")
            sys.exit(1)
        print(f"\n📍 Lade Family-Places für {target_country}...")
        fetch_country(target_country, COUNTRY_BOUNDS[target_country], force)

    elif target_file:
        fpath = os.path.join(SCRIPT_DIR, target_file)
        if not os.path.exists(fpath):
            print(f"❌ Datei nicht gefunden: {fpath}")
            sys.exit(1)
        cc = get_country_from_file(fpath)
        if cc and cc in COUNTRY_BOUNDS:
            print(f"\n📍 {target_file} → {cc}")
            fetch_country(cc, COUNTRY_BOUNDS[cc], force)
        else:
            print(f"⚠️  Kein Bounding-Box für {cc} definiert")

    else:
        # Process all
        print("🌍 Lade Family-Places für alle Länder...\n")

        # Index.html = Schweiz
        print("📍 index.html → CH")
        fetch_country('CH', COUNTRY_BOUNDS['CH'], force)
        time.sleep(2)

        # All country maps
        for fpath in sorted(glob.glob(os.path.join(SCRIPT_DIR, 'map_*.html'))):
            fname = os.path.basename(fpath)
            if 'template' in fname:
                continue
            cc = get_country_from_file(fpath)
            if cc and cc in COUNTRY_BOUNDS:
                print(f"\n📍 {fname} → {cc}")
                fetch_country(cc, COUNTRY_BOUNDS[cc], force)
                time.sleep(3)  # Be nice to Overpass API
            else:
                print(f"\n⚠️  {fname}: Code={cc} - kein Bounding-Box")

    print("\n✅ Fertig! JSON-Dateien gespeichert.")
    print("   Die HTML-Karten laden diese automatisch beim Öffnen.")


if __name__ == '__main__':
    main()
