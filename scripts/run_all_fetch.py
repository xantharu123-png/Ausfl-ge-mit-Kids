#!/usr/bin/env python3
"""Orchestriert fetch_wiki_photos.py für alle Länder.

Reihenfolge: klein zuerst, damit schnell sichtbare Ergebnisse. Läuft seriell,
aber fetch_wiki_photos selbst nutzt Thread-Pool. Status wird fortlaufend in
fetch_status.json geschrieben.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

SESSION = Path('/sessions/elegant-great-turing')
STATUS_FILE = SESSION / 'fetch_status.json'

# Reihenfolge: klein (schnelle Ergebnisse) → mittel → gross.
# Bewertung nach "würdigen" Kandidaten-Zahlen aus pois_*.json.
ORDER = [
    # Tier small (<500)
    'CA_ZEN', 'CA_OST', 'CA_ON', 'QA', 'CA_WEST', 'AE',
    # Tier medium (1200-1700)
    'BE', 'AT', 'FO', 'ES', 'SI', 'FI', 'LU', 'NO', 'CY', 'IS',
    # Tier large (1700-2000)
    'IT', 'NL', 'SK', 'BA', 'SE', 'PT', 'HR', 'PL', 'CZ',
    # Tier very large (>2000)
    'DE', 'GR', 'JP',
]


def load_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {'started': datetime.now().isoformat(), 'countries': {}}


def save_status(status):
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))


def count_photos(cc):
    p = Path(f'/sessions/elegant-great-turing/mnt/Jahresguide/photos_{cc}.json')
    if not p.exists():
        return 0
    try:
        return len(json.loads(p.read_text()))
    except Exception:
        return 0


def main():
    status = load_status()

    for cc in ORDER:
        if status['countries'].get(cc, {}).get('done'):
            print(f'[{cc}] übersprungen (bereits fertig)')
            continue

        before = count_photos(cc)
        t0 = time.time()
        status['countries'][cc] = {
            'started': datetime.now().isoformat(),
            'before': before,
            'done': False,
        }
        save_status(status)

        print(f'\n=== [{cc}] Fetch startet ({before} Bilder schon im Cache) ===',
              flush=True)
        try:
            subprocess.run(
                [
                    'python3',
                    str(SESSION / 'fetch_wiki_photos.py'),
                    cc, '--only-worthy', '--workers', '12',
                ],
                check=False,
            )
        except Exception as e:
            print(f'[{cc}] Fehler: {e}')

        after = count_photos(cc)
        dur = int(time.time() - t0)
        status['countries'][cc].update({
            'finished': datetime.now().isoformat(),
            'after': after,
            'added': after - before,
            'duration_s': dur,
            'done': True,
        })
        save_status(status)
        print(f'=== [{cc}] fertig: +{after-before} Bilder, {dur}s ===', flush=True)

    status['finished'] = datetime.now().isoformat()
    save_status(status)
    print('\n=== ALLE LÄNDER FERTIG ===')


if __name__ == '__main__':
    main()
