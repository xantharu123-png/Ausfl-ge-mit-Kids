import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Jahresguide 2026", page_icon="🗺️", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>#MainMenu,footer,header{visibility:hidden;}.block-container{padding:0!important;max-width:100%!important;}</style>""", unsafe_allow_html=True)

html = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--bg:#1a1a2e;--card:#16213e;--hover:#1f2b47;--teal:#4ecca3;--pink:#e94560;--orange:#f39c12;--txt:#fff;--txt2:#a0a0a0;--border:rgba(255,255,255,0.1)}
        body{font-family:system-ui,sans-serif;background:var(--bg);color:var(--txt);overflow:hidden}
        .wrap{display:flex;height:100vh}
        .side{width:400px;background:linear-gradient(180deg,#16213e,#1a1a2e);display:flex;flex-direction:column;border-right:1px solid var(--border)}
        .head{padding:14px;border-bottom:1px solid var(--border)}
        .logo{display:flex;align-items:center;gap:10px}
        .logo-i{width:40px;height:40px;background:linear-gradient(135deg,#e94560,#9b59b6);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
        .logo h1{font-size:1.1rem}
        .logo p{font-size:.6rem;color:var(--txt2)}
        .stats{display:flex;gap:10px;margin-top:8px;font-size:.65rem;color:var(--txt2)}
        .stats strong{color:var(--teal)}
        .flt{padding:8px 14px;border-bottom:1px solid var(--border)}
        .search{position:relative;margin-bottom:6px}
        .search input{width:100%;padding:7px 10px 7px 30px;background:var(--card);border:1px solid var(--border);border-radius:6px;color:var(--txt);font-size:.75rem}
        .search input:focus{outline:none;border-color:var(--pink)}
        .search::before{content:"🔍";position:absolute;left:8px;top:50%;transform:translateY(-50%);font-size:.75rem}
        .tabs{display:flex;gap:4px;flex-wrap:wrap}
        .tab{padding:3px 7px;background:var(--card);border:1px solid var(--border);border-radius:10px;font-size:.6rem;color:var(--txt2);cursor:pointer}
        .tab:hover{border-color:var(--pink)}
        .tab.on{background:var(--pink);border-color:var(--pink);color:#fff}
        .mons{padding:6px 14px;border-bottom:1px solid var(--border);display:flex;gap:3px;flex-wrap:wrap}
        .mon{padding:3px 6px;background:transparent;border:1px solid var(--border);border-radius:4px;font-size:.55rem;color:var(--txt2);cursor:pointer}
        .mon:hover{border-color:var(--teal);color:var(--teal)}
        .mon.on{background:var(--teal);border-color:var(--teal);color:#fff}
        .list{flex:1;overflow-y:auto;padding:8px}
        .list::-webkit-scrollbar{width:4px}
        .list::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
        .card{background:var(--card);border-radius:8px;margin-bottom:6px;cursor:pointer;border-left:3px solid var(--pink);transition:.2s;display:flex;overflow:hidden}
        .card:hover{background:var(--hover);transform:translateX(2px)}
        .card.on{background:rgba(233,69,96,.15)}
        .card-img{width:70px;height:70px;object-fit:cover;flex-shrink:0}
        .card-info{padding:8px;flex:1;min-width:0}
        .card-t{font-size:.8rem;font-weight:600;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .card-l{font-size:.6rem;color:var(--txt2);margin-bottom:4px}
        .tags{display:flex;flex-wrap:wrap;gap:3px}
        .tag{font-size:.5rem;padding:2px 5px;border-radius:6px}
        .tag.d{background:rgba(233,69,96,.2);color:var(--pink)}
        .tag.p{background:rgba(78,204,163,.2);color:var(--teal)}
        .tag.h{background:rgba(243,156,18,.2);color:var(--orange)}
        #map{flex:1;height:100%}
        .leaflet-popup-content-wrapper{background:var(--card);color:var(--txt);border-radius:10px}
        .leaflet-popup-tip{background:var(--card)}
        .leaflet-popup-content{margin:0;width:280px!important}
        .pop{padding:0}
        .pop-img{width:100%;height:120px;object-fit:cover;border-radius:10px 10px 0 0}
        .pop-body{padding:12px}
        .pop-c{font-size:.55rem;text-transform:uppercase;color:var(--teal);margin-bottom:3px}
        .pop-t{font-size:1rem;font-weight:700;margin-bottom:4px}
        .pop-l{font-size:.7rem;color:var(--txt2);margin-bottom:6px}
        .pop-d{font-size:.7rem;color:#ccc;line-height:1.3;margin-bottom:8px}
        .pop-i{display:flex;gap:6px;margin-bottom:8px}
        .pop-i>div{flex:1;background:rgba(255,255,255,.05);padding:5px;border-radius:4px}
        .pop-i label{font-size:.5rem;color:var(--txt2);text-transform:uppercase}
        .pop-i span{font-size:.7rem;font-weight:600;display:block}
        .pop-b{display:flex;gap:6px}
        .pop-b a{flex:1;padding:6px;border-radius:4px;font-size:.65rem;font-weight:600;text-decoration:none;text-align:center}
        .pop-b .pr{background:var(--teal);color:#fff}
        .pop-b .sc{background:rgba(255,255,255,.1);color:var(--txt2)}
        .empty{text-align:center;padding:20px;color:var(--txt2);font-size:.8rem}
        @media(max-width:768px){.wrap{flex-direction:column}.side{width:100%;height:50%;order:2}#map{height:50%}}
    </style>
</head>
<body>
<div class="wrap">
    <div class="side">
        <div class="head">
            <div class="logo">
                <div class="logo-i">🗺️</div>
                <div><h1>Jahresguide 2026</h1><p>Bodensee • Ostschweiz • Tessin • Graubünden • Liechtenstein</p></div>
            </div>
            <div class="stats"><span>📍 <strong id="cnt">0</strong> Orte</span><span>🎉 <strong id="evt">0</strong> Events</span><span>⭐ <strong id="hl">0</strong> Highlights</span></div>
        </div>
        <div class="flt">
            <div class="search"><input type="text" id="src" placeholder="Suchen..."></div>
            <div class="tabs" id="tabs">
                <button class="tab on" data-c="all">Alle</button>
                <button class="tab" data-c="festival">🎵 Festivals</button>
                <button class="tab" data-c="volksfest">🎪 Feste</button>
                <button class="tab" data-c="kultur">🎭 Kultur</button>
                <button class="tab" data-c="sport">⚽ Sport</button>
                <button class="tab" data-c="familie">👨‍👩‍👧 Familie</button>
                <button class="tab" data-c="sehenswuerdigkeit">🏛️ Sights</button>
                <button class="tab" data-c="weihnachten">🎄 Märkte</button>
            </div>
        </div>
        <div class="mons" id="mons">
            <button class="mon on" data-m="all">Alle</button>
            <button class="mon" data-m="1">Jan</button>
            <button class="mon" data-m="2">Feb</button>
            <button class="mon" data-m="3">Mär</button>
            <button class="mon" data-m="4">Apr</button>
            <button class="mon" data-m="5">Mai</button>
            <button class="mon" data-m="6">Jun</button>
            <button class="mon" data-m="7">Jul</button>
            <button class="mon" data-m="8">Aug</button>
            <button class="mon" data-m="9">Sep</button>
            <button class="mon" data-m="10">Okt</button>
            <button class="mon" data-m="11">Nov</button>
            <button class="mon" data-m="12">Dez</button>
        </div>
        <div class="list" id="list"></div>
    </div>
    <div id="map"></div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const D=[
// ========== MUSIK-FESTIVALS ==========
{id:1,n:"OpenAir St. Gallen",c:"festival",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"25.-28. Juni",m:6,p:"Ab 230 CHF",desc:"Legendäres Festival mit Twenty One Pilots, Nina Chuba und 45+ Acts.",w:"https://www.openairsg.ch",h:1,img:"https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400"},
{id:2,n:"FL1.LIFE Festival",c:"festival",l:"Schaan",r:"LI",lat:47.165,lng:9.5094,d:"3.-4. Juli",m:7,p:"Ab 89 CHF",desc:"Liechtensteins grösstes Open-Air mit Mark Forster, Sportfreunde Stiller.",w:"https://www.fl1.life",h:0,img:"https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400"},
{id:3,n:"OpenAir Frauenfeld",c:"festival",l:"Frauenfeld",r:"TG",lat:47.557,lng:8.8987,d:"9.-11. Juli",m:7,p:"Ab 199 CHF",desc:"Europas grösstes Hip-Hop Festival mit Sido, SSIO.",w:"https://www.openair-frauenfeld.ch",h:1,img:"https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=400"},
{id:4,n:"Moon & Stars",c:"festival",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"9.-19. Juli",m:7,p:"Ab 79 CHF",desc:"Magische Nächte auf der Piazza Grande mit Neil Young, Jamiroquai, OneRepublic.",w:"https://www.moonandstars.ch",h:1,img:"https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400"},
{id:5,n:"VaduzSOUNDZ",c:"festival",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"22.-25. Juli",m:7,p:"Kinder GRATIS",desc:"Familien-Festival vor der Schlosskulisse mit Fritz Kalkbrenner, Jovanotti.",w:"https://www.vaduzsoundz.li",h:1,img:"https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=400"},
{id:6,n:"Bregenzer Festspiele",c:"festival",l:"Bregenz",r:"AT",lat:47.5027,lng:9.7472,d:"22.7.-23.8.",m:7,p:"Ab 35€",desc:"80 Jahre Jubiläum! Verdis La traviata auf der weltberühmten Seebühne.",w:"https://bregenzerfestspiele.com",h:1,img:"https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=400"},
{id:7,n:"Street Parade",c:"festival",l:"Zürich",r:"ZH",lat:47.3669,lng:8.5417,d:"8. August",m:8,p:"Gratis",desc:"Grösste Techno-Parade der Welt mit 1 Million Teilnehmern.",w:"https://www.streetparade.com",h:1,img:"https://images.unsplash.com/photo-1574391884720-bbc3740c59d1?w=400"},
{id:8,n:"Zürich Openair",c:"festival",l:"Zürich",r:"ZH",lat:47.3769,lng:8.58,d:"28.-29.8. + 4.-5.9.",m:8,p:"Ab 99 CHF",desc:"Mehrere Wochenenden mit Top-Acts.",w:"https://www.zurichopenair.ch",h:0,img:"https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400"},
{id:9,n:"Campus Festival",c:"festival",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"29.-30. Mai",m:5,p:"Ab 49€",desc:"NEU! Sean Paul, 2 Tage, 4 Bühnen.",w:"https://campus-festival.de",h:0,img:"https://images.unsplash.com/photo-1506157786151-b8491531f063?w=400"},
{id:10,n:"Heiden Festival",c:"festival",l:"Heiden",r:"AR",lat:47.4432,lng:9.5322,d:"23.-25. Mai",m:5,p:"Ab 45 CHF",desc:"10 Jahre Jubiläum! Gastkanton Tessin, 40h Live-Musik.",w:"https://www.heidenfestival.ch",h:1,img:"https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=400"},
{id:11,n:"Schlossplatzkonzerte",c:"festival",l:"Meersburg",r:"DE",lat:47.6957,lng:9.2711,d:"11.-14. Juni",m:6,p:"Ab 45€",desc:"Culcha Candela, Clueso, Herbert Pixner.",w:"https://www.meersburg.de",h:0,img:"https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?w=400"},
{id:12,n:"Konzerte Markdorf",c:"festival",l:"Markdorf",r:"DE",lat:47.7167,lng:9.3833,d:"17.-20. Juni",m:6,p:"Ab 40€",desc:"Sportfreunde Stiller, Capital Bra, BossHoss.",w:"https://www.markdorf.de",h:0,img:"https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?w=400"},
{id:13,n:"REWIND Festival",c:"festival",l:"Rapperswil",r:"SG",lat:47.2269,lng:8.818,d:"12.-13. Juni",m:6,p:"Ab 59 CHF",desc:"NEU! Tribute-Bands: Tina Turner, Queen, Coldplay.",w:"https://www.rewind-festival.ch",h:0,img:"https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400"},
{id:14,n:"Clanx Festival",c:"festival",l:"Appenzell",r:"AI",lat:47.3308,lng:9.4089,d:"28.-30. Aug",m:8,p:"Ab 60 CHF",desc:"Non-Profit Bergfestival mit Camping in den Alpen.",w:"https://www.clanx.ch",h:0,img:"https://images.unsplash.com/photo-1478147427282-58a87a120781?w=400"},
{id:15,n:"SunIce Festival",c:"festival",l:"Ascona",r:"TI",lat:46.1542,lng:8.7726,d:"17.-19. Sept",m:9,p:"Ab 69 CHF",desc:"Electronic Beach Festival am Lido.",w:"https://www.sunice.ch",h:0,img:"https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=400"},
{id:16,n:"Bodenseefestival",c:"festival",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"1.-24. Mai",m:5,p:"Variiert",desc:"38. Ausgabe, Motto 'in motion', länderübergreifendes Klassik-Festival.",w:"https://www.bodenseefestival.de",h:0,img:"https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=400"},
{id:17,n:"St. Galler Festspiele",c:"festival",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"18.6.-4.7.",m:6,p:"Ab 45 CHF",desc:"Verdis 'Aida' auf dem Klosterplatz.",w:"https://www.stgaller-festspiele.ch",h:0,img:"https://images.unsplash.com/photo-1580809361436-42a7ec204889?w=400"},
{id:18,n:"Ticino Musica",c:"festival",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"Juli 2026",m:7,p:"Variiert",desc:"80+ Veranstaltungen im ganzen Tessin.",w:"https://www.ticinomusica.com",h:0,img:"https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=400"},
{id:19,n:"Rheinberger Festival",c:"festival",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"14.-22. März",m:3,p:"Ab 30 CHF",desc:"NEU! 125. Todestag, Oratorium 'Christoforus'.",w:"https://www.musikstiftung.li",h:0,img:"https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=400"},
{id:20,n:"classicAscona",c:"festival",l:"Ascona",r:"TI",lat:46.1542,lng:8.7726,d:"18.9.-10.10.",m:9,p:"Ab 40 CHF",desc:"81. Ausgabe, komplett neu konzipiert, 80 Jahre Jubiläum.",w:"https://www.settimane-musicali.ch",h:1,img:"https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=400"},
{id:21,n:"Davos Festival",c:"festival",l:"Davos",r:"GR",lat:46.8027,lng:9.8360,d:"1.-15. Aug",m:8,p:"Ab 35 CHF",desc:"Motto 'Mut', Kammermusik in den Bergen.",w:"https://www.davosfestival.ch",h:0,img:"https://images.unsplash.com/photo-1544928147-79a2dbc1f389?w=400"},
{id:22,n:"Estival Jazz",c:"festival",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"15.-24. Juli",m:7,p:"Gratis",desc:"Jazz Festival mit NEU: Jazz Parade als Strassenumzug.",w:"https://www.estivaljazz.ch",h:0,img:"https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=400"},
{id:23,n:"Nordklang Festival",c:"festival",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"21. Februar",m:2,p:"Ab 25 CHF",desc:"18. Ausgabe, nordeuropäische Musik.",w:"https://www.nordklang.ch",h:0,img:"https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=400"},

// ========== VOLKSFESTE ==========
{id:30,n:"Churer Fasnacht",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"12.-17. Feb",m:2,p:"Gratis",desc:"25-30'000 Zuschauer, traditionelle Wagenkliggen.",w:"https://www.churerfasnacht.ch",h:0,img:"https://images.unsplash.com/photo-1517263904808-5dc91e3e7044?w=400"},
{id:31,n:"Konstanzer Fasnet",c:"volksfest",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"12.-17. Feb",m:2,p:"Gratis",desc:"Traditionelle Masken und Umzüge.",w:"https://www.konstanz.de",h:0,img:"https://images.unsplash.com/photo-1519340241574-2cec6aef0c01?w=400"},
{id:32,n:"St. Galler Fasnacht",c:"volksfest",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"12.-17. Feb",m:2,p:"Gratis",desc:"Guggenkonzerte in der Altstadt.",w:"https://www.fasnacht.sg",h:0,img:"https://images.unsplash.com/photo-1551887373-3c5bd224f6e2?w=400"},
{id:33,n:"Rabadan",c:"volksfest",l:"Bellinzona",r:"TI",lat:46.1952,lng:9.0241,d:"19.-21. Feb",m:2,p:"Gratis",desc:"Grösste Tessiner Fasnacht mit farbenfrohen Umzügen.",w:"https://www.rabadan.ch",h:0,img:"https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400"},
{id:34,n:"Basler Fasnacht",c:"volksfest",l:"Basel",r:"BS",lat:47.5596,lng:7.5886,d:"23.-25. Feb",m:2,p:"Gratis",desc:"UNESCO-Weltkulturerbe! Morgestraich um 4 Uhr morgens.",w:"https://www.fasnachts-comite.ch",h:1,img:"https://images.unsplash.com/photo-1577368287217-16ff9373a733?w=400"},
{id:35,n:"Sechseläuten",c:"volksfest",l:"Zürich",r:"ZH",lat:47.3669,lng:8.5417,d:"17.-20. April",m:4,p:"Gratis",desc:"Böögg-Verbrennen am 20.4. um 18:00, Gastkanton Graubünden.",w:"https://www.sechselaeuten.ch",h:1,img:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
{id:36,n:"Frühlingsfest Rapperswil",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"24.-26. April",m:4,p:"Gratis",desc:"'Grösstes Klassentreffen der Region'.",w:"https://www.rapperswil-jona.ch",h:0,img:"https://images.unsplash.com/photo-1464207687620-d74108d67529?w=400"},
{id:37,n:"Mitsommerfest",c:"volksfest",l:"Frauenfeld",r:"TG",lat:47.557,lng:8.8987,d:"12.-14. Juni",m:6,p:"Gratis",desc:"30-40'000 Besucher, grösstes Volksfest der Region.",w:"https://www.frauenfeld.ch",h:0,img:"https://images.unsplash.com/photo-1528495612343-9ca9f4a4de28?w=400"},
{id:38,n:"Lake and Sound Festival",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"19.-21. Juni",m:6,p:"Ab 49 CHF",desc:"NEU! Marc Sway, Milow, Lo & Leduc am Zürichsee.",w:"https://www.lakeandsound.ch",h:1,img:"https://images.unsplash.com/photo-1485872299829-c673f5194813?w=400"},
{id:39,n:"Seehasenfest",c:"volksfest",l:"Friedrichshafen",r:"DE",lat:47.6541,lng:9.4795,d:"16.-20. Juli",m:7,p:"Gratis",desc:"76. Ausgabe! Grosses Feuerwerk am 18.7. um 22:30.",w:"https://www.seehasenfest.de",h:1,img:"https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400"},
{id:40,n:"Churer Fest",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"14.-16. Aug",m:8,p:"Gratis",desc:"Grösstes Volksfest Graubündens in der Altstadt.",w:"https://www.churerfest.ch",h:0,img:"https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?w=400"},
{id:41,n:"Schlagerparade Chur",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"25.-26. Sept",m:9,p:"Ab 35 CHF",desc:"NEU: 25 Jahre Jubiläum!",w:"https://www.schlagerparade.ch",h:1,img:"https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=400"},
{id:42,n:"Fantastical",c:"volksfest",l:"Kreuzlingen",r:"TG",lat:47.6467,lng:9.1781,d:"7.-9. Aug",m:8,p:"Gratis",desc:"Seenachtfest mit grossem Feuerwerk am Bodensee.",w:"https://www.fantastical.ch",h:0,img:"https://images.unsplash.com/photo-1498931299472-f7a63a5a1cfa?w=400"},
{id:43,n:"Seenachtfest Rapperswil",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7.-9. Aug",m:8,p:"Gratis",desc:"Doppel-Feuerwerk Fr + Sa, Flugshows.",w:"https://www.seenachtfest.ch",h:0,img:"https://images.unsplash.com/photo-1436891620584-47fd0e565afb?w=400"},
{id:44,n:"Seenachtfest Konstanz",c:"volksfest",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"8. August",m:8,p:"Variiert",desc:"NEU: Drohnen-Vorshow! 1 Mio+ Besucher erwartet.",w:"https://www.konstanzer-seenachtfest.de",h:1,img:"https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400"},

// ========== KULTUR ==========
{id:50,n:"Locarno Film Festival",c:"kultur",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"5.-15. Aug",m:8,p:"Ab 25 CHF",desc:"79. Ausgabe! Open-Air Piazza Grande mit 8'000 Plätzen.",w:"https://www.locarnofestival.ch",h:1,img:"https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400"},
{id:51,n:"Zurich Film Festival",c:"kultur",l:"Zürich",r:"ZH",lat:47.3769,lng:8.5417,d:"24.9.-4.10.",m:9,p:"Ab 22 CHF",desc:"Internationales Filmfestival mit Stars und Premieren.",w:"https://zff.com",h:0,img:"https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400"},
{id:52,n:"Weltfilmtage Thusis",c:"kultur",l:"Thusis",r:"GR",lat:46.6973,lng:9.4396,d:"Januar 2026",m:1,p:"Ab 15 CHF",desc:"Ältestes Filmfestival Graubündens.",w:"https://www.weltfilmtage.ch",h:0,img:"https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400"},
{id:53,n:"OtherMovie Film Festival",c:"kultur",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"17.-25. April",m:4,p:"Ab 12 CHF",desc:"NEU: Thema 'Change', 15. Ausgabe.",w:"https://www.othermovie.ch",h:0,img:"https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400"},
{id:54,n:"Filmtage Eschenz",c:"kultur",l:"Eschenz",r:"TG",lat:47.6472,lng:8.8731,d:"26.-28. Juni",m:6,p:"Ab 10 CHF",desc:"NEU: Open-Air-Kino am Untersee.",w:"https://www.eschenz.ch",h:0,img:"https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=400"},
{id:55,n:"Eleanor Antin Retrospektive",c:"kultur",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"27.3.-27.9.",m:3,p:"15 CHF",desc:"Erste Retrospektive in Europa im Kunstmuseum Liechtenstein.",w:"https://www.kunstmuseum.li",h:0,img:"https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400"},
{id:56,n:"150 Jahre Rätisches Museum",c:"kultur",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"Ganzjährig",m:0,p:"12 CHF",desc:"Jubiläumsausstellung mit 150 ausgewählten Objekten.",w:"https://www.raetischesmuseum.gr.ch",h:1,img:"https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=400"},
{id:57,n:"Mensch und Universum",c:"kultur",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"Ab November",m:11,p:"15 CHF",desc:"Grösster Spiegelraum der Schweiz im Naturmuseum.",w:"https://www.naturmuseumsg.ch",h:0,img:"https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400"},
{id:58,n:"Open House Chur",c:"kultur",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"25.-26. April",m:4,p:"Gratis",desc:"PREMIERE: Architektur für alle, inkl. Kinderprogramm.",w:"https://www.openhousechur.ch",h:0,img:"https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400"},
{id:59,n:"Design Week St. Gallen",c:"kultur",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"14. März",m:3,p:"Gratis",desc:"Gestaltung erlebbar machen.",w:"https://www.designweek.sg",h:0,img:"https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400"},
{id:60,n:"20. Museumsnacht",c:"kultur",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"12. September",m:9,p:"25 CHF",desc:"Jubiläumsausgabe mit Sonderprogramm.",w:"https://www.museumsnacht.ch",h:1,img:"https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?w=400"},
{id:61,n:"Street Art Festival",c:"kultur",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"26.-28. Juni",m:6,p:"Gratis",desc:"Stadt als offene Galerie.",w:"https://www.streetart-chur.ch",h:0,img:"https://images.unsplash.com/photo-1499781350541-7783f6c6a0c8?w=400"},
{id:62,n:"Poesie- & Literaturfestival",c:"kultur",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"November",m:11,p:"Variiert",desc:"PREMIERE: Neues Kulturformat in Konstanz.",w:"https://www.konstanz.de",h:0,img:"https://images.unsplash.com/photo-1474932430478-367dbb6832c1?w=400"},
{id:63,n:"Wiborada-Jubiläum",c:"kultur",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"Mai 2026",m:5,p:"Gratis",desc:"1100. Todestag, Fest bei St. Mangen.",w:"https://www.stgallen.ch",h:0,img:"https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400"},
{id:64,n:"Asisi-Panorama",c:"kultur",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ab März 2026",m:3,p:"Ca. 15€",desc:"NEU 2026! Spektakuläres 360-Grad-Rundbild der Vierländerregion.",w:"https://www.asisi.de",h:1,img:"https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=400"},

// ========== SPORT ==========
{id:70,n:"Zürich Marathon",c:"sport",l:"Zürich",r:"ZH",lat:47.3769,lng:8.5417,d:"12. April",m:4,p:"Ab 85 CHF",desc:"Einer der schönsten Stadt-Marathons der Schweiz.",w:"https://www.zurichmarathon.ch",h:0,img:"https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=400"},
{id:71,n:"Tanzfestival",c:"sport",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7.-10. Mai",m:5,p:"Ab 25 CHF",desc:"Workshops, Shows, Tanzbegeisterte.",w:"https://www.tanzfestival.ch",h:0,img:"https://images.unsplash.com/photo-1508700929628-666bc8bd84ea?w=400"},
{id:72,n:"Landesturnfest",c:"sport",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"13.-17. Mai",m:5,p:"Variiert",desc:"NEU: Tausende Turner am Bodensee.",w:"https://www.konstanz.de",h:0,img:"https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=400"},
{id:73,n:"Bodenseewoche",c:"sport",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"29.-31. Mai",m:5,p:"Gratis",desc:"Internationale Bodenseewoche, Segeln.",w:"https://www.bodenseewoche.de",h:0,img:"https://images.unsplash.com/photo-1500917293891-ef795e70e1f6?w=400"},
{id:74,n:"75. RUND UM Regatta",c:"sport",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"4.-6. Juni",m:6,p:"Gratis",desc:"75 Jahre Jubiläum! Grösste Segelregatta am Bodensee, 350-400 Boote.",w:"https://www.rund-um.com",h:1,img:"https://images.unsplash.com/photo-1534113414509-0eec2bfb493f?w=400"},
{id:75,n:"IRONMAN 70.3",c:"sport",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7. Juni",m:6,p:"Ab 399 CHF",desc:"Triathlon-Klassiker am Zürichsee.",w:"https://www.ironman.com",h:0,img:"https://images.unsplash.com/photo-1530549387789-4c1017266635?w=400"},
{id:76,n:"LGT Alpin Marathon",c:"sport",l:"Bendern",r:"LI",lat:47.2119,lng:9.5014,d:"13. Juni",m:6,p:"Ab 95 CHF",desc:"NEU: 42km durch ganz Liechtenstein, 1870 Höhenmeter.",w:"https://www.lgt-alpin-marathon.li",h:1,img:"https://images.unsplash.com/photo-1461896836934-eff98832f889?w=400"},
{id:77,n:"Eidg. Schützenfest",c:"sport",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"27.6.-25.7.",m:6,p:"Variiert",desc:"Grösster Sportanlass 2026! 36'000 Schützen, 100'000 Besucher erwartet.",w:"https://www.esf2026.ch",h:1,img:"https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=400"},
{id:78,n:"Weltklasse Zürich",c:"sport",l:"Zürich",r:"ZH",lat:47.3831,lng:8.5036,d:"26.-27. Aug",m:8,p:"Ab 45 CHF",desc:"Diamond League Leichtathletik im Letzigrund.",w:"https://www.weltklassezuerich.ch",h:0,img:"https://images.unsplash.com/photo-1461896836934-eff98832f889?w=400"},
{id:79,n:"Bodensee-Radmarathon",c:"sport",l:"Kressbronn",r:"DE",lat:47.5944,lng:9.6028,d:"12. September",m:9,p:"Ab 50€",desc:"270 km rund um den ganzen Bodensee, Start in Kressbronn.",w:"https://www.bodensee-radmarathon.de",h:0,img:"https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400"},
{id:80,n:"3-Länder-Marathon",c:"sport",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"11. Oktober",m:10,p:"Ab 65 CHF",desc:"Einzigartiger Marathon durch 3 Länder, Start Lindau.",w:"https://www.sparkasse-3-laender-marathon.at",h:0,img:"https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=400"},
{id:81,n:"Eisklettern Jugend-WM",c:"sport",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"30.1.-1.2.",m:1,p:"Gratis",desc:"UIAA PREMIERE in Liechtenstein!",w:"https://www.malbun.li",h:1,img:"https://images.unsplash.com/photo-1522163182402-834f871fd851?w=400"},
{id:82,n:"SVB-Skirennen",c:"sport",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"13.-14. Januar",m:1,p:"Gratis",desc:"63. Ausgabe, erstmals ausserhalb der Schweiz!",w:"https://www.malbun.li",h:0,img:"https://images.unsplash.com/photo-1551524559-8af4e6624178?w=400"},
{id:83,n:"IOF Orienteering World Cup",c:"sport",l:"Ascona",r:"TI",lat:46.1542,lng:8.7726,d:"24.-26. April",m:4,p:"Gratis",desc:"PREMIERE: 250+ Athleten aus 30+ Ländern.",w:"https://www.ol-tessin.ch",h:1,img:"https://images.unsplash.com/photo-1551632811-561732d1e306?w=400"},
{id:84,n:"Giro d'Italia Etappe",c:"sport",l:"Bellinzona",r:"TI",lat:46.1952,lng:9.0241,d:"26. Mai",m:5,p:"Gratis",desc:"Etappe 16: 113km Bergetappe Bellinzona-Cari durchs Tessin.",w:"https://www.giroditalia.it",h:1,img:"https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400"},
{id:85,n:"UCI MTB World Cup",c:"sport",l:"Lenzerheide",r:"GR",lat:46.7333,lng:9.55,d:"19.-21. Juni",m:6,p:"Gratis",desc:"Weltcup Mountainbike: Short Track, XC, Downhill.",w:"https://www.lenzerheide.swiss",h:0,img:"https://images.unsplash.com/photo-1544191696-102dbdaeeaa0?w=400"},
{id:86,n:"Nobelpreisträgertagung",c:"sport",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"28.6.-3.7.",m:6,p:"Einladung",desc:"75. Ausgabe! Physik-Nobelpreisträger.",w:"https://www.lindau-nobel.org",h:1,img:"https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400"},
{id:87,n:"Transalpine Run",c:"sport",l:"Lenzerheide",r:"GR",lat:46.7333,lng:9.55,d:"28.8.-3.9.",m:8,p:"Ab 1200€",desc:"NEU: 7 Tage, 250km, neue Route von Lenzerheide bis Locarno.",w:"https://www.transalpine-run.com",h:1,img:"https://images.unsplash.com/photo-1551632811-561732d1e306?w=400"},

// ========== MESSEN ==========
{id:90,n:"Motorradwelt Bodensee",c:"volksfest",l:"Friedrichshafen",r:"DE",lat:47.6541,lng:9.4795,d:"23.-25. Januar",m:1,p:"Ab 15€",desc:"NEU: Indoor-Cross Show!",w:"https://www.motorradwelt-bodensee.de",h:0,img:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
{id:91,n:"OFFA",c:"volksfest",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"15.-19. April",m:4,p:"Ab 12 CHF",desc:"Frühlings- und Freizeitmesse.",w:"https://www.offa.ch",h:0,img:"https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400"},
{id:92,n:"Gartentage",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7.-10. Mai",m:5,p:"Ab 15 CHF",desc:"Grüne Stadtentwicklung.",w:"https://www.gartentage.ch",h:0,img:"https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"},
{id:93,n:"Green City Days",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7.-10. Mai",m:5,p:"Gratis",desc:"NEU: Nachhaltige Lebensstile.",w:"https://www.greencitydays.ch",h:0,img:"https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=400"},
{id:94,n:"Arbon Classics",c:"volksfest",l:"Arbon",r:"TG",lat:47.5168,lng:9.4321,d:"30.-31. Mai",m:5,p:"Gratis",desc:"10 Jahre Jubiläum! 50'000+ Besucher, Oldtimer-Treffen.",w:"https://www.arbon-classics.ch",h:1,img:"https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=400"},
{id:95,n:"higa Chur",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"Frühjahr",m:4,p:"Ab 10 CHF",desc:"Bündner Kultmesse, erweitert.",w:"https://www.higa.ch",h:0,img:"https://images.unsplash.com/photo-1531058020387-3be344556be6?w=400"},
{id:96,n:"OLMA",c:"volksfest",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"8.-18. Okt",m:10,p:"Ab 18 CHF",desc:"Grösste Schweizer Landwirtschaftsmesse.",w:"https://www.olma-messen.ch",h:0,img:"https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400"},
{id:97,n:"preXcon",c:"volksfest",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"3.-5. November",m:11,p:"Fachpublikum",desc:"PREMIERE: Präzisionsindustrie-Messe.",w:"https://www.prexcon.ch",h:0,img:"https://images.unsplash.com/photo-1565514020179-026b92b2ed8b?w=400"},
{id:98,n:"Thai Street Food Festival",c:"volksfest",l:"Amriswil",r:"TG",lat:47.5476,lng:9.2994,d:"21.-23. Mai",m:5,p:"Gratis",desc:"NEU: Kulinarik & Kultur.",w:"https://www.amriswil.ch",h:0,img:"https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400"},
{id:99,n:"Genussfestival Vaduz",c:"volksfest",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"5.-13. Sept",m:9,p:"Variiert",desc:"15'000 Besucher, Sterneköche.",w:"https://www.genussfestival.li",h:0,img:"https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400"},
{id:100,n:"Streetfood Festival Chur",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"Juni 2026",m:6,p:"Gratis",desc:"Live-Kochshows.",w:"https://www.streetfood-chur.ch",h:0,img:"https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400"},
{id:101,n:"Alp Spektakel",c:"volksfest",l:"Klosters",r:"GR",lat:46.8686,lng:9.8783,d:"August 2026",m:8,p:"Gratis",desc:"Grosser Alpabzug im Prättigau.",w:"https://www.praettigau.ch",h:0,img:"https://images.unsplash.com/photo-1527003720830-92712ad7d5a4?w=400"},
{id:102,n:"Streetfood Festival RJ",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"20.-30. Aug",m:8,p:"Gratis",desc:"NEU: Erweitert auf 10 Tage!",w:"https://www.streetfood-rj.ch",h:0,img:"https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400"},
{id:103,n:"WINE DATE Vaduz",c:"volksfest",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"13.-14. März",m:3,p:"Ab 20 CHF",desc:"NEU: Boutique-Weinmesse.",w:"https://www.winedate.li",h:0,img:"https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=400"},
{id:104,n:"Käsefest",c:"volksfest",l:"Rapperswil-Jona",r:"SG",lat:47.2269,lng:8.818,d:"7. November",m:11,p:"Gratis",desc:"NEU: Regionale Spezialitäten.",w:"https://www.kaesefest.ch",h:0,img:"https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400"},

// ========== WEIHNACHTSMÄRKTE ==========
{id:110,n:"Winterland Locarno",c:"weihnachten",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"20.11.-6.1.",m:11,p:"Gratis",desc:"Eisbahn, Lichtshow auf der Piazza Grande.",w:"https://www.winterland-locarno.ch",h:0,img:"https://images.unsplash.com/photo-1512389142860-9c449e58a814?w=400"},
{id:111,n:"Christkindlmarkt Zürich HB",c:"weihnachten",l:"Zürich",r:"ZH",lat:47.3778,lng:8.5403,d:"20.11.-23.12.",m:11,p:"Gratis",desc:"130 Stände, grösster überdachter Markt Europas.",w:"https://www.christkindlimarkt.ch",h:0,img:"https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400"},
{id:112,n:"Bellevue Noël",c:"weihnachten",l:"Zürich",r:"ZH",lat:47.3667,lng:8.545,d:"20.11.-23.12.",m:11,p:"Gratis",desc:"50m begehbarer Adventskranz!",w:"https://www.zuerich.com",h:0,img:"https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=400"},
{id:113,n:"Vaduz on Ice",c:"weihnachten",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"7.11.-6.1.",m:11,p:"8 CHF",desc:"Eisbahn, Outdoor-Disco, Winterzauber.",w:"https://www.vaduzonice.li",h:0,img:"https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=400"},
{id:114,n:"Sternenstadt",c:"weihnachten",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"27.11.-24.12.",m:11,p:"Gratis",desc:"700 Sterne in der UNESCO-Altstadt.",w:"https://www.sternenstadt.ch",h:0,img:"https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=400"},
{id:115,n:"Weihnachtsmarkt Konstanz",c:"weihnachten",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"26.11.-23.12.",m:11,p:"Gratis",desc:"150 Stände, 1 Mio. Lichter am See.",w:"https://www.weihnachtsmarkt-konstanz.de",h:0,img:"https://images.unsplash.com/photo-1545622783-b3e021430fee?w=400"},
{id:116,n:"Lindauer Hafenweihnacht",c:"weihnachten",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"27.11.-21.12.",m:11,p:"Gratis",desc:"90 Stände in historischer Kulisse am Hafen.",w:"https://www.lindau.de",h:0,img:"https://images.unsplash.com/photo-1482517967863-00e15c9b44be?w=400"},
{id:117,n:"Weihnachtsmarkt Frauenfeld",c:"weihnachten",l:"Frauenfeld",r:"TG",lat:47.557,lng:8.8987,d:"18.-20. Dez",m:12,p:"Gratis",desc:"160 Stände in der Altstadt.",w:"https://www.frauenfeld.ch",h:0,img:"https://images.unsplash.com/photo-1511963211013-83bba110595d?w=400"},

// ========== FAMILIE ==========
{id:120,n:"Zoo Zürich",c:"familie",l:"Zürich",r:"ZH",lat:47.3846,lng:8.5749,d:"Ganzjährig",m:0,p:"29 CHF",desc:"360 Tierarten, Masoala Regenwaldhalle.",w:"https://www.zoo.ch",h:0,img:"https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=400"},
{id:121,n:"Wildnispark Langenberg",c:"familie",l:"Zürich",r:"ZH",lat:47.2852,lng:8.5445,d:"Ganzjährig",m:0,p:"GRATIS",desc:"Komplett kostenlos! 19 Arten, Bären, Wölfe, Luchse.",w:"https://www.wildnispark.ch",h:1,img:"https://images.unsplash.com/photo-1474511320723-9a56873571b7?w=400"},
{id:122,n:"Walter Zoo",c:"familie",l:"Gossau",r:"SG",lat:47.4167,lng:9.25,d:"Ganzjährig",m:0,p:"22 CHF",desc:"500+ Tiere, Theater-Shows.",w:"https://www.walterzoo.ch",h:0,img:"https://images.unsplash.com/photo-1507666405895-422eee7d517f?w=400"},
{id:123,n:"Sea Life",c:"familie",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ganzjährig",m:0,p:"18.50€",desc:"3'000+ Fische, 8m-Unterwassertunnel.",w:"https://www.visitsealife.com/konstanz",h:0,img:"https://images.unsplash.com/photo-1545671913-b89ac1b4ac10?w=400"},
{id:124,n:"Affenberg Salem",c:"familie",l:"Salem",r:"DE",lat:47.7833,lng:9.2833,d:"März-Nov",m:0,p:"11€",desc:"200 Berberaffen, Fütterung erlaubt!",w:"https://www.affenberg-salem.de",h:0,img:"https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=400"},
{id:125,n:"Falknerei Galina",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"15 CHF",desc:"Greifvogelschau, Adler-Erlebniswanderung.",w:"https://www.galina.li",h:0,img:"https://images.unsplash.com/photo-1557401620-67270b61ea82?w=400"},
{id:126,n:"Knies Kinderzoo",c:"familie",l:"Rapperswil",r:"SG",lat:47.2269,lng:8.818,d:"März-Nov",m:0,p:"18 CHF",desc:"NEU: Elefantenfüttern (ersetzt Reiten), Elektro-Zootram.",w:"https://www.kfreutz.ch",h:1,img:"https://images.unsplash.com/photo-1564349683136-77e08dba1ef3?w=400"},
{id:127,n:"Connyland",c:"familie",l:"Lipperswil",r:"TG",lat:47.6342,lng:9.0103,d:"April-Okt",m:0,p:"49 CHF",desc:"Grösster CH-Freizeitpark, Cobra Achterbahn.",w:"https://www.connyland.ch",h:0,img:"https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?w=400"},
{id:128,n:"Ravensburger Spieleland",c:"familie",l:"Meckenbeuren",r:"DE",lat:47.7022,lng:9.5736,d:"April-Okt",m:0,p:"46.50€",desc:"70+ Attraktionen für 2-12 Jahre.",w:"https://www.spieleland.de",h:0,img:"https://images.unsplash.com/photo-1560969184-10fe8719e047?w=400"},
{id:129,n:"EXPLORiT Kindercity",c:"familie",l:"Volketswil",r:"ZH",lat:47.3833,lng:8.6833,d:"Ganzjährig",m:0,p:"25 CHF",desc:"6'000m² Edutainment.",w:"https://www.kindercity.ch",h:0,img:"https://images.unsplash.com/photo-1566454825481-9c31bd88c36f?w=400"},
{id:130,n:"Splash & Spa Tamaro",c:"familie",l:"Rivera",r:"TI",lat:46.1167,lng:8.8667,d:"Ganzjährig",m:0,p:"38 CHF",desc:"Wasserpark, Rutschen, Wellness.",w:"https://www.splashespa.ch",h:0,img:"https://images.unsplash.com/photo-1519915028121-7d3463d5b1ff?w=400"},
{id:131,n:"Alpamare",c:"familie",l:"Pfäffikon",r:"SZ",lat:47.2,lng:8.7833,d:"Ganzjährig",m:0,p:"49 CHF",desc:"Grosser Wasserpark mit Rutschen.",w:"https://www.alpamare.ch",h:0,img:"https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=400"},
{id:132,n:"Malbi-Park",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"Gratis",desc:"Kinderkarussell, Zauberteppich.",w:"https://www.malbun.li",h:0,img:"https://images.unsplash.com/photo-1560969184-10fe8719e047?w=400"},
{id:133,n:"Säntis",c:"familie",l:"Schwägalp",r:"AR",lat:47.2492,lng:9.3439,d:"Ganzjährig",m:0,p:"46 CHF",desc:"6-Länder-Panorama auf 2'502m.",w:"https://www.saentisbahn.ch",h:0,img:"https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400"},
{id:134,n:"Pfänder",c:"familie",l:"Bregenz",r:"AT",lat:47.5027,lng:9.7472,d:"Ganzjährig",m:0,p:"14.80€",desc:"GRATIS Alpenwildpark, Greifvogelwarte.",w:"https://www.pfaender.at",h:1,img:"https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=400"},
{id:135,n:"Schaukelpfad Malbun",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"Gratis",desc:"10 Schaukeln mit Bergpanorama! Sareiserjoch.",w:"https://www.malbun.li",h:1,img:"https://images.unsplash.com/photo-1519378058457-4c29a0a2efac?w=400"},
{id:136,n:"Forscherweg Malbun",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"Gratis",desc:"4km Erlebnisweg, 150 Höhenmeter.",w:"https://www.malbun.li",h:0,img:"https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400"},
{id:137,n:"Detektiv-Trail",c:"familie",l:"Vaduz & Malbun",r:"LI",lat:47.141,lng:9.5215,d:"Ganzjährig",m:0,p:"10 CHF",desc:"Schatzsuche durch Stadt und Berge.",w:"https://www.detektiv-trail.li",h:0,img:"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400"},
{id:138,n:"Bogenschiessen Malbun",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"15 CHF",desc:"Bogenschiessen in Bergkulisse.",w:"https://www.malbun.li",h:0,img:"https://images.unsplash.com/photo-1565992441121-4367c2967103?w=400"},
{id:139,n:"Monte Brè",c:"familie",l:"Lugano",r:"TI",lat:46.0067,lng:8.9867,d:"Ganzjährig",m:0,p:"25 CHF",desc:"Standseilbahn seit 1912, Spielplatz.",w:"https://www.montebre.ch",h:0,img:"https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=400"},
{id:140,n:"Monte San Salvatore",c:"familie",l:"Lugano",r:"TI",lat:45.9667,lng:8.95,d:"März-Nov",m:0,p:"30 CHF",desc:"360-Grad-Aussicht über Lugano.",w:"https://www.montesansalvatore.ch",h:0,img:"https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400"},
{id:141,n:"Monte Tamaro",c:"familie",l:"Rivera",r:"TI",lat:46.1167,lng:8.8667,d:"April-Nov",m:0,p:"38 CHF",desc:"Rodelbahn, Attraktionen, Botta-Kirche.",w:"https://www.montetamaro.ch",h:0,img:"https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"},
{id:142,n:"Cardada-Cimetta",c:"familie",l:"Locarno",r:"TI",lat:46.18,lng:8.78,d:"Ganzjährig",m:0,p:"32 CHF",desc:"Aussicht, Spielplatz, Wanderwege.",w:"https://www.cardada.ch",h:0,img:"https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=400"},
{id:143,n:"Brambrüesch",c:"familie",l:"Chur",r:"GR",lat:46.85,lng:9.5,d:"Ganzjährig",m:0,p:"25 CHF",desc:"Churer Hausberg, Familienskigebiet.",w:"https://www.brambruesch.ch",h:0,img:"https://images.unsplash.com/photo-1551524559-8af4e6624178?w=400"},
{id:144,n:"Lenzerheide",c:"familie",l:"Lenzerheide",r:"GR",lat:46.7333,lng:9.55,d:"Ganzjährig",m:0,p:"Variiert",desc:"Familienberg, Wanderwege, Bikepark.",w:"https://www.lenzerheide.swiss",h:0,img:"https://images.unsplash.com/photo-1454496522488-7a8e488e8606?w=400"},
{id:145,n:"Technorama",c:"familie",l:"Winterthur",r:"ZH",lat:47.4993,lng:8.7268,d:"Ganzjährig",m:0,p:"32 CHF",desc:"500+ Experimente, grösste Plasmakugel der Welt.",w:"https://www.technorama.ch",h:1,img:"https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"},
{id:146,n:"Zeppelin Museum",c:"familie",l:"Friedrichshafen",r:"DE",lat:47.6541,lng:9.4795,d:"Ganzjährig",m:0,p:"14€",desc:"33m begehbare Hindenburg-Rekonstruktion.",w:"https://www.zeppelin-museum.de",h:0,img:"https://images.unsplash.com/photo-1540962351504-03099e0a754b?w=400"},
{id:147,n:"100 J. Pfahlbaumuseum",c:"familie",l:"Unteruhldingen",r:"DE",lat:47.726,lng:9.2236,d:"Ganzjährig",m:0,p:"12€",desc:"UNESCO-Welterbe, 100 Jahre Jubiläum! 23 Pfahlbauten.",w:"https://www.pfahlbauten.de",h:1,img:"https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
{id:148,n:"Swissminiatur",c:"familie",l:"Melide",r:"TI",lat:45.9536,lng:8.95,d:"März-Nov",m:0,p:"19 CHF",desc:"129 CH-Wahrzeichen im Massstab 1:25.",w:"https://www.swissminiatur.ch",h:0,img:"https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=400"},
{id:149,n:"Museo in Erba",c:"familie",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"Ganzjährig",m:0,p:"10 CHF",desc:"Kinderkunstmuseum.",w:"https://www.museoinerba.com",h:0,img:"https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=400"},
{id:150,n:"Landesmuseum Vaduz",c:"familie",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"Ganzjährig",m:0,p:"Kinder GRATIS",desc:"Kinder bis 16 Jahre gratis!",w:"https://www.landesmuseum.li",h:0,img:"https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?w=400"},
{id:151,n:"Citytrain Vaduz",c:"familie",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"Ganzjährig",m:0,p:"10 CHF",desc:"35 Min. Rundfahrt, 30+ Sprachen.",w:"https://www.citytrain.li",h:0,img:"https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=400"},
{id:152,n:"Rheinfall",c:"familie",l:"Schaffhausen",r:"SH",lat:47.6778,lng:8.6156,d:"Ganzjährig",m:0,p:"5 CHF",desc:"Europas grösster Wasserfall, 150m breit!",w:"https://www.rheinfall.ch",h:1,img:"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"},
{id:153,n:"Insel Mainau",c:"familie",l:"Bodensee",r:"DE",lat:47.7051,lng:9.1919,d:"Ganzjährig",m:0,p:"26€",desc:"45 ha Blumenparadies, Kinder unter 12 GRATIS!",w:"https://www.mainau.de",h:0,img:"https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"},
{id:154,n:"Verzascatal",c:"familie",l:"Lavertezzo",r:"TI",lat:46.2544,lng:8.8372,d:"Ganzjährig",m:0,p:"Gratis",desc:"Kristallklares Wasser, ikonische Steinbrücke Ponte dei Salti.",w:"https://www.ascona-locarno.com",h:0,img:"https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400"},
{id:155,n:"Gänglesee",c:"familie",l:"Liechtenstein",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"Gratis",desc:"Staudämme bauen, Schwimmen.",w:"https://www.malbun.li",h:0,img:"https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=400"},
{id:156,n:"Marienschlucht",c:"familie",l:"Allensbach",r:"DE",lat:47.7167,lng:9.0722,d:"Ab 28. März",m:3,p:"Gratis",desc:"NEU: Nach 11 Jahren wieder offen!",w:"https://www.bodensee.eu",h:1,img:"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"},
{id:157,n:"Bodensee-Therme",c:"familie",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ganzjährig",m:0,p:"18€",desc:"3'000m² Wasserfläche.",w:"https://www.bodensee-therme.de",h:0,img:"https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=400"},
{id:158,n:"Therme Lindau",c:"familie",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"Ganzjährig",m:0,p:"22€",desc:"50m-Aussenbecken, 11 Saunen.",w:"https://www.therme-lindau.de",h:0,img:"https://images.unsplash.com/photo-1519823551278-64ac92734fb1?w=400"},
{id:159,n:"Säntispark",c:"familie",l:"St. Gallen-Abtwil",r:"SG",lat:47.4,lng:9.3,d:"Ganzjährig",m:0,p:"35 CHF",desc:"Bad, Wellness, Bowling.",w:"https://www.saentispark.ch",h:0,img:"https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=400"},
{id:160,n:"Termali Salini",c:"familie",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"Ganzjährig",m:0,p:"42 CHF",desc:"Grösstes NaturSolebad im Tessin.",w:"https://www.termalisalini.ch",h:0,img:"https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=400"},
{id:161,n:"Lido di Lugano",c:"familie",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"Mai-Sept",m:0,p:"12 CHF",desc:"Sandstrand, 10m-Sprungturm.",w:"https://www.lugano.ch",h:0,img:"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400"},
{id:162,n:"Schwimmbad Mühleholz",c:"familie",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"Mai-Sept",m:0,p:"6 CHF",desc:"Einziges Freibad LI, Wellenbad.",w:"https://www.vaduz.li",h:0,img:"https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=400"},

// ========== SEHENSWÜRDIGKEITEN ==========
{id:170,n:"Stiftsbibliothek",c:"sehenswuerdigkeit",l:"St. Gallen",r:"SG",lat:47.4232,lng:9.3772,d:"Ganzjährig",m:0,p:"18 CHF",desc:"UNESCO-Welterbe! 170'000 Bücher, 2'700 Jahre alte Mumie Schepenese.",w:"https://www.stiftsbibliothek.ch",h:1,img:"https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=400"},
{id:171,n:"UNESCO Burgen Bellinzona",c:"sehenswuerdigkeit",l:"Bellinzona",r:"TI",lat:46.1952,lng:9.0241,d:"Ganzjährig",m:0,p:"15 CHF",desc:"3 mittelalterliche UNESCO-Festungen.",w:"https://www.bellinzonaturismo.ch",h:1,img:"https://images.unsplash.com/photo-1555952494-efd681c7e3f9?w=400"},
{id:172,n:"1200 Jahre Radolfzell",c:"sehenswuerdigkeit",l:"Radolfzell",r:"DE",lat:47.7381,lng:8.9706,d:"Ganzjährig",m:0,p:"Variiert",desc:"Grosses Stadtjubiläum 2026! Motto 'Geschtern.Heit.Morge'.",w:"https://www.radolfzell.de",h:1,img:"https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=400"},
{id:173,n:"100 J. Flugplatz Altenrhein",c:"sehenswuerdigkeit",l:"Altenrhein",r:"SG",lat:47.485,lng:9.56,d:"28.-30. Aug",m:8,p:"Variiert",desc:"Jahrhundertfeier! 50-100'000 Besucher erwartet, Flugshow.",w:"https://www.peoples.ch",h:1,img:"https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400"},
{id:174,n:"Niederdorf Zürich",c:"sehenswuerdigkeit",l:"Zürich",r:"ZH",lat:47.3769,lng:8.5417,d:"Ganzjährig",m:0,p:"Gratis",desc:"Grossmünster, Chagall-Fenster, Altstadt.",w:"https://www.zuerich.com",h:0,img:"https://images.unsplash.com/photo-1515488764276-beab7607c1e6?w=400"},
{id:175,n:"Imperia Konstanz",c:"sehenswuerdigkeit",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ganzjährig",m:0,p:"Gratis",desc:"Berühmte Statue, Konzilsstadt.",w:"https://www.konstanz.de",h:0,img:"https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=400"},
{id:176,n:"Lindau Insel",c:"sehenswuerdigkeit",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"Ganzjährig",m:0,p:"Gratis",desc:"Bayerischer Löwe, Leuchtturm, Hafen.",w:"https://www.lindau.de",h:0,img:"https://images.unsplash.com/photo-1508193638397-1c4234db14d8?w=400"},
{id:177,n:"Stein am Rhein",c:"sehenswuerdigkeit",l:"Stein am Rhein",r:"SH",lat:47.6592,lng:8.8592,d:"Ganzjährig",m:0,p:"Gratis",desc:"Bemalte Fassaden aus den 1520er Jahren.",w:"https://www.steinamrhein.ch",h:0,img:"https://images.unsplash.com/photo-1580137189272-c9379f8864fd?w=400"},
{id:178,n:"Burg Meersburg",c:"sehenswuerdigkeit",l:"Meersburg",r:"DE",lat:47.6957,lng:9.2711,d:"Ganzjährig",m:0,p:"14.80€",desc:"Älteste bewohnte Burg Deutschlands.",w:"https://www.burg-meersburg.de",h:0,img:"https://images.unsplash.com/photo-1585036156171-384164a8c675?w=400"},
{id:179,n:"Schloss Vaduz",c:"sehenswuerdigkeit",l:"Vaduz",r:"LI",lat:47.142,lng:9.523,d:"Nur aussen",m:0,p:"Gratis",desc:"Residenz des Fürstenhauses (nicht begehbar).",w:"https://www.tourismus.li",h:0,img:"https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"},
{id:180,n:"Altstadt Chur",c:"sehenswuerdigkeit",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"Ganzjährig",m:0,p:"Gratis",desc:"Älteste Stadt der Schweiz, 5000 Jahre Geschichte.",w:"https://www.churtourismus.ch",h:0,img:"https://images.unsplash.com/photo-1519677100203-a0e668c92439?w=400"},
{id:181,n:"Piazza Riforma Lugano",c:"sehenswuerdigkeit",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"Ganzjährig",m:0,p:"Gratis",desc:"LAC Kulturzentrum, See-Promenade.",w:"https://www.lugano.ch",h:0,img:"https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?w=400"},
{id:182,n:"Piazza Grande Locarno",c:"sehenswuerdigkeit",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"Ganzjährig",m:0,p:"Gratis",desc:"Madonna del Sasso, Filmfestival-Location.",w:"https://www.ascona-locarno.com",h:0,img:"https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=400"},
{id:183,n:"Schloss Rapperswil",c:"sehenswuerdigkeit",l:"Rapperswil",r:"SG",lat:47.226,lng:8.82,d:"Ganzjährig",m:0,p:"Gratis",desc:"Rosenstadt, Polenmuseum, Holzsteg.",w:"https://www.rapperswil-zuerichsee.ch",h:0,img:"https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"},
{id:184,n:"Insel Reichenau",c:"sehenswuerdigkeit",l:"Bodensee",r:"DE",lat:47.6919,lng:9.0553,d:"Ganzjährig",m:0,p:"Gratis",desc:"UNESCO-Welterbe, älteste Wandmalereien nördl. der Alpen.",w:"https://www.reichenau.de",h:0,img:"https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400"},
{id:185,n:"Burg Gutenberg",c:"sehenswuerdigkeit",l:"Balzers",r:"LI",lat:47.0667,lng:9.5,d:"April-Okt",m:0,p:"Gratis",desc:"Begehbare Burg mit Ausstellungen.",w:"https://www.balzers.li",h:0,img:"https://images.unsplash.com/photo-1555952494-efd681c7e3f9?w=400"},
{id:186,n:"Schloss Arenenberg",c:"sehenswuerdigkeit",l:"Salenstein",r:"TG",lat:47.6667,lng:9.0333,d:"Ganzjährig",m:0,p:"14 CHF",desc:"Napoleon-Museum mit Seeblick.",w:"https://www.arenenberg.ch",h:0,img:"https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400"},
{id:187,n:"Kartause Ittingen",c:"sehenswuerdigkeit",l:"Warth",r:"TG",lat:47.5833,lng:8.8667,d:"Ganzjährig",m:0,p:"15 CHF",desc:"1'000+ Rosen, Heckenlabyrinth, Kloster.",w:"https://www.kartause.ch",h:0,img:"https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"}
];

const CC={festival:"#9b59b6",volksfest:"#f39c12",kultur:"#e94560",sport:"#4ecca3",familie:"#3498db",sehenswuerdigkeit:"#f1c40f",weihnachten:"#e94560"};
const CI={festival:"🎵",volksfest:"🎪",kultur:"🎭",sport:"⚽",familie:"👨‍👩‍👧",sehenswuerdigkeit:"🏛️",weihnachten:"🎄"};

let map,M={},fC="all",fM="all",fS="";

function init(){
    map=L.map("map").setView([47.2,9.2],8);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"©OSM"}).addTo(map);
    document.getElementById("cnt").textContent=D.length;
    document.getElementById("evt").textContent=D.filter(p=>p.m>0).length;
    document.getElementById("hl").textContent=D.filter(p=>p.h).length;
    render(D);
    document.getElementById("src").addEventListener("input",e=>{fS=e.target.value;go();});
    document.querySelectorAll(".tab").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));b.classList.add("on");fC=b.dataset.c;go();}));
    document.querySelectorAll(".mon").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".mon").forEach(x=>x.classList.remove("on"));b.classList.add("on");fM=b.dataset.m;go();}));
}

function icon(c,h){
    const col=CC[c]||"#3498db",ic=CI[c]||"📍",s=h?34:26;
    return L.divIcon({className:"",html:`<div style="background:${col};width:${s}px;height:${s}px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;font-size:${h?14:11}px">${ic}</div>`,iconSize:[s,s],iconAnchor:[s/2,s/2]});
}

function render(data){
    Object.values(M).forEach(m=>map.removeLayer(m));M={};
    data.forEach(p=>{
        const m=L.marker([p.lat,p.lng],{icon:icon(p.c,p.h)}).addTo(map);
        m.bindPopup(`<div class="pop"><img class="pop-img" src="${p.img}" onerror="this.style.display='none'"><div class="pop-body"><div class="pop-c">${CI[p.c]} ${p.c}</div><div class="pop-t">${p.n}</div><div class="pop-l">📍 ${p.l} (${p.r})</div><div class="pop-d">${p.desc}</div><div class="pop-i"><div><label>Datum</label><span>${p.d}</span></div><div><label>Preis</label><span>${p.p}</span></div></div><div class="pop-b"><a href="https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lng}" target="_blank" class="pr">📍 Route</a><a href="${p.w}" target="_blank" class="sc">🔗 Web</a></div></div></div>`);
        m.on("click",()=>hl(p.id));
        M[p.id]=m;
    });
    const L1=document.getElementById("list");
    if(!data.length){L1.innerHTML='<div class="empty">Keine Ergebnisse</div>';return;}
    L1.innerHTML=data.map(p=>`<div class="card" data-id="${p.id}" style="border-left-color:${CC[p.c]}"><img class="card-img" src="${p.img}" onerror="this.style.display='none'"><div class="card-info"><div class="card-t">${CI[p.c]} ${p.n}</div><div class="card-l">📍 ${p.l}</div><div class="tags"><span class="tag d">${p.d}</span><span class="tag p">${p.p}</span>${p.h?'<span class="tag h">⭐</span>':''}</div></div></div>`).join("");
    L1.querySelectorAll(".card").forEach(c=>c.addEventListener("click",()=>{const id=+c.dataset.id,p=D.find(x=>x.id===id);if(p&&M[id]){map.setView([p.lat,p.lng],12);M[id].openPopup();hl(id);}}));
}

function hl(id){document.querySelectorAll(".card").forEach(c=>c.classList.remove("on"));const c=document.querySelector(`.card[data-id="${id}"]`);if(c){c.classList.add("on");c.scrollIntoView({behavior:"smooth",block:"nearest"});}}

function go(){
    let f=D;
    if(fC!=="all")f=f.filter(p=>p.c===fC);
    if(fM!=="all"){const m=+fM;f=f.filter(p=>p.m===m||p.m===0);}
    if(fS){const s=fS.toLowerCase();f=f.filter(p=>p.n.toLowerCase().includes(s)||p.l.toLowerCase().includes(s)||p.desc.toLowerCase().includes(s));}
    render(f);
    if(f.length)map.fitBounds(f.map(p=>[p.lat,p.lng]),{padding:[30,30]});
}

document.addEventListener("DOMContentLoaded",init);
</script>
</body>
</html>
'''

components.html(html, height=900, scrolling=False)
