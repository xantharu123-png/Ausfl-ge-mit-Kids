import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="🌍 Europa Familien-Guide 2026", page_icon="🌍", layout="wide")

# ============================================================================
# REGIONEN MIT BOUNDING BOXES
# ============================================================================
REGIONS = {
    "canarias": {"name": "🇮🇨 Kanaren", "center": [28.3, -15.8], "zoom": 8},
    "spain": {"name": "🇪🇸 Spanien", "center": [40.0, -3.5], "zoom": 6},
    "italy": {"name": "🇮🇹 Italien", "center": [42.5, 12.5], "zoom": 6},
    "croatia": {"name": "🇭🇷 Kroatien", "center": [44.5, 16.0], "zoom": 7},
    "switzerland": {"name": "🇨🇭 Schweiz", "center": [46.8, 8.2], "zoom": 8},
    "germany": {"name": "🇩🇪 Deutschland", "center": [51.0, 10.0], "zoom": 6}
}

# ============================================================================
# KATEGORIEN
# ============================================================================
CATEGORIES = {
    "festival": {"icon": "🎵", "color": "#e94560", "name": "Festivals"},
    "volksfest": {"icon": "🎪", "color": "#ff6b35", "name": "Volksfeste"},
    "kultur": {"icon": "🎭", "color": "#9b59b6", "name": "Kultur"},
    "familie": {"icon": "👨‍👩‍👧", "color": "#2ecc71", "name": "Familie"},
    "sehenswuerdigkeit": {"icon": "🏛️", "color": "#f39c12", "name": "Sehenswürdigkeiten"},
    "weihnachten": {"icon": "🎄", "color": "#c0392b", "name": "Weihnachtsmärkte"},
    "strand": {"icon": "🏖️", "color": "#00cec9", "name": "Strände"},
    "spielplatz": {"icon": "🛝", "color": "#a29bfe", "name": "Spielplätze"},
    "rodelbahn": {"icon": "🛷", "color": "#74b9ff", "name": "Rodelbahnen"},
    "wasserpark": {"icon": "🌊", "color": "#0984e3", "name": "Wasserparks"},
    "tierpark": {"icon": "🦁", "color": "#00b894", "name": "Tierparks"},
    "freizeitpark": {"icon": "🎢", "color": "#e17055", "name": "Freizeitparks"},
    "natur": {"icon": "🏞️", "color": "#55a630", "name": "Natur"}
}

# ============================================================================
# POI DATEN - ALLE REGIONEN
# ============================================================================
ALL_POIS = [
    # ==================== KANARISCHE INSELN ====================
    {"id":"can001","name":"Karneval Santa Cruz","cat":"festival","lat":28.4698,"lng":-16.2549,"region":"canarias","month":"2","date":"11.-22. Feb 2026","desc":"Zweitgrößter Karneval der Welt! Thema: Ritmos Latinos.","price":"Gratis","img":"https://images.unsplash.com/photo-1551907034-d5976cd79e5a?w=400","family":"Tagesparaden ideal für Familien"},
    {"id":"can002","name":"Karneval Las Palmas","cat":"festival","lat":28.1335,"lng":-15.4343,"region":"canarias","month":"2","date":"23. Jan - 1. März","desc":"Thema Las Vegas. Kinderkarneval am 15. Feb.","price":"Gratis","img":"https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400","family":"Spezieller Kinderkarneval-Tag"},
    {"id":"can010","name":"Siam Park","cat":"wasserpark","lat":28.0733,"lng":-16.7261,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Weltbester Wasserpark! Thai-Thema, 1km Lazy River, Wave Palace.","price":"Erw. €38-47, Kind €26-34","img":"https://images.unsplash.com/photo-1565375085685-fe7f5d9fa3c0?w=400","family":"Kinderbereich 'The Lost City'"},
    {"id":"can011","name":"Aqualand Costa Adeje","cat":"wasserpark","lat":28.0825,"lng":-16.7217,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Delfinshow inklusive (15:30), Dragonland Kinderbereich.","price":"Erw. €36, Kind €29","img":"https://images.unsplash.com/photo-1526336024786-1abd38c8f4f2?w=400","family":"Gratis Shuttle, Delfinshow"},
    {"id":"can020","name":"Loro Parque","cat":"tierpark","lat":28.4086,"lng":-16.5639,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Europas bester Zoo! Orcas, Pinguine, 500+ Papageienarten.","price":"Erw. €39-42, <6 gratis","img":"https://images.unsplash.com/photo-1557178985-891ca9b9b01c?w=400","family":"Kinderlandia Spielplatz"},
    {"id":"can021","name":"Palmitos Park","cat":"tierpark","lat":27.8161,"lng":-15.5456,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Größtes Schmetterlingshaus Europas, Delphinarium.","price":"Erw. €34, Kind €25","img":"https://images.unsplash.com/photo-1452570053594-1b985d6ea890?w=400","family":"Schmetterlinge faszinieren"},
    {"id":"can022","name":"Oasis Wildlife","cat":"tierpark","lat":28.1847,"lng":-14.1667,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Größtes Dromedarreservat Europas, Safari-Zug.","price":"Erw. €40, Kind €25.50","img":"https://images.unsplash.com/photo-1547970810-dc1eac37d174?w=400","family":"Giraffenfütterung möglich"},
    {"id":"can030","name":"Playa de Las Teresitas","cat":"strand","lat":28.5089,"lng":-16.1875,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Goldener Saharasand, Palmen, sehr ruhiges Wasser.","price":"Gratis","img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400","family":"Perfekt für Kleinkinder"},
    {"id":"can031","name":"Playa de Amadores","cat":"strand","lat":27.7833,"lng":-15.7167,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Künstliche Lagune, Blue Flag, behindertengerecht.","price":"Gratis","img":"https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400","family":"Blue Flag, extrem sicher"},
    {"id":"can032","name":"Caleta de Fuste","cat":"strand","lat":28.3989,"lng":-13.8556,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Bester Strand für Kleinkinder auf Fuerteventura!","price":"Gratis","img":"https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=400","family":"Geschützte Bucht, flach"},
    {"id":"can040","name":"Teide Seilbahn","cat":"sehenswuerdigkeit","lat":28.2567,"lng":-16.6217,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Spaniens höchster Berg. ACHTUNG: <3 Jahre verboten!","price":"Erw. €41, Kind €20.50","img":"https://images.unsplash.com/photo-1580910527557-cd3ba5354805?w=400","family":"Ab 3 Jahren erlaubt"},
    {"id":"can041","name":"Timanfaya","cat":"natur","lat":29.0117,"lng":-13.7600,"region":"canarias","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Feuerberge Lanzarote, Busrundfahrt, Kamelreiten.","price":"€12, Kamel €6-12","img":"https://images.unsplash.com/photo-1584824486509-112e4181ff6b?w=400","family":"Kamelreiten begeistert Kinder"},

    # ==================== SPANIEN & BALEAREN ====================
    {"id":"esp001","name":"La Tomatina","cat":"volksfest","lat":39.4197,"lng":-0.7911,"region":"spain","month":"8","date":"26. Aug 2026","desc":"Weltgrößte Tomatenschlacht in Buñol!","price":"€15","img":"https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400","family":"Für ältere Kinder/Teens"},
    {"id":"esp002","name":"Feria de Abril","cat":"volksfest","lat":37.3733,"lng":-6.0010,"region":"spain","month":"4","date":"21.-26. April","desc":"Sevillas größtes Fest - Flamenco, Pferde, Sherry.","price":"Gratis","img":"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400","family":"Pferdeparaden spannend"},
    {"id":"esp003","name":"Las Fallas","cat":"festival","lat":39.4699,"lng":-0.3763,"region":"spain","month":"3","date":"15.-19. März","desc":"UNESCO Welterbe - Riesenfiguren werden verbrannt.","price":"Gratis","img":"https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400","family":"Gehörschutz für Kinder!"},
    {"id":"esp004","name":"La Mercè Barcelona","cat":"festival","lat":41.3851,"lng":2.1734,"region":"spain","month":"9","date":"20.-24. Sept","desc":"Barcelonas Stadtfest mit Menschentürmen.","price":"Gratis","img":"https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=400","family":"Castellers faszinieren"},
    {"id":"esp010","name":"PortAventura World","cat":"freizeitpark","lat":41.0866,"lng":1.1544,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Spaniens größter Park! SésamoAventura für 0-12 Jahre.","price":"Erw. ab €43, Kind €36","img":"https://images.unsplash.com/photo-1536768139911-e290a59011e4?w=400","family":"Sesamstraße-Bereich"},
    {"id":"esp011","name":"Parque Warner","cat":"freizeitpark","lat":40.2219,"lng":-3.5928,"region":"spain","month":"3,4,5,6,7,8,9,10,11,12","date":"März-Dez","desc":"Cartoon Village, DC Super Heroes World.","price":"Ab €35","img":"https://images.unsplash.com/photo-1560969184-10fe8719e047?w=400","family":"Looney Tunes für Kleine"},
    {"id":"esp012","name":"Tibidabo Barcelona","cat":"freizeitpark","lat":41.4217,"lng":2.1186,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Wochenenden","desc":"Ältester Freizeitpark Spaniens (1901)!","price":"Erw. €35, Kind €14","img":"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400","family":"Tolle Aussicht"},
    {"id":"esp020","name":"Oceanogràfic Valencia","cat":"tierpark","lat":39.4527,"lng":-0.3475,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Europas größtes Aquarium! Einzige Belugas Europas.","price":"Erw. ~€38.90","img":"https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400","family":"Delfine & Belugas"},
    {"id":"esp021","name":"Bioparc Valencia","cat":"tierpark","lat":39.4756,"lng":-0.4097,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Zoo-Immersion - keine Barrieren sichtbar!","price":"Erw. €27-32, <4 gratis","img":"https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=400","family":"Immersives Erlebnis"},
    {"id":"esp030","name":"Sagrada Família","cat":"sehenswuerdigkeit","lat":41.4036,"lng":2.1744,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Gaudís Meisterwerk - 2026 höchste Kirche der Welt!","price":"Erw. €26-36, <11 gratis","img":"https://images.unsplash.com/photo-1583779457711-21a6e86cb678?w=400","family":"2-3 Monate vorher buchen!"},
    {"id":"esp031","name":"Alhambra Granada","cat":"sehenswuerdigkeit","lat":37.1760,"lng":-3.5881,"region":"spain","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Maurische Palastanlage - UNESCO Welterbe.","price":"Erw. €21, Kind 3-11 gratis","img":"https://images.unsplash.com/photo-1591973708472-6b2c085c0fbd?w=400","family":"2 Monate vorher buchen!"},
    {"id":"esp040","name":"Cala Galdana","cat":"strand","lat":39.9361,"lng":3.9575,"region":"spain","month":"5,6,7,8,9,10","date":"Mai-Okt","desc":"Menorcas bester Familienstrand - Hufeisenbucht.","price":"Gratis","img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400","family":"Sehr flach, perfekt für Babys"},
    {"id":"esp041","name":"Platja de Muro","cat":"strand","lat":39.7917,"lng":3.1167,"region":"spain","month":"5,6,7,8,9,10","date":"Mai-Okt","desc":"Mallorcas längster Sandstrand, sehr flach.","price":"Gratis","img":"https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400","family":"Flaches Wasser"},

    # ==================== ITALIEN ====================
    {"id":"ita001","name":"Karneval Venedig","cat":"festival","lat":45.4343,"lng":12.3388,"region":"italy","month":"2","date":"31. Jan - 17. Feb","desc":"Thema: Olympus. Maskenbasteln-Workshops für Kinder.","price":"Gratis (Straße)","img":"https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400","family":"Masken basteln"},
    {"id":"ita002","name":"Karneval Viareggio","cat":"festival","lat":43.8688,"lng":10.2421,"region":"italy","month":"2","date":"1.-21. Feb","desc":"30m hohe Pappmaché-Wagen! Toskana.","price":"Ab €16.50","img":"https://images.unsplash.com/photo-1551907034-d5976cd79e5a?w=400","family":"Riesenwagen faszinieren"},
    {"id":"ita010","name":"Gardaland","cat":"freizeitpark","lat":45.4557,"lng":10.7167,"region":"italy","month":"3,4,5,6,7,8,9,10,11","date":"März-Nov","desc":"Italiens bester Park! Peppa Pig Land, 40+ Attraktionen.","price":"Online ab €44","img":"https://images.unsplash.com/photo-1536768139911-e290a59011e4?w=400","family":"Peppa Pig für Kleine"},
    {"id":"ita011","name":"Mirabilandia","cat":"freizeitpark","lat":44.3378,"lng":12.2619,"region":"italy","month":"4,5,6,7,8,9,10","date":"April-Okt","desc":"Größter Park Italiens! Dinoland, Nickelodeon.","price":"Variabel","img":"https://images.unsplash.com/photo-1560969184-10fe8719e047?w=400","family":"Dinoland für Dino-Fans"},
    {"id":"ita020","name":"Alpine Bob Merano","cat":"rodelbahn","lat":46.6667,"lng":11.2500,"region":"italy","month":"6,7,8,9","date":"Sommer","desc":"1.100m Bahn bis 12m über dem Boden!","price":"~€8-10","img":"https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400","family":"Sommer & Winter"},
    {"id":"ita021","name":"Klausberg-Flitzer","cat":"rodelbahn","lat":47.0333,"lng":12.1167,"region":"italy","month":"6,7,8,9","date":"Sommer","desc":"1.800m mit 360°-Drehungen! Südtirol.","price":"~€10-12","img":"https://images.unsplash.com/photo-1605540436563-5bca919ae766?w=400","family":"Adrenalinkick"},
    {"id":"ita030","name":"Jamaica Beach","cat":"strand","lat":45.5003,"lng":10.6089,"region":"italy","month":"6,7,8,9","date":"Sommer","desc":"Gardasee - Karibik-Feeling am See!","price":"Gratis","img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400","family":"Einzigartiger See-Strand"},
    {"id":"ita031","name":"La Pelosa","cat":"strand","lat":40.9558,"lng":8.2014,"region":"italy","month":"5,6,7,8,9","date":"Mai-Sept","desc":"Sardiniens berühmtester - extrem flach!","price":"€3.50 (Sommer)","img":"https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400","family":"Ikonisch flach"},
    {"id":"ita040","name":"Kolosseum","cat":"sehenswuerdigkeit","lat":41.8902,"lng":12.4922,"region":"italy","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Antikes Amphitheater - <18 GRATIS!","price":"Erw. €16-22, <18 gratis","img":"https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400","family":"Geschichte anfassen"},
    {"id":"ita041","name":"Aquarium Genua","cat":"tierpark","lat":44.4095,"lng":8.9260,"region":"italy","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Italiens größtes! 'Nacht mit Haien' möglich.","price":"Erw. €22-37, <3 gratis","img":"https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400","family":"Hai-Übernachtung!"},
    {"id":"ita050","name":"Weihnachtsmarkt Bozen","cat":"weihnachten","lat":46.4983,"lng":11.3548,"region":"italy","month":"11,12","date":"28. Nov - 6. Jan","desc":"Italiens größter mit 130+ Ständen.","price":"Gratis","img":"https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=400","family":"Magische Atmosphäre"},
    {"id":"ita051","name":"Weihnachtsmarkt Meran","cat":"weihnachten","lat":46.6712,"lng":11.1616,"region":"italy","month":"11,12","date":"28. Nov - 6. Jan","desc":"80 Stände am Fluss, Eislaufbahn.","price":"Gratis","img":"https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=400","family":"Eislaufen für Kinder"},

    # ==================== KROATIEN ====================
    {"id":"cro001","name":"Plitvicer Seen","cat":"natur","lat":44.8654,"lng":15.5820,"region":"croatia","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"UNESCO! 16 Seen, Boot + Zug inklusive.","price":"Haupt €40/€25, Neben €10/€5","img":"https://images.unsplash.com/photo-1555990538-1e74b3c594a9?w=400","family":"Route A (2-3h) einfachste"},
    {"id":"cro002","name":"Krka Nationalpark","cat":"natur","lat":43.8011,"lng":15.9619,"region":"croatia","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Schwimmen erlaubt (Juni-Sept)!","price":"€40/€20","img":"https://images.unsplash.com/photo-1596395819471-9c31f2fc4eb9?w=400","family":"Schwimmen bei Wasserfällen"},
    {"id":"cro003","name":"Brijuni Safari","cat":"tierpark","lat":44.9167,"lng":13.7667,"region":"croatia","month":"4,5,6,7,8,9,10","date":"April-Okt","desc":"Safari + 125 Mio Jahre alte Dinosaurierspuren!","price":"Erw. €40, Kind €16","img":"https://images.unsplash.com/photo-1547970810-dc1eac37d174?w=400","family":"Safari + Dinos!"},
    {"id":"cro010","name":"Istralandia","cat":"wasserpark","lat":45.3367,"lng":13.5617,"region":"croatia","month":"6,7,8,9","date":"Juni-Sept","desc":"Kroatiens bester! 23 Rutschen, Geburtstagskinder GRATIS!","price":"Erw. €34, Kind €27","img":"https://images.unsplash.com/photo-1565375085685-fe7f5d9fa3c0?w=400","family":"Geburtstagskinder gratis!"},
    {"id":"cro020","name":"Paradise Beach Rab","cat":"strand","lat":44.8333,"lng":14.7333,"region":"croatia","month":"6,7,8,9","date":"Sommer","desc":"KROATIENS BESTER für Kleinkinder!","price":"Gratis","img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400","family":"#1 für Babys"},
    {"id":"cro021","name":"Queen's Beach Nin","cat":"strand","lat":44.2333,"lng":15.1833,"region":"croatia","month":"6,7,8,9","date":"Sommer","desc":"3km Sandstrand, Heilschlamm!","price":"Gratis","img":"https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400","family":"Heilschlamm + flach"},
    {"id":"cro022","name":"Zlatni Rat","cat":"strand","lat":43.2586,"lng":16.6314,"region":"croatia","month":"6,7,8,9","date":"Sommer","desc":"Ikonisches 'Goldenes Horn' auf Brač.","price":"Gratis","img":"https://images.unsplash.com/photo-1520454974749-611b7248ffdb?w=400","family":"Ikonisch, Kiesel"},
    {"id":"cro030","name":"Diokletianpalast","cat":"sehenswuerdigkeit","lat":43.5081,"lng":16.4402,"region":"croatia","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"24/7","desc":"UNESCO, Game of Thrones Drehort.","price":"Gelände gratis, Keller €8","img":"https://images.unsplash.com/photo-1555990538-1e74b3c594a9?w=400","family":"GoT für ältere Kids"},
    {"id":"cro031","name":"Zadar Meeresorgel","cat":"sehenswuerdigkeit","lat":44.1194,"lng":15.2233,"region":"croatia","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Wellen erzeugen Musik! + Lichtshow.","price":"Gratis","img":"https://images.unsplash.com/photo-1596395819471-9c31f2fc4eb9?w=400","family":"Musik aus dem Meer!"},
    {"id":"cro032","name":"Pula Arena","cat":"sehenswuerdigkeit","lat":44.8734,"lng":13.8498,"region":"croatia","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Römisches Amphitheater, Sommerkonzerte.","price":"Familie (2+3) €15","img":"https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400","family":"Günstiges Familienpaket"},

    # ==================== SCHWEIZ ====================
    {"id":"ch001","name":"Basler Fasnacht","cat":"festival","lat":47.5596,"lng":7.5886,"region":"switzerland","month":"2","date":"23.-25. Feb 2026","desc":"UNESCO! Start 4:00 Uhr Morgestraich.","price":"Gratis","img":"https://images.unsplash.com/photo-1551907034-d5976cd79e5a?w=400","family":"Dienstag = Kinderfasnacht"},
    {"id":"ch002","name":"Sechseläuten Zürich","cat":"volksfest","lat":47.3654,"lng":8.5448,"region":"switzerland","month":"4","date":"17.-20. April","desc":"Böögg-Verbrennung um 18:00!","price":"Gratis","img":"https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400","family":"Kinderumzug Sonntag"},
    {"id":"ch003","name":"Montreux Jazz","cat":"festival","lat":46.4312,"lng":6.9107,"region":"switzerland","month":"7","date":"3.-18. Juli","desc":"60. Jubiläum! GRATIS Kinderbetreuung!","price":"Variabel","img":"https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=400","family":"Gratis Kinderbetreuung"},
    {"id":"ch010","name":"Fräkigaudi Pilatus","cat":"rodelbahn","lat":46.9667,"lng":8.2573,"region":"switzerland","month":"5,6,7,8,9,10","date":"Mai-Okt","desc":"LÄNGSTE der Schweiz (1.350m)!","price":"~CHF 8-10","img":"https://images.unsplash.com/photo-1605540436563-5bca919ae766?w=400","family":"<8 mit Erwachsenem"},
    {"id":"ch011","name":"Pradaschier","cat":"rodelbahn","lat":46.7750,"lng":9.5500,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"LÄNGSTE GANZJÄHRIGE (3.1km)!","price":"~CHF 15-20","img":"https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400","family":"Ganzjährig nutzbar"},
    {"id":"ch012","name":"Kronberg Bobsled","cat":"rodelbahn","lat":47.3167,"lng":9.2833,"region":"switzerland","month":"5,6,7,8,9,10","date":"Sommer","desc":"+ 25 Seilrutschen, Schatzsuche!","price":"CHF 15-23.50","img":"https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400","family":"Seilrutschen + Schatzsuche"},
    {"id":"ch020","name":"GZ Wipkingen","cat":"spielplatz","lat":47.3944,"lng":8.5278,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Zürichs BESTER! Seilklettern, Bauernhof.","price":"Gratis","img":"https://images.unsplash.com/photo-1566454825481-9c31bd88c36f?w=400","family":"Kinderbauernhof"},
    {"id":"ch030","name":"Titlis","cat":"sehenswuerdigkeit","lat":46.7717,"lng":8.4258,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Höchste Hängebrücke Europas! Schnee-Tubing ganzjährig!","price":"Ab CHF 84","img":"https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=400","family":"Ganzjährig Schnee!"},
    {"id":"ch031","name":"Pilatus","cat":"sehenswuerdigkeit","lat":46.9792,"lng":8.2542,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Steilste Zahnradbahn der Welt (48%)!","price":"Ab CHF 84","img":"https://images.unsplash.com/photo-1527095655498-b491637ecb6c?w=400","family":"Steilste Zahnradbahn!"},
    {"id":"ch040","name":"Technorama","cat":"familie","lat":47.5000,"lng":8.7667,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"EUROPAS GRÖSSTES Science Center! 500+ Experimente.","price":"Erw. CHF 29, Kind CHF 18","img":"https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=400","family":"Perfekt für Regentage"},
    {"id":"ch041","name":"Zoo Zürich","cat":"tierpark","lat":47.3833,"lng":8.5667,"region":"switzerland","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Masoala-Halle (Regenwald). 380 Arten.","price":"Erw. CHF 29, <6 gratis","img":"https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=400","family":"Masoala einzigartig"},
    {"id":"ch042","name":"Conny-Land","cat":"freizeitpark","lat":47.6333,"lng":9.0167,"region":"switzerland","month":"4,5,6,7,8,9,10","date":"April-Okt","desc":"Schweizer größter Park, Seelöwenshows.","price":"CHF 39-49","img":"https://images.unsplash.com/photo-1536768139911-e290a59011e4?w=400","family":"Seelöwenshows"},
    {"id":"ch050","name":"Weihnachtsmarkt Basel","cat":"weihnachten","lat":47.5596,"lng":7.5886,"region":"switzerland","month":"11,12","date":"20. Nov - 23. Dez","desc":"Ältester & größter der Schweiz (180+ Stände).","price":"Gratis","img":"https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=400","family":"Schweizer Tradition"},
    {"id":"ch051","name":"Christkindlimarkt Zürich","cat":"weihnachten","lat":47.3782,"lng":8.5401,"region":"switzerland","month":"11,12","date":"20. Nov - 24. Dez","desc":"Europas größter Indoor-Markt!","price":"Gratis","img":"https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=400","family":"Indoor = wetterfest"},

    # ==================== DEUTSCHLAND ====================
    {"id":"de001","name":"Oktoberfest","cat":"volksfest","lat":48.1310,"lng":11.5495,"region":"germany","month":"9,10","date":"19. Sept - 4. Okt","desc":"Weltgrößtes Volksfest! FAMILIENTAGE: Di 22.9. & 29.9.","price":"Eintritt gratis","img":"https://images.unsplash.com/photo-1505489435671-80b5c327b7b3?w=400","family":"Dienstage = Familientage"},
    {"id":"de010","name":"Europa-Park","cat":"freizeitpark","lat":48.2660,"lng":7.7220,"region":"germany","month":"3,4,5,6,7,8,9,10,11,12,1","date":"März - Jan","desc":"DEUTSCHLANDS BESTER! 100+ Attraktionen.","price":"Erw. €67-76, Kind €56.50","img":"https://images.unsplash.com/photo-1536768139911-e290a59011e4?w=400","family":"Geburtstagskinder bis 12 GRATIS!"},
    {"id":"de011","name":"LEGOLAND","cat":"freizeitpark","lat":48.4257,"lng":10.2987,"region":"germany","month":"3,4,5,6,7,8,9,10,11","date":"März-Nov","desc":"23 Mio LEGO-Steine! NEU: PEPPA PIG Park!","price":"Kind €58, Erw. €64","img":"https://images.unsplash.com/photo-1560969184-10fe8719e047?w=400","family":"LEGO + PEPPA PIG"},
    {"id":"de012","name":"Phantasialand","cat":"freizeitpark","lat":50.7996,"lng":6.8789,"region":"germany","month":"3,4,5,6,7,8,9,10,11,12,1","date":"März-Jan","desc":"6 Themenbereiche, weltbestes Theming!","price":"Ab €29, <4 gratis","img":"https://images.unsplash.com/photo-1569959220744-ff553533f492?w=400","family":"Weltklasse Theming"},
    {"id":"de013","name":"Ravensburger Spieleland","cat":"freizeitpark","lat":47.7333,"lng":9.6167,"region":"germany","month":"4,5,6,7,8,9,10","date":"April-Okt","desc":"70+ Attraktionen für 2-12 Jahre!","price":"Variabel","img":"https://images.unsplash.com/photo-1566454825481-9c31bd88c36f?w=400","family":"Speziell für 2-12"},
    {"id":"de020","name":"Therme Erding","cat":"wasserpark","lat":48.2949,"lng":11.9054,"region":"germany","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"WELTGRÖSSTE THERME! 27 Rutschen.","price":"Ab €22, mit Galaxy €35-45","img":"https://images.unsplash.com/photo-1565375085685-fe7f5d9fa3c0?w=400","family":"27 Rutschen alle Level"},
    {"id":"de021","name":"Tropical Islands","cat":"wasserpark","lat":52.0392,"lng":13.7463,"region":"germany","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"WELTGRÖSSTER INDOOR-Wasserpark!","price":"Erw. ~€45-50, Kind ~€35-40","img":"https://images.unsplash.com/photo-1526336024786-1abd38c8f4f2?w=400","family":"Tropisch ganzjährig"},
    {"id":"de030","name":"Alpsee Bergwelt","cat":"rodelbahn","lat":47.5333,"lng":10.2333,"region":"germany","month":"4,5,6,7,8,9,10,11","date":"April-Nov","desc":"LÄNGSTE DEUTSCHLANDS (~3km)! 10 Min Fahrt!","price":"Variabel","img":"https://images.unsplash.com/photo-1605540436563-5bca919ae766?w=400","family":"10 Min Fahrspaß!"},
    {"id":"de031","name":"Blombergbahn","cat":"rodelbahn","lat":47.7167,"lng":11.5833,"region":"germany","month":"4,5,6,7,8,9,10","date":"April-Okt","desc":"ZWEI 1.300m Bahnen - Wettrennen möglich!","price":"Variabel","img":"https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400","family":"Wettrennen!"},
    {"id":"de040","name":"Westerland Sylt","cat":"strand","lat":54.9050,"lng":8.3117,"region":"germany","month":"5,6,7,8,9","date":"Sommer","desc":"5km Strand, ikonische Strandkörbe.","price":"Strandkorb €10-25/Tag","img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400","family":"Strandkorb-Erlebnis"},
    {"id":"de041","name":"Binz Rügen","cat":"strand","lat":54.4000,"lng":13.6167,"region":"germany","month":"5,6,7,8,9","date":"Sommer","desc":"5km weißer Sand, Sicherheitsarmbänder!","price":"Gratis","img":"https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400","family":"Armbänder für Kinder"},
    {"id":"de050","name":"Schloss Neuschwanstein","cat":"sehenswuerdigkeit","lat":47.5576,"lng":10.7498,"region":"germany","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Disneys Vorbild! <18 GRATIS, 2-3 Monate buchen!","price":"Erw. €15-17.50, <18 gratis","img":"https://images.unsplash.com/photo-1534313314376-a72289b6181e?w=400","family":"<18 gratis aber Ticket nötig!"},
    {"id":"de051","name":"Miniatur Wunderland","cat":"familie","lat":53.5436,"lng":9.9887,"region":"germany","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"WELTGRÖSSTE MODELLBAHN! 200 Knöpfe für Kinder!","price":"Erw. €22-25, Kind €13","img":"https://images.unsplash.com/photo-1565098772267-60af42b81ef2?w=400","family":"200 Knöpfe drücken!"},
    {"id":"de060","name":"Insel Mainau","cat":"familie","lat":47.7050,"lng":9.1917,"region":"germany","month":"3,4,5,6,7,8,9,10","date":"März-Okt","desc":"Blumeninsel mit 1.000 Schmetterlingen!","price":"Variabel","img":"https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400","family":"Schmetterlingshaus"},
    {"id":"de061","name":"SEA LIFE Konstanz","cat":"tierpark","lat":47.6594,"lng":9.1772,"region":"germany","month":"1,2,3,4,5,6,7,8,9,10,11,12","date":"Ganzjährig","desc":"Unterwasserwelt am Bodensee.","price":"Variabel","img":"https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400","family":"Perfekt für Regentage"},
    {"id":"de062","name":"Affenberg Salem","cat":"tierpark","lat":47.7667,"lng":9.2833,"region":"germany","month":"3,4,5,6,7,8,9,10,11","date":"März-Nov","desc":"Begehbares Affengehege! Füttern erlaubt!","price":"Variabel","img":"https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=400","family":"Affen füttern!"},
    {"id":"de070","name":"Christkindlesmarkt Nürnberg","cat":"weihnachten","lat":49.4540,"lng":11.0770,"region":"germany","month":"11,12","date":"27. Nov - 24. Dez","desc":"BERÜHMTESTER deutscher Weihnachtsmarkt!","price":"Gratis","img":"https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=400","family":"Kinderweihnachtsmarkt"},
]

# ============================================================================
# MAP HTML GENERIEREN
# ============================================================================
def generate_map_html():
    pois_json = json.dumps(ALL_POIS)
    regions_json = json.dumps(REGIONS)
    categories_json = json.dumps(CATEGORIES)
    
    html = f'''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{{--bg:#1a1a2e;--card:#16213e;--pink:#e94560;--teal:#4ecca3;--text:#eee;--border:#0f3460}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:var(--bg);color:var(--text);height:100vh;overflow:hidden}}
.container{{display:flex;height:100vh}}
.sidebar{{width:380px;background:var(--card);display:flex;flex-direction:column;border-right:2px solid var(--border)}}
.logo{{padding:12px;background:linear-gradient(135deg,var(--pink),#9b59b6);text-align:center}}
.logo h1{{font-size:1.2em;margin-bottom:2px}}
.logo span{{font-size:0.8em;opacity:0.9}}
.search-box{{padding:8px 12px;border-bottom:1px solid var(--border)}}
.search-box input{{width:100%;padding:8px 10px;border:none;border-radius:20px;background:var(--bg);color:var(--text);font-size:0.9em}}
.filters{{padding:6px 12px;border-bottom:1px solid var(--border)}}
.filter-row{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:5px}}
.filter-btn{{padding:4px 8px;border:none;border-radius:12px;background:var(--bg);color:var(--text);cursor:pointer;font-size:0.7em;transition:all 0.2s}}
.filter-btn:hover,.filter-btn.active{{background:var(--pink);transform:scale(1.05)}}
.month-row{{display:flex;flex-wrap:wrap;gap:2px}}
.month-btn{{padding:3px 6px;border:none;border-radius:8px;background:var(--bg);color:var(--text);cursor:pointer;font-size:0.65em}}
.month-btn:hover,.month-btn.active{{background:var(--teal)}}
.region-bar{{padding:6px 12px;border-bottom:1px solid var(--border);background:rgba(78,204,163,0.1)}}
.region-btns{{display:flex;flex-wrap:wrap;gap:3px}}
.region-btn{{padding:4px 8px;border:none;border-radius:10px;background:var(--bg);color:var(--text);cursor:pointer;font-size:0.68em;transition:all 0.2s}}
.region-btn:hover{{background:var(--teal);transform:scale(1.05)}}
.area-btn-wrap{{padding:6px 12px;border-bottom:1px solid var(--border)}}
.area-btn{{width:100%;padding:6px;background:linear-gradient(135deg,var(--pink),#9b59b6);border:none;border-radius:6px;color:white;cursor:pointer;font-size:0.8em}}
.area-btn.active{{background:linear-gradient(135deg,var(--teal),#2ecc71)}}
.counter{{padding:6px 12px;background:rgba(233,69,96,0.2);font-size:0.8em;text-align:center}}
.list{{flex:1;overflow-y:auto;padding:8px}}
.card{{background:var(--bg);border-radius:10px;margin-bottom:8px;overflow:hidden;cursor:pointer;transition:transform 0.2s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 4px 15px rgba(233,69,96,0.3)}}
.card-img{{height:100px;background-size:cover;background-position:center;position:relative}}
.card-cat{{position:absolute;top:6px;left:6px;padding:3px 8px;border-radius:10px;font-size:0.7em;font-weight:bold}}
.card-body{{padding:10px}}
.card-title{{font-size:0.95em;margin-bottom:4px;color:var(--pink)}}
.card-meta{{font-size:0.75em;opacity:0.8;margin-bottom:3px}}
.card-price{{font-size:0.8em;color:var(--teal)}}
#map{{flex:1;z-index:1}}
.leaflet-popup-content-wrapper{{background:var(--card);color:var(--text);border-radius:10px}}
.leaflet-popup-tip{{background:var(--card)}}
.popup-img{{width:100%;height:90px;object-fit:cover;border-radius:6px;margin-bottom:6px}}
.popup-title{{font-size:1em;color:var(--pink);margin-bottom:4px}}
.popup-meta{{font-size:0.8em;opacity:0.8;margin-bottom:4px}}
.popup-desc{{font-size:0.8em;margin-bottom:6px}}
.popup-price{{color:var(--teal);font-weight:bold}}
.popup-family{{background:rgba(78,204,163,0.2);padding:4px 6px;border-radius:4px;font-size:0.75em;margin-top:4px}}
@media(max-width:768px){{.sidebar{{width:100%;height:50vh}}.container{{flex-direction:column}}}}
</style>
</head><body>
<div class="container">
<div class="sidebar">
<div class="logo"><h1>🌍 Europa Familien-Guide 2026</h1><span>{len(ALL_POIS)} Aktivitäten für Familien</span></div>
<div class="search-box"><input type="text" id="search" placeholder="🔍 Suchen..."></div>
<div class="region-bar"><div class="region-btns" id="regionBtns"></div></div>
<div class="filters"><div class="filter-row" id="catBtns"></div><div class="month-row" id="monthBtns"></div></div>
<div class="area-btn-wrap"><button class="area-btn" id="areaBtn">🔍 In diesem Bereich suchen</button></div>
<div class="counter" id="counter">Lade...</div>
<div class="list" id="list"></div>
</div>
<div id="map"></div>
</div>
<script>
const POIS={pois_json};
const REGIONS={regions_json};
const CATS={categories_json};
const MONTHS=['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
let map,markers=[],fCat=null,fMonth=null,fSearch='',fArea=false,areaBounds=null;
map=L.map('map').setView([46.5,10],5);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{attribution:'© OpenStreetMap © CARTO',maxZoom:19}}).addTo(map);
const regionDiv=document.getElementById('regionBtns');
Object.entries(REGIONS).forEach(([k,v])=>{{const b=document.createElement('button');b.className='region-btn';b.textContent=v.name;b.onclick=()=>{{map.flyTo(v.center,v.zoom);fArea=false;updateAreaBtn()}};regionDiv.appendChild(b)}});
const catDiv=document.getElementById('catBtns');
Object.entries(CATS).forEach(([k,v])=>{{const b=document.createElement('button');b.className='filter-btn';b.innerHTML=v.icon+' '+v.name;b.dataset.cat=k;b.onclick=()=>{{if(fCat===k){{fCat=null;b.classList.remove('active')}}else{{document.querySelectorAll('.filter-btn').forEach(x=>x.classList.remove('active'));fCat=k;b.classList.add('active')}}render()}};catDiv.appendChild(b)}});
const monthDiv=document.getElementById('monthBtns');
MONTHS.forEach((m,i)=>{{const b=document.createElement('button');b.className='month-btn';b.textContent=m;b.onclick=()=>{{const mo=String(i+1);if(fMonth===mo){{fMonth=null;b.classList.remove('active')}}else{{document.querySelectorAll('.month-btn').forEach(x=>x.classList.remove('active'));fMonth=mo;b.classList.add('active')}}render()}};monthDiv.appendChild(b)}});
document.getElementById('search').oninput=e=>{{fSearch=e.target.value.toLowerCase();render()}};
const areaBtn=document.getElementById('areaBtn');
function updateAreaBtn(){{if(fArea){{areaBtn.textContent='✕ Bereichsfilter aufheben';areaBtn.classList.add('active')}}else{{areaBtn.textContent='🔍 In diesem Bereich suchen';areaBtn.classList.remove('active')}}}}
areaBtn.onclick=()=>{{fArea=!fArea;if(fArea)areaBounds=map.getBounds();updateAreaBtn();render()}};
map.on('moveend',()=>{{if(fArea){{areaBounds=map.getBounds();render()}}}});
function render(){{
markers.forEach(m=>map.removeLayer(m));markers=[];
const list=document.getElementById('list');list.innerHTML='';
let filtered=POIS.filter(p=>{{
if(fCat&&p.cat!==fCat)return false;
if(fMonth&&p.month&&!p.month.split(',').includes(fMonth))return false;
if(fSearch&&!p.name.toLowerCase().includes(fSearch)&&!(p.desc||'').toLowerCase().includes(fSearch))return false;
if(fArea&&areaBounds&&!areaBounds.contains([p.lat,p.lng]))return false;
return true;
}});
document.getElementById('counter').textContent=filtered.length+' Aktivitäten';
filtered.forEach(p=>{{
const cat=CATS[p.cat]||{{icon:'📍',color:'#888',name:'Sonstiges'}};
const icon=L.divIcon({{html:'<div style="background:'+cat.color+';width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;border:2px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3)">'+cat.icon+'</div>',className:'',iconSize:[28,28],iconAnchor:[14,14]}});
const m=L.marker([p.lat,p.lng],{{icon}}).addTo(map);
m.bindPopup('<img class="popup-img" src="'+p.img+'" onerror="this.src=\\'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400\\'"><div class="popup-title">'+p.name+'</div><div class="popup-meta">'+cat.icon+' '+cat.name+' · '+(p.date||'Ganzjährig')+'</div><div class="popup-desc">'+(p.desc||'')+'</div><div class="popup-price">'+(p.price||'')+'</div>'+(p.family?'<div class="popup-family">👨‍👩‍👧 '+p.family+'</div>':''),{{maxWidth:260}});
markers.push(m);
const card=document.createElement('div');card.className='card';
card.innerHTML='<div class="card-img" style="background-image:url('+p.img+')"><span class="card-cat" style="background:'+cat.color+'">'+cat.icon+' '+cat.name+'</span></div><div class="card-body"><div class="card-title">'+p.name+'</div><div class="card-meta">📅 '+(p.date||'Ganzjährig')+' · 📍 '+(REGIONS[p.region]?.name||p.region)+'</div><div class="card-price">'+(p.price||'')+'</div></div>';
card.onclick=()=>{{map.flyTo([p.lat,p.lng],12);m.openPopup()}};
list.appendChild(card);
}});
if(!fArea&&filtered.length>0&&filtered.length<50){{const bounds=L.latLngBounds(filtered.map(p=>[p.lat,p.lng]));map.fitBounds(bounds,{{padding:[50,50]}})}}
}}
render();
</script></body></html>'''
    return html

# ============================================================================
# STREAMLIT UI
# ============================================================================
st.markdown("""<style>
.stApp {background: #1a1a2e}
.stat-box {background: linear-gradient(135deg, #e94560, #9b59b6); padding: 12px; border-radius: 8px; text-align: center; color: white; margin-bottom: 5px}
.stat-num {font-size: 1.8em; font-weight: bold}
.stat-label {font-size: 0.85em; opacity: 0.9}
</style>""", unsafe_allow_html=True)

st.title("🌍 Europa Familien-Guide 2026")
st.caption(f"{len(ALL_POIS)} Aktivitäten für Familien mit Kindern 0-12 Jahre")

# Stats
by_region = {}
for p in ALL_POIS:
    r = p.get('region', 'other')
    by_region[r] = by_region.get(r, 0) + 1

cols = st.columns(7)
stats = [
    (str(len(ALL_POIS)), "Total"),
    (str(by_region.get('canarias', 0)), "🇮🇨 Kanaren"),
    (str(by_region.get('spain', 0)), "🇪🇸 Spanien"),
    (str(by_region.get('italy', 0)), "🇮🇹 Italien"),
    (str(by_region.get('croatia', 0)), "🇭🇷 Kroatien"),
    (str(by_region.get('switzerland', 0)), "🇨🇭 Schweiz"),
    (str(by_region.get('germany', 0)), "🇩🇪 Deutschland"),
]
for col, (num, label) in zip(cols, stats):
    col.markdown(f'<div class="stat-box"><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Map
components.html(generate_map_html(), height=700, scrolling=False)

st.markdown("---")
st.caption("🗺️ Klicke Region-Buttons zum Zoomen | 🔍 Filter nach Kategorie & Monat | 📍 Klicke Karten für Details")
