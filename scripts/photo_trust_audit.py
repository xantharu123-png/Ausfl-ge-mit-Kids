#!/usr/bin/env python3
"""Audit and prune POI photo baselines.

The product rule is intentionally strict: no image is better than a wrong
image. This script removes only hard trust failures by default:

- photo entries for missing POIs
- maps, flags, logos, SVG/TIFF/video thumbnails, signs
- known generic/cross-country landmark fallbacks
- the same image URL used more than two times

It also regenerates photos_<CC>.js files for file:// usage and refreshes the
dashboard audit summary when run with --apply.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import unicodedata
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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

CC_LABELS = {
    "CH": "Schweiz",
    "DE": "Deutschland",
    "FR": "Frankreich",
    "AT": "Oesterreich",
    "IT": "Italien",
    "ES": "Spanien",
    "PT": "Portugal",
    "NL": "Niederlande",
    "BE": "Belgien",
    "LU": "Luxemburg",
    "NO": "Norwegen",
    "SE": "Schweden",
    "FI": "Finnland",
    "IS": "Island",
    "FO": "Faeroeer",
    "PL": "Polen",
    "CZ": "Tschechien",
    "SK": "Slowakei",
    "SI": "Slowenien",
    "HR": "Kroatien",
    "BA": "Bosnien",
    "GR": "Griechenland",
    "CY": "Zypern",
    "AE": "VAE",
    "QA": "Katar",
    "JP": "Japan",
    "CA_WEST": "Kanada West",
    "CA_ZEN": "Kanada Zentral",
    "CA_ON": "Kanada Ontario",
    "CA_OST": "Kanada Ost",
}

FIELD_STR = re.compile(r'(\w+):\s*"((?:[^"\\]|\\.)*)"')
FIELD_NUM = re.compile(r"(\w+):\s*(-?\d+(?:\.\d+)?)")

BAD_URL_RE = re.compile(
    r"(karte|wappen|flag|coat_of_arms|logo|map[_.]|locator|location_in|"
    r"positionskarte|relief_|verwaltung|im_bezirk|blank|icon|symbol|blason|escudo|"
    r"stemma|bandiera|banner|diagram|schema|schild|signboard|signage|nameplate|"
    r"plaque|infotafel|grundriss|thumbnail\.jpg)",
    re.I,
)
BAD_EXT_RE = re.compile(r"\.(svg|tif|tiff|webm|ogv|gif)(?:[/?#]|$)", re.I)
KNOWN_GENERIC_RE = re.compile(
    r"(matterhorn_from_domh|bern_luftaufnahme|sphinx_et_jungfrau|"
    r"altstadt_z%c3%bcrich|altstadt_zurich|lugano_from_sighignola|"
    r"interlaken_aer|appenzell_2022|thun_be|solothurn_2023|"
    r"la_tour_eiffel_vue_de_la_tour_saint-jacques|arc_de_triomphe|"
    r"mont-saint-michel_vu_du_ciel|big_ben|tower_bridge_london|"
    r"colosseum_in_rome|brandenburger_tor_abends|pratergarten_berlin|"
    r"flora\.png|coffee_plantation.*kaua|trajan(?:'|%27)?s_column|trajan_column|"
    r"lisbontram|jellingsten|str%c3%b6hl-rangkronen|"
    r"fire_inside_an_abandoned_convent.*quebec|libreoffice_writer|"
    r"hapag-lloyd_antwerpen_express|anamur_burnu|embrik_strand|"
    r"tent_camping_along_the_sulayr_trail|amaterske_akvarium|"
    r"vesting_index|mathildenhoehe-ernst-ludwig|hallenbad_huetteldorf|"
    r"ramsau_am_dachstein|handscheermolen|iceland_satellite|"
    r"chimney_rock_trail_point_reyes|united_nations_geographical_subregions|"
    r"locationsapmi|pallas-yll%c3%a4stunturin_kp|"
    r"corfe-castle_im_h%c3%bcgelland|bucht_in_neuseeland|"
    r"mariagerfjord_ved_hadsund|slanic_salt_mine|fraenkische_schweiz\.png|"
    r"ammerthal_as_006|arles.*roman_amphitheatre|"
    r"st_mary%27s_church.*castle_street|neusiedler_lake_satellite|"
    r"santiago_cathedral_2021|franz_joseph_i_of_austria|"
    r"basilicasemproniareconstruction|golfer_swing|"
    r"schade.*gletscher|baltic.*ship|zeller_see_grafik|"
    r"eifelpark_coaster|lingelbach_karneval|palio_-_manifesto|"
    r"christkindlesmarkt_nuernberg|duesseldorf_firework|"
    r"landsgemeinde_-_glarus|tradition-warner-highsmith|jungfraubahn\.png|"
    r"s-bahn_berlin_innsbrucker_platz|nationalpark_hohe_tauern\.png|"
    r"destruction_of_pompeii_and_herculaneum|san_sebastiano_fuori_le_mura|"
    r"milan_centralstation|d%c3%bcrnstein_in_kr\.png|"
    r"steingartencambridge|mangastorejapan|the_ladies%27_home_journal|"
    r"die_gartenlaube|benzaiten_.*white_dragon|cnw_brakeman|"
    r"opera_garnier_stairway|various_products_made_from_paper|"
    r"marycarpenter|16-hole_chrom|sonneratia_alba|changingseasons|"
    r"mana_-_glas|kengo_box|cream_on_fanclub|asashoryu_fight|"
    r"dried_soba_noodles|wakkanai_montage|wikitreff_002|"
    r"chemin_de_ronde_muraille_long|russell_falls|"
    r"og%c3%b3rki_w_trakcie_kiszenia|arboretum\.westonbirt|"
    r"galeries_lafayette_haussmann|carnaval-festival|wine_grapes03|"
    r"bundesarchiv_bild_183-1990-1003-400)",
    re.I,
)

STOP_WORDS = {
    "der",
    "die",
    "das",
    "und",
    "von",
    "in",
    "im",
    "am",
    "an",
    "auf",
    "zu",
    "de",
    "des",
    "du",
    "la",
    "le",
    "les",
    "of",
    "the",
    "and",
    "st",
    "sankt",
    "saint",
    "stadt",
    "city",
    "museum",
    "park",
    "see",
    "lake",
    "schloss",
    "castle",
    "kirche",
    "church",
    "altstadt",
    "zentrum",
    "center",
    "wanderung",
    "route",
    "trail",
}

DROP_REASONS = {
    "empty",
    "orphan",
    "bad_format",
    "known_generic",
    "duplicate_overuse",
    "weak_duplicate",
}


def parse_poi_line(line: str) -> dict[str, Any] | None:
    if "{id:" not in line:
        return None
    match = re.search(r"\{(id:[^}]*)\}", line)
    if not match:
        return None
    body = match.group(1)
    poi: dict[str, Any] = {}
    for key, value in FIELD_STR.findall(body):
        poi[key] = value.replace('\\"', '"')
    for key, value in FIELD_NUM.findall(body):
        if key in poi:
            continue
        poi[key] = float(value) if "." in value else int(value)
    return poi if "id" in poi and "name" in poi else None


def extract_pois(html_path: Path) -> list[dict[str, Any]]:
    content = html_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+allPOIs\s*=\s*\[(.*?)\n\];", content, re.S)
    if not match:
        match = re.search(r"(?:var|let|const)\s+allPOIs\s*=\s*\[(.*?)\];", content, re.S)
    if not match:
        return []
    pois = []
    for line in match.group(1).splitlines():
        poi = parse_poi_line(line)
        if poi:
            pois.append(poi)
    return pois


def normalize(value: str) -> str:
    value = urllib.parse.unquote(str(value)).lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def meaningful_tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in normalize(value).split():
            if len(token) >= 4 and token not in STOP_WORDS:
                tokens.add(token)
    return tokens


def image_filename(url: str) -> str:
    match = re.search(r"/commons/(?:thumb/)?(?:[^/]+/){0,2}([^/]+?)(?:/\d+px-|$)", url)
    if match:
        return urllib.parse.unquote(match.group(1))
    return urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)


def classify(
    cc: str,
    pid_text: str,
    url: str,
    poi_by_id: dict[int, dict[str, Any]],
    url_counts: Counter[str],
    max_duplicate: int,
) -> tuple[list[str], dict[str, Any]]:
    reasons: list[str] = []
    details: dict[str, Any] = {}
    if not url:
        return ["empty"], details

    try:
        pid = int(pid_text)
    except ValueError:
        return ["orphan"], details

    poi = poi_by_id.get(pid)
    if not poi:
        return ["orphan"], details

    lower_url = url.lower()
    filename = image_filename(url)
    filename_norm = normalize(filename)
    poi_tokens = meaningful_tokens(
        str(poi.get("name", "")),
        str(poi.get("location", "")),
        str(poi.get("region", "")),
    )
    filename_tokens = set(filename_norm.split())
    overlap = poi_tokens & filename_tokens
    substring_hit = any(token in filename_norm for token in poi_tokens)
    duplicate_count = url_counts[url]

    if BAD_EXT_RE.search(lower_url) or BAD_URL_RE.search(lower_url):
        reasons.append("bad_format")
    if KNOWN_GENERIC_RE.search(lower_url):
        reasons.append("known_generic")
    if duplicate_count > max_duplicate:
        reasons.append("duplicate_overuse")
    elif duplicate_count > 1 and not (overlap or substring_hit):
        reasons.append("weak_duplicate")

    details.update(
        {
            "cc": cc,
            "poi_id": pid,
            "poi_name": poi.get("name", ""),
            "location": poi.get("location", ""),
            "filename": filename,
            "duplicate_count": duplicate_count,
            "token_overlap": sorted(overlap),
        }
    )
    return reasons, details


def load_photos(cc: str) -> dict[str, str]:
    path = ROOT / f"photos_{cc}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_photos(cc: str, photos: dict[str, str]) -> None:
    json_path = ROOT / f"photos_{cc}.json"
    js_path = ROOT / f"photos_{cc}.js"
    payload = json.dumps(photos, ensure_ascii=False, separators=(",", ":"))
    json_path.write_text(payload + "\n", encoding="utf-8")
    js_path.write_text(
        "window.__PHOTO_BASELINE__ = window.__PHOTO_BASELINE__ || {};\n"
        f"window.__PHOTO_BASELINE__['{cc}'] = {payload};\n",
        encoding="utf-8",
    )


def coord_cluster_count(pois: list[dict[str, Any]]) -> int:
    counts: Counter[tuple[float, float]] = Counter()
    for poi in pois:
        lat = poi.get("lat")
        lng = poi.get("lng")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            counts[(round(float(lat), 4), round(float(lng), 4))] += 1
    return sum(1 for count in counts.values() if count > 1)


def write_audit_summary(
    pois_by_cc: dict[str, list[dict[str, Any]]],
    photos_by_cc: dict[str, dict[str, str]],
    suspicious_urls: int,
    removed_suspicious_urls: int,
) -> None:
    per_country = []
    for cc, pois in pois_by_cc.items():
        poi_count = len(pois)
        baseline_count = len(photos_by_cc.get(cc, {}))
        coverage = round((baseline_count / poi_count * 100), 1) if poi_count else 0
        per_country.append(
            {
                "cc": cc,
                "label": CC_LABELS.get(cc, cc),
                "pois": poi_count,
                "baseline_photos": baseline_count,
                "coverage_pct": coverage,
                "coord_cluster_locations": coord_cluster_count(pois),
            }
        )

    all_names = Counter()
    for pois in pois_by_cc.values():
        all_names.update(normalize(str(poi.get("name", ""))) for poi in pois)

    total_pois = sum(item["pois"] for item in per_country)
    total_photos = sum(item["baseline_photos"] for item in per_country)
    summary = {
        "generated_at": dt.date.today().isoformat(),
        "totals": {
            "countries": len(per_country),
            "pois": total_pois,
            "baseline_photos": total_photos,
            "with_baseline": total_photos,
            "orphan_photos": 0,
            "exact_name_dups": sum(1 for name, count in all_names.items() if name and count > 1),
            "coord_cluster_locations": sum(item["coord_cluster_locations"] for item in per_country),
            "suspicious_urls": suspicious_urls,
            "removed_suspicious_urls": removed_suspicious_urls,
            "coverage_pct": round((total_photos / total_pois * 100), 1) if total_pois else 0,
        },
        "cluster_hotspots": sorted(
            per_country,
            key=lambda item: item["coord_cluster_locations"],
            reverse=True,
        )[:5],
        "lowest_coverage": sorted(per_country, key=lambda item: item["coverage_pct"])[:5],
    }
    (ROOT / "audit-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_report(report: dict[str, Any]) -> None:
    (ROOT / "photo_trust_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Photo Trust Report",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Mode: {report['mode']}",
        f"- Before: {report['totals']['before']}",
        f"- After: {report['totals']['after']}",
        f"- Dropped: {report['totals']['dropped']}",
        "",
        "## Reasons",
    ]
    for reason, count in sorted(report["reasons"].items(), key=lambda item: item[0]):
        lines.append(f"- {reason}: {count}")
    lines.extend(["", "## Countries"])
    for item in report["countries"]:
        lines.append(
            f"- {item['cc']}: {item['before']} -> {item['after']} "
            f"(dropped {item['dropped']}, coverage {item['coverage_pct']}%)"
        )
    (ROOT / "photo_trust_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="rewrite photos JSON/JS files")
    parser.add_argument("--max-duplicate", type=int, default=2)
    args = parser.parse_args()

    pois_by_cc = {
        cc: extract_pois(ROOT / html_name)
        for html_name, cc in HTML_TO_CC.items()
    }
    photos_by_cc = {cc: load_photos(cc) for cc in HTML_TO_CC.values()}

    global_url_counts: Counter[str] = Counter()
    for photos in photos_by_cc.values():
        global_url_counts.update(photos.values())

    reasons_counter: Counter[str] = Counter()
    sample_by_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    country_rows: list[dict[str, Any]] = []
    cleaned_by_cc: dict[str, dict[str, str]] = {}

    for cc, photos in photos_by_cc.items():
        poi_by_id = {int(poi["id"]): poi for poi in pois_by_cc.get(cc, [])}
        keep: dict[str, str] = {}
        dropped = 0
        for pid_text, url in photos.items():
            reasons, details = classify(cc, pid_text, url, poi_by_id, global_url_counts, args.max_duplicate)
            if reasons:
                for reason in reasons:
                    reasons_counter[reason] += 1
                    if len(sample_by_reason[reason]) < 20:
                        sample = dict(details)
                        sample["url"] = url
                        sample_by_reason[reason].append(sample)
            if set(reasons) & DROP_REASONS:
                dropped += 1
                continue
            keep[pid_text] = url

        cleaned_by_cc[cc] = keep
        poi_count = len(pois_by_cc.get(cc, []))
        country_rows.append(
            {
                "cc": cc,
                "before": len(photos),
                "after": len(keep),
                "dropped": dropped,
                "pois": poi_count,
                "coverage_pct": round((len(keep) / poi_count * 100), 1) if poi_count else 0,
            }
        )

    if args.apply:
        for cc, photos in cleaned_by_cc.items():
            write_photos(cc, photos)
        write_audit_summary(
            pois_by_cc,
            cleaned_by_cc,
            suspicious_urls=0,
            removed_suspicious_urls=sum(reasons_counter.values()),
        )

    report = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "mode": "apply" if args.apply else "dry-run",
        "max_duplicate": args.max_duplicate,
        "totals": {
            "before": sum(row["before"] for row in country_rows),
            "after": sum(row["after"] for row in country_rows),
            "dropped": sum(row["dropped"] for row in country_rows),
            "unique_urls_before": len(global_url_counts),
            "unique_urls_after": len(Counter(url for photos in cleaned_by_cc.values() for url in photos.values())),
        },
        "reasons": dict(reasons_counter),
        "samples": sample_by_reason,
        "countries": country_rows,
    }
    write_report(report)

    print(
        f"{report['mode']}: {report['totals']['before']} -> "
        f"{report['totals']['after']} photos "
        f"(dropped {report['totals']['dropped']})"
    )
    for reason, count in sorted(reasons_counter.items()):
        print(f"  {reason}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
