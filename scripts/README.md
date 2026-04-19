# POI-Foto-Pipeline — Scripts

Werkzeuge für das Pflegen der `photos_<CC>.json`-Baselines.

## Dateien

| Script | Zweck |
|---|---|
| `extract_pois.py` | Extrahiert POI-Listen aus `map_*.html` → `pois_<CC>.json`. Einmalig nötig wenn sich POI-Daten ändern. |
| `fetch_wiki_photos.py` | Holt für einen einzelnen Ländercode passende Wikipedia-Bilder. Hat Duplicate-Guard, Generika-Blacklist und Content-Verifikation. |
| `run_all_fetch.py` | Orchestriert `fetch_wiki_photos.py` sequenziell für alle 28 Länder (klein → gross). Schreibt `fetch_status.json`, resumable. |
| `run_large_fetch.py` | Parallel-Chain für DE/GR/JP. Läuft gleichzeitig mit `run_all_fetch.py`. |
| `run_recovery_fetch.py` | Zweiter Fetch-Pass für Länder, die beim ersten aggressiven Cleanup Einträge verloren haben (QA, CA_*, AE, LU, BE, AT). Nur bei Bedarf. |
| `cleanup_all_photos.py` | Entfernt Orphan-Einträge, Generika-Duplikate und länderfremde Kontamination. Nicht aggressiv; vertraut der Fetcher-Verifikation. |
| `patch_baseline_loader.py` | Fügt in `map_*.html` den `photos_<CC>.json`-Loader ein. Idempotent. |
| `patch_maps.py` | Patched den clientseitigen `_isMapOrBadImage`-Filter und Cache-Version. |

## Typischer Workflow

```bash
# 1. POI-Daten aus Map-HTMLs extrahieren (einmalig)
python3 extract_pois.py

# 2. Fetcher parallel laufen lassen
python3 run_all_fetch.py > fetch_all.log 2>&1 &
python3 run_large_fetch.py > fetch_large.log 2>&1 &

# 3. Status prüfen
cat fetch_status.json        # Hauptchain
cat fetch_status_large.json  # Parallele grosse Länder

# 4. Nach Abschluss: sanften Cleanup laufen lassen
python3 cleanup_all_photos.py
```

## Wichtige Flags von `fetch_wiki_photos.py`

- `--only-worthy` — überspringt Sport/Volksfest/Familie (kaum Wikipedia-Artikel)
- `--workers 12` — parallele HTTP-Worker (12 respektiert Wikipedias Richtlinien)
- `--limit 100` / `--offset 200` — Stückweise abarbeiten, z. B. für Tests

## Wikipedia-Etikette

- User-Agent ist gesetzt: `JahresguidePhotoRefresher/1.0 (https://jahresguide.app; contact miroslav.mikulic@gmail.com) Python/3`
- Max 12 parallele Worker pro Ländercode. Zwei Chains gleichzeitig sind OK, weil unterschiedliche Wikipedia-Sprachversionen.
- Bei 429-Fehlern: Worker reduzieren.

## Resumable

`run_all_fetch.py` merkt sich fertige Länder in `fetch_status.json`. Neustart überspringt diese. Für einzelne Länder neu fetchen:

```bash
rm mnt/Jahresguide/photos_XX.json
# In fetch_status.json den Eintrag für XX löschen
python3 run_all_fetch.py
```
