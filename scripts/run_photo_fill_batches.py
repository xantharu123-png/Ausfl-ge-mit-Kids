#!/usr/bin/env python3
"""Run resumable POI photo fill batches.

This orchestrates the strict Wikimedia verifier in small waves and stores
checked POI ids locally, so repeated runs keep moving forward without relying
on shifting offsets after photos have been added.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import fetch_verified_photos as fetcher
from photo_trust_audit import HTML_TO_CC, ROOT, extract_pois, load_photos, write_photos


STATUS_PATH = ROOT / "photo_fill_status.json"

WAVES: dict[str, dict[str, Any]] = {
    "title-worthy": {
        "categories": "sehenswuerdigkeit,kultur,weihnachten",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-family": {
        "categories": "familie",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-sport": {
        "categories": "sport",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-events": {
        "categories": "festival,volksfest",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-all": {
        "categories": None,
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-clean-worthy": {
        "categories": "sehenswuerdigkeit,kultur,weihnachten",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "title-clean-family": {
        "categories": "familie",
        "title_only": True,
        "skip_search": False,
        "skip_geo": False,
        "min_score": 3.5,
    },
    "search-worthy": {
        "categories": "sehenswuerdigkeit,kultur,weihnachten",
        "title_only": False,
        "skip_search": False,
        "skip_geo": True,
        "min_score": 7.0,
    },
    "search-family": {
        "categories": "familie",
        "title_only": False,
        "skip_search": False,
        "skip_geo": True,
        "min_score": 7.0,
    },
    "wikidata-worthy": {
        "categories": "sehenswuerdigkeit,kultur,weihnachten",
        "title_only": True,
        "skip_search": True,
        "skip_geo": True,
        "wikidata_search": True,
        "min_score": 5.0,
    },
    "wikidata-family": {
        "categories": "familie",
        "title_only": True,
        "skip_search": True,
        "skip_geo": True,
        "wikidata_search": True,
        "min_score": 5.0,
    },
    "wikidata-geo-worthy": {
        "categories": "sehenswuerdigkeit,kultur,weihnachten",
        "title_only": True,
        "skip_search": True,
        "skip_geo": True,
        "wikidata_search": True,
        "min_score": 5.0,
    },
    "wikidata-geo-family": {
        "categories": "familie",
        "title_only": True,
        "skip_search": True,
        "skip_geo": True,
        "wikidata_search": True,
        "min_score": 5.0,
    },
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_status() -> dict[str, Any]:
    if STATUS_PATH.exists():
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    return {"started_at": now_iso(), "updated_at": now_iso(), "waves": {}}


def save_status(status: dict[str, Any]) -> None:
    status["updated_at"] = now_iso()
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def country_codes(value: str) -> list[str]:
    if value.upper() == "ALL":
        return list(dict.fromkeys(HTML_TO_CC.values()))
    codes = []
    aliases = {"CA_E": "CA_OST", "CA_O": "CA_OST", "CA_Z": "CA_ZEN", "CA_W": "CA_WEST"}
    for raw in value.split(","):
        cc = aliases.get(raw.strip().upper(), raw.strip().upper())
        if cc not in set(HTML_TO_CC.values()):
            raise SystemExit(f"Unknown country code: {raw}")
        codes.append(cc)
    return list(dict.fromkeys(codes))


def html_for_country(cc: str) -> Path:
    html_name = next(name for name, mapped_cc in HTML_TO_CC.items() if mapped_cc == cc)
    return ROOT / html_name


def category_set(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def country_stats(cc: str, categories: set[str] | None, checked_ids: set[str]) -> dict[str, Any]:
    pois = extract_pois(html_for_country(cc))
    photos = load_photos(cc)
    candidates = [poi for poi in pois if str(poi["id"]) not in photos]
    if categories is not None:
        candidates = [poi for poi in candidates if str(poi.get("category")) in categories]
    unchecked = [poi for poi in candidates if str(poi["id"]) not in checked_ids]
    return {
        "cc": cc,
        "pois": len(pois),
        "photos": len(photos),
        "coverage": (len(photos) / len(pois)) if pois else 1,
        "candidates": len(candidates),
        "unchecked": len(unchecked),
    }


def ensure_wave_country(status: dict[str, Any], wave: str, cc: str) -> dict[str, Any]:
    wave_state = status.setdefault("waves", {}).setdefault(wave, {})
    return wave_state.setdefault(cc, {"checked_ids": [], "runs": [], "found": 0})


def run_country_batch(
    cc: str,
    wave: str,
    wave_config: dict[str, Any],
    state: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    checked_ids = set(str(pid) for pid in state.get("checked_ids", []))
    categories = category_set(wave_config.get("categories"))
    pois = extract_pois(html_for_country(cc))
    photos = load_photos(cc)
    before_count = len(photos)
    used_urls = Counter(photos.values())

    candidates = [poi for poi in pois if str(poi["id"]) not in photos]
    if categories is not None:
        candidates = [poi for poi in candidates if str(poi.get("category")) in categories]
    priority = {"sehenswuerdigkeit": 0, "kultur": 1, "weihnachten": 2, "familie": 3}
    candidates.sort(key=lambda poi: priority.get(str(poi.get("category")), 9))
    selected = [poi for poi in candidates if str(poi["id"]) not in checked_ids][: args.limit]

    print(f"[{wave}:{cc}] checking {len(selected)} POIs", flush=True)
    started = time.time()
    found: dict[str, str] = {}
    meta: dict[str, Any] = {}

    def work(poi: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
        result = fetcher.find_photo_for_poi(
            cc,
            poi,
            used_urls,
            args.max_duplicate,
            float(wave_config.get("min_score", args.min_score)),
            allow_search=not (wave_config.get("title_only") or wave_config.get("skip_search")),
            allow_geo=not (wave_config.get("title_only") or wave_config.get("skip_geo")),
            allow_wikidata_search=bool(wave_config.get("wikidata_search")),
        )
        return poi, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(work, poi) for poi in selected]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            poi, result = future.result()
            pid = str(poi["id"])
            checked_ids.add(pid)
            if result:
                url = result["url"]
                if used_urls[url] < args.max_duplicate:
                    found[pid] = url
                    used_urls[url] += 1
                    meta[pid] = {"poi_name": poi.get("name"), "location": poi.get("location"), **result}
            if index % 25 == 0:
                print(f"[{wave}:{cc}] {index}/{len(selected)} checked, +{len(found)}", flush=True)

    if args.apply and found:
        photos.update(found)
        write_photos(cc, dict(sorted(photos.items(), key=lambda item: int(item[0]))))

    report = {
        "wave": wave,
        "cc": cc,
        "mode": "apply" if args.apply else "dry-run",
        "checked": len(selected),
        "found": len(found),
        "before": before_count,
        "after": before_count + len(found),
        "remaining_unchecked": max(0, len(candidates) - len(checked_ids)),
        "seconds": round(time.time() - started, 1),
        "items": meta,
    }

    if args.apply:
        state["checked_ids"] = sorted(checked_ids, key=lambda value: int(value))
        state["found"] = int(state.get("found", 0)) + len(found)
        state.setdefault("runs", []).append(
            {
                "at": now_iso(),
                "checked": report["checked"],
                "found": report["found"],
                "seconds": report["seconds"],
            }
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=sorted(WAVES), default="title-worthy")
    parser.add_argument("--countries", default="ALL")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--max-runs", type=int, default=8)
    parser.add_argument("--max-duplicate", type=int, default=2)
    parser.add_argument("--min-score", type=float, default=3.5)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    status = load_status()
    wave_config = WAVES[args.wave]
    codes = country_codes(args.countries)

    rows = []
    for cc in codes:
        state = ensure_wave_country(status, args.wave, cc)
        rows.append(country_stats(cc, category_set(wave_config.get("categories")), set(state.get("checked_ids", []))))
    rows.sort(key=lambda item: (item["unchecked"] <= 0, item["coverage"], -item["unchecked"], item["cc"]))

    reports = []
    for row in rows:
        if len(reports) >= args.max_runs:
            break
        if row["unchecked"] <= 0:
            continue
        state = ensure_wave_country(status, args.wave, row["cc"])
        report = run_country_batch(row["cc"], args.wave, wave_config, state, args)
        reports.append(report)
        save_status(status)
        print(
            f"[{args.wave}:{row['cc']}] found {report['found']} in {report['seconds']}s; "
            f"remaining unchecked {report['remaining_unchecked']}",
            flush=True,
        )

    summary = {
        "wave": args.wave,
        "mode": "apply" if args.apply else "dry-run",
        "runs": len(reports),
        "checked": sum(report["checked"] for report in reports),
        "found": sum(report["found"] for report in reports),
        "seconds": round(sum(report["seconds"] for report in reports), 1),
        "reports": reports,
    }
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    (ROOT / f"photo_fill_report_{args.wave}_{stamp}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"total: runs {summary['runs']}, checked {summary['checked']}, "
        f"found {summary['found']} in {summary['seconds']}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
