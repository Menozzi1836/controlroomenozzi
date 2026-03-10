from datetime import datetime, date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(
    page_title="Naval & Magazzino — Collaboratore",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚢"
)

ACCENT      = "#00C4FF"
ACCENT2     = "#FF6B35"
GREEN_OK    = "#2ECC71"
YELLOW_WARN = "#F1C40F"
RED_ALERT   = "#E74C3C"
BG_DARK     = "#0D1117"
BG_CARD     = "#161B22"
BG_PANEL    = "#1C2330"
TEXT_MAIN   = "#E6EDF3"
TEXT_MUTED  = "#8B949E"
BORDER      = "#30363D"
PALETTE = [ACCENT, ACCENT2, "#A855F7", GREEN_OK, YELLOW_WARN,
           "#F97316", "#EC4899", "#14B8A6", "#EAB308", "#6366F1"]

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=DM+Sans:wght@300;400;600&display=swap');
  html, body, [class*="css"] {{ background-color: {BG_DARK} !important; color: {TEXT_MAIN} !important; font-family: 'DM Sans', sans-serif; }}
  .section-title {{ font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:600; color:{ACCENT}; letter-spacing:2px; text-transform:uppercase; border-bottom:1px solid {BORDER}; padding-bottom:8px; margin:28px 0 16px 0; }}
  .alert-red    {{ background:rgba(231,76,60,0.12);  border-left:4px solid {RED_ALERT};   border-radius:6px; padding:12px 16px; margin:8px 0; }}
  .alert-yellow {{ background:rgba(241,196,15,0.10); border-left:4px solid {YELLOW_WARN}; border-radius:6px; padding:12px 16px; margin:8px 0; }}
  .alert-green  {{ background:rgba(46,204,113,0.10); border-left:4px solid {GREEN_OK};    border-radius:6px; padding:12px 16px; margin:8px 0; }}
  .alert-text   {{ font-family:'DM Sans',sans-serif; font-size:0.88rem; color:{TEXT_MAIN}; }}
  [data-testid="stMetric"] {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:8px; padding:16px 20px !important; }}
  [data-testid="stMetricLabel"] {{ font-family:'JetBrains Mono',monospace !important; font-size:0.72rem !important; color:{TEXT_MUTED} !important; text-transform:uppercase; letter-spacing:1px; }}
  [data-testid="stMetricValue"] {{ font-family:'JetBrains Mono',monospace !important; font-size:1.4rem !important; color:{TEXT_MAIN} !important; font-weight:700 !important; }}
  [data-baseweb="tab-list"] {{ background:{BG_CARD} !important; border-bottom:1px solid {BORDER} !important; }}
  [data-baseweb="tab"] {{ font-family:'JetBrains Mono',monospace !important; font-size:0.78rem !important; color:{TEXT_MUTED} !important; text-transform:uppercase; letter-spacing:1px; }}
  [aria-selected="true"] {{ color:{ACCENT} !important; border-bottom:2px solid {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

def plotly_layout(title="", height=420):
    return dict(
        title=dict(text=title, font=dict(color=TEXT_MAIN, size=15, family="monospace"), x=0.01),
        paper_bgcolor=BG_CARD, plot_bgcolor=BG_PANEL,
        font=dict(color=TEXT_MUTED, size=12, family="monospace"),
        height=height, margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickcolor=TEXT_MUTED),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickcolor=TEXT_MUTED, tickformat=",.0f"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, font=dict(color=TEXT_MUTED)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=BG_CARD, font_color=TEXT_MAIN, bordercolor=ACCENT),
    )

def pie_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(color=TEXT_MAIN, size=14, family="monospace"), x=0.01),
        paper_bgcolor=BG_CARD, font=dict(color=TEXT_MUTED, size=11, family="monospace"),
        height=380, margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, font=dict(color=TEXT_MUTED)),
    )

def section(label):
    st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)

def format_euro(x):
    if x is None: return "N/D"
    return ("€ {:,.0f}".format(x)).replace(",","X").replace(".",",").replace("X",".")

def render_alert(msg, cls):
    st.markdown(f'<div class="{cls}"><span class="alert-text">{msg}</span></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="background:linear-gradient(135deg,{BG_CARD} 0%,#0f1923 100%);
border:1px solid {BORDER};border-left:4px solid {ACCENT};
border-radius:8px;padding:20px 28px;margin-bottom:24px;">
  <h1 style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
  color:{TEXT_MAIN};margin:0 0 4px 0;">▸ NAVAL CONTROL & MAGAZZINO</h1>
  <p style="color:{TEXT_MUTED};font-size:0.85rem;margin:0;font-family:'JetBrains Mono',monospace;">
  Vista collaboratore &nbsp;|&nbsp; {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚢 Naval Control Room", "🏭 Magazzino Materie Prime"])

with tab1:
    import asyncio
    import websockets
    import json
    import folium
    from streamlit_folium import st_folium

    # Hero banner con SVG nave grande
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{BG_CARD} 0%,#0a1628 100%);
    border:1px solid {BORDER};border-radius:12px;padding:28px 32px;margin-bottom:24px;
    display:flex;align-items:center;gap:32px;overflow:hidden;position:relative;">

      <!-- Onde animate sfondo -->
      <div style="position:absolute;bottom:0;left:0;right:0;height:60px;opacity:0.07;">
        <svg viewBox='0 0 1200 60' preserveAspectRatio='none' style='width:100%;height:100%;'>
          <path d='M0,30 C150,60 350,0 600,30 C850,60 1050,0 1200,30 L1200,60 L0,60 Z' fill='{ACCENT}'/>
        </svg>
      </div>

      <!-- SVG NAVE GRANDE -->
      <div style="flex-shrink:0;">
        <svg width="140" height="90" viewBox="0 0 200 130" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Scafo principale -->
          <path d="M10,80 L20,100 L180,100 L190,80 L10,80 Z" fill="{ACCENT}" opacity="0.9"/>
          <!-- Prua (parte anteriore) -->
          <path d="M180,80 L190,80 L195,90 L180,100 Z" fill="{ACCENT}" opacity="0.7"/>
          <!-- Poppa -->
          <path d="M10,80 L5,90 L20,100 Z" fill="{ACCENT}" opacity="0.7"/>
          <!-- Corpo suprastruttura centrale -->
          <rect x="70" y="55" width="60" height="25" rx="2" fill="{ACCENT}" opacity="0.8"/>
          <!-- Torre di comando -->
          <rect x="85" y="35" width="30" height="22" rx="2" fill="{ACCENT}" opacity="0.9"/>
          <!-- Finestrini ponte -->
          <rect x="88" y="40" width="6" height="5" rx="1" fill="{BG_DARK}" opacity="0.8"/>
          <rect x="97" y="40" width="6" height="5" rx="1" fill="{BG_DARK}" opacity="0.8"/>
          <rect x="106" y="40" width="6" height="5" rx="1" fill="{BG_DARK}" opacity="0.8"/>
          <!-- Antenna radar -->
          <line x1="100" y1="35" x2="100" y2="18" stroke="{ACCENT}" stroke-width="1.5"/>
          <line x1="92" y1="22" x2="108" y2="22" stroke="{ACCENT}" stroke-width="1.5"/>
          <circle cx="100" cy="18" r="3" fill="{ACCENT2}" opacity="0.9"/>
          <!-- Container stack sinistra -->
          <rect x="20" y="62" width="18" height="10" rx="1" fill="{ACCENT2}" opacity="0.7"/>
          <rect x="20" y="52" width="18" height="10" rx="1" fill="#A855F7" opacity="0.7"/>
          <rect x="40" y="62" width="18" height="10" rx="1" fill="#2ECC71" opacity="0.7"/>
          <rect x="40" y="52" width="18" height="10" rx="1" fill="{ACCENT2}" opacity="0.7"/>
          <!-- Container stack destra -->
          <rect x="132" y="62" width="18" height="10" rx="1" fill="#2ECC71" opacity="0.7"/>
          <rect x="132" y="52" width="18" height="10" rx="1" fill="{ACCENT}" opacity="0.7"/>
          <rect x="152" y="62" width="18" height="10" rx="1" fill="{ACCENT2}" opacity="0.7"/>
          <rect x="152" y="52" width="18" height="10" rx="1" fill="#A855F7" opacity="0.7"/>
          <!-- Fumaiolo -->
          <rect x="118" y="42" width="10" height="18" rx="2" fill="{TEXT_MUTED}" opacity="0.6"/>
          <ellipse cx="123" cy="41" rx="6" ry="3" fill="{TEXT_MUTED}" opacity="0.5"/>
          <!-- Scia acqua -->
          <path d="M5,105 C50,98 100,112 195,105" stroke="{ACCENT}" stroke-width="1.5" fill="none" opacity="0.3" stroke-dasharray="4,3"/>
          <path d="M5,112 C60,105 110,118 195,112" stroke="{ACCENT}" stroke-width="1" fill="none" opacity="0.2" stroke-dasharray="4,3"/>
          <!-- Punto GPS pulsante -->
          <circle cx="100" cy="72" r="4" fill="{ACCENT2}" opacity="0.9"/>
          <circle cx="100" cy="72" r="8" fill="{ACCENT2}" opacity="0.2"/>
        </svg>
      </div>

      <!-- Info testo -->
      <div style="flex:1;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
        color:{TEXT_MAIN};letter-spacing:-0.5px;margin-bottom:4px;">MSC JADE</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{ACCENT};
        letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">
        Container Ship · IMO 9762326 · 19.437 TEU · 398 m
        </div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;">
          <div><span style="color:{TEXT_MUTED};font-size:0.72rem;">PARTENZA</span><br>
               <span style="color:{TEXT_MAIN};font-size:0.88rem;font-weight:600;">Shanghai / CN</span></div>
          <div><span style="color:{TEXT_MUTED};font-size:0.72rem;">DESTINAZIONE</span><br>
               <span style="color:{TEXT_MAIN};font-size:0.88rem;font-weight:600;">Rotterdam / NL</span></div>
          <div><span style="color:{TEXT_MUTED};font-size:0.72rem;">ETA</span><br>
               <span style="color:{YELLOW_WARN};font-size:0.88rem;font-weight:700;">18 Apr 2026</span></div>
          <div><span style="color:{TEXT_MUTED};font-size:0.72rem;">STATO</span><br>
               <span style="color:{GREEN_OK};font-size:0.88rem;font-weight:600;">🟢 In transit</span></div>
        </div>
      </div>

      <!-- Badge container -->
      <div style="text-align:center;flex-shrink:0;">
        <div style="background:{BG_PANEL};border:1px solid {BORDER};border-radius:8px;padding:12px 16px;">
          <div style="font-size:2rem;margin-bottom:4px;">📦</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:{ACCENT};
          letter-spacing:1px;">2 CONTAINER</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:{TEXT_MUTED};margin-top:4px;">
          MSMU5685418<br>FDCU0247618</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{TEXT_MAIN};
          font-weight:700;margin-top:6px;">22.320 kg</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Zone conflitto nel mondo
    CONFLICT_ZONES = [
        {"name": "Mar Rosso / Yemen", "lat": 14.0, "lon": 43.0, "radius": 400, "color": "red"},
        {"name": "Stretto di Hormuz", "lat": 26.5, "lon": 56.5, "radius": 150, "color": "red"},
        {"name": "Mar Nero", "lat": 43.0, "lon": 34.0, "radius": 350, "color": "orange"},
        {"name": "Gaza / Mediterraneo Est", "lat": 31.5, "lon": 34.5, "radius": 150, "color": "red"},
        {"name": "Stretto di Taiwan", "lat": 24.0, "lon": 119.5, "radius": 200, "color": "orange"},
        {"name": "Mar della Cina Meridionale", "lat": 12.0, "lon": 114.0, "radius": 500, "color": "orange"},
        {"name": "Golfo di Aden", "lat": 12.0, "lon": 47.0, "radius": 300, "color": "red"},
    ]

    AIS_API_KEY = "53e2c31b9484b5777c55142e6c7d1270d7ca9710"

    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-left:3px solid {ACCENT};
    border-radius:6px;padding:12px 16px;margin-bottom:16px;font-family:'DM Sans',sans-serif;font-size:0.85rem;color:{TEXT_MUTED};">
    🛰️ Dati AIS in tempo reale via AISstream.io &nbsp;|&nbsp; 
    🔴 Zone conflitto attive monitorate: {len(CONFLICT_ZONES)}
    </div>
    """, unsafe_allow_html=True)

    # Scheda spedizione attiva
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-left:4px solid {ACCENT2};
    border-radius:8px;padding:16px 20px;margin-bottom:20px;font-family:'DM Sans',sans-serif;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:{ACCENT};
    letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">📦 Spedizione attiva</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">NAVE</span><br>
           <span style="color:{TEXT_MAIN};font-weight:700;font-size:1rem;">MSC JADE</span></div>
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">ROTTA</span><br>
           <span style="color:{TEXT_MAIN};font-weight:600;">Shanghai → Rotterdam</span></div>
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">ETA ROTTERDAM</span><br>
           <span style="color:{YELLOW_WARN};font-weight:700;">18 Apr 2026</span></div>
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">CONTAINER 1</span><br>
           <span style="color:{TEXT_MAIN};font-family:'JetBrains Mono',monospace;">MSMU5685418</span></div>
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">CONTAINER 2</span><br>
           <span style="color:{TEXT_MAIN};font-family:'JetBrains Mono',monospace;">FDCU0247618</span></div>
      <div><span style="color:{TEXT_MUTED};font-size:0.75rem;">PESO TOTALE</span><br>
           <span style="color:{TEXT_MAIN};font-weight:600;">22.320 kg</span></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Input ricerca nave
    col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
    with col_s1:
        ship_name = st.text_input("🔍 Nome nave", value="MSC JADE")
    with col_s2:
        ship_imo = st.text_input("🔢 IMO / MMSI", value="636017506")
    with col_s3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🚢 Traccia nave", use_container_width=True)

    # Funzione per recuperare dati AIS
    async def get_ship_position(ship_name=None, mmsi=None):
        try:
            subscribe_msg = {
                "APIKey": AIS_API_KEY,
                "BoundingBoxes": [[[-90, -180], [90, 180]]],
                "FilterMessageTypes": ["PositionReport"]
            }
            if ship_name:
                subscribe_msg["ShipName"] = ship_name.upper()

            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
                await ws.send(json.dumps(subscribe_msg))
                results = []
                try:
                    for _ in range(30):
                        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        data = json.loads(msg)
                        if "Message" in data and "PositionReport" in data["Message"]:
                            pos = data["Message"]["PositionReport"]
                            meta = data.get("MetaData", {})
                            name = meta.get("ShipName", "").strip()
                            if ship_name and ship_name.upper() not in name.upper():
                                continue
                            results.append({
                                "name": name,
                                "lat": pos.get("Latitude", 0),
                                "lon": pos.get("Longitude", 0),
                                "speed": pos.get("Sog", 0),
                                "course": pos.get("Cog", 0),
                                "mmsi": meta.get("MMSI", ""),
                                "time": meta.get("time_utc", ""),
                            })
                            if len(results) >= 1:
                                break
                except asyncio.TimeoutError:
                    pass
                return results
        except Exception as e:
            return []

    def check_conflict_zone(lat, lon):
        """Verifica se la nave è in una zona conflitto"""
        import math
        alerts = []
        for zone in CONFLICT_ZONES:
            dlat = math.radians(lat - zone["lat"])
            dlon = math.radians(lon - zone["lon"])
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(zone["lat"])) * math.sin(dlon/2)**2
            dist_km = 6371 * 2 * math.asin(math.sqrt(a))
            if dist_km <= zone["radius"]:
                alerts.append(zone["name"])
        return alerts

    def build_map(ship_data=None):
        """Costruisce mappa Folium con zone conflitto e nave"""
        m = folium.Map(
            location=[20, 20],
            zoom_start=3,
            tiles="CartoDB dark_matter"
        )

        # Disegna zone conflitto
        for zone in CONFLICT_ZONES:
            color = zone["color"]
            folium.Circle(
                location=[zone["lat"], zone["lon"]],
                radius=zone["radius"] * 1000,
                color=color,
                fill=True,
                fill_opacity=0.15,
                weight=2,
                popup=folium.Popup(f"⚠️ {zone['name']}", max_width=200),
                tooltip=f"⚠️ {zone['name']}"
            ).add_to(m)

            # Icona zona
            folium.Marker(
                location=[zone["lat"], zone["lon"]],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size:11px;color:{'red' if color=='red' else 'orange'};
                    font-weight:bold;font-family:monospace;white-space:nowrap;
                    text-shadow:1px 1px 2px black;">
                    {'🔴' if color=='red' else '🟠'} {zone['name']}
                    </div>""", icon_size=(200, 20))
            ).add_to(m)

        # Aggiungi nave se trovata
        if ship_data:
            lat, lon = ship_data["lat"], ship_data["lon"]
            name = ship_data["name"]
            speed = ship_data["speed"]
            course = ship_data["course"]

            # Marker nave
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size:24px;transform:rotate({course}deg);">🚢</div>
                """, icon_size=(30, 30), icon_anchor=(15, 15)),
                popup=folium.Popup(f"""
                    <div style='font-family:monospace;font-size:12px;min-width:180px;'>
                    <b>🚢 {name}</b><br>
                    📍 {lat:.4f}°, {lon:.4f}°<br>
                    ⚡ Velocità: {speed:.1f} kn<br>
                    🧭 Rotta: {course:.0f}°<br>
                    🕐 {ship_data.get('time','N/D')}
                    </div>
                """, max_width=220),
                tooltip=f"🚢 {name} — {speed:.1f} kn"
            ).add_to(m)

            # Cerchio pulsante intorno alla nave
            folium.Circle(
                location=[lat, lon],
                radius=50000,
                color=ACCENT,
                fill=True,
                fill_opacity=0.2,
                weight=2,
            ).add_to(m)

            # Centra mappa sulla nave
            m.location = [lat, lon]
            m.zoom_start = 6

        return m

    # Stato sessione per dati nave
    if "ship_data" not in st.session_state:
        st.session_state.ship_data = None
    if "ship_error" not in st.session_state:
        st.session_state.ship_error = None

    # Ricerca nave
    if search_btn and (ship_name or ship_imo):
        with st.spinner(f"🛰️ Ricerca {ship_name or ship_imo} in corso..."):
            try:
                results = asyncio.run(get_ship_position(ship_name=ship_name))
                if results:
                    st.session_state.ship_data = results[0]
                    st.session_state.ship_error = None
                else:
                    st.session_state.ship_data = None
                    st.session_state.ship_error = f"Nave '{ship_name}' non trovata o non in navigazione al momento."
            except Exception as e:
                st.session_state.ship_data = None
                st.session_state.ship_error = str(e)

    # Alert zona conflitto
    if st.session_state.ship_data:
        sd = st.session_state.ship_data
        conflict_alerts = check_conflict_zone(sd["lat"], sd["lon"])

        if conflict_alerts:
            for alert in conflict_alerts:
                render_alert(f"🔴 ATTENZIONE — La nave {sd['name']} si trova nella zona a rischio: {alert}", "alert-red")
        else:
            render_alert(f"🟢 La nave {sd['name']} non si trova in zone a rischio attualmente", "alert-green")

        # KPI nave
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("🚢 Nome nave", sd["name"])
        with c2: st.metric("⚡ Velocità", f"{sd['speed']:.1f} nodi")
        with c3: st.metric("🧭 Rotta", f"{sd['course']:.0f}°")
        with c4: st.metric("📍 Posizione", f"{sd['lat']:.2f}°, {sd['lon']:.2f}°")

    if st.session_state.ship_error:
        render_alert(f"⚠️ {st.session_state.ship_error}", "alert-yellow")

    # ── Barra progresso viaggio ──────────────────────────
    section("🗺️ Progresso viaggio — MSC JADE")

    from datetime import date
    PARTENZA   = date(2026, 3, 7)
    ARRIVO_ETA = date(2026, 4, 18)
    OGGI       = date.today()
    giorni_tot    = (ARRIVO_ETA - PARTENZA).days
    giorni_passati = max(0, min((OGGI - PARTENZA).days, giorni_tot))
    giorni_restanti = max(0, (ARRIVO_ETA - OGGI).days)
    perc = int(giorni_passati / giorni_tot * 100) if giorni_tot > 0 else 0

    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:10px;
    padding:20px 24px;margin-bottom:20px;">

      <!-- Intestazione rotta -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <div style="font-family:'JetBrains Mono',monospace;">
          <span style="font-size:1rem;color:{TEXT_MAIN};font-weight:700;">🚢 Shanghai</span>
          <span style="color:{TEXT_MUTED};font-size:0.85rem;"> → </span>
          <span style="font-size:1rem;color:{TEXT_MAIN};font-weight:700;">🏁 Rotterdam</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:{ACCENT};">
          {perc}% completato
        </div>
      </div>

      <!-- Barra progresso -->
      <div style="background:{BG_PANEL};border-radius:20px;height:18px;overflow:hidden;
      border:1px solid {BORDER};margin-bottom:12px;position:relative;">
        <div style="background:linear-gradient(90deg,{ACCENT} 0%,{ACCENT2} 100%);
        width:{perc}%;height:100%;border-radius:20px;transition:width 0.5s ease;
        box-shadow:0 0 10px {ACCENT}55;"></div>
        <!-- Nave icona sulla barra -->
        <div style="position:absolute;top:50%;left:calc({perc}% - 10px);
        transform:translateY(-50%);font-size:14px;">🚢</div>
      </div>

      <!-- Info sotto barra -->
      <div style="display:flex;justify-content:space-between;
      font-family:'JetBrains Mono',monospace;font-size:0.75rem;">
        <div>
          <span style="color:{TEXT_MUTED};">Partenza</span><br>
          <span style="color:{TEXT_MAIN};">{PARTENZA.strftime("%d %b %Y")}</span>
        </div>
        <div style="text-align:center;">
          <span style="color:{TEXT_MUTED};">Giorni passati / totali</span><br>
          <span style="color:{ACCENT};font-weight:700;">{giorni_passati} / {giorni_tot} gg</span>
        </div>
        <div style="text-align:center;">
          <span style="color:{TEXT_MUTED};">Giorni rimanenti</span><br>
          <span style="color:{YELLOW_WARN};font-weight:700;">⏳ {giorni_restanti} giorni</span>
        </div>
        <div style="text-align:right;">
          <span style="color:{TEXT_MUTED};">ETA Rotterdam</span><br>
          <span style="color:{GREEN_OK};font-weight:700;">{ARRIVO_ETA.strftime("%d %b %Y")}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mappa con pulsante live verde ────────────────────
    section("🗺️ Mappa mondiale — Zone conflitto & posizione nave")

    # Mappa pulsante live stile world monitor
    col_map1, col_map2 = st.columns([3, 1])
    with col_map2:
        # Pannello live stile radar
        lat_disp = st.session_state.ship_data["lat"] if st.session_state.ship_data else "N/D"
        lon_disp = st.session_state.ship_data["lon"] if st.session_state.ship_data else "N/D"
        spd_disp = f"{st.session_state.ship_data['speed']:.1f} kn" if st.session_state.ship_data else "N/D"
        crs_disp = f"{st.session_state.ship_data['course']:.0f}°" if st.session_state.ship_data else "N/D"
        lat_str  = f"{lat_disp:.4f}°" if isinstance(lat_disp, float) else lat_disp
        lon_str  = f"{lon_disp:.4f}°" if isinstance(lon_disp, float) else lon_disp

        st.markdown(f"""
        <div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:10px;
        padding:16px;height:100%;font-family:'JetBrains Mono',monospace;">

          <!-- Titolo con pulsante verde animato -->
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <div style="width:10px;height:10px;border-radius:50%;background:{GREEN_OK};
            box-shadow:0 0 8px {GREEN_OK};
            animation:pulse 1.5s infinite;"></div>
            <span style="font-size:0.7rem;color:{ACCENT};letter-spacing:2px;
            text-transform:uppercase;">LIVE AIS</span>
          </div>
          <style>
          @keyframes pulse {{
            0%   {{ box-shadow: 0 0 4px {GREEN_OK}; opacity:1; }}
            50%  {{ box-shadow: 0 0 14px {GREEN_OK}; opacity:0.6; }}
            100% {{ box-shadow: 0 0 4px {GREEN_OK}; opacity:1; }}
          }}
          </style>

          <div style="font-size:1.1rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:12px;">
          MSC JADE</div>

          <div style="color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;
          letter-spacing:1px;margin-bottom:4px;">Latitudine</div>
          <div style="color:{ACCENT};font-size:0.9rem;margin-bottom:10px;">{lat_str}</div>

          <div style="color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;
          letter-spacing:1px;margin-bottom:4px;">Longitudine</div>
          <div style="color:{ACCENT};font-size:0.9rem;margin-bottom:10px;">{lon_str}</div>

          <div style="color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;
          letter-spacing:1px;margin-bottom:4px;">Velocità</div>
          <div style="color:{ACCENT2};font-size:0.9rem;margin-bottom:10px;">{spd_disp}</div>

          <div style="color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;
          letter-spacing:1px;margin-bottom:4px;">Rotta</div>
          <div style="color:{ACCENT2};font-size:0.9rem;margin-bottom:16px;">{crs_disp}</div>

          <div style="border-top:1px solid {BORDER};padding-top:12px;">
          <div style="color:{TEXT_MUTED};font-size:0.68rem;margin-bottom:4px;">IMO</div>
          <div style="color:{TEXT_MAIN};font-size:0.8rem;">9762326</div>
          <div style="color:{TEXT_MUTED};font-size:0.68rem;margin-top:8px;margin-bottom:4px;">MMSI</div>
          <div style="color:{TEXT_MAIN};font-size:0.8rem;">636017506</div>
          <div style="color:{TEXT_MUTED};font-size:0.68rem;margin-top:8px;margin-bottom:4px;">ETA</div>
          <div style="color:{YELLOW_WARN};font-size:0.8rem;font-weight:700;">18 Apr 2026</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_map1:
        ship_map = build_map(st.session_state.ship_data)
        st_folium(ship_map, width=None, height=520, returned_objects=[])

    # ── Mappa di supporto con nave lampeggiante ───────────
    section("📡 Posizione nave — Zoom locale")

    # Coordinate nave (fallback oceano indiano se non ancora tracciata)
    _lat = st.session_state.ship_data["lat"] if st.session_state.ship_data else 5.0
    _lon = st.session_state.ship_data["lon"] if st.session_state.ship_data else 80.0

    # Mappa zoom locale — CartoDB dark, solo nave, niente zone conflitto
    m_zoom = folium.Map(
        location=[_lat, _lon],
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )

    # Cerchi pulsanti concentrici (effetto sonar)
    for r, op in [(80000, 0.25), (160000, 0.12), (260000, 0.06)]:
        folium.Circle(
            location=[_lat, _lon],
            radius=r,
            color=GREEN_OK,
            fill=True,
            fill_opacity=op,
            weight=1.5 if r == 80000 else 1,
        ).add_to(m_zoom)

    # Marker nave con animazione lampeggio verde
    folium.Marker(
        location=[_lat, _lon],
        icon=folium.DivIcon(html="""
            <style>
            @keyframes ship-pulse {
                0%   { box-shadow: 0 0 0 0 rgba(46,204,113,0.8); transform: scale(1); }
                50%  { box-shadow: 0 0 0 18px rgba(46,204,113,0); transform: scale(1.1); }
                100% { box-shadow: 0 0 0 0 rgba(46,204,113,0); transform: scale(1); }
            }
            @keyframes ship-glow {
                0%,100% { filter: drop-shadow(0 0 4px #2ECC71); opacity:1; }
                50%      { filter: drop-shadow(0 0 14px #2ECC71); opacity:0.85; }
            }
            .ship-dot {
                width:14px; height:14px; border-radius:50%;
                background:#2ECC71; border:2px solid #fff;
                animation: ship-pulse 1.4s ease-in-out infinite;
                margin: 0 auto 4px auto;
            }
            .ship-icon { animation: ship-glow 1.4s ease-in-out infinite; font-size:30px; }
            </style>
            <div style="text-align:center;">
              <div class="ship-dot"></div>
              <div class="ship-icon">🚢</div>
              <div style="font-family:monospace;font-size:10px;color:#2ECC71;
              font-weight:700;white-space:nowrap;text-shadow:0 0 6px #000;
              margin-top:2px;">MSC JADE</div>
            </div>
        """, icon_size=(80, 70), icon_anchor=(40, 35)),
        popup=folium.Popup(f"""
            <div style='font-family:monospace;font-size:12px;min-width:180px;background:#161B22;
            color:#E6EDF3;padding:10px;border-radius:6px;border:1px solid #30363D;'>
            <b style='color:#00C4FF;'>🚢 MSC JADE</b><br>
            📍 {_lat:.4f}°, {_lon:.4f}°<br>
            IMO: 9762326 | MMSI: 636017506<br>
            <span style='color:#F1C40F;'>ETA Rotterdam: 18 Apr 2026</span>
            </div>
        """, max_width=250)
    ).add_to(m_zoom)

    # Linea rotta stimata Shanghai → posizione attuale → Rotterdam
    rotta_punti = [
        [31.23, 121.47],   # Shanghai
        [_lat, _lon],       # Posizione attuale
        [51.90, 4.48],      # Rotterdam
    ]
    folium.PolyLine(
        rotta_punti,
        color=ACCENT,
        weight=2,
        opacity=0.5,
        dash_array="6 4",
        tooltip="Rotta stimata Shanghai → Rotterdam"
    ).add_to(m_zoom)

    # Marker porti
    for nome, lat_p, lon_p, col in [
        ("🇨🇳 Shanghai", 31.23, 121.47, ACCENT2),
        ("🇳🇱 Rotterdam", 51.90, 4.48, GREEN_OK)
    ]:
        folium.Marker(
            location=[lat_p, lon_p],
            icon=folium.DivIcon(html=f"""
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                color:{col};font-weight:700;white-space:nowrap;
                text-shadow:1px 1px 3px #000;">{nome}</div>
            """, icon_size=(120, 20))
        ).add_to(m_zoom)

    col_mz1, col_mz2 = st.columns([2, 1])
    with col_mz1:
        st_folium(m_zoom, width=None, height=440, returned_objects=[])
    with col_mz2:
        # Mini pannello coordinate stile cockpit
        st.markdown(f"""
        <div style="background:{BG_CARD};border:1px solid {BORDER};
        border-left:3px solid {GREEN_OK};border-radius:8px;padding:16px;
        font-family:'JetBrains Mono',monospace;height:440px;box-sizing:border-box;">

          <div style="display:flex;align-items:center;gap:6px;margin-bottom:16px;">
            <div style="width:8px;height:8px;border-radius:50%;background:{GREEN_OK};
            box-shadow:0 0 8px {GREEN_OK};"></div>
            <span style="font-size:0.65rem;color:{GREEN_OK};letter-spacing:2px;">POSIZIONE ATTUALE</span>
          </div>

          <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;margin-bottom:3px;">LAT</div>
          <div style="font-size:1.1rem;color:{GREEN_OK};font-weight:700;margin-bottom:12px;">
          {"N/D" if not st.session_state.ship_data else f"{_lat:+.4f}°"}</div>

          <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;margin-bottom:3px;">LON</div>
          <div style="font-size:1.1rem;color:{GREEN_OK};font-weight:700;margin-bottom:16px;">
          {"N/D" if not st.session_state.ship_data else f"{_lon:+.4f}°"}</div>

          <div style="border-top:1px solid {BORDER};padding-top:12px;margin-bottom:12px;"></div>

          <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;margin-bottom:3px;">VELOCITÀ</div>
          <div style="font-size:0.95rem;color:{ACCENT2};font-weight:600;margin-bottom:10px;">
          {"N/D" if not st.session_state.ship_data else f"{st.session_state.ship_data['speed']:.1f} nodi"}</div>

          <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;margin-bottom:3px;">ROTTA</div>
          <div style="font-size:0.95rem;color:{ACCENT2};font-weight:600;margin-bottom:10px;">
          {"N/D" if not st.session_state.ship_data else f"{st.session_state.ship_data['course']:.0f}°"}</div>

          <div style="border-top:1px solid {BORDER};padding-top:12px;"></div>
          <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;margin-bottom:3px;">DEST.</div>
          <div style="font-size:0.85rem;color:{YELLOW_WARN};font-weight:700;">Rotterdam</div>
          <div style="font-size:0.75rem;color:{GREEN_OK};margin-top:4px;">ETA 18 Apr 2026</div>
        </div>
        """, unsafe_allow_html=True)

    # Legenda zone conflitto
    section("⚠️ Zone conflitto monitorate")
    cols_z = st.columns(3)
    for i, zone in enumerate(CONFLICT_ZONES):
        with cols_z[i % 3]:
            emoji = "🔴" if zone["color"] == "red" else "🟠"
            st.markdown(f"""
            <div style="background:{BG_CARD};border:1px solid {BORDER};
            border-left:3px solid {'#E74C3C' if zone['color']=='red' else '#F97316'};
            border-radius:6px;padding:10px 14px;margin-bottom:8px;font-family:'DM Sans',sans-serif;">
            <span style="font-size:0.85rem;color:{TEXT_MAIN};">{emoji} <b>{zone['name']}</b></span><br>
            <span style="font-size:0.75rem;color:{TEXT_MUTED};">Raggio monitorato: {zone['radius']} km</span>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 7 — MATERIE PRIME
# ════════════════════════════════════════════════════════

with tab2:
    section("🏭 Materie Prime — Scorte & Prezzi")

    @st.cache_data
    def load_scorte():
        df = pd.read_excel("magazzino_mat_prim.xlsx", sheet_name="SITUAZIONE GENERALE SCORTE")
        row = df.iloc[0]
        scorte = {
            "Liquirizia MF":      float(row.get("LIQUIRIZIA MF (matrin free)", 0) or 0),
            "Liquirizia LM":      float(row.get("LIQUIRIZIA LM (low matrin)", 0) or 0),
            "Liquirizia ITA":     float(row.get("liquirizia ITA SPERLARI", 0) or 0),
            "Melasso":            float(str(row.get("MELASSO ", 0) or 0).replace("-","0") or 0),
            "Glucosio":           float(str(row.get("GLUCOSIO ", 0) or 0).replace("-","0") or 0),
            "LESD":               float(str(row.get("LESD ", 0) or 0).replace("-","0") or 0),
            "Zucchero":           float(row.get("ZUCCHERO", 0) or 0),
            "Caramello":          float(row.get("CARAMELLO", 0) or 0),
            "Maltodestrina 01910":float(row.get("MALTODESTINA 01910", 0) or 0),
            "Destrina":           float(row.get("DESTRINA", 0) or 0),
            "Carbone":            float(row.get("CARBONE", 0) or 0),
        }
        return scorte

    @st.cache_data
    def load_prezzi_storico():
        df = pd.read_excel("prezzi_materie_prime.xlsx", sheet_name="cruscotto")
        df = df.rename(columns={df.columns[0]: "Materia"})
        anni = [c for c in df.columns if str(c).isdigit()]
        records = []
        for _, row in df.iterrows():
            nome = str(row["Materia"]).strip()
            for a in anni:
                val = row[a]
                try:
                    v = float(str(val).replace("-","").replace("€","").strip())
                    if v > 0:
                        records.append({"Materia": nome, "Anno": int(a), "Prezzo": v})
                except:
                    pass
        return pd.DataFrame(records)

    # Soglie minime configurabili (kg)
    SOGLIE_MIN = {
        "Liquirizia MF":       1000,
        "Liquirizia LM":       1000,
        "Liquirizia ITA":       500,
        "Melasso":             3000,
        "Glucosio":            3000,
        "LESD":                 200,
        "Zucchero":            2000,
        "Caramello":            500,
        "Maltodestrina 01910":  300,
        "Destrina":             500,
        "Carbone":              200,
    }

    # Prezzi correnti 2026 (€/kg) per calcolo valore magazzino
    PREZZI_2026 = {
        "Liquirizia MF":       6.10,
        "Liquirizia LM":       6.10,
        "Liquirizia ITA":      6.10,
        "Melasso":             0.83,
        "Glucosio":            0.058,
        "LESD":                1.50,
        "Zucchero":            0.67,
        "Caramello":           2.20,
        "Maltodestrina 01910": 1.40,
        "Destrina":            1.90,
        "Carbone":            11.33,
    }

    scorte  = load_scorte()
    df_prez = load_prezzi_storico()

    # ── Alert scorte ────────────────────────────────────
    alerts_scorte = []
    warn_scorte   = []
    for mat, qty in scorte.items():
        soglia = SOGLIE_MIN.get(mat, 500)
        if qty <= 0:
            alerts_scorte.append(f"🔴 {mat}: ESAURITA (0 kg)")
        elif qty < soglia:
            warn_scorte.append(f"🟡 {mat}: {qty:,.0f} kg — sotto soglia minima ({soglia:,.0f} kg)")

    if alerts_scorte:
        for a in alerts_scorte:
            render_alert(a, "alert-red")
    if warn_scorte:
        for w in warn_scorte:
            render_alert(w, "alert-yellow")
    if not alerts_scorte and not warn_scorte:
        render_alert("🟢 Tutte le scorte nei range di normalità", "alert-green")

    # ── KPI rapidi ────────────────────────────────────
    section("📊 Stato scorte al " + datetime.now().strftime("%d/%m/%Y"))

    valore_totale = sum(scorte.get(m, 0) * PREZZI_2026.get(m, 0) for m in scorte)
    peso_totale   = sum(scorte.values())
    n_critiche    = len(alerts_scorte)
    n_warning     = len(warn_scorte)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💰 Valore magazzino", format_euro(valore_totale))
    with c2: st.metric("⚖️ Peso totale scorte", f"{peso_totale:,.0f} kg")
    with c3: st.metric("🔴 Materie critiche", n_critiche)
    with c4: st.metric("🟡 Materie in warning", n_warning)

    # ── Tabella scorte con semafori ────────────────────
    section("🏭 Dettaglio scorte con semafori")
    rows = []
    for mat, qty in scorte.items():
        soglia = SOGLIE_MIN.get(mat, 500)
        prezzo = PREZZI_2026.get(mat, 0)
        valore = qty * prezzo
        if qty <= 0:           stato = "🔴 ESAURITA"
        elif qty < soglia:     stato = "🟡 BASSA"
        else:                  stato = "🟢 OK"
        rows.append({
            "Materia Prima":   mat,
            "Scorta (kg)":     f"{qty:,.0f}",
            "Soglia min (kg)": f"{soglia:,.0f}",
            "Prezzo €/kg":     f"€ {prezzo:.3f}",
            "Valore € tot":    format_euro(valore),
            "Stato":           stato,
        })
    # Riga totale
    rows.append({
        "Materia Prima":   "── TOTALE ──",
        "Scorta (kg)":     f"{sum(scorte.values()):,.0f}",
        "Soglia min (kg)": "—",
        "Prezzo €/kg":     "—",
        "Valore € tot":    format_euro(valore_totale),
        "Stato":           "📊",
    })
    df_tab = pd.DataFrame(rows)
    st.dataframe(df_tab, use_container_width=True, hide_index=True)

    # ── Grafici scorte ─────────────────────────────────
    section("📊 Visualizzazione scorte")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        # Bar chart scorte con colori semaforo
        colors_bar = []
        for mat, qty in scorte.items():
            soglia = SOGLIE_MIN.get(mat, 500)
            if qty <= 0:       colors_bar.append(RED_ALERT)
            elif qty < soglia: colors_bar.append(YELLOW_WARN)
            else:              colors_bar.append(GREEN_OK)

        fig_sc = go.Figure(go.Bar(
            x=list(scorte.keys()),
            y=list(scorte.values()),
            marker_color=colors_bar,
            text=[f"{v:,.0f}" for v in scorte.values()],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=TEXT_MAIN),
        ))
        lay_sc = plotly_layout("SCORTE ATTUALI (KG)")
        lay_sc["xaxis"]["tickangle"] = -35
        lay_sc["yaxis"]["tickformat"] = ",.0f"
        fig_sc.update_layout(**lay_sc)
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_b2:
        # Pie chart valore economico
        mat_vals = {m: scorte.get(m,0)*PREZZI_2026.get(m,0) for m in scorte if scorte.get(m,0)>0}
        fig_pv = px.pie(
            names=list(mat_vals.keys()),
            values=list(mat_vals.values()),
            hole=0.45,
            color_discrete_sequence=PALETTE
        )
        fig_pv.update_traces(
            pull=[0.04]*len(mat_vals),
            marker=dict(line=dict(color=BG_DARK, width=2)),
            textfont=dict(family="JetBrains Mono", color=TEXT_MAIN)
        )
        fig_pv.update_layout(**pie_layout("VALORE ECONOMICO SCORTE"))
        st.plotly_chart(fig_pv, use_container_width=True)

    # ── Storico prezzi ────────────────────────────────
    section("📈 Storico prezzi materie prime (2014 → 2026)")

    if not df_prez.empty:
        # Selettore materie prime
        materie_disp = sorted(df_prez["Materia"].unique())
        mat_sel = st.multiselect(
            "Seleziona materie prime da confrontare",
            materie_disp,
            default=materie_disp[:5]
        )

        if mat_sel:
            df_plot = df_prez[df_prez["Materia"].isin(mat_sel)]

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                fig_px = px.line(
                    df_plot.sort_values(["Materia","Anno"]),
                    x="Anno", y="Prezzo", color="Materia",
                    markers=True, color_discrete_sequence=PALETTE
                )
                fig_px.update_traces(line=dict(width=2.5), marker=dict(size=7))
                lay_px = plotly_layout("ANDAMENTO PREZZI (€/KG)", height=440)
                lay_px["yaxis"]["tickprefix"] = "€ "
                lay_px["yaxis"]["tickformat"] = ".3f"
                lay_px["legend"] = dict(
                    bgcolor="rgba(0,0,0,0)", bordercolor=BORDER,
                    font=dict(color=TEXT_MUTED), orientation="h",
                    yanchor="bottom", y=-0.45
                )
                fig_px.update_layout(**lay_px)
                st.plotly_chart(fig_px, use_container_width=True)

            with col_p2:
                # Variazione % rispetto al 2020 (base=100)
                df_idx = df_plot.copy()
                base = df_idx[df_idx["Anno"]==2020].set_index("Materia")["Prezzo"]
                df_idx["Indice"] = df_idx.apply(
                    lambda r: (r["Prezzo"] / base.get(r["Materia"], r["Prezzo"])) * 100
                    if base.get(r["Materia"]) else 100, axis=1
                )
                fig_idx = px.line(
                    df_idx.sort_values(["Materia","Anno"]),
                    x="Anno", y="Indice", color="Materia",
                    markers=True, color_discrete_sequence=PALETTE
                )
                fig_idx.update_traces(line=dict(width=2.5), marker=dict(size=7))
                lay_idx = plotly_layout("INDICE PREZZI (base 2020 = 100)", height=440)
                lay_idx["yaxis"]["ticksuffix"] = ""
                lay_idx["yaxis"]["tickformat"] = ".0f"
                lay_idx["legend"] = dict(
                    bgcolor="rgba(0,0,0,0)", bordercolor=BORDER,
                    font=dict(color=TEXT_MUTED), orientation="h",
                    yanchor="bottom", y=-0.45
                )
                # Linea base 100
                fig_idx.add_hline(y=100, line_dash="dot", line_color=BORDER,
                                  annotation_text="base 2020",
                                  annotation_font_color=TEXT_MUTED)
                fig_idx.update_layout(**lay_idx)
                st.plotly_chart(fig_idx, use_container_width=True)

        # YoY prezzi
        section("📊 Variazione prezzi YoY — Anno su anno")
        mat_yoy = st.selectbox("Seleziona materia prima per YoY", materie_disp)
        df_yoy_m = df_prez[df_prez["Materia"]==mat_yoy].sort_values("Anno").copy()
        df_yoy_m["YoY_%"] = df_yoy_m["Prezzo"].pct_change() * 100
        df_yoy_m = df_yoy_m.dropna(subset=["YoY_%"])
        if not df_yoy_m.empty:
            fig_yoy_m = px.bar(
                df_yoy_m, x="Anno", y="YoY_%",
                color="YoY_%",
                color_continuous_scale=[[0,"#E74C3C"],[0.5,"#F1C40F"],[1,"#2ECC71"]],
                text=df_yoy_m["YoY_%"].apply(lambda x: f"{x:+.1f}%")
            )
            fig_yoy_m.update_traces(
                textfont=dict(family="JetBrains Mono", color=TEXT_MAIN),
                textposition="outside"
            )
            lay_yoy_m = plotly_layout(f"VARIAZIONE PREZZO YoY — {mat_yoy}")
            lay_yoy_m["yaxis"]["ticksuffix"] = "%"
            lay_yoy_m["coloraxis_showscale"] = False
            fig_yoy_m.update_layout(**lay_yoy_m)
            st.plotly_chart(fig_yoy_m, use_container_width=True)

