#!/usr/bin/env python3
"""Fetch high-trust Wikimedia photos for missing POI baselines.

This is intentionally stricter than the legacy fetcher. It accepts an image
only when the article title/extract matches meaningful POI name tokens. A
nearby geosearch result helps ranking, but location alone is never enough.

Examples:
  python scripts/fetch_verified_photos.py CH --limit 50
  python scripts/fetch_verified_photos.py CH --limit 50 --apply
  python scripts/fetch_verified_photos.py ALL --only-worthy --limit 100 --apply
"""

from __future__ import annotations

import argparse
import concurrent.futures
import functools
import json
import math
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from photo_trust_audit import (
    HTML_TO_CC,
    ROOT,
    BAD_EXT_RE,
    BAD_URL_RE,
    KNOWN_GENERIC_RE,
    extract_pois,
    image_filename,
    load_photos,
    meaningful_tokens,
    normalize,
    write_photos,
)


UA = (
    "JahresguidePhotoVerifier/1.0 "
    "(https://jahresguide.app; contact miroslav.mikulic@gmail.com) Python/3"
)
SSL_CTX = ssl.create_default_context()

LANG_PRIO = {
    "CH": ["de", "fr", "it", "en"],
    "FR": ["fr", "de", "en"],
    "DE": ["de", "en"],
    "AT": ["de", "en"],
    "IT": ["it", "de", "en"],
    "ES": ["es", "de", "en"],
    "PT": ["pt", "de", "en"],
    "GR": ["el", "de", "en"],
    "NL": ["nl", "de", "en"],
    "BE": ["nl", "fr", "de", "en"],
    "LU": ["fr", "de", "lb", "en"],
    "CZ": ["cs", "de", "en"],
    "SK": ["sk", "de", "en"],
    "PL": ["pl", "de", "en"],
    "HR": ["hr", "de", "en"],
    "SI": ["sl", "de", "en"],
    "BA": ["bs", "hr", "sr", "de", "en"],
    "NO": ["no", "nb", "de", "en"],
    "SE": ["sv", "de", "en"],
    "FI": ["fi", "de", "en"],
    "IS": ["is", "de", "en"],
    "FO": ["fo", "da", "de", "en"],
    "CY": ["el", "de", "en"],
    "JP": ["ja", "en", "de"],
    "QA": ["ar", "en", "de"],
    "AE": ["ar", "en", "de"],
    "CA_ON": ["en", "fr", "de"],
    "CA_OST": ["en", "fr", "de"],
    "CA_WEST": ["en", "fr", "de"],
    "CA_ZEN": ["en", "fr", "de"],
}

WORTHY_CATEGORIES = {"sehenswuerdigkeit", "kultur", "weihnachten"}
GENERIC_TITLE_RE = re.compile(
    r"^(observation deck|arc de triomphe|jardin des plantes|sea life|der bote vom gardasee|"
    r"kasteel keukenhof|carnival festival|botanischer garten|botanical garden|"
    r"harbor|harbour|marina|vineyard|funicular|fountain|windmill|"
    r"aquadukt|aqueduct|nationalmuseum|schildkroten|watermill|"
    r"monastery|kloster|catacombs|river cruise|wald|dorf|"
    r"strasse|stra e|street|weingut|town square|torre civica|"
    r"piazza del popolo|stadtmuseum|valley|kurpark|"
    r"monumento ai caduti|gargano|cilento|kunstmuseum|kunstlerkolonie|"
    r"chapel|museo diocesano|museo civico|ponte vecchio|castello|funivia|"
    r"sebastien le prestre.*vauban|kunstweg|archaologie|archaeologie|"
    r"opera house|pinacoteca|giovanni.*evangelista|foro romano|"
    r"benediktinerkloster|fischerdorf|canal|grand place|grun|gruen|"
    r"seen|mosque|wasserkraft|belfort|belle epoque|badlands|marsh|louvre|"
    r"corn maze|butterfly house|science center|madame tussauds|dungeon|"
    r"central park|natural history museum|thermalbad|plage|musee des automates|"
    r"adventskalender|noel|marche de noel|tour de france|motocross|boat racing|"
    r"terry fox run|bergsteigen|wanderweg|klettern|surfing)$",
    re.I,
)
NON_PLACE_ENTITY_RE = re.compile(
    r"(album|book|film|fictional|human settlement|painting|song|street in|video game|"
    r"wikimedia disambiguation page)",
    re.I,
)
AMBIGUOUS_SINGLE_TOKENS = {
    "beach",
    "bernstein",
    "bridge",
    "bruecke",
    "brucke",
    "bucht",
    "aquarium",
    "amphitheater",
    "amphitheatre",
    "basilica",
    "burg",
    "camping",
    "carnival",
    "castle",
    "cave",
    "caves",
    "cathedral",
    "church",
    "dorf",
    "dom",
    "donau",
    "einkaufszentrum",
    "eisenbahn",
    "arboretum",
    "fachwerk",
    "fernsehturm",
    "festival",
    "festung",
    "forest",
    "fortress",
    "feuerwerk",
    "firework",
    "fireworks",
    "garden",
    "garten",
    "gebirge",
    "glacier",
    "gletscher",
    "golf",
    "gorge",
    "hachiman",
    "hafen",
    "halbinsel",
    "hiking",
    "hohle",
    "hoehle",
    "huette",
    "hut",
    "hutte",
    "hugel",
    "insel",
    "kapelle",
    "kirche",
    "kathedrale",
    "karneval",
    "kriegerdenkmal",
    "kurhaus",
    "landsgemeinde",
    "lagoon",
    "lagune",
    "market",
    "markt",
    "mall",
    "mittelalter",
    "minster",
    "muenster",
    "munster",
    "museum",
    "mountain",
    "mountains",
    "nationalpark",
    "nationalfeiertag",
    "naturpark",
    "onsen",
    "palace",
    "palast",
    "park",
    "peninsula",
    "platz",
    "porto",
    "range",
    "region",
    "railway",
    "rathaus",
    "ruine",
    "ruins",
    "scharen",
    "schlucht",
    "schluecht",
    "seerosen",
    "salzlake",
    "shrine",
    "schloss",
    "seilbahn",
    "schiff",
    "ship",
    "sommerrodelbahn",
    "station",
    "stadtmauer",
    "strand",
    "swarovski",
    "synagoge",
    "synagogue",
    "tempel",
    "temple",
    "theater",
    "theatre",
    "tower",
    "town",
    "tradition",
    "tunnel",
    "turm",
    "uhrturm",
    "village",
    "viaduct",
    "viadukt",
    "wallfahrtskirche",
    "wald",
    "waldviertel",
    "wasserfall",
    "waterfall",
    "watchtower",
    "weihnachtsmarkt",
    "wein",
    "wine",
    "woods",
    "archipelago",
    "bay",
    "coast",
    "fjord",
    "hill",
    "island",
    "kueste",
    "kuste",
}
WEAK_PLACE_TOKENS = {"center", "central", "centre", "mitte", "stadt", "zentrum"}
SHORT_CONTEXT_TOKENS = {"arc", "zoo"}
REQUIRED_CONTEXT_TOKENS = {
    "abbey",
    "basilica",
    "burg",
    "castle",
    "cathedral",
    "chateau",
    "dom",
    "fort",
    "kloster",
    "museum",
    "palace",
    "schloss",
}
TOKEN_SYNONYMS = {
    "bruecke": {"bridge"},
    "brucke": {"bridge"},
    "fischmarkt": {"market"},
    "markt": {"market"},
    "palast": {"palace"},
    "schrein": {"shrine"},
    "tempel": {"temple"},
    "turm": {"tower"},
}


def fetch_json(url: str, timeout: int = 8) -> dict[str, Any] | None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=SSL_CTX) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    return None


@functools.lru_cache(maxsize=20000)
def summary(lang: str, title: str) -> dict[str, Any] | None:
    encoded = urllib.parse.quote(title.replace(" ", "_"))
    return fetch_json(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded}")


@functools.lru_cache(maxsize=20000)
def wiki_search(lang: str, query: str, limit: int = 5) -> list[str]:
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
        f"&list=search&srsearch={urllib.parse.quote(query)}&srlimit={limit}"
    )
    data = fetch_json(url, timeout=8)
    if not data:
        return []
    return [hit["title"] for hit in data.get("query", {}).get("search", []) if hit.get("title")]


@functools.lru_cache(maxsize=20000)
def wikidata_search(lang: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
    url = (
        f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json"
        f"&language={urllib.parse.quote(lang)}&uselang=en&srlimit={limit}"
        f"&limit={limit}&search={urllib.parse.quote(query)}"
    )
    data = fetch_json(url, timeout=8)
    if not data:
        return []
    return data.get("search", [])


@functools.lru_cache(maxsize=20000)
def wiki_geosearch(lang: str, lat: float, lng: float, radius: int = 1200, limit: int = 10) -> list[dict[str, Any]]:
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
        f"&list=geosearch&gscoord={lat}%7C{lng}&gsradius={radius}&gslimit={limit}"
    )
    data = fetch_json(url, timeout=8)
    if not data:
        return []
    return data.get("query", {}).get("geosearch", [])


@functools.lru_cache(maxsize=20000)
def wiki_pageprops(lang: str, title: str) -> dict[str, Any] | None:
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json"
        f"&prop=pageprops|pageimages&piprop=original&titles={urllib.parse.quote(title)}"
    )
    data = fetch_json(url, timeout=8)
    pages = data.get("query", {}).get("pages", {}) if data else {}
    for page in pages.values():
        if "missing" not in page:
            return page
    return None


def commons_thumb_url(file_name: str, width: int = 500) -> str:
    encoded = urllib.parse.quote(file_name.replace(" ", "_"), safe="")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width={width}"


@functools.lru_cache(maxsize=20000)
def wikidata_entity(qid: str) -> dict[str, Any]:
    data = fetch_json(f"https://www.wikidata.org/wiki/Special:EntityData/{urllib.parse.quote(qid)}.json", timeout=8)
    return data.get("entities", {}).get(qid, {}) if data else {}


@functools.lru_cache(maxsize=20000)
def wikidata_p18_url(qid: str) -> str | None:
    entity = wikidata_entity(qid)
    claims = entity.get("claims", {}).get("P18", [])
    for claim in claims:
        value = (
            claim.get("mainsnak", {})
            .get("datavalue", {})
            .get("value")
        )
        if isinstance(value, str):
            url = commons_thumb_url(value)
            lower = url.lower()
            if BAD_EXT_RE.search(lower) or BAD_URL_RE.search(lower) or KNOWN_GENERIC_RE.search(lower):
                continue
            if re.search(r"\.(jpe?g|png)(?:[/?#]|$)", lower):
                return url
    return None


@functools.lru_cache(maxsize=20000)
def wikidata_coord(qid: str) -> tuple[float, float] | None:
    entity = wikidata_entity(qid)
    claims = entity.get("claims", {}).get("P625", [])
    for claim in claims:
        value = (
            claim.get("mainsnak", {})
            .get("datavalue", {})
            .get("value")
        )
        if isinstance(value, dict) and "latitude" in value and "longitude" in value:
            return float(value["latitude"]), float(value["longitude"])
    return None


def distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    radius_m = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return round(radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def wikidata_distance_m(qid: str, poi: dict[str, Any]) -> int | None:
    coord = wikidata_coord(qid)
    lat = poi.get("lat")
    lng = poi.get("lng")
    if not coord or not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return None
    return distance_m(float(lat), float(lng), coord[0], coord[1])


def expand_tokens(tokens: set[str], raw_name: str = "") -> set[str]:
    expanded = set(tokens)
    raw_tokens = set(normalize(raw_name).split())
    expanded.update(token for token in raw_tokens if token in SHORT_CONTEXT_TOKENS)
    for token in raw_tokens | tokens:
        expanded.update(TOKEN_SYNONYMS.get(token, set()))
    return expanded


def matching_tokens(tokens: set[str], normalized_text: str) -> set[str]:
    words = set(normalized_text.split())
    return {
        token
        for token in tokens
        if token in words or (len(token) >= 5 and token in normalized_text)
    }


def photo_from_summary(data: dict[str, Any] | None) -> str | None:
    if not data or data.get("type") == "disambiguation":
        return None
    src = (
        data.get("thumbnail", {}).get("source")
        or data.get("originalimage", {}).get("source")
        or ""
    )
    if not src:
        return None
    lower = src.lower()
    if BAD_EXT_RE.search(lower) or BAD_URL_RE.search(lower) or KNOWN_GENERIC_RE.search(lower):
        return None
    if not re.search(r"\.(jpe?g|png)(?:[/?#]|$)", lower):
        return None
    return re.sub(r"/\d+px-", "/500px-", src)


def photo_from_wikidata(lang: str, title: str) -> str | None:
    page = wiki_pageprops(lang, title)
    qid = (page or {}).get("pageprops", {}).get("wikibase_item")
    if not qid:
        return None
    return wikidata_p18_url(str(qid))


def data_from_wikidata_hit(hit: dict[str, Any]) -> dict[str, Any] | None:
    qid = hit.get("id")
    if not qid:
        return None
    aliases = hit.get("aliases") or []
    match_text = hit.get("match", {}).get("text") or ""
    label = str(hit.get("label") or match_text or qid)
    description = str(hit.get("description") or "")
    if NON_PLACE_ENTITY_RE.search(description):
        return None
    return {
        "title": label,
        "description": description,
        "extract": " ".join(str(value) for value in [match_text, *aliases, description] if value),
        "wikidata_id": qid,
    }


def stripped_name_variants(name: str, location: str, region: str = "") -> list[str]:
    variants: list[str] = []
    location_parts = [
        location,
        location.split(",")[0],
        location.split("-")[0],
        location.split("\u2013")[0],
        region,
        region.split(",")[0],
        region.split("-")[0],
        region.split("\u2013")[0],
    ]
    for raw_location in location_parts:
        loc = raw_location.strip()
        if len(loc) < 3:
            continue
        match = re.match(rf"^\s*{re.escape(loc)}(?:[\s:]+|[-\u2013\u2014]+)(.+)$", name, re.I)
        if match:
            stripped = match.group(1).strip()
            if len(stripped) >= 4 and stripped.lower() != name.lower():
                variants.append(stripped)
        suffix_match = re.match(rf"^(.+?)(?:[\s:]+|[-\u2013\u2014]+){re.escape(loc)}\s*$", name, re.I)
        if suffix_match:
            stripped = suffix_match.group(1).strip()
            if len(stripped) >= 4 and stripped.lower() != name.lower():
                variants.append(stripped)
                variants.append(f"{stripped} ({loc})")
    seen: set[str] = set()
    return [value for value in variants if not (value.lower() in seen or seen.add(value.lower()))]


def is_ambiguous_single_query(value: str) -> bool:
    tokens = meaningful_tokens(value)
    return len(tokens) == 1 and next(iter(tokens)) in AMBIGUOUS_SINGLE_TOKENS


def build_queries(poi: dict[str, Any]) -> list[str]:
    name = str(poi.get("name", "")).strip()
    location = str(poi.get("location", "")).strip()
    region = str(poi.get("region", "")).strip()
    place_tokens = meaningful_tokens(location, region)
    stripped_names = [
        value
        for value in stripped_name_variants(name, location, region)
        if not is_ambiguous_single_query(value)
        and not (meaningful_tokens(value) and meaningful_tokens(value) <= place_tokens)
    ]
    queries = [
        name,
        name.replace("-", " "),
        *stripped_names,
        *(stripped.replace("-", " ") for stripped in stripped_names),
        f"{name} {location}" if location and location.lower() not in name.lower() else "",
        f"{name} de {location}" if location and location.lower() not in name.lower() else "",
        f"{name} of {location}" if location and location.lower() not in name.lower() else "",
        f"{name} {region}" if region and len(region) <= 12 else "",
        f"{name} ({location})" if location and location.lower() not in name.lower() else "",
    ]
    seen = set()
    return [q for q in queries if q and not (q.lower() in seen or seen.add(q.lower()))]


def score_candidate(
    poi: dict[str, Any],
    data: dict[str, Any],
    method: str,
    distance_m: int | None,
    photo_url_override: str | None = None,
) -> tuple[float, dict[str, Any]]:
    place_tokens = meaningful_tokens(str(poi.get("location", "")), str(poi.get("region", "")))
    raw_name = str(poi.get("name", ""))
    raw_name_tokens = expand_tokens(meaningful_tokens(raw_name), raw_name)
    core_name_tokens = raw_name_tokens - place_tokens
    name_tokens = core_name_tokens or raw_name_tokens
    title = str(data.get("title", ""))
    photo_url = photo_url_override or photo_from_summary(data) or ""
    filename_norm = normalize(image_filename(photo_url))
    text = " ".join(
        [
            title,
            str(data.get("description", "")),
            str(data.get("extract", ""))[:800],
            image_filename(photo_url),
        ]
    )
    title_norm = normalize(title)
    text_norm = normalize(text)

    title_hits = matching_tokens(name_tokens, title_norm)
    file_hits = matching_tokens(name_tokens, filename_norm)
    name_hits = matching_tokens(name_tokens, text_norm)
    place_hits = matching_tokens(place_tokens, text_norm)

    score = 0.0
    score += len(title_hits) * 3
    score += len(file_hits) * 2
    score += len(name_hits) * 1.5
    score += len(place_hits) * 0.75
    if method == "geo" and distance_m is not None:
        score += max(0.0, 2.5 - (distance_m / 600.0))
    if method == "wikidata" and distance_m is not None:
        score += max(0.0, 3.0 - (distance_m / 500.0))

    details = {
        "title": title,
        "method": method,
        "distance_m": distance_m,
        "core_name_tokens": sorted(name_tokens),
        "title_hits": sorted(title_hits),
        "file_hits": sorted(file_hits),
        "name_hits": sorted(name_hits),
        "place_hits": sorted(place_hits),
        "score": round(score, 2),
    }
    return score, details


def is_accepted(
    poi: dict[str, Any],
    data: dict[str, Any],
    method: str,
    distance_m: int | None,
    min_score: float,
    photo_url_override: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    score, details = score_candidate(poi, data, method, distance_m, photo_url_override)
    title_norm = normalize(str(data.get("title", "")))
    poi_norm = normalize(str(poi.get("name", "")))
    exact_title_match = title_norm == poi_norm
    name_hit_count = len(details["title_hits"]) + len(details["name_hits"])
    if name_hit_count == 0:
        return False, details
    if GENERIC_TITLE_RE.search(title_norm):
        return False, details
    if title_norm in AMBIGUOUS_SINGLE_TOKENS:
        return False, details
    if method == "wikidata" and NON_PLACE_ENTITY_RE.search(str(data.get("description", ""))):
        return False, details
    if method == "title" and not exact_title_match and not (details["title_hits"] or details["file_hits"]):
        return False, details
    if method == "title" and not exact_title_match and len(details["core_name_tokens"]) > 1:
        if len(details["title_hits"]) < 2 and not details["file_hits"]:
            return False, details
    core_tokens = set(details["core_name_tokens"])
    if (
        method == "title"
        and exact_title_match
        and len(core_tokens) > 1
        and not details["file_hits"]
        and not details["place_hits"]
    ):
        return False, details
    if (
        method == "title"
        and exact_title_match
        and len(core_tokens) == 1
        and not (set(details["place_hits"]) - WEAK_PLACE_TOKENS)
    ):
        return False, details
    raw_name_tokens = set(meaningful_tokens(str(poi.get("name", ""))))
    raw_place_tokens = set(meaningful_tokens(str(poi.get("location", "")), str(poi.get("region", ""))))
    if (
        method == "title"
        and exact_title_match
        and raw_name_tokens
        and raw_name_tokens <= raw_place_tokens
        and not details["file_hits"]
    ):
        return False, details
    if (
        method == "title"
        and not exact_title_match
        and len(core_tokens) == 1
        and next(iter(core_tokens)) in AMBIGUOUS_SINGLE_TOKENS
        and not (set(details["place_hits"]) - WEAK_PLACE_TOKENS)
    ):
        return False, details
    if (
        method in {"search", "geo"}
        and len(core_tokens) == 1
        and next(iter(core_tokens)) in AMBIGUOUS_SINGLE_TOKENS
        and title_norm != poi_norm
        and not (set(details["place_hits"]) - WEAK_PLACE_TOKENS)
    ):
        return False, details
    required_context = [
        token for token in normalize(str(poi.get("name", ""))).split()
        if token in REQUIRED_CONTEXT_TOKENS
    ]
    if method == "search" and required_context and not any(token in title_norm for token in required_context):
        return False, details
    if method == "search" and len(details["core_name_tokens"]) > 1 and len(details["title_hits"]) < 2:
        return False, details
    if method == "search" and not exact_title_match and not (set(details["place_hits"]) - WEAK_PLACE_TOKENS):
        return False, details
    if method == "search" and not exact_title_match and not details["file_hits"] and not details["place_hits"]:
        return False, details
    if method == "wikidata":
        strong_hits = set(details["title_hits"]) | set(details["file_hits"])
        strong_place_hits = set(details["place_hits"]) - WEAK_PLACE_TOKENS
        close_entity = distance_m is not None and distance_m <= 750
        if distance_m is not None and distance_m > 25000:
            return False, details
        if len(core_tokens) > 1 and len(strong_hits) < 2 and not strong_place_hits and not close_entity:
            return False, details
        if len(core_tokens) == 1 and next(iter(core_tokens)) in AMBIGUOUS_SINGLE_TOKENS and title_norm != poi_norm and not strong_place_hits:
            return False, details
        if not (strong_hits or details["place_hits"] or close_entity):
            return False, details
    if method == "geo" and len(details["core_name_tokens"]) > 1:
        strong_hits = set(details["title_hits"]) | set(details["file_hits"])
        if len(strong_hits) < 2:
            return False, details
    if method in {"search", "geo"} and not exact_title_match and score < 7.0:
        return False, details
    if method == "geo" and not (details["title_hits"] or details["file_hits"]):
        return False, details
    if method == "geo" and distance_m is not None and distance_m > 1200:
        return False, details
    if score < min_score:
        return False, details
    return True, details


def find_photo_for_poi(
    cc: str,
    poi: dict[str, Any],
    used_urls: Counter[str],
    max_duplicate: int,
    min_score: float,
    allow_search: bool = True,
    allow_geo: bool = True,
    allow_wikidata_search: bool = False,
) -> dict[str, Any] | None:
    langs = LANG_PRIO.get(cc, ["de", "en"])
    tried: set[tuple[str, str]] = set()

    def try_title(lang: str, title: str, method: str, distance_m: int | None = None) -> dict[str, Any] | None:
        key = (lang, title.lower())
        if key in tried:
            return None
        tried.add(key)
        data = summary(lang, title)
        url = photo_from_summary(data)
        source = "summary"
        if not url:
            url = photo_from_wikidata(lang, title)
            source = "wikidata_p18"
        if not data or not url or used_urls[url] >= max_duplicate:
            return None
        accepted, details = is_accepted(poi, data, method, distance_m, min_score, url)
        if not accepted:
            return None
        details.update({"lang": lang, "url": url, "source": source})
        return details

    for lang in langs:
        for query in build_queries(poi):
            found = try_title(lang, query, "title")
            if found:
                return found

    search_langs = list(dict.fromkeys([langs[0], "en", "de"]))
    if allow_search:
        for lang in search_langs:
            for query in build_queries(poi)[:3]:
                for title in wiki_search(lang, query, limit=5):
                    found = try_title(lang, title, "search")
                    if found:
                        return found

    if allow_wikidata_search:
        for lang in search_langs:
            for query in build_queries(poi)[:4]:
                for hit in wikidata_search(lang, query, limit=5):
                    data = data_from_wikidata_hit(hit)
                    if not data:
                        continue
                    qid = str(data.get("wikidata_id", ""))
                    url = wikidata_p18_url(qid)
                    if not url or used_urls[url] >= max_duplicate:
                        continue
                    entity_distance_m = wikidata_distance_m(qid, poi)
                    accepted, details = is_accepted(poi, data, "wikidata", entity_distance_m, min_score, url)
                    if not accepted:
                        continue
                    details.update({"lang": lang, "url": url, "source": "wikidata_search", "wikidata_id": qid})
                    return details

    lat = poi.get("lat")
    lng = poi.get("lng")
    if allow_geo and isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
        for lang in search_langs:
            for hit in wiki_geosearch(lang, float(lat), float(lng)):
                title = hit.get("title")
                if not title:
                    continue
                found = try_title(lang, title, "geo", int(hit.get("dist", 999999)))
                if found:
                    return found
    return None


def country_from_arg(value: str) -> list[str]:
    if value.upper() == "ALL":
        return list(HTML_TO_CC.values())
    cc = value.upper()
    aliases = {"CA_E": "CA_OST", "CA_O": "CA_OST", "CA_Z": "CA_ZEN", "CA_W": "CA_WEST"}
    cc = aliases.get(cc, cc)
    if cc not in set(HTML_TO_CC.values()):
        raise SystemExit(f"Unknown country code: {value}")
    return [cc]


def process_country(args: argparse.Namespace, cc: str) -> dict[str, Any]:
    html_name = next(name for name, mapped_cc in HTML_TO_CC.items() if mapped_cc == cc)
    pois = extract_pois(ROOT / html_name)
    photos = load_photos(cc)
    before_count = len(photos)
    used_urls = Counter(photos.values())

    candidates = [poi for poi in pois if str(poi["id"]) not in photos]
    if args.only_worthy:
        candidates = [poi for poi in candidates if poi.get("category") in WORTHY_CATEGORIES]
    if args.categories:
        allowed_categories = {category.strip() for category in args.categories.split(",") if category.strip()}
        candidates = [poi for poi in candidates if str(poi.get("category")) in allowed_categories]
    priority = {"sehenswuerdigkeit": 0, "kultur": 1, "weihnachten": 2, "familie": 3}
    candidates.sort(key=lambda poi: priority.get(str(poi.get("category")), 9))
    if args.offset:
        candidates = candidates[args.offset :]
    if args.limit:
        candidates = candidates[: args.limit]

    print(f"[{cc}] checking {len(candidates)} POIs", flush=True)
    found: dict[str, str] = {}
    meta: dict[str, Any] = {}
    started = time.time()

    def work(poi: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
        return poi, find_photo_for_poi(
            cc,
            poi,
            used_urls,
            args.max_duplicate,
            args.min_score,
            allow_search=not (args.title_only or args.skip_search),
            allow_geo=not (args.title_only or args.skip_geo),
            allow_wikidata_search=args.wikidata_search,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(work, poi) for poi in candidates]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            poi, result = future.result()
            if result:
                pid = str(poi["id"])
                url = result["url"]
                if used_urls[url] >= args.max_duplicate:
                    continue
                found[pid] = url
                used_urls[url] += 1
                meta[pid] = {
                    "poi_name": poi.get("name"),
                    "location": poi.get("location"),
                    **result,
                }
            if index % 25 == 0:
                print(f"[{cc}] {index}/{len(candidates)} checked, +{len(found)}", flush=True)

    if args.apply and found:
        photos.update(found)
        write_photos(cc, dict(sorted(photos.items(), key=lambda item: int(item[0]))))

    report = {
        "cc": cc,
        "mode": "apply" if args.apply else "dry-run",
        "offset": args.offset,
        "title_only": args.title_only,
        "skip_search": args.skip_search,
        "skip_geo": args.skip_geo,
        "wikidata_search": args.wikidata_search,
        "categories": args.categories,
        "checked": len(candidates),
        "found": len(found),
        "before": before_count,
        "after": before_count + len(found),
        "seconds": round(time.time() - started, 1),
        "items": meta,
    }
    suffix = "apply" if args.apply else "dry_run"
    (ROOT / f"photo_fetch_report_{cc}_{suffix}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[{cc}] found {len(found)} in {report['seconds']}s", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("country", help="Country code, e.g. CH, DE, FR, or ALL")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--max-duplicate", type=int, default=2)
    parser.add_argument("--min-score", type=float, default=3.5)
    parser.add_argument("--only-worthy", action="store_true")
    parser.add_argument("--categories", help="Comma-separated POI categories to include")
    parser.add_argument("--title-only", action="store_true", help="Only accept direct title/query matches")
    parser.add_argument("--skip-search", action="store_true")
    parser.add_argument("--skip-geo", action="store_true")
    parser.add_argument("--wikidata-search", action="store_true")
    args = parser.parse_args()

    reports = [process_country(args, cc) for cc in country_from_arg(args.country)]
    total_checked = sum(report["checked"] for report in reports)
    total_found = sum(report["found"] for report in reports)
    print(f"total: checked {total_checked}, found {total_found}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
