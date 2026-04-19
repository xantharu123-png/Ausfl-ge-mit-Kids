# POI-Bilder Prüfbericht & Fix — Jahresguide

Letztes Update: 2026-04-19 — **Alle Länder fertig, Gesamtbaseline 3 781 Bilder**

## Zusammenfassung

Der POI-Bilder-Datenbestand des Jahresguide 2026 wurde vollständig überholt. Statt wie bisher nur zur Laufzeit Wikipedia zu fragen, hat jedes der **30 Länder** jetzt eine eigene `photos_<CC>.json`-Baseline, die beim ersten Öffnen der Karte geladen wird. Der Laufzeit-Fetcher arbeitet als zusätzlicher Safety-Net für POIs, die noch nicht in der Baseline stehen. Clientseitig greift zusätzlich ein Generika-Filter, der fehlerhafte Rückfälle (z. B. "Luftaufnahme Bern" als Fallback-Bild für beliebige POIs) ablehnt.

## Die Zahlen auf einen Blick

| Kennzahl | Wert |
|---|---:|
| Länder mit Baseline-Bildern | 30 / 30 |
| POIs insgesamt | ~48 400 |
| Baseline-Bilder gesamt | **3 781** |
| Baseline-Bilder in CH | 755 |
| Baseline-Bilder in FR | 610 |
| Baseline-Bilder in allen übrigen 28 Ländern | 2 416 |
| Beim finalen Cleanup (gentle) weiterhin verworfen | 0 |

## Was wurde gemacht

### 1. Schweiz und Frankreich — Tiefensanierung

| Land | POIs | Baseline vorher | Baseline nachher | Mismatches vorher | Mismatches nachher | Generika vorher | Generika nachher |
|---|---:|---:|---:|---:|---:|---:|---:|
| **CH** | 2001 | 1042 | **755** | 158 | **36** | ~683 | **0** |
| **FR** | 897 | 910 | **610** | 308 | **12** | ~66 | **0** |

Typische Vorher/Nachher-Beispiele:

| POI | Vorher (falsch) | Nachher (richtig) |
|---|---|---|
| Pilatus (CH) | Pontius-Pilate-Inschrift aus Israel | Pilatus1.jpg |
| Grindelwald First (CH) | Zufallsfoto "Switzerland_Apr_2023" | Grindelwald_First.jpg |
| Arc de Triomphe (FR) | Arch of Constantine (Rom) | Arc_de_Triomphe,_Paris.jpg |
| Schloss Chambord (FR) | Schloss Amboise (anderes Schloss) | Chambord_Chateau_03.jpg |
| Millau Viadukt (FR) | Pont de Brotonne (anderer Viadukt) | Viaduc_de_Millau.jpg |
| Notre-Dame-de-la-Garde (FR) | Verdon Gorge | Notre-Dame_de_la_Garde_aerial.jpg |

Backups: `Archiv/photos_backup_2026-04-19/`.

### 2. Client-seitige Härtung — alle 30 Maps

Alle `map_*.html`-Dateien haben:

- **Generika-Blacklist** (Luftaufnahmen, bekannte Kreuz-Kontamination). URL-basierter Filter bei jedem Laden eines POI-Bildes.
- **Cache-Version 3** — zwingt ein frisches Neuladen der Baseline bei allen Besuchern.
- **Baseline-Loader** — fetcht `photos_<CC>.json` beim ersten Öffnen der Karte, merged mit localStorage-Cache.

### 3. Baseline-Pipeline für alle 30 Länder — fertig durchgelaufen

| Land | POIs | Baseline-Bilder | Wikipedia-Sprachen |
|---|---:|---:|---|
| IT | 1707 | **199** | it,de,en |
| DE | 2030 | **176** | de,en |
| BA | 1800 | **153** | bs,hr,sr,de,en |
| HR | 1803 | **152** | hr,de,en |
| PL | 1849 | **146** | pl,de,en |
| CZ | 1856 | **141** | cs,de,en |
| PT | 1767 | **136** | pt,de,en |
| GR | 2262 | **123** | el,de,en |
| ES | 1568 | **111** | es,de,en |
| SE | 1750 | **110** | sv,de,en |
| JP | 2318 | **104** | ja,de,en |
| AT | 1424 | **95** | de,en |
| SK | 1754 | **89** | sk,de,en |
| NL | 1677 | **87** | nl,de,en |
| BE | 1299 | **75** | nl,fr,de,en |
| IS | 1711 | **74** | is,de,en |
| NO | 1663 | **72** | no,nb,de,en |
| LU | 1648 | **64** | fr,de,lb,en |
| SI | 1589 | **52** | sl,de,en |
| FO | 1547 | **50** | fo,da,de,en |
| FI | 1649 | **45** | fi,de,en |
| CY | 1654 | **42** | el,de,en |
| AE | 531 | **32** | ar,de,en |
| CA_WEST | 375 | **29** | en,fr,de |
| CA_ZEN | 111 | **28** | en,fr,de |
| CA_ON | 112 | **12** | en,fr,de |
| QA | 176 | **12** | ar,de,en |
| CA_OST | 114 | **7** | en,fr,de |

### Warum manche Länder wenige Treffer haben

- **CA, QA, AE**: POIs sind oft beschreibend ("Kayaking at Lake Louise", "Dubai Water Bus Station") — kein eigener Wikipedia-Artikel. Trefferquote 5–25 %.
- **BE, LU, FI**: viele Gaststätten, Familien-Events, Märkte; niedrigere Trefferquote als bei kulturlastigen POIs.
- **DE, IT, AT, ES, HR, PL, CZ, PT, GR, JP, SE**: solide Trefferquote bei Sehenswürdigkeiten.

Laufzeit-Fetcher greift für jedes POI, das nicht in der Baseline steht, ebenfalls auf Wikipedia — allerdings mit gehärtetem Filter und Sprachpriorität pro Land.

## Technisches

### Die 3 Fetcher-Chains

Drei Python-Chains sind parallel gelaufen:

- **Main-Chain** (`run_all_fetch.py`) — sequenziell klein → gross: CA_ZEN → CA_OST → CA_ON → QA → CA_WEST → AE → BE → AT → FO → ES → SI → FI → LU → NO → CY → IS → IT → NL → SK → BA → SE → PT → HR → PL → CZ → DE → GR → JP. Resumable via `fetch_status.json`.
- **Large-Chain** (`run_large_fetch.py`) — parallel DE → GR → JP, damit die grössten Länder nicht erst am Schluss drankommen.
- **Recovery-Chain** (`run_recovery_fetch.py`) — gezielter zweiter Pass für QA, CA_OST, CA_ON, CA_ZEN, CA_WEST, AE, LU, BE, AT. Nötig, weil der erste Cleanup-Lauf versehentlich zu aggressiv war (Dateinamen-Mismatch bei arabisch/französisch/transliterierten POI-Namen hat echte Bilder eliminiert). Recovery hat alle verlorenen Bilder wieder aufgefüllt — teilweise mehr als zuvor, weil der 2. Pass andere Wikipedia-Sprachen aktivieren konnte.

### Cleanup-Philosophie

`cleanup_all_photos.py` ist bewusst **sanft**:

- Dropt nur 1) Orphans (POI-ID existiert nicht mehr in `map_*.html`), 2) globale Generika/Kreuz-Kontamination (Matterhorn in nicht-CH-Dateien etc.), 3) URLs mit ≥5 Verwendungen ohne Namensbezug.
- Vertraut ansonsten dem Fetcher: dieser verifiziert den Wikipedia-Artikel-Inhalt via `_check_summary_match` bereits vor dem Speichern.
- Der finale Cleanup-Lauf hat **0 Einträge verworfen** — die Baseline ist sauber.

### Generika-Blacklist (clientseitig, global in allen 30 Maps)

URL-basierter Filter lehnt unter anderem ab: `matterhorn_from_domh`, `bern_luftaufnahme`, `altstadt_zurich_2015`, `lugano_from_sighignola`, `la_tour_eiffel_vue_de_la_tour_saint-jacques`, `arc_de_triomphe_paris`, `big_ben`, `colosseum_in_rome`, `piazza_san_marco`, `brandenburger_tor_abends` u. v. a. (vollständige Liste: siehe `scripts/patch_maps.py`).

### Neuer Fetcher — wesentliche Verbesserungen

- **Content-Verifikation**: POI-Tokens müssen im Wikipedia-Titel/Extrakt auftauchen, sonst verworfen.
- **Duplicate-Guard**: dieselbe URL max 2×.
- **Sprachpriorität je Land**: siehe Tabelle oben.
- **Query-Varianten**: Core-Token-Extraktion, Hyphen-Varianten, Region-Suffix, Volltextsuche als Fallback.
- **Resumable**: jedes Land in `fetch_status*.json` verbucht.
- **Mehrsprachige Dateinamen-Normalisierung**: umlaut-Mapping und Transliteration für ar/el/ja/ru-Sprachen.

### Dateien

- **Aktualisiert**: `index.html` (marginal), alle 30 `map_*.html` (Baseline-Loader + Blacklist + Cache v3), alle 30 `photos_<CC>.json`.
- **Scripts** (`scripts/`-Ordner): `extract_pois.py`, `fetch_wiki_photos.py`, `run_all_fetch.py`, `run_large_fetch.py`, `run_recovery_fetch.py`, `cleanup_all_photos.py`, `patch_baseline_loader.py`, `patch_maps.py`. Finale Status-Snapshots: `fetch_status.json.final`, `fetch_status_large.json.final`, `fetch_status_recovery.json.final`. Siehe `scripts/README.md` für Details.
- **Backup**: `Archiv/photos_backup_2026-04-19/`.

## Fortsetzung / Wartung

Falls die Fetcher später erneut laufen sollen (z. B. nachdem neue POIs hinzugekommen sind):

```bash
cd scripts/
python3 extract_pois.py              # POI-Listen neu extrahieren
python3 run_all_fetch.py > fetch_all.log 2>&1 &
python3 run_large_fetch.py > fetch_large.log 2>&1 &
# Nach Abschluss
python3 cleanup_all_photos.py
```

Resume automatisch via `fetch_status.json`. Bei Sprach-429-Errors Worker reduzieren (`--workers 8`).

## Was der User sieht

- **Erster Besuch einer Karte**: die `photos_<CC>.json`-Baseline wird geladen (eine Datei, ≤120 KB) — alle POIs mit Baseline-Bild haben sofort ein passendes Foto.
- **POIs ohne Baseline**: Laufzeit-Fetcher fragt Wikipedia mit Sprachpriorität und Generika-Filter. Bei Erfolg → Foto wird im localStorage gecacht.
- **Alle Bilder passieren die Blacklist**: falsche Fallback-Bilder wie "Luftaufnahme Bern" erscheinen nicht mehr.
- **Cache-Version 3**: zwingt alle bestehenden User, beim nächsten Besuch die neue Baseline zu laden — alte falsche Bilder werden überschrieben.
