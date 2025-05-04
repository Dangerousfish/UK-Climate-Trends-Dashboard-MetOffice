import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import re
from io import StringIO

# ----------------------
# Constants & Stations
# ----------------------
stations = {
    "aberporth": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/aberporthdata.txt",
    "armagh": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/armaghdata.txt",
    "ballypatrick": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/ballypatrickdata.txt",
    "bradford": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/bradforddata.txt",
    "braemar": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/braemardata.txt",
    "camborne": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/cambornedata.txt",
    "cambridge": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/cambridgedata.txt",
    "cardiff": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/cardiffdata.txt",
    "chivenor": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/chivenordata.txt",
    "cwmystwyth": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/cwmystwythdata.txt",
    "dunstaffnage": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/dunstaffnagedata.txt",
    "durham": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/durhamdata.txt",
    "eastbourne": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/eastbournedata.txt",
    "eskdalemuir": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/eskdalemuirdata.txt",
    "heathrow": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/heathrowdata.txt",
    "hurn": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/hurndata.txt",
    "lerwick": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/lerwickdata.txt",
    "leuchars": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/leucharsdata.txt",
    "lowestoft": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/lowestoftdata.txt",
    "manston": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/manstondata.txt",
    "nairn": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/nairndata.txt",
    "newtonrigg": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/newtonriggdata.txt",
    "oxford": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/oxforddata.txt",
    "paisley": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/paisleydata.txt",
    "ringway": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/ringwaydata.txt",
    "rossonwye": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/rossonwyedata.txt",
    "shawbury": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/shawburydata.txt",
    "sheffield": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/sheffielddata.txt",
    "southampton": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/southamptondata.txt",
    "stornoway": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/stornowaydata.txt",
    "valley": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/valleydata.txt",
    "waddington": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/waddingtondata.txt",
    "whitby": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/whitbydata.txt",
    "wick": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/wickairportdata.txt",
    "yeovilton": "https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/yeoviltondata.txt"
}

def clean_value(val):
    v = str(val).strip()
    estimated = '*' in v
    auto_sensor = '#' in v
    v = v.replace('*', '').replace('#', '')
    if v in {'---', ''}:
        return None, estimated, auto_sensor
    try:
        return float(v), estimated, auto_sensor
    except ValueError:
        return None, estimated, auto_sensor


def parse_station_data(text, station):
    lines = text.strip().splitlines()
    header_idx = next(i for i,l in enumerate(lines) if re.match(r'^\s*yyyy', l.lower()))
    data = lines[header_idx+1:]
    df = pd.read_fwf(StringIO("\n".join(data)), names=["year","month","tmax_raw","tmin_raw","af_raw","rain_raw","sun_raw"])
    df['station'] = station
    for col in ['tmax','tmin','af','rain','sun']:
        df[col], df[f'{col}_estimated'], df[f'{col}_auto_sensor'] = zip(*df[f'{col}_raw'].map(clean_value))
        df.drop(columns=[f'{col}_raw'], inplace=True)
    # Clean year/month and date
    df = df[pd.to_numeric(df['year'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['month'], errors='coerce').notnull()]
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['date'] = pd.to_datetime(dict(year=df['year'], month=df['month'], day=1), errors='coerce')
    return df

# ----------------------
# Compile Data
# ----------------------
@st.cache_data(show_spinner=False)
def compile_data():
    all_data = []
    for station,url in stations.items():
        try:
            r = requests.get(url)
            r.raise_for_status()
            df = parse_station_data(r.text, station)
            all_data.append(df)
        except Exception:
            continue
    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv('combined_uk_station_climate_data.csv', index=False)
    return combined

# ----------------------
# Extract Coordinates
# ----------------------
coord_pattern = re.compile(r'Lat\s+([\-\d\.]+)\s+Lon\s+([\-\d\.]+)', re.IGNORECASE)

@st.cache_data(show_spinner=False)
def extract_coords():
    coords = []
    for station,url in stations.items():
        try:
            text = requests.get(url).text
            header = '\n'.join(text.splitlines()[:10])
            m = coord_pattern.search(header)
            lat,lon = (float(m.group(1)), float(m.group(2))) if m else (None,None)
            coords.append({'station': station, 'latitude': lat, 'longitude': lon})
        except Exception:
            coords.append({'station': station, 'latitude': None, 'longitude': None})
    dfc = pd.DataFrame(coords)
    dfc.to_csv('station_coordinates.csv', index=False)
    return dfc

combined_df = compile_data()
coords_df = extract_coords()

# Prepare data
combined_df['avg_temp'] = combined_df[['tmax','tmin']].mean(axis=1)
combined_df['year'] = pd.to_datetime(combined_df['date']).dt.year
combined_df['month'] = pd.to_datetime(combined_df['date']).dt.month

# ----------------------
# Streamlit App UI
# ----------------------
st.sidebar.title("Filter Options")
with st.sidebar.expander("Station & Time"):
    station_list = sorted(combined_df['station'].unique())
    selected_stations = st.multiselect("Stations", station_list, default=['sheffield'])
    min_year, max_year = int(combined_df['year'].min()), int(combined_df['year'].max())
    selected_years = st.slider("Year Range", min_year, max_year, (min_year, max_year))

with st.sidebar.expander("Metric"):
    metric = st.selectbox("Metric", ['Average Temperature','Rainfall','Sunshine'])

filtered = combined_df[
    (combined_df['station'].isin(selected_stations)) &
    (combined_df['year']>=selected_years[0]) &
    (combined_df['year']<=selected_years[1])
]

st.title("UK Climate Trends Dashboard")
tabs = st.tabs(["Time Series","Heatmap","Map","Download"])

# Time Series
def plot_time_series():
    if metric=='Average Temperature': ycol,ylabel='avg_temp','Avg Temp (°C)'
    elif metric=='Rainfall': ycol,ylabel='rain','Rainfall (mm)'
    else: ycol,ylabel='sun','Sunshine (hrs)'
    df_agg = filtered.groupby(['station','year'])[ycol].mean().reset_index()
    fig = px.line(df_agg, x='year',y=ycol,color='station',markers=True,
                  labels={ycol: ylabel,'year':'Year'},title=f"{ylabel} Trends")
    st.plotly_chart(fig,use_container_width=True)

# Heatmap
def plot_heatmap():
    for stn in selected_stations:
        st.subheader(stn.title())
        piv = filtered[filtered['station']==stn].pivot_table(index='year',columns='month',values='avg_temp')
        fig=px.imshow(piv,labels=dict(color='°C'),aspect='auto',
                      color_continuous_scale='RdYlBu_r',title=f"Monthly Avg Temp – {stn.title()}")
        st.plotly_chart(fig,use_container_width=True)

# Map
def plot_map():
    dfm = filtered.groupby('station')['avg_temp'].mean().reset_index()
    dfm = dfm.merge(coords_df,on='station')
    fig=px.scatter_geo(dfm,lat='latitude',lon='longitude',color='avg_temp',size='avg_temp',
                        hover_name='station',projection='natural earth',
                        color_continuous_scale='RdYlBu_r',title="Station Mean Temp")
    fig.update_geos(fitbounds='locations',landcolor='LightGray')
    st.plotly_chart(fig,use_container_width=True)

# Download

def download_data():
    st.dataframe(filtered)
    csv=filtered.to_csv(index=False).encode('utf-8')
    st.download_button('Download CSV',csv,'filtered_climate.csv','text/csv')

# Render tabs
with tabs[0]: plot_time_series()
with tabs[1]: plot_heatmap()
with tabs[2]: plot_map()
with tabs[3]: download_data()
