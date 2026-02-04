# 🗺️ Jahresguide 2026 - Interaktive Karte

Eine interaktive Web-App für Events, Familienaktivitäten und Sehenswürdigkeiten in der Bodenseeregion, Ostschweiz, Liechtenstein, Tessin und Graubünden.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 🗺️ **Interaktive Karte** mit allen 100+ Locations
- 🔍 **Suchfunktion** nach Name, Ort, Region
- 📂 **Kategorie-Filter**: Festivals, Volksfeste, Kultur, Sport, Familie, Sehenswürdigkeiten, Weihnachtsmärkte
- 📅 **Monats-Filter** für zeitbasierte Events
- ⭐ **Highlight-Modus** für die besten Events 2026
- 📍 **Google Maps Integration** für Routenplanung
- 🔗 **Direkte Website-Links** zu allen Events

## 🎯 Kategorien

| Kategorie | Icon | Anzahl |
|-----------|------|--------|
| Festivals & Konzerte | 🎵 | 13 |
| Volksfeste & Messen | 🎪 | 13 |
| Sport-Events | ⚽ | 10 |
| Kultur & Ausstellungen | 🎭 | 6 |
| Familienaktivitäten | 👨‍👩‍👧 | 15 |
| Sehenswürdigkeiten | 🏛️ | 11 |
| Weihnachtsmärkte | 🎄 | 6 |

## 🚀 Installation

### Lokal ausführen

```bash
# Repository klonen
git clone https://github.com/DEIN-USERNAME/jahresguide-2026.git
cd jahresguide-2026

# Dependencies installieren
pip install -r requirements.txt

# App starten
streamlit run app.py
```

### Online via Streamlit Cloud

Die App ist auch online verfügbar unter:
**[jahresguide-2026.streamlit.app](https://jahresguide-2026.streamlit.app)**

## 📸 Screenshots

### Interaktive Karte
Die Karte zeigt alle Events und Aktivitäten mit farbcodierten Markern je nach Kategorie.

### Sidebar Filter
Einfache Filterung nach Kategorien, Monaten und Highlights.

### Detail-Popups
Klick auf einen Marker zeigt Details wie Datum, Preis, Beschreibung und direkte Links.

## 🎪 Highlight Events 2026

- 🎵 **OpenAir St. Gallen** (25.-28. Juni) - Twenty One Pilots
- 🎵 **Moon & Stars Locarno** (9.-19. Juli) - Neil Young, Jamiroquai
- 🎵 **Street Parade Zürich** (8. August) - 1 Million Teilnehmer
- 🏛️ **100 Jahre Flugplatz Altenrhein** (28.-30. August) - Flugshow
- ⚽ **Eidg. Schützenfest Chur** (Juni-Juli) - 36'000 Schützen
- 🎭 **79. Locarno Film Festival** (5.-15. August) - Piazza Grande

## 🛠️ Technologie

- **Frontend**: Streamlit
- **Karte**: Folium + streamlit-folium
- **Daten**: Pandas DataFrame
- **Styling**: Custom CSS (Pompeii-Style)

## 📄 Datenquellen

Alle Daten basieren auf dem **Jahresguide 2026** - einer Zusammenstellung von Events und Aktivitäten in der Region.

## 🤝 Contributing

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei.

---

Made with ❤️ für die Bodenseeregion, Ostschweiz, Tessin und Graubünden
