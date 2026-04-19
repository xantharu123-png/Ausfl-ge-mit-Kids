# POI- & Bilder-Audit — Familienguide 2026

**Stand:** 2026-04-19 (nach „alles fixen"-Pass)

## Vorher / Nachher

| Metrik | Vorher | Nachher | Δ |
|---|---:|---:|---:|
| POIs gesamt | 52,432 | 51,591 | -841 |
| Baseline-Bilder | 3,781 | 3,295 | -486 |
| Coverage % | 7.2 | 6.4 | -0.8 |
| Exakt-Duplikate | 277 | 0 | -277 |
| Orphan-Fotos | 24 | 0 | -24 |
| Verdächtige URLs | 6 | 0 | -6 |
| Koord-Cluster | 2656 | 2460 | -196 |

Bilder-Coverage sinkt absichtlich, weil **427 mehrfach-genutzte Stadt-Default-Bilder** (z. B. 45× „Altstadt Zürich", 14× „Bordeaux Bourse de nuit") aus der Baseline entfernt wurden. Diese POIs holen jetzt zur Laufzeit ein präziseres Bild aus Wikipedia statt das undifferenzierte Stadt-Default zu zeigen.

## Pro Land — POIs vorher/nachher und Cluster-Hotspots

| Land | POIs vorher | POIs nachher | Δ POIs | Fotos | Coverage | Cluster verbleiben |
|---|---:|---:|---:|---:|---:|---:|
| VAE (AE) | 984 | 977 | -7 | 32 | 3.3% | 75 |
| Österreich (AT) | 2002 | 1990 | -12 | 95 | 4.8% | 48 |
| Bosnien (BA) | 2006 | 1987 | -19 | 153 | 7.7% | 52 |
| Belgien (BE) | 2000 | 1957 | -43 | 73 | 3.7% | 316 |
| Kanada Ontario (CA_ON) | 160 | 156 | -4 | 12 | 7.7% | 21 |
| Kanada Ost (CA_OST) | 140 | 139 | -1 | 7 | 5.0% | 16 |
| Kanada West (CA_WEST) | 492 | 478 | -14 | 27 | 5.6% | 46 |
| Kanada Zentral (CA_ZEN) | 140 | 138 | -2 | 27 | 19.6% | 19 |
| Schweiz (CH) | 2001 | 1975 | -26 | 360 | 18.2% | 105 |
| Zypern (CY) | 2002 | 1970 | -32 | 41 | 2.1% | 110 |
| Tschechien (CZ) | 2002 | 1978 | -24 | 139 | 7.0% | 51 |
| Deutschland (DE) | 2504 | 2501 | -3 | 176 | 7.0% | 16 |
| Spanien (ES) | 2001 | 1953 | -48 | 111 | 5.7% | 149 |
| Finnland (FI) | 2003 | 1971 | -32 | 44 | 2.2% | 81 |
| Färöer (FO) | 2001 | 1949 | -52 | 50 | 2.6% | 78 |
| Frankreich (FR) | 2062 | 2061 | -1 | 544 | 26.4% | 18 |
| Griechenland (GR) | 2502 | 2471 | -31 | 122 | 4.9% | 68 |
| Kroatien (HR) | 2001 | 1993 | -8 | 151 | 7.6% | 30 |
| Island (IS) | 2003 | 1970 | -33 | 73 | 3.7% | 91 |
| Italien (IT) | 2103 | 2084 | -19 | 196 | 9.4% | 91 |
| Japan (JP) | 2979 | 2874 | -105 | 101 | 3.5% | 435 |
| Luxemburg (LU) | 2002 | 1974 | -28 | 64 | 3.2% | 97 |
| Niederlande (NL) | 2004 | 1992 | -12 | 87 | 4.4% | 29 |
| Norwegen (NO) | 2000 | 1960 | -40 | 71 | 3.6% | 34 |
| Polen (PL) | 2002 | 1983 | -19 | 144 | 7.3% | 88 |
| Portugal (PT) | 2002 | 1973 | -29 | 135 | 6.8% | 34 |
| Katar (QA) | 327 | 327 | +0 | 12 | 3.7% | 13 |
| Schweden (SE) | 2002 | 1845 | -157 | 107 | 5.8% | 22 |
| Slowenien (SI) | 2001 | 1979 | -22 | 52 | 2.6% | 133 |
| Slowakei (SK) | 2004 | 1986 | -18 | 89 | 4.5% | 94 |
| **Summe** | **52,432** | **51,591** | **-841** | **3,295** | **6.4%** | **2,460** |

## Was wurde gemacht

1. **24 Orphan-Fotos** in `photos_FR.json` entfernt (POI-IDs, die im allPOIs-Array nicht mehr existierten).
2. **6 verdächtige URLs** mit generischem `vue_aérienne`-Token aus FR (5) und CH (1) gelöscht.
3. **427 heavily-reused URLs** (≥5× wiederverwendet) blacklisted – pro URL wird nur der POI mit bestem Token-Match zum URL-Filename behalten:
   - CH: −390 Baseline-Einträge (Altstadt Zürich, Appenzell, Säntis usw.)
   - FR: −37 Baseline-Einträge (Bordeaux Bourse, Subé Fountain, Toulouse-Montage)
4. **Multi-Country-Dedupe**:
   - **461 exakte name+location-Duplikate** entfernt (war 277, höher weil Normalisierung auch Ziffern strippt)
   - **380 Koord-Cluster-Duplikate** zusammengeführt (gleiche 4-Dez-Koord + ähnliche Namen / „Panorama"-Suffix)
   - Insgesamt **−841 POIs**, hauptsächlich SE (−157), JP (−105), FO (−52), ES (−48), BE (−43)
5. **Audit-Heuristik korrigiert**: CH wird nicht mehr fälschlich für eigene Schweizer Landmarks als „kontaminiert" gemeldet (Homeland-Whitelist pro Token).

## Verbleibende Cluster-Hotspots

| Land | Cluster | POIs | Bemerkung |
|---|---:|---:|---|
| Japan | 435 | 2874 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Belgien | 316 | 1957 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Spanien | 149 | 1953 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Slowenien | 133 | 1979 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Zypern | 110 | 1970 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Schweiz | 105 | 1975 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Luxemburg | 97 | 1974 | echte enge Nachbarschaft – konservativ stehen gelassen |
| Slowakei | 94 | 1986 | echte enge Nachbarschaft – konservativ stehen gelassen |

Die ~2.460 verbleibenden Cluster sind echte Nachbarn (Tokio dicht, Brüssel-Innenstadt, Madrid-Centro), die keine identische Namensbasis haben.

## Coverage-Schlusslichter

| Land | Coverage | Fotos / POIs |
|---|---:|---:|
| Zypern | 2.1% | 41 / 1970 |
| Finnland | 2.2% | 44 / 1971 |
| Färöer | 2.6% | 50 / 1949 |
| Slowenien | 2.6% | 52 / 1979 |
| Luxemburg | 3.2% | 64 / 1974 |
| VAE | 3.3% | 32 / 977 |
| Japan | 3.5% | 101 / 2874 |
| Norwegen | 3.6% | 71 / 1960 |

Diese Länder hängen am Laufzeit-Fetcher. Nächster sinnvoller Schritt: gezielter Wikipedia-Refetch.

## Backups

Pro modifizierter Datei wurde ein `.bak_*` neben die Originaldatei geschrieben:

- `*.html.bak_dedupe_all` — vor Multi-Country-Dedupe
- `photos_FR.json.bak_orphans` — vor Orphan-Cleanup
- `photos_*.json.bak_reuse` — vor Reuse-URL-Blacklist
- `POI_Audit_BEFORE.json` — Audit-Snapshot vor Änderungen

---

Skripte: `dedupe_all.py`, `audit_pois.py` · Roh-JSON: `POI_Audit.json`