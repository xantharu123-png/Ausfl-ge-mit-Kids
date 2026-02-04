import streamlit as st
import pandas as pd

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Jahresguide 2026",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - Pompeii Style
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #1a1a2e 100%);
    }
    
    h1, h2, h3 { color: #ffffff !important; }
    
    .main-title {
        background: linear-gradient(135deg, #e94560, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .subtitle { color: #a0a0a0; font-size: 0.95rem; }
    
    .stat-box {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stat-number { font-size: 1.8rem; font-weight: 700; color: #4ecca3; }
    .stat-label { color: #a0a0a0; font-size: 0.8rem; }
    
    .poi-card {
        background: #16213e;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #e94560;
    }
    
    .poi-card:hover { background: #1f2b47; }
    
    .poi-title { color: #ffffff; font-weight: 600; font-size: 1.1rem; margin-bottom: 5px; }
    .poi-location { color: #a0a0a0; font-size: 0.85rem; margin-bottom: 8px; }
    .poi-desc { color: #cccccc; font-size: 0.9rem; margin-bottom: 10px; }
    
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .tag-date { background: rgba(233,69,96,0.2); color: #e94560; }
    .tag-price { background: rgba(78,204,163,0.2); color: #4ecca3; }
    .tag-highlight { background: rgba(243,156,18,0.2); color: #f39c12; }
    
    .cat-festival { border-left-color: #9b59b6 !important; }
    .cat-volksfest { border-left-color: #f39c12 !important; }
    .cat-kultur { border-left-color: #e94560 !important; }
    .cat-sport { border-left-color: #4ecca3 !important; }
    .cat-familie { border-left-color: #3498db !important; }
    .cat-sehenswuerdigkeit { border-left-color: #f1c40f !important; }
    .cat-weihnachten { border-left-color: #e94560 !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA
# ============================================
@st.cache_data
def load_data():
    data = [
        # FESTIVALS
        {"name": "OpenAir St. Gallen", "category": "festival", "location": "St. Gallen", "region": "SG", "lat": 47.4245, "lng": 9.3767, "date": "25.-28. Juni", "month": 6, "price": "Ab 230 CHF", "description": "Legendäres Festival mit Twenty One Pilots, Nina Chuba und 45+ Acts.", "highlights": "Twenty One Pilots, Nina Chuba", "website": "https://www.openairsg.ch", "is_highlight": True},
        {"name": "FL1.LIFE Festival", "category": "festival", "location": "Schaan", "region": "LI", "lat": 47.165, "lng": 9.5094, "date": "3.-4. Juli", "month": 7, "price": "Ab 89 CHF", "description": "Liechtensteins grösstes Open-Air mit Mark Forster.", "highlights": "Mark Forster, Sportfreunde Stiller", "website": "https://www.fl1.life", "is_highlight": False},
        {"name": "OpenAir Frauenfeld", "category": "festival", "location": "Frauenfeld", "region": "TG", "lat": 47.557, "lng": 8.8987, "date": "9.-11. Juli", "month": 7, "price": "Ab 199 CHF", "description": "Europas grösstes Hip-Hop Festival.", "highlights": "Sido, SSIO, Hip-Hop", "website": "https://www.openair-frauenfeld.ch", "is_highlight": True},
        {"name": "Moon & Stars Locarno", "category": "festival", "location": "Locarno", "region": "TI", "lat": 46.167, "lng": 8.794, "date": "9.-19. Juli", "month": 7, "price": "Ab 79 CHF", "description": "Magische Nächte auf der Piazza Grande.", "highlights": "Neil Young, Jamiroquai, OneRepublic", "website": "https://www.moonandstars.ch", "is_highlight": True},
        {"name": "VaduzSOUNDZ", "category": "festival", "location": "Vaduz", "region": "LI", "lat": 47.141, "lng": 9.5215, "date": "22.-25. Juli", "month": 7, "price": "Kinder bis 14 GRATIS", "description": "Familien-Festival vor der Schlosskulisse.", "highlights": "Fritz Kalkbrenner, Jovanotti", "website": "https://www.vaduzsoundz.li", "is_highlight": True},
        {"name": "Bregenzer Festspiele", "category": "festival", "location": "Bregenz", "region": "AT", "lat": 47.5027, "lng": 9.7472, "date": "22.7.-23.8.", "month": 7, "price": "Ab 35€", "description": "80 Jahre Jubiläum! Seebühne mit La traviata.", "highlights": "80 Jahre, La traviata, Seebühne", "website": "https://bregenzerfestspiele.com", "is_highlight": True},
        {"name": "Street Parade Zürich", "category": "festival", "location": "Zürich", "region": "ZH", "lat": 47.3669, "lng": 8.5417, "date": "8. August", "month": 8, "price": "Gratis", "description": "Grösste Techno-Parade der Welt.", "highlights": "1 Million Teilnehmer, Gratis", "website": "https://www.streetparade.com", "is_highlight": True},
        {"name": "Heiden Festival", "category": "festival", "location": "Heiden", "region": "AR", "lat": 47.4432, "lng": 9.5322, "date": "23.-25. Mai", "month": 5, "price": "Ab 45 CHF", "description": "10 Jahre Jubiläum! 40h Live-Musik.", "highlights": "10 Jahre Jubiläum", "website": "https://www.heidenfestival.ch", "is_highlight": False},
        {"name": "Clanx Festival", "category": "festival", "location": "Appenzell", "region": "AI", "lat": 47.3308, "lng": 9.4089, "date": "28.-30. August", "month": 8, "price": "Ab 60 CHF", "description": "Non-Profit Bergfestival mit Camping.", "highlights": "Bergfestival, Camping", "website": "https://www.clanx.ch", "is_highlight": False},
        {"name": "Estival Jazz Lugano", "category": "festival", "location": "Lugano", "region": "TI", "lat": 46.0037, "lng": 8.9511, "date": "15.-24. Juli", "month": 7, "price": "Gratis", "description": "Jazz Festival mit Strassenumzug.", "highlights": "Jazz Parade, Gratis", "website": "https://www.estivaljazz.ch", "is_highlight": False},
        
        # VOLKSFESTE
        {"name": "Basler Fasnacht", "category": "volksfest", "location": "Basel", "region": "BS", "lat": 47.5596, "lng": 7.5886, "date": "23.-25. Februar", "month": 2, "price": "Gratis", "description": "UNESCO-Weltkulturerbe! Morgestraich.", "highlights": "UNESCO, Morgestraich", "website": "https://www.fasnachts-comite.ch", "is_highlight": True},
        {"name": "Sechseläuten", "category": "volksfest", "location": "Zürich", "region": "ZH", "lat": 47.3669, "lng": 8.5417, "date": "17.-20. April", "month": 4, "price": "Gratis", "description": "Böögg-Verbrennen, Gastkanton Graubünden.", "highlights": "Böögg-Verbrennen, Tradition", "website": "https://www.sechselaeuten.ch", "is_highlight": True},
        {"name": "Seenachtfest Konstanz", "category": "volksfest", "location": "Konstanz", "region": "DE", "lat": 47.6603, "lng": 9.1753, "date": "8. August", "month": 8, "price": "Variiert", "description": "NEU: Drohnen-Show! 1 Mio+ Besucher.", "highlights": "Drohnen-Show, 1 Mio Besucher", "website": "https://www.konstanzer-seenachtfest.de", "is_highlight": True},
        {"name": "Fantastical Kreuzlingen", "category": "volksfest", "location": "Kreuzlingen", "region": "TG", "lat": 47.6467, "lng": 9.1781, "date": "7.-9. August", "month": 8, "price": "Gratis", "description": "Seenachtfest mit Feuerwerk.", "highlights": "Feuerwerk, Bodensee", "website": "https://www.fantastical.ch", "is_highlight": False},
        {"name": "Churer Fest", "category": "volksfest", "location": "Chur", "region": "GR", "lat": 46.8499, "lng": 9.5329, "date": "14.-16. August", "month": 8, "price": "Gratis", "description": "Grösstes Volksfest Graubündens.", "highlights": "Altstadt-Festival", "website": "https://www.churerfest.ch", "is_highlight": False},
        {"name": "OLMA St. Gallen", "category": "volksfest", "location": "St. Gallen", "region": "SG", "lat": 47.4245, "lng": 9.3767, "date": "8.-18. Oktober", "month": 10, "price": "Ab 18 CHF", "description": "Grösste Schweizer Landwirtschaftsmesse.", "highlights": "Grösste CH-Messe", "website": "https://www.olma-messen.ch", "is_highlight": False},
        {"name": "Arbon Classics", "category": "volksfest", "location": "Arbon", "region": "TG", "lat": 47.5168, "lng": 9.4321, "date": "30.-31. Mai", "month": 5, "price": "Gratis", "description": "10 Jahre Jubiläum! Oldtimer-Treffen.", "highlights": "10 Jahre, 50'000 Besucher", "website": "https://www.arbon-classics.ch", "is_highlight": False},
        {"name": "Genussfestival Vaduz", "category": "volksfest", "location": "Vaduz", "region": "LI", "lat": 47.141, "lng": 9.5215, "date": "5.-13. September", "month": 9, "price": "Variiert", "description": "Kulinarik mit Sterneköchen.", "highlights": "15'000 Besucher, Sterneköche", "website": "https://www.genussfestival.li", "is_highlight": False},
        
        # SPORT
        {"name": "Zürich Marathon", "category": "sport", "location": "Zürich", "region": "ZH", "lat": 47.3769, "lng": 8.5417, "date": "12. April", "month": 4, "price": "Ab 85 CHF", "description": "Schönster Stadt-Marathon der Schweiz.", "highlights": "42.195 km", "website": "https://www.zurichmarathon.ch", "is_highlight": False},
        {"name": "IRONMAN 70.3", "category": "sport", "location": "Rapperswil-Jona", "region": "SG", "lat": 47.2269, "lng": 8.818, "date": "7. Juni", "month": 6, "price": "Ab 399 CHF", "description": "Triathlon-Klassiker am Zürichsee.", "highlights": "Triathlon", "website": "https://www.ironman.com", "is_highlight": False},
        {"name": "75. RUND UM Regatta", "category": "sport", "location": "Lindau", "region": "DE", "lat": 47.546, "lng": 9.6842, "date": "4.-6. Juni", "month": 6, "price": "Gratis", "description": "75 Jahre Jubiläum! 350-400 Boote.", "highlights": "75 Jahre, Grösste Regatta", "website": "https://www.rund-um.com", "is_highlight": True},
        {"name": "Eidg. Schützenfest", "category": "sport", "location": "Chur", "region": "GR", "lat": 46.8499, "lng": 9.5329, "date": "27.6.-25.7.", "month": 6, "price": "Variiert", "description": "Grösster Sportanlass 2026! 36'000 Schützen.", "highlights": "36'000 Schützen, 100'000 Besucher", "website": "https://www.esf2026.ch", "is_highlight": True},
        {"name": "Weltklasse Zürich", "category": "sport", "location": "Zürich", "region": "ZH", "lat": 47.3831, "lng": 8.5036, "date": "26.-27. August", "month": 8, "price": "Ab 45 CHF", "description": "Diamond League Leichtathletik.", "highlights": "Diamond League", "website": "https://www.weltklassezuerich.ch", "is_highlight": False},
        {"name": "Giro d'Italia Etappe", "category": "sport", "location": "Bellinzona", "region": "TI", "lat": 46.1952, "lng": 9.0241, "date": "26. Mai", "month": 5, "price": "Gratis", "description": "Etappe 16: 113km durchs Tessin.", "highlights": "Giro d'Italia, Bergetappe", "website": "https://www.giroditalia.it", "is_highlight": True},
        {"name": "UCI MTB World Cup", "category": "sport", "location": "Lenzerheide", "region": "GR", "lat": 46.7333, "lng": 9.55, "date": "19.-21. Juni", "month": 6, "price": "Gratis", "description": "Weltcup Mountainbike.", "highlights": "Downhill, Cross Country", "website": "https://www.lenzerheide.swiss", "is_highlight": False},
        {"name": "3-Länder-Marathon", "category": "sport", "location": "Bodensee", "region": "CH-AT-DE", "lat": 47.5, "lng": 9.5, "date": "11. Oktober", "month": 10, "price": "Ab 65 CHF", "description": "Marathon durch 3 Länder.", "highlights": "3 Länder, Bodensee", "website": "https://www.sparkasse-3-laender-marathon.at", "is_highlight": False},
        
        # KULTUR
        {"name": "79. Locarno Film Festival", "category": "kultur", "location": "Locarno", "region": "TI", "lat": 46.167, "lng": 8.794, "date": "5.-15. August", "month": 8, "price": "Ab 25 CHF", "description": "Legendäres Open-Air Kino, 8'000 Plätze.", "highlights": "Piazza Grande, Open-Air", "website": "https://www.locarnofestival.ch", "is_highlight": True},
        {"name": "Zurich Film Festival", "category": "kultur", "location": "Zürich", "region": "ZH", "lat": 47.3769, "lng": 8.5417, "date": "24.9.-4.10.", "month": 9, "price": "Ab 22 CHF", "description": "Internationales Filmfestival.", "highlights": "Premieren, Stars", "website": "https://zff.com", "is_highlight": False},
        {"name": "Asisi-Panorama", "category": "kultur", "location": "Konstanz", "region": "DE", "lat": 47.6603, "lng": 9.1753, "date": "Ab März 2026", "month": 3, "price": "Ca. 15€", "description": "NEU: 360-Grad-Rundbild Bodensee.", "highlights": "NEU 2026, 360-Grad", "website": "https://www.asisi.de", "is_highlight": True},
        {"name": "150 J. Rätisches Museum", "category": "kultur", "location": "Chur", "region": "GR", "lat": 46.8499, "lng": 9.5329, "date": "Ganzjährig", "month": 0, "price": "12 CHF", "description": "Jubiläumsausstellung, 150 Objekte.", "highlights": "150 Jahre Jubiläum", "website": "https://www.raetischesmuseum.gr.ch", "is_highlight": False},
        {"name": "20. Museumsnacht SG", "category": "kultur", "location": "St. Gallen", "region": "SG", "lat": 47.4245, "lng": 9.3767, "date": "12. September", "month": 9, "price": "25 CHF", "description": "Jubiläumsausgabe der Museumsnacht.", "highlights": "20 Jahre Jubiläum", "website": "https://www.museumsnacht.ch", "is_highlight": False},
        
        # FAMILIE
        {"name": "Zoo Zürich", "category": "familie", "location": "Zürich", "region": "ZH", "lat": 47.3846, "lng": 8.5749, "date": "Ganzjährig", "month": 0, "price": "29 CHF", "description": "360 Tierarten, Masoala Regenwaldhalle.", "highlights": "360 Tierarten, Masoala", "website": "https://www.zoo.ch", "is_highlight": False},
        {"name": "Wildnispark Langenberg", "category": "familie", "location": "Zürich", "region": "ZH", "lat": 47.2852, "lng": 8.5445, "date": "Ganzjährig", "month": 0, "price": "GRATIS", "description": "Kostenlos! Bären, Wölfe, Luchse.", "highlights": "GRATIS, Bären, Wölfe", "website": "https://www.wildnispark.ch", "is_highlight": True},
        {"name": "Technorama", "category": "familie", "location": "Winterthur", "region": "ZH", "lat": 47.4993, "lng": 8.7268, "date": "Ganzjährig", "month": 0, "price": "32 CHF", "description": "500+ Experimente zum Anfassen.", "highlights": "500+ Experimente", "website": "https://www.technorama.ch", "is_highlight": True},
        {"name": "Connyland", "category": "familie", "location": "Lipperswil", "region": "TG", "lat": 47.6342, "lng": 9.0103, "date": "April-Okt", "month": 0, "price": "49 CHF", "description": "Grösster Freizeitpark der Schweiz.", "highlights": "Cobra Achterbahn", "website": "https://www.connyland.ch", "is_highlight": False},
        {"name": "100 J. Pfahlbaumuseum", "category": "familie", "location": "Unteruhldingen", "region": "DE", "lat": 47.726, "lng": 9.2236, "date": "Ganzjährig", "month": 0, "price": "12€", "description": "UNESCO-Welterbe, 100 Jahre Jubiläum!", "highlights": "100 Jahre, UNESCO", "website": "https://www.pfahlbauten.de", "is_highlight": True},
        {"name": "Rheinfall", "category": "familie", "location": "Schaffhausen", "region": "SH", "lat": 47.6778, "lng": 8.6156, "date": "Ganzjährig", "month": 0, "price": "5 CHF", "description": "Europas grösster Wasserfall, 150m breit.", "highlights": "Grösster Wasserfall Europas", "website": "https://www.rheinfall.ch", "is_highlight": True},
        {"name": "Schaukelpfad Malbun", "category": "familie", "location": "Malbun", "region": "LI", "lat": 47.1023, "lng": 9.6089, "date": "Mai-Okt", "month": 0, "price": "Gratis", "description": "10 Schaukeln mit Bergpanorama!", "highlights": "10 Schaukeln, Gratis", "website": "https://www.malbun.li", "is_highlight": True},
        {"name": "Insel Mainau", "category": "familie", "location": "Konstanz", "region": "DE", "lat": 47.7051, "lng": 9.1919, "date": "Ganzjährig", "month": 0, "price": "26€", "description": "45 ha Blumenparadies, Kinder gratis.", "highlights": "Kinder GRATIS", "website": "https://www.mainau.de", "is_highlight": False},
        {"name": "Säntis", "category": "familie", "location": "Schwägalp", "region": "AR", "lat": 47.2492, "lng": 9.3439, "date": "Ganzjährig", "month": 0, "price": "46 CHF", "description": "6-Länder-Panorama auf 2'502m.", "highlights": "6-Länder-Panorama", "website": "https://www.saentisbahn.ch", "is_highlight": False},
        {"name": "Marienschlucht", "category": "familie", "location": "Bodanrück", "region": "DE", "lat": 47.75, "lng": 9.05, "date": "Ab 28. März", "month": 3, "price": "Gratis", "description": "WIEDERERÖFFNUNG nach 11 Jahren!", "highlights": "Nach 11 Jahren offen!", "website": "https://www.bodensee.eu", "is_highlight": True},
        
        # SEHENSWÜRDIGKEITEN
        {"name": "Stiftsbibliothek St.Gallen", "category": "sehenswuerdigkeit", "location": "St. Gallen", "region": "SG", "lat": 47.4232, "lng": 9.3772, "date": "Ganzjährig", "month": 0, "price": "18 CHF", "description": "UNESCO! 170'000 Bücher, Mumie.", "highlights": "UNESCO, Mumie Schepenese", "website": "https://www.stiftsbibliothek.ch", "is_highlight": True},
        {"name": "UNESCO Burgen Bellinzona", "category": "sehenswuerdigkeit", "location": "Bellinzona", "region": "TI", "lat": 46.1952, "lng": 9.0241, "date": "Ganzjährig", "month": 0, "price": "15 CHF", "description": "3 mittelalterliche UNESCO-Festungen.", "highlights": "UNESCO, 3 Burgen", "website": "https://www.bellinzonaturismo.ch", "is_highlight": True},
        {"name": "1200 Jahre Radolfzell", "category": "sehenswuerdigkeit", "location": "Radolfzell", "region": "DE", "lat": 47.7381, "lng": 8.9706, "date": "Ganzjährig", "month": 0, "price": "Variiert", "description": "Grosses Stadtjubiläum 2026!", "highlights": "1200 Jahre!", "website": "https://www.radolfzell.de", "is_highlight": True},
        {"name": "100 J. Flugplatz Altenrhein", "category": "sehenswuerdigkeit", "location": "Altenrhein", "region": "SG", "lat": 47.485, "lng": 9.56, "date": "28.-30. August", "month": 8, "price": "Variiert", "description": "Jahrhundertfeier! 50-100'000 Besucher.", "highlights": "100 Jahre, Flugshow", "website": "https://www.peoples.ch", "is_highlight": True},
        {"name": "Burg Meersburg", "category": "sehenswuerdigkeit", "location": "Meersburg", "region": "DE", "lat": 47.6957, "lng": 9.2711, "date": "Ganzjährig", "month": 0, "price": "14.80€", "description": "Älteste bewohnte Burg Deutschlands.", "highlights": "Älteste Burg DE", "website": "https://www.burg-meersburg.de", "is_highlight": False},
        {"name": "Lindau Insel", "category": "sehenswuerdigkeit", "location": "Lindau", "region": "DE", "lat": 47.546, "lng": 9.6842, "date": "Ganzjährig", "month": 0, "price": "Gratis", "description": "Leuchtturm und Bayerischer Löwe.", "highlights": "Leuchtturm, Löwe", "website": "https://www.lindau.de", "is_highlight": False},
        {"name": "Altstadt Chur", "category": "sehenswuerdigkeit", "location": "Chur", "region": "GR", "lat": 46.8499, "lng": 9.5329, "date": "Ganzjährig", "month": 0, "price": "Gratis", "description": "Älteste Stadt der Schweiz.", "highlights": "Älteste Stadt CH", "website": "https://www.churtourismus.ch", "is_highlight": False},
        
        # WEIHNACHTSMÄRKTE
        {"name": "Sternenstadt St. Gallen", "category": "weihnachten", "location": "St. Gallen", "region": "SG", "lat": 47.4245, "lng": 9.3767, "date": "27.11.-24.12.", "month": 11, "price": "Gratis", "description": "700 Sterne in der UNESCO-Altstadt.", "highlights": "700 Sterne", "website": "https://www.sternenstadt.ch", "is_highlight": False},
        {"name": "Weihnachtsmarkt Konstanz", "category": "weihnachten", "location": "Konstanz", "region": "DE", "lat": 47.6603, "lng": 9.1753, "date": "26.11.-23.12.", "month": 11, "price": "Gratis", "description": "150 Stände, 1 Mio. Lichter.", "highlights": "150 Stände", "website": "https://www.weihnachtsmarkt-konstanz.de", "is_highlight": False},
        {"name": "Vaduz on Ice", "category": "weihnachten", "location": "Vaduz", "region": "LI", "lat": 47.141, "lng": 9.5215, "date": "7.11.-6.1.", "month": 11, "price": "8 CHF", "description": "Eisbahn und Outdoor-Disco.", "highlights": "Eisbahn", "website": "https://www.vaduzonice.li", "is_highlight": False},
        {"name": "Christkindlmarkt Zürich", "category": "weihnachten", "location": "Zürich HB", "region": "ZH", "lat": 47.3778, "lng": 8.5403, "date": "20.11.-23.12.", "month": 11, "price": "Gratis", "description": "Grösster überdachter Markt Europas.", "highlights": "130 Stände", "website": "https://www.christkindlimarkt.ch", "is_highlight": False},
        {"name": "Winterland Locarno", "category": "weihnachten", "location": "Locarno", "region": "TI", "lat": 46.167, "lng": 8.794, "date": "20.11.-6.1.", "month": 11, "price": "Gratis", "description": "Winterzauber auf der Piazza Grande.", "highlights": "Eisbahn, Lichtshow", "website": "https://www.winterland-locarno.ch", "is_highlight": False},
    ]
    return pd.DataFrame(data)

# ============================================
# CONSTANTS
# ============================================
CATEGORY_ICONS = {"festival": "🎵", "volksfest": "🎪", "kultur": "🎭", "sport": "⚽", "familie": "👨‍👩‍👧", "sehenswuerdigkeit": "🏛️", "weihnachten": "🎄"}
CATEGORY_NAMES = {"festival": "Festivals", "volksfest": "Volksfeste", "kultur": "Kultur", "sport": "Sport", "familie": "Familie", "sehenswuerdigkeit": "Sights", "weihnachten": "Weihnachten"}
MONTHS = {0: "Ganzjährig", 1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni", 7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"}

# ============================================
# MAIN
# ============================================
df = load_data()

# SIDEBAR
with st.sidebar:
    st.markdown('<p class="main-title">🗺️ Jahresguide 2026</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Bodensee • Ostschweiz • Tessin • Graubünden</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Stats
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(df)}</div><div class="stat-label">📍 Orte</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{len(df[df["is_highlight"]])}</div><div class="stat-label">⭐ Highlights</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    search = st.text_input("🔍 Suchen", placeholder="Event, Ort...")
    
    categories = st.multiselect(
        "📂 Kategorien",
        options=list(CATEGORY_NAMES.keys()),
        format_func=lambda x: f"{CATEGORY_ICONS[x]} {CATEGORY_NAMES[x]}",
        default=list(CATEGORY_NAMES.keys())
    )
    
    month = st.select_slider("📅 Monat", options=list(MONTHS.keys()), format_func=lambda x: MONTHS[x], value=0)
    
    highlights_only = st.checkbox("⭐ Nur Highlights")

# FILTER
df_f = df.copy()
if search:
    s = search.lower()
    df_f = df_f[df_f['name'].str.lower().str.contains(s) | df_f['location'].str.lower().str.contains(s) | df_f['description'].str.lower().str.contains(s)]
if categories:
    df_f = df_f[df_f['category'].isin(categories)]
if month != 0:
    df_f = df_f[(df_f['month'] == month) | (df_f['month'] == 0)]
if highlights_only:
    df_f = df_f[df_f['is_highlight'] == True]

# MAIN CONTENT
st.markdown("## 🗺️ Jahresguide 2026")
st.markdown(f"**{len(df_f)} Ergebnisse** • Klicke auf 📍 für Google Maps Route")

# Embedded Map (lightweight iframe)
st.markdown("### 🗺️ Karte")
map_html = f"""
<iframe 
    width="100%" 
    height="400" 
    frameborder="0" 
    scrolling="no" 
    marginheight="0" 
    marginwidth="0" 
    src="https://www.openstreetmap.org/export/embed.html?bbox=7.5%2C45.8%2C10.5%2C47.8&layer=mapnik"
    style="border: 1px solid #16213e; border-radius: 10px;">
</iframe>
<p style="color: #a0a0a0; font-size: 0.8em; margin-top: 5px;">
    💡 Klicke unten bei einem Event auf "📍 Route" für die genaue Position in Google Maps
</p>
"""
st.markdown(map_html, unsafe_allow_html=True)

st.markdown("---")

# POI LIST
st.markdown("### 📋 Alle Events & Aktivitäten")

for cat in categories:
    cat_df = df_f[df_f['category'] == cat]
    if len(cat_df) > 0:
        with st.expander(f"{CATEGORY_ICONS[cat]} {CATEGORY_NAMES[cat]} ({len(cat_df)})", expanded=True):
            for _, row in cat_df.iterrows():
                hl = '<span class="tag tag-highlight">⭐ Highlight</span>' if row['is_highlight'] else ''
                
                st.markdown(f"""
                <div class="poi-card cat-{row['category']}">
                    <div class="poi-title">{row['name']} {hl}</div>
                    <div class="poi-location">📍 {row['location']} ({row['region']})</div>
                    <div class="poi-desc">{row['description']}</div>
                    <span class="tag tag-date">📅 {row['date']}</span>
                    <span class="tag tag-price">💰 {row['price']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button("🔗 Website", row['website'], use_container_width=True)
                with c2:
                    st.link_button("📍 Route", f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}", use_container_width=True)
