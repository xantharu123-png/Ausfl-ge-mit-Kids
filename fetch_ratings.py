#!/usr/bin/env python3
"""
Fetch Google Places ratings for all POIs and save as JSON files.
These JSON files are loaded by the HTML maps as baseline ratings.

Usage:
    python3 fetch_ratings.py YOUR_GOOGLE_API_KEY
    python3 fetch_ratings.py YOUR_GOOGLE_API_KEY --file map_italien.html
    python3 fetch_ratings.py YOUR_GOOGLE_API_KEY --all

Requirements:
    pip install requests (usually pre-installed)

The script uses the Places API (New) REST endpoint.
Enable "Places API (New)" in Google Cloud Console.
"""

import json, os, re, sys, time, glob
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests --quiet")
    import requests

API_URL = "https://places.googleapis.com/v1/places:searchText"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_pois_from_html(filepath):
    """Extract allPOIs array from an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find allPOIs = [ ... ];
    match = re.search(r'const allPOIs\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not match:
        return []

    pois_str = match.group(1).strip()
    if not pois_str:
        return []

    # Convert JS object notation to valid JSON
    # Add quotes around keys: {id:1,name:"foo"} -> {"id":1,"name":"foo"}
    pois_str = re.sub(r'(\{|,)\s*(\w+)\s*:', r'\1"\2":', pois_str)
    # Wrap in array
    try:
        pois = json.loads('[' + pois_str + ']')
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parse error: {e}")
        # Try line-by-line
        pois = []
        for line in pois_str.split('\n'):
            line = line.strip().rstrip(',')
            if line.startswith('{'):
                try:
                    pois.append(json.loads(line))
                except:
                    pass
    return pois


def get_country_code(filepath):
    """Extract country cache key from HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"localStorage\.getItem\('ratingCache(\w+)'\)", content)
    if match:
        return match.group(1)
    return None


def fetch_rating(api_key, name, location, lat, lng, retries=2):
    """Fetch rating from Google Places API (New)."""
    query = f"{name} {location}" if location else name
    payload = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 5000.0
            }
        },
        "maxResultCount": 1
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.rating,places.userRatingCount,places.displayName"
    }

    for attempt in range(retries + 1):
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Rate limit, waiting {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code == 403:
                print(f"    ❌ API nicht aktiviert oder Key ungültig (403)")
                return None, "API_ERROR"
            if resp.status_code != 200:
                print(f"    ⚠️  HTTP {resp.status_code}")
                return None, f"HTTP_{resp.status_code}"

            data = resp.json()
            if data.get("places") and len(data["places"]) > 0:
                place = data["places"][0]
                return {
                    "rating": place.get("rating", 0),
                    "count": place.get("userRatingCount", 0)
                }, None
            else:
                return {"rating": 0, "count": 0}, None

        except requests.Timeout:
            if attempt < retries:
                time.sleep(2)
                continue
            return None, "TIMEOUT"
        except Exception as e:
            return None, str(e)

    return None, "MAX_RETRIES"


def process_file(filepath, api_key, force=False):
    """Process a single HTML file: fetch ratings for all POIs and save JSON."""
    fname = os.path.basename(filepath)
    country_code = get_country_code(filepath)
    if not country_code:
        print(f"⚠️  No country code found in {fname}, skipping")
        return

    json_file = os.path.join(SCRIPT_DIR, f"ratings_{country_code}.json")

    # Load existing ratings
    existing = {}
    if os.path.exists(json_file) and not force:
        with open(json_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    # Extract POIs
    pois = extract_pois_from_html(filepath)
    if not pois:
        print(f"⚠️  No POIs found in {fname}")
        return

    # Filter out already fetched
    to_fetch = [p for p in pois if str(p.get('id', '')) not in existing]
    total = len(pois)
    cached = total - len(to_fetch)

    print(f"\n📍 {fname} ({country_code}): {total} POIs, {cached} bereits geladen, {len(to_fetch)} neu")

    if not to_fetch:
        print(f"   ✅ Alle Bewertungen bereits vorhanden!")
        return

    errors = 0
    success = 0
    api_error = False

    for i, poi in enumerate(to_fetch):
        poi_id = str(poi.get('id', i))
        name = poi.get('name', '')
        location = poi.get('location', '')
        lat = poi.get('lat', 0)
        lng = poi.get('lng', 0)

        result, err = fetch_rating(api_key, name, location, lat, lng)

        if err == "API_ERROR":
            api_error = True
            break

        if result:
            existing[poi_id] = result
            if result['rating'] > 0:
                success += 1
            else:
                success += 1  # Zero results is still a valid response
        else:
            errors += 1

        # Progress
        done = cached + i + 1
        pct = round(done / total * 100)
        print(f"\r   {done}/{total} ({pct}%) · ✓{success} · ✗{errors}", end="", flush=True)

        # Save periodically
        if (i + 1) % 50 == 0:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False)

        # Rate limiting: ~3 requests per second
        time.sleep(0.35)

    print()  # newline

    if api_error:
        print("   ❌ API Fehler! Prüfe ob 'Places API (New)' aktiviert ist und der Key stimmt.")
        if existing:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False)
        return

    # Save final
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False)

    print(f"   💾 Gespeichert: {json_file} ({len(existing)} Einträge)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_ratings.py YOUR_API_KEY [--file map_xyz.html] [--all] [--force]")
        print("\nOptions:")
        print("  --file FILE   Process only this file")
        print("  --all         Process all map files + index.html")
        print("  --force       Re-fetch all ratings (ignore existing JSON)")
        print("\nWithout --file or --all, processes only index.html (Schweiz)")
        sys.exit(1)

    api_key = sys.argv[1]
    force = '--force' in sys.argv

    # Determine which files to process
    target_file = None
    process_all = '--all' in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == '--file' and i + 1 < len(sys.argv):
            target_file = sys.argv[i + 1]

    if target_file:
        fpath = os.path.join(SCRIPT_DIR, target_file)
        if not os.path.exists(fpath):
            print(f"❌ Datei nicht gefunden: {fpath}")
            sys.exit(1)
        process_file(fpath, api_key, force)
    elif process_all:
        # Process index.html first
        index_path = os.path.join(SCRIPT_DIR, 'index.html')
        if os.path.exists(index_path):
            process_file(index_path, api_key, force)

        # Then all country maps
        for fpath in sorted(glob.glob(os.path.join(SCRIPT_DIR, 'map_*.html'))):
            if 'template' in os.path.basename(fpath):
                continue
            process_file(fpath, api_key, force)
    else:
        # Default: just index.html
        index_path = os.path.join(SCRIPT_DIR, 'index.html')
        process_file(index_path, api_key, force)

    print("\n✅ Fertig! JSON-Dateien im Projektordner gespeichert.")
    print("   Die HTML-Karten laden diese automatisch beim Öffnen.")


if __name__ == '__main__':
    main()
