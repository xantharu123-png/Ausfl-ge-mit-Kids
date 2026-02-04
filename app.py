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
        .side{width:380px;background:linear-gradient(180deg,#16213e,#1a1a2e);display:flex;flex-direction:column;border-right:1px solid var(--border)}
        .head{padding:16px;border-bottom:1px solid var(--border)}
        .logo{display:flex;align-items:center;gap:10px}
        .logo-i{width:40px;height:40px;background:linear-gradient(135deg,#e94560,#9b59b6);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
        .logo h1{font-size:1.2rem}
        .logo p{font-size:.65rem;color:var(--txt2)}
        .stats{display:flex;gap:12px;margin-top:10px;font-size:.7rem;color:var(--txt2)}
        .stats strong{color:var(--teal)}
        .flt{padding:10px 16px;border-bottom:1px solid var(--border)}
        .search{position:relative;margin-bottom:8px}
        .search input{width:100%;padding:8px 12px 8px 32px;background:var(--card);border:1px solid var(--border);border-radius:6px;color:var(--txt);font-size:.8rem}
        .search input:focus{outline:none;border-color:var(--pink)}
        .search::before{content:"🔍";position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:.8rem}
        .tabs{display:flex;gap:5px;flex-wrap:wrap}
        .tab{padding:4px 8px;background:var(--card);border:1px solid var(--border);border-radius:12px;font-size:.65rem;color:var(--txt2);cursor:pointer}
        .tab:hover{border-color:var(--pink)}
        .tab.on{background:var(--pink);border-color:var(--pink);color:#fff}
        .mons{padding:8px 16px;border-bottom:1px solid var(--border);display:flex;gap:4px;overflow-x:auto}
        .mons::-webkit-scrollbar{display:none}
        .mon{padding:4px 6px;background:0;border:1px solid var(--border);border-radius:4px;font-size:.6rem;color:var(--txt2);cursor:pointer;white-space:nowrap}
        .mon:hover{border-color:var(--teal);color:var(--teal)}
        .mon.on{background:var(--teal);border-color:var(--teal);color:#fff}
        .list{flex:1;overflow-y:auto;padding:10px}
        .list::-webkit-scrollbar{width:4px}
        .list::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
        .card{background:var(--card);border-radius:8px;padding:10px;margin-bottom:6px;cursor:pointer;border-left:3px solid var(--pink);transition:.2s}
        .card:hover{background:var(--hover);transform:translateX(2px)}
        .card.on{background:rgba(233,69,96,.15)}
        .card-t{font-size:.85rem;font-weight:600;margin-bottom:2px}
        .card-l{font-size:.65rem;color:var(--txt2);margin-bottom:5px}
        .tags{display:flex;flex-wrap:wrap;gap:4px}
        .tag{font-size:.55rem;padding:2px 6px;border-radius:8px}
        .tag.d{background:rgba(233,69,96,.2);color:var(--pink)}
        .tag.p{background:rgba(78,204,163,.2);color:var(--teal)}
        .tag.h{background:rgba(243,156,18,.2);color:var(--orange)}
        #map{flex:1;height:100%}
        .leaflet-popup-content-wrapper{background:var(--card);color:var(--txt);border-radius:10px}
        .leaflet-popup-tip{background:var(--card)}
        .leaflet-popup-content{margin:0;width:260px!important}
        .pop{padding:12px}
        .pop-c{font-size:.6rem;text-transform:uppercase;color:var(--teal);margin-bottom:4px}
        .pop-t{font-size:1rem;font-weight:700;margin-bottom:5px}
        .pop-l{font-size:.75rem;color:var(--txt2);margin-bottom:8px}
        .pop-d{font-size:.75rem;color:#ccc;line-height:1.4;margin-bottom:10px}
        .pop-i{display:flex;gap:6px;margin-bottom:10px}
        .pop-i>div{flex:1;background:rgba(255,255,255,.05);padding:6px;border-radius:5px}
        .pop-i label{font-size:.55rem;color:var(--txt2);text-transform:uppercase}
        .pop-i span{font-size:.75rem;font-weight:600;display:block}
        .pop-b{display:flex;gap:6px}
        .pop-b a{flex:1;padding:7px;border-radius:5px;font-size:.7rem;font-weight:600;text-decoration:none;text-align:center}
        .pop-b .pr{background:var(--teal);color:#fff}
        .pop-b .sc{background:rgba(255,255,255,.1);color:var(--txt2)}
        .empty{text-align:center;padding:30px;color:var(--txt2)}
        @media(max-width:768px){.wrap{flex-direction:column}.side{width:100%;height:45%;order:2}#map{height:55%}}
    </style>
</head>
<body>
<div class="wrap">
    <div class="side">
        <div class="head">
            <div class="logo">
                <div class="logo-i">🗺️</div>
                <div><h1>Jahresguide 2026</h1><p>Bodensee • Ostschweiz • Tessin • Graubünden</p></div>
            </div>
            <div class="stats"><span>📍 <strong id="cnt">0</strong> Orte</span><span>⭐ <strong>25</strong> Highlights</span></div>
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
{id:1,n:"OpenAir St. Gallen",c:"festival",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"25.-28. Juni",m:6,p:"Ab 230 CHF",desc:"Legendäres Festival mit Twenty One Pilots, Nina Chuba und 45+ Acts.",w:"https://www.openairsg.ch",h:1},
{id:2,n:"FL1.LIFE Festival",c:"festival",l:"Schaan",r:"LI",lat:47.165,lng:9.5094,d:"3.-4. Juli",m:7,p:"Ab 89 CHF",desc:"Liechtensteins grösstes Open-Air mit Mark Forster.",w:"https://www.fl1.life",h:0},
{id:3,n:"OpenAir Frauenfeld",c:"festival",l:"Frauenfeld",r:"TG",lat:47.557,lng:8.8987,d:"9.-11. Juli",m:7,p:"Ab 199 CHF",desc:"Europas grösstes Hip-Hop Festival mit Sido, SSIO.",w:"https://www.openair-frauenfeld.ch",h:1},
{id:4,n:"Moon & Stars",c:"festival",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"9.-19. Juli",m:7,p:"Ab 79 CHF",desc:"Magische Nächte auf der Piazza Grande mit Neil Young, Jamiroquai.",w:"https://www.moonandstars.ch",h:1},
{id:5,n:"VaduzSOUNDZ",c:"festival",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"22.-25. Juli",m:7,p:"Kinder GRATIS",desc:"Familien-Festival vor der Schlosskulisse mit Jovanotti.",w:"https://www.vaduzsoundz.li",h:1},
{id:6,n:"Bregenzer Festspiele",c:"festival",l:"Bregenz",r:"AT",lat:47.5027,lng:9.7472,d:"22.7.-23.8.",m:7,p:"Ab 35€",desc:"80 Jahre Jubiläum! Seebühne mit La traviata.",w:"https://bregenzerfestspiele.com",h:1},
{id:7,n:"Street Parade",c:"festival",l:"Zürich",r:"ZH",lat:47.3669,lng:8.5417,d:"8. August",m:8,p:"Gratis",desc:"Grösste Techno-Parade der Welt, 1 Mio Teilnehmer.",w:"https://www.streetparade.com",h:1},
{id:8,n:"Heiden Festival",c:"festival",l:"Heiden",r:"AR",lat:47.4432,lng:9.5322,d:"23.-25. Mai",m:5,p:"Ab 45 CHF",desc:"10 Jahre Jubiläum! 40h Live-Musik.",w:"https://www.heidenfestival.ch",h:0},
{id:9,n:"Clanx Festival",c:"festival",l:"Appenzell",r:"AI",lat:47.3308,lng:9.4089,d:"28.-30. Aug",m:8,p:"Ab 60 CHF",desc:"Non-Profit Bergfestival mit Camping.",w:"https://www.clanx.ch",h:0},
{id:10,n:"Estival Jazz",c:"festival",l:"Lugano",r:"TI",lat:46.0037,lng:8.9511,d:"15.-24. Juli",m:7,p:"Gratis",desc:"Jazz Festival mit Strassenumzug.",w:"https://www.estivaljazz.ch",h:0},
{id:20,n:"Basler Fasnacht",c:"volksfest",l:"Basel",r:"BS",lat:47.5596,lng:7.5886,d:"23.-25. Feb",m:2,p:"Gratis",desc:"UNESCO-Weltkulturerbe! Morgestraich.",w:"https://www.fasnachts-comite.ch",h:1},
{id:21,n:"Sechseläuten",c:"volksfest",l:"Zürich",r:"ZH",lat:47.3669,lng:8.5417,d:"17.-20. April",m:4,p:"Gratis",desc:"Böögg-Verbrennen, Gastkanton Graubünden.",w:"https://www.sechselaeuten.ch",h:1},
{id:22,n:"Seenachtfest Konstanz",c:"volksfest",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"8. August",m:8,p:"Variiert",desc:"NEU: Drohnen-Show! 1 Mio+ Besucher.",w:"https://www.konstanzer-seenachtfest.de",h:1},
{id:23,n:"Fantastical",c:"volksfest",l:"Kreuzlingen",r:"TG",lat:47.6467,lng:9.1781,d:"7.-9. Aug",m:8,p:"Gratis",desc:"Seenachtfest mit Feuerwerk am Bodensee.",w:"https://www.fantastical.ch",h:0},
{id:24,n:"Churer Fest",c:"volksfest",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"14.-16. Aug",m:8,p:"Gratis",desc:"Grösstes Volksfest Graubündens.",w:"https://www.churerfest.ch",h:0},
{id:25,n:"OLMA",c:"volksfest",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"8.-18. Okt",m:10,p:"Ab 18 CHF",desc:"Grösste Schweizer Landwirtschaftsmesse.",w:"https://www.olma-messen.ch",h:0},
{id:26,n:"Arbon Classics",c:"volksfest",l:"Arbon",r:"TG",lat:47.5168,lng:9.4321,d:"30.-31. Mai",m:5,p:"Gratis",desc:"10 Jahre Jubiläum! Oldtimer-Treffen.",w:"https://www.arbon-classics.ch",h:0},
{id:30,n:"Zürich Marathon",c:"sport",l:"Zürich",r:"ZH",lat:47.3769,lng:8.5417,d:"12. April",m:4,p:"Ab 85 CHF",desc:"Schönster Stadt-Marathon der Schweiz.",w:"https://www.zurichmarathon.ch",h:0},
{id:31,n:"IRONMAN 70.3",c:"sport",l:"Rapperswil",r:"SG",lat:47.2269,lng:8.818,d:"7. Juni",m:6,p:"Ab 399 CHF",desc:"Triathlon-Klassiker am Zürichsee.",w:"https://www.ironman.com",h:0},
{id:32,n:"75. RUND UM Regatta",c:"sport",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"4.-6. Juni",m:6,p:"Gratis",desc:"75 Jahre Jubiläum! 350-400 Segelboote.",w:"https://www.rund-um.com",h:1},
{id:33,n:"Eidg. Schützenfest",c:"sport",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"27.6.-25.7.",m:6,p:"Variiert",desc:"Grösster Sportanlass 2026! 36'000 Schützen.",w:"https://www.esf2026.ch",h:1},
{id:34,n:"Weltklasse Zürich",c:"sport",l:"Zürich",r:"ZH",lat:47.3831,lng:8.5036,d:"26.-27. Aug",m:8,p:"Ab 45 CHF",desc:"Diamond League Leichtathletik.",w:"https://www.weltklassezuerich.ch",h:0},
{id:35,n:"Giro d'Italia",c:"sport",l:"Bellinzona",r:"TI",lat:46.1952,lng:9.0241,d:"26. Mai",m:5,p:"Gratis",desc:"Etappe 16: 113km Bergetappe durchs Tessin.",w:"https://www.giroditalia.it",h:1},
{id:36,n:"UCI MTB World Cup",c:"sport",l:"Lenzerheide",r:"GR",lat:46.7333,lng:9.55,d:"19.-21. Juni",m:6,p:"Gratis",desc:"Weltcup Mountainbike, Downhill.",w:"https://www.lenzerheide.swiss",h:0},
{id:37,n:"3-Länder-Marathon",c:"sport",l:"Bodensee",r:"CH-AT-DE",lat:47.5,lng:9.5,d:"11. Okt",m:10,p:"Ab 65 CHF",desc:"Marathon durch 3 Länder am Bodensee.",w:"https://www.sparkasse-3-laender-marathon.at",h:0},
{id:40,n:"Locarno Film Festival",c:"kultur",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"5.-15. Aug",m:8,p:"Ab 25 CHF",desc:"Legendäres Open-Air Kino, Piazza Grande.",w:"https://www.locarnofestival.ch",h:1},
{id:41,n:"Zurich Film Festival",c:"kultur",l:"Zürich",r:"ZH",lat:47.3769,lng:8.5417,d:"24.9.-4.10.",m:9,p:"Ab 22 CHF",desc:"Internationales Filmfestival mit Stars.",w:"https://zff.com",h:0},
{id:42,n:"Asisi-Panorama",c:"kultur",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ab März",m:3,p:"Ca. 15€",desc:"NEU: 360-Grad-Rundbild der Bodenseeregion.",w:"https://www.asisi.de",h:1},
{id:43,n:"150 J. Rätisches Museum",c:"kultur",l:"Chur",r:"GR",lat:46.8499,lng:9.5329,d:"Ganzjährig",m:0,p:"12 CHF",desc:"Jubiläumsausstellung mit 150 Objekten.",w:"https://www.raetischesmuseum.gr.ch",h:0},
{id:44,n:"20. Museumsnacht",c:"kultur",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"12. Sept",m:9,p:"25 CHF",desc:"Jubiläumsausgabe der Museumsnacht.",w:"https://www.museumsnacht.ch",h:0},
{id:50,n:"Zoo Zürich",c:"familie",l:"Zürich",r:"ZH",lat:47.3846,lng:8.5749,d:"Ganzjährig",m:0,p:"29 CHF",desc:"360 Tierarten, Masoala Regenwaldhalle.",w:"https://www.zoo.ch",h:0},
{id:51,n:"Wildnispark Langenberg",c:"familie",l:"Zürich",r:"ZH",lat:47.2852,lng:8.5445,d:"Ganzjährig",m:0,p:"GRATIS",desc:"Kostenlos! Bären, Wölfe, Luchse.",w:"https://www.wildnispark.ch",h:1},
{id:52,n:"Technorama",c:"familie",l:"Winterthur",r:"ZH",lat:47.4993,lng:8.7268,d:"Ganzjährig",m:0,p:"32 CHF",desc:"500+ Experimente zum Anfassen.",w:"https://www.technorama.ch",h:1},
{id:53,n:"Connyland",c:"familie",l:"Lipperswil",r:"TG",lat:47.6342,lng:9.0103,d:"April-Okt",m:0,p:"49 CHF",desc:"Grösster Freizeitpark der Schweiz.",w:"https://www.connyland.ch",h:0},
{id:54,n:"100 J. Pfahlbaumuseum",c:"familie",l:"Unteruhldingen",r:"DE",lat:47.726,lng:9.2236,d:"Ganzjährig",m:0,p:"12€",desc:"UNESCO, 100 Jahre Jubiläum!",w:"https://www.pfahlbauten.de",h:1},
{id:55,n:"Rheinfall",c:"familie",l:"Schaffhausen",r:"SH",lat:47.6778,lng:8.6156,d:"Ganzjährig",m:0,p:"5 CHF",desc:"Europas grösster Wasserfall, 150m breit.",w:"https://www.rheinfall.ch",h:1},
{id:56,n:"Schaukelpfad Malbun",c:"familie",l:"Malbun",r:"LI",lat:47.1023,lng:9.6089,d:"Mai-Okt",m:0,p:"Gratis",desc:"10 Schaukeln mit Bergpanorama!",w:"https://www.malbun.li",h:1},
{id:57,n:"Insel Mainau",c:"familie",l:"Konstanz",r:"DE",lat:47.7051,lng:9.1919,d:"Ganzjährig",m:0,p:"26€",desc:"45 ha Blumenparadies, Kinder gratis.",w:"https://www.mainau.de",h:0},
{id:58,n:"Säntis",c:"familie",l:"Schwägalp",r:"AR",lat:47.2492,lng:9.3439,d:"Ganzjährig",m:0,p:"46 CHF",desc:"6-Länder-Panorama auf 2502m.",w:"https://www.saentisbahn.ch",h:0},
{id:59,n:"Marienschlucht",c:"familie",l:"Bodanrück",r:"DE",lat:47.75,lng:9.05,d:"Ab 28. März",m:3,p:"Gratis",desc:"WIEDERERÖFFNUNG nach 11 Jahren!",w:"https://www.bodensee.eu",h:1},
{id:60,n:"Sea Life",c:"familie",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"Ganzjährig",m:0,p:"18.50€",desc:"3000+ Fische, 8m Unterwassertunnel.",w:"https://www.visitsealife.com",h:0},
{id:61,n:"Ravensburger Spieleland",c:"familie",l:"Meckenbeuren",r:"DE",lat:47.7022,lng:9.5736,d:"April-Okt",m:0,p:"46.50€",desc:"70+ Attraktionen für 2-12 Jahre.",w:"https://www.spieleland.de",h:0},
{id:70,n:"Stiftsbibliothek",c:"sehenswuerdigkeit",l:"St. Gallen",r:"SG",lat:47.4232,lng:9.3772,d:"Ganzjährig",m:0,p:"18 CHF",desc:"UNESCO! 170'000 Bücher, Mumie.",w:"https://www.stiftsbibliothek.ch",h:1},
{id:71,n:"UNESCO Burgen",c:"sehenswuerdigkeit",l:"Bellinzona",r:"TI",lat:46.1952,lng:9.0241,d:"Ganzjährig",m:0,p:"15 CHF",desc:"3 mittelalterliche UNESCO-Festungen.",w:"https://www.bellinzonaturismo.ch",h:1},
{id:72,n:"1200 Jahre Radolfzell",c:"sehenswuerdigkeit",l:"Radolfzell",r:"DE",lat:47.7381,lng:8.9706,d:"Ganzjährig",m:0,p:"Variiert",desc:"Grosses Stadtjubiläum 2026!",w:"https://www.radolfzell.de",h:1},
{id:73,n:"100 J. Flugplatz",c:"sehenswuerdigkeit",l:"Altenrhein",r:"SG",lat:47.485,lng:9.56,d:"28.-30. Aug",m:8,p:"Variiert",desc:"Jahrhundertfeier! 50-100'000 Besucher.",w:"https://www.peoples.ch",h:1},
{id:74,n:"Burg Meersburg",c:"sehenswuerdigkeit",l:"Meersburg",r:"DE",lat:47.6957,lng:9.2711,d:"Ganzjährig",m:0,p:"14.80€",desc:"Älteste bewohnte Burg Deutschlands.",w:"https://www.burg-meersburg.de",h:0},
{id:75,n:"Lindau Insel",c:"sehenswuerdigkeit",l:"Lindau",r:"DE",lat:47.546,lng:9.6842,d:"Ganzjährig",m:0,p:"Gratis",desc:"Leuchtturm und Bayerischer Löwe.",w:"https://www.lindau.de",h:0},
{id:76,n:"Schloss Vaduz",c:"sehenswuerdigkeit",l:"Vaduz",r:"LI",lat:47.142,lng:9.523,d:"Nur aussen",m:0,p:"Gratis",desc:"Residenz des Fürstenhauses.",w:"https://www.tourismus.li",h:0},
{id:80,n:"Sternenstadt",c:"weihnachten",l:"St. Gallen",r:"SG",lat:47.4245,lng:9.3767,d:"27.11.-24.12.",m:11,p:"Gratis",desc:"700 Sterne in der UNESCO-Altstadt.",w:"https://www.sternenstadt.ch",h:0},
{id:81,n:"Weihnachtsmarkt",c:"weihnachten",l:"Konstanz",r:"DE",lat:47.6603,lng:9.1753,d:"26.11.-23.12.",m:11,p:"Gratis",desc:"150 Stände, 1 Mio. Lichter.",w:"https://www.weihnachtsmarkt-konstanz.de",h:0},
{id:82,n:"Vaduz on Ice",c:"weihnachten",l:"Vaduz",r:"LI",lat:47.141,lng:9.5215,d:"7.11.-6.1.",m:11,p:"8 CHF",desc:"Eisbahn und Outdoor-Disco.",w:"https://www.vaduzonice.li",h:0},
{id:83,n:"Christkindlmarkt",c:"weihnachten",l:"Zürich HB",r:"ZH",lat:47.3778,lng:8.5403,d:"20.11.-23.12.",m:11,p:"Gratis",desc:"Grösster überdachter Markt Europas.",w:"https://www.christkindlimarkt.ch",h:0},
{id:84,n:"Winterland",c:"weihnachten",l:"Locarno",r:"TI",lat:46.167,lng:8.794,d:"20.11.-6.1.",m:11,p:"Gratis",desc:"Winterzauber auf der Piazza Grande.",w:"https://www.winterland-locarno.ch",h:0}
];

const CC={festival:"#9b59b6",volksfest:"#f39c12",kultur:"#e94560",sport:"#4ecca3",familie:"#3498db",sehenswuerdigkeit:"#f1c40f",weihnachten:"#e94560"};
const CI={festival:"🎵",volksfest:"🎪",kultur:"🎭",sport:"⚽",familie:"👨‍👩‍👧",sehenswuerdigkeit:"🏛️",weihnachten:"🎄"};

let map,M={},fC="all",fM="all",fS="";

function init(){
    map=L.map("map").setView([47.2,9.2],8);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"©OSM"}).addTo(map);
    document.getElementById("cnt").textContent=D.length;
    render(D);
    document.getElementById("src").addEventListener("input",e=>{fS=e.target.value;go();});
    document.querySelectorAll(".tab").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));b.classList.add("on");fC=b.dataset.c;go();}));
    document.querySelectorAll(".mon").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".mon").forEach(x=>x.classList.remove("on"));b.classList.add("on");fM=b.dataset.m;go();}));
}

function icon(c,h){
    const col=CC[c]||"#3498db",ic=CI[c]||"📍",s=h?34:28;
    return L.divIcon({className:"",html:`<div style="background:${col};width:${s}px;height:${s}px;border-radius:50%;border:3px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;font-size:${h?15:13}px">${ic}</div>`,iconSize:[s,s],iconAnchor:[s/2,s/2]});
}

function render(data){
    Object.values(M).forEach(m=>map.removeLayer(m));M={};
    data.forEach(p=>{
        const m=L.marker([p.lat,p.lng],{icon:icon(p.c,p.h)}).addTo(map);
        m.bindPopup(`<div class="pop"><div class="pop-c">${CI[p.c]} ${p.c}</div><div class="pop-t">${p.n}</div><div class="pop-l">📍 ${p.l} (${p.r})</div><div class="pop-d">${p.desc}</div><div class="pop-i"><div><label>Datum</label><span>${p.d}</span></div><div><label>Preis</label><span>${p.p}</span></div></div><div class="pop-b"><a href="https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lng}" target="_blank" class="pr">📍 Route</a><a href="${p.w}" target="_blank" class="sc">🔗 Web</a></div></div>`);
        m.on("click",()=>hl(p.id));
        M[p.id]=m;
    });
    const L1=document.getElementById("list");
    if(!data.length){L1.innerHTML='<div class="empty">Keine Ergebnisse</div>';return;}
    L1.innerHTML=data.map(p=>`<div class="card" data-id="${p.id}" style="border-left-color:${CC[p.c]}"><div class="card-t">${CI[p.c]} ${p.n}</div><div class="card-l">📍 ${p.l} (${p.r})</div><div class="tags"><span class="tag d">📅 ${p.d}</span><span class="tag p">💰 ${p.p}</span>${p.h?'<span class="tag h">⭐</span>':''}</div></div>`).join("");
    L1.querySelectorAll(".card").forEach(c=>c.addEventListener("click",()=>{const id=+c.dataset.id,p=D.find(x=>x.id===id);if(p&&M[id]){map.setView([p.lat,p.lng],12);M[id].openPopup();hl(id);}}));
}

function hl(id){document.querySelectorAll(".card").forEach(c=>c.classList.remove("on"));const c=document.querySelector(`.card[data-id="${id}"]`);if(c){c.classList.add("on");c.scrollIntoView({behavior:"smooth",block:"nearest"});}}

function go(){
    let f=D;
    if(fC!=="all")f=f.filter(p=>p.c===fC);
    if(fM!=="all"){const m=+fM;f=f.filter(p=>p.m===m||p.m===0);}
    if(fS){const s=fS.toLowerCase();f=f.filter(p=>p.n.toLowerCase().includes(s)||p.l.toLowerCase().includes(s)||p.desc.toLowerCase().includes(s));}
    render(f);
    if(f.length)map.fitBounds(f.map(p=>[p.lat,p.lng]),{padding:[40,40]});
}

document.addEventListener("DOMContentLoaded",init);
</script>
</body>
</html>
'''

components.html(html, height=850, scrolling=False)
