#!/usr/bin/env python3
"""Parallel-Fetcher für die grossen Länder (DE, GR, JP).

Läuft gleichzeitig zu run_all_fetch.py, aber bearbeitet ausschliesslich die
grössten Länder, damit diese nicht erst ganz am Schluss drankommen.
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

SESSION = Path('/sessions/elegant-great-turing')
STATUS_FILE = SESSION / 'fetch_status_large.json'

# Grosse Länder — andere Wikipedia-Sprachen als der Haupt-Chain, damit
# Wikipedia nicht an einer Sprache überlastet wird.
ORDER = ['DE', 'GR', 'JP']


def count_photos(cc):
    p = Path(f'/sessions/elegant-great-turing/mnt/Jahresguide/photos_{cc}.json')
    if not p.exists():
        return 0
    try:
        return len(json.loads(p.read_text()))
    except Exception:
        return 0


def main():
    status = {'started': datetime.now().isoformat(), 'countries': {}}
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))

    for cc in ORDER:
        before = count_photos(cc)
        t0 = time.time()
        status['countries'][cc] = {'started': datetime.now().isoformat(),
                                   'before': before, 'done': False}
        STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))

        print(f'\n=== [L-{cc}] Fetch startet ({before} Bilder) ===', flush=True)
        subprocess.run(
            ['python3', str(SESSION / 'fetch_wiki_photos.py'),
             cc, '--only-worthy', '--workers', '10'],
            check=False,
        )

        after = count_photos(cc)
        dur = int(time.time() - t0)
        status['countries'][cc].update({
            'finished': datetime.now().isoformat(),
            'after': after, 'added': after - before, 'duration_s': dur,
            'done': True,
        })
        STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))
        print(f'=== [L-{cc}] fertig: +{after-before}, {dur}s ===', flush=True)

    status['finished'] = datetime.now().isoformat()
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
