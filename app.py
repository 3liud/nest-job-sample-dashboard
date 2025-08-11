import os
import hashlib
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask_caching import Cache

# -----------------------------
# Load data (Parquet preferred)
# -----------------------------
DATA_PATHS = [
    "data/synthetic_mnd_data_enhanced.parquet",
    "data/synthetic_mnd_data_enhanced.csv",
    "data/synthetic_mnd_data.csv",
]
for p in DATA_PATHS:
    if os.path.exists(p):
        if p.endswith(".parquet"):
            df = pd.read_parquet(p)
        else:
            df = pd.read_csv(p, parse_dates=["Admission_Date", "Discharge_Date"])
        break
else:
    raise FileNotFoundError("No dataset found in ./data")

df["Month"] = df["Admission_Date"].dt.to_period("M").astype(str)
df["Year"] = df["Admission_Date"].dt.year.astype(str)

# City coordinates for the ~30 cities in the generator
CITY_LATLON = {
    # Kenya
    "Nairobi": (-1.286389, 36.817223),
    "Mombasa": (-4.043477, 39.668206),
    "Kisumu": (-0.091702, 34.767956),
    # Nigeria
    "Lagos": (6.524379, 3.379206),
    "Abuja": (9.076479, 7.398574),
    "Kano": (12.002179, 8.591956),
    # South Africa
    "Johannesburg": (-26.204103, 28.047304),
    "Cape Town": (-33.924869, 18.424055),
    "Durban": (-29.858681, 31.021839),
    # Egypt
    "Cairo": (30.044420, 31.235712),
    "Alexandria": (31.200092, 29.918739),
    "Giza": (30.013055, 31.208853),
    # Ethiopia
    "Addis Ababa": (8.980603, 38.757759),
    "Gondar": (12.607000, 37.466000),
    "Hawassa": (7.066667, 38.500000),
    # Ghana
    "Accra": (5.603717, -0.187000),
    "Kumasi": (6.688481, -1.624431),
    "Tamale": (9.404700, -0.839300),
    # Uganda
    "Kampala": (0.347596, 32.582520),
    "Gulu": (2.774600, 32.298900),
    "Mbarara": (-0.607200, 30.654500),
    # Tanzania
    "Dar es Salaam": (-6.792354, 39.208328),
    "Arusha": (-3.386925, 36.682995),
    "Mwanza": (-2.516433, 32.917480),
    # Morocco
    "Casablanca": (33.573110, -7.589843),
    "Rabat": (34.020882, -6.841650),
    "Marrakesh": (31.629472, -7.981084),
    # Senegal
    "Dakar": (14.716677, -17.467686),
    "Saint-Louis": (16.032619, -16.481001),
    "Touba": (14.866667, -15.883333),
}

df["lat"] = df["City"].map(lambda c: CITY_LATLON.get(c, (None, None))[0])
df["lon"] = df["City"].map(lambda c: CITY_LATLON.get(c, (None, None))[1])

# -----------------------------
# App (dark theme) + cache
# -----------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server
cache = Cache(
    server, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
)

# Dark plotly template
px.defaults.template = "plotly_dark"

# -----------------------------
# Header: title + filters (single row, nice spacing)
# -----------------------------
header = html.Div(
    [
        html.Div(
            [
                html.H2("African Neonatal Outcomes Dashboard", className="m-0"),
                dbc.Button(
                    "Clear Map Selection",
                    id="btn-clear-map",
                    size="sm",
                    color="secondary",
                    className="ms-3",
                ),
            ],
            className="d-flex align-items-center justify-content-between flex-wrap",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="f-country",
                        options=[
                            {"label": c, "value": c}
                            for c in sorted(df["Country"].unique())
                        ],
                        multi=True,
                        placeholder="Country",
                    ),
                    className="filter-col",
                    md=2,
                    sm=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="f-city",
                        options=[
                            {"label": c, "value": c}
                            for c in sorted(df["City"].unique())
                        ],
                        multi=True,
                        placeholder="City",
                    ),
                    className="filter-col",
                    md=3,
                    sm=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="f-dx",
                        options=[
                            {"label": c, "value": c}
                            for c in sorted(df["Diagnosis"].unique())
                        ],
                        multi=True,
                        placeholder="Diagnosis",
                    ),
                    className="filter-col",
                    md=3,
                    sm=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="f-outcome",
                        options=[
                            {"label": c, "value": c}
                            for c in sorted(df["Outcome"].unique())
                        ],
                        multi=True,
                        placeholder="Outcome",
                    ),
                    className="filter-col",
                    md=2,
                    sm=6,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="f-year",
                        options=[
                            {"label": y, "value": y}
                            for y in sorted(df["Year"].unique())
                        ],
                        multi=True,
                        placeholder="Year",
                    ),
                    className="filter-col",
                    md=2,
                    sm=6,
                ),
                dbc.Col(
                    dbc.Button(
                        "Reset",
                        id="btn-reset",
                        size="sm",
                        color="light",
                        className="w-100",
                    ),
                    md=1,
                    sm=6,
                    className="mt-2 mt-md-0",
                ),
                dbc.Col(
                    dbc.Button(
                        "Download CSV",
                        id="btn-dl",
                        size="sm",
                        color="primary",
                        className="w-100",
                    ),
                    md=2,
                    sm=6,
                    className="mt-2 mt-md-0",
                ),
                dcc.Download(id="dl-data"),
            ],
            className="gx-2 gy-2 mt-2 filters-row",
        ),
    ],
    className="header",
)


# -----------------------------
# KPI helper
# -----------------------------
def kpi(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(title, className="text-muted small"),
                html.H4(value, className=f"text-{color} m-0"),
            ]
        ),
        className="shadow-sm kpi-card",
    )


# -----------------------------
# Layout
# -----------------------------
app.layout = dbc.Container(
    [
        header,
        dcc.Store(id="store-map-city"),  # holds city selected via map click
        html.Div(id="summary-alert"),
        dbc.Row(id="kpi-row", className="g-3 my-2"),
        # Big map on its own row
        dbc.Row(
            [dbc.Col(dcc.Graph(id="fig-map", style={"height": "640px"}), width=12)],
            className="g-3 mb-2",
        ),
        # Smaller charts below
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="fig-treemap"), md=6, className="mb-3"),
                dbc.Col(dcc.Graph(id="fig-season"), md=6, className="mb-3"),
            ],
            className="g-3",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="fig-income"), md=6, className="mb-3"),
                dbc.Col(dcc.Graph(id="fig-facout"), md=6, className="mb-5"),
            ],
            className="g-3",
        ),
    ],
    fluid=True,
    style={"padding": "16px", "maxWidth": "1800px"},
)


# -----------------------------
# Utilities: reset + cache
# -----------------------------
@app.callback(
    Output("f-country", "value"),
    Output("f-city", "value"),
    Output("f-dx", "value"),
    Output("f-outcome", "value"),
    Output("f-year", "value"),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return None, None, None, None, None


def _hash_filters(country, city, dx, outcome, year, map_city):
    key = repr(
        (
            tuple(country or []),
            tuple(city or []),
            tuple(dx or []),
            tuple(outcome or []),
            tuple(year or []),
            map_city or "",
        )
    )
    return hashlib.sha256(key.encode()).hexdigest()


@cache.memoize()
def get_filtered_df(key_hash, country, city, dx, outcome, year, map_city):
    dff = df
    # map selection narrows City/Country
    if map_city:
        dff = dff[dff["City"].eq(map_city)]
    if country:
        dff = dff[dff["Country"].isin(country)]
    if city:
        dff = dff[dff["City"].isin(city)]
    if dx:
        dff = dff[dff["Diagnosis"].isin(dx)]
    if outcome:
        dff = dff[dff["Outcome"].isin(outcome)]
    if year:
        dff = dff[dff["Year"].isin(year)]
    cols = [
        "Country",
        "City",
        "lat",
        "lon",
        "Facility_Level",
        "Outcome",
        "Diagnosis",
        "Household_Income_USD",
        "Gestational_Age_weeks",
        "Birth_Weight_g",
        "Admission_Date",
        "Discharge_Date",
        "Length_of_Stay_days",
        "Month",
        "Year",
    ]
    return dff.loc[:, cols].copy()


# -----------------------------
# Map click -> store selected city
# -----------------------------
@app.callback(
    Output("store-map-city", "data"),
    Input("fig-map", "clickData"),
    Input("btn-clear-map", "n_clicks"),
    prevent_initial_call=True,
)
def on_map_click(click, clear_clicks):
    # Clear has priority
    trigger = dash.callback_context.triggered[0]["prop_id"]
    if "btn-clear-map" in trigger:
        return None
    if click and "points" in click and click["points"]:
        # px.scatter_geo exposes point's 'text' (City) and customdata if set
        pt = click["points"][0]
        city = pt.get("text")  # we set text="City"
        return city
    return dash.no_update


# -----------------------------
# Main update
# -----------------------------
@app.callback(
    Output("summary-alert", "children"),
    Output("kpi-row", "children"),
    Output("fig-map", "figure"),
    Output("fig-treemap", "figure"),
    Output("fig-season", "figure"),
    Output("fig-income", "figure"),
    Output("fig-facout", "figure"),
    Input("f-country", "value"),
    Input("f-city", "value"),
    Input("f-dx", "value"),
    Input("f-outcome", "value"),
    Input("f-year", "value"),
    Input("store-map-city", "data"),
)
def update(country, city, dx, outcome, year, map_city):
    key = _hash_filters(country, city, dx, outcome, year, map_city)
    dff = get_filtered_df(key, country, city, dx, outcome, year, map_city)

    if dff.empty:
        alert = dbc.Alert(
            "No data for the current filters. Adjust and try again.",
            color="warning",
            className="my-2",
        )
        empty = px.scatter(title="No data")
        empty.update_layout(template="plotly_dark")
        empty.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        return alert, [], empty, empty, empty, empty, empty

    alert = None

    # KPIs
    admissions = f"{len(dff):,}"
    mort = f"{(dff['Outcome'].eq('Succumbed/Died').mean()*100):.1f}%"
    los = f"{dff['Length_of_Stay_days'].mean():.1f} days"
    inc = f"${dff['Household_Income_USD'].median():,.0f}"
    kpis = [
        dbc.Col(kpi("Admissions", admissions, "primary"), md=2, sm=6),
        dbc.Col(kpi("Mortality Rate", mort, "danger"), md=2, sm=6),
        dbc.Col(kpi("Avg LOS", los, "info"), md=2, sm=6),
        dbc.Col(kpi("Median Income", inc, "success"), md=2, sm=6),
    ]

    # Map: aggregate by City with lat/lon; Africa scope
    geo_agg = (
        dff.dropna(subset=["lat", "lon"])
        .groupby(["Country", "City", "lat", "lon"], as_index=False)
        .agg(
            Admissions=("Outcome", "count"),
            Mortality=("Outcome", lambda s: (s == "Succumbed/Died").mean() * 100),
        )
    )
    fig_map = px.scatter_geo(
        geo_agg,
        lat="lat",
        lon="lon",
        size="Admissions",
        size_max=30,
        color="Mortality",
        color_continuous_scale="Reds",
        text="City",
        hover_data={
            "Admissions": ":,",
            "Mortality": ":.1f",
            "lat": False,
            "lon": False,
        },
        title=(
            "Click a city to filter • " + (f"Selected: {map_city}" if map_city else "")
        ),
    )
    fig_map.update_geos(
        scope="africa", showcountries=True, showcoastlines=True, fitbounds="locations"
    )
    fig_map.update_layout(
        coloraxis_colorbar_title="Mortality (%)",
        margin=dict(l=10, r=10, t=60, b=10),
        height=640,
    )

    # Treemap: Diagnosis→Outcome (counts)
    dff["_one"] = 1
    fig_treemap = px.treemap(
        dff,
        path=["Diagnosis", "Outcome"],
        values="_one",
        title="Diagnosis & Outcome Breakdown (counts)",
    )
    fig_treemap.update_layout(margin=dict(l=10, r=10, t=50, b=10))

    # Seasonality
    season = (
        dff.groupby(["Month", "Country"], as_index=False)
        .size()
        .rename(columns={"size": "Admissions"})
    )
    fig_season = px.line(
        season,
        x="Month",
        y="Admissions",
        color="Country",
        markers=True,
        title="Monthly Admissions Trend by Country",
    )
    fig_season.update_xaxes(dtick="M1", tickangle=-45)
    fig_season.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=420)

    # Income vs Outcome
    fig_income = px.box(
        dff,
        x="Outcome",
        y="Household_Income_USD",
        color="Outcome",
        points=False,
        title="Household Income by Outcome",
    )
    fig_income.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=420)

    # Facility outcomes (percent stacked)
    fig_facout = px.histogram(
        dff,
        x="Facility_Level",
        color="Outcome",
        barmode="stack",
        barnorm="percent",
        title="Outcome Proportions by Facility Level",
    )
    fig_facout.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=420)

    return alert, kpis, fig_map, fig_treemap, fig_season, fig_income, fig_facout


# -----------------------------
# Download (cached slice)
# -----------------------------
@app.callback(
    Output("dl-data", "data"),
    Input("btn-dl", "n_clicks"),
    State("f-country", "value"),
    State("f-city", "value"),
    State("f-dx", "value"),
    State("f-outcome", "value"),
    State("f-year", "value"),
    State("store-map-city", "data"),
    prevent_initial_call=True,
)
def download_csv(n, country, city, dx, outcome, year, map_city):
    key = _hash_filters(country, city, dx, outcome, year, map_city)
    dff = get_filtered_df(key, country, city, dx, outcome, year, map_city)
    return dcc.send_data_frame(dff.to_csv, "filtered_data.csv", index=False)


# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
