#!/usr/bin/env python3
"""Recovery-Fetcher: holt Bilder für die Länder, die beim aggressiven Cleanup
am 09:22 Einträge verloren haben.

Die betroffenen Länder sind bereits in fetch_status.json als "done" markiert,
aber photos_<CC>.json hat weniger Einträge als der Fetcher ursprünglich gefunden hat.
Diese Script startet für sie einen gezielten Zweit-Fetch und ergänzt die Lücken.

Läuft parallel zu run_all_fetch.py / run_large_fetch.py — keine Sprach-Überlappung
mit FI/SE/NO (Main-Chain derzeit) oder JP (Large-Chain).
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

SESSION = Path('/sessions/elegant-great-turing')
STATUS_FILE = SESSION / 'fetch_status_recovery.json'

# Betroffene Länder (verloren Einträge beim 09:22 Cleanup)
ORDER = ['QA', 'CA_OST', 'CA_ON', 'CA_ZEN', 'CA_WEST', 'AE', 'LU', 'BE', 'AT']


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

        print(f'\n=== [R-{cc}] Recovery startet ({before} Bilder) ===', flush=True)
        # 8 workers — vorsichtiger, da 2 andere Chains parallel laufen
        subprocess.run(
            ['python3', str(SESSION / 'fetch_wiki_photos.py'),
             cc, '--only-worthy', '--workers', '8'],
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
        print(f'=== [R-{cc}] fertig: +{after-before}, {dur}s ===', flush=True)

    status['finished'] = datetime.now().isoformat()
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
