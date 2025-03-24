import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

# Load data
df = pd.read_csv(
    "data/synthetic_mnd_data.csv", parse_dates=["Admission_Date", "Discharge_Date"]
)
df["Month"] = df["Admission_Date"].dt.to_period("M").astype(str)
df["Year"] = df["Admission_Date"].dt.year.astype(str)

# Summary card style
card_style = {
    "padding": "1rem",
    "backgroundColor": "#f0f0f0",
    "borderRadius": "0.5rem",
    "textAlign": "center",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
}

app = dash.Dash(__name__)
app.title = "NEST360 Sample Neonatal Dashboard"

app.layout = html.Div(
    [
        # Title
        html.Div(
            [
                html.H1(
                    "NEST360 Sample Neonatal Dashboard",
                    style={
                        "textAlign": "center",
                        "margin": "0",
                        "padding": "1rem",
                        "backgroundColor": "#ffffff",
                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                        "zIndex": "1100",
                        "position": "fixed",
                        "top": "0",
                        "width": "100%",
                    },
                )
            ]
        ),
        # Filters + Summary
        html.Div(
            [
                html.H3(
                    "Filters Menu",
                    style={
                        "textAlign": "center",
                        "margin": "0",
                    },
                ),
                html.Label("Filter by Hospital:"),
                dcc.Dropdown(
                    options=[
                        {"label": h, "value": h}
                        for h in sorted(df["Hospital"].unique())
                    ],
                    id="hospital-dropdown",
                    value=[],
                    placeholder="Select hospital(s)",
                    multi=True,
                ),
                html.Label("Filter by Outcome:"),
                dcc.Dropdown(
                    options=[
                        {"label": o, "value": o} for o in sorted(df["Outcome"].unique())
                    ],
                    id="outcome-dropdown",
                    value=[],
                    placeholder="Select outcome(s)",
                    multi=True,
                ),
                html.Label("Filter by Diagnosis:"),
                dcc.Dropdown(
                    options=[
                        {"label": d, "value": d}
                        for d in sorted(df["Diagnosis"].unique())
                    ],
                    id="diagnosis-dropdown",
                    value=[],
                    placeholder="Select diagnosis(es)",
                    multi=True,
                ),
                html.Label("Filter by Year:"),
                dcc.Dropdown(
                    options=[
                        {"label": y, "value": y} for y in sorted(df["Year"].unique())
                    ],
                    id="year-dropdown",
                    value=[],
                    placeholder="Select year(s)",
                    multi=True,
                ),
                html.Hr(),
                html.H3(
                    "Summary Details",
                    style={
                        "textAlign": "center",
                        "margin": "0",
                    },
                ),
                html.Div(
                    id="summary-cards",
                    style={
                        "marginTop": "1rem",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "1rem",
                    },
                ),
            ],
            style={
                "width": "25%",
                "position": "fixed",
                "top": "4rem",
                "left": "1rem",
                "padding": "1rem",
                "backgroundColor": "#f9f9f9",
                "boxShadow": "0 0 10px rgba(0,0,0,0.1)",
                "zIndex": "1000",
                "marginTop": "5rem",
            },
        ),
        # Graphs
        html.Div(
            [
                dcc.Graph(id="fig_outcome_diag"),
                dcc.Graph(id="fig_los_outcome"),
                dcc.Graph(id="fig_admit_trend"),
                dcc.Graph(id="fig_bw"),
                dcc.Graph(id="fig_pie_outcomes"),
            ],
            style={
                "width": "70%",
                "float": "right",
                "marginLeft": "30%",
                "padding": "2rem",
                "marginTop": "1rem",
            },
        ),
    ]
)


@app.callback(
    Output("summary-cards", "children"),
    Output("fig_outcome_diag", "figure"),
    Output("fig_los_outcome", "figure"),
    Output("fig_admit_trend", "figure"),
    Output("fig_bw", "figure"),
    Output("fig_pie_outcomes", "figure"),
    Input("hospital-dropdown", "value"),
    Input("outcome-dropdown", "value"),
    Input("diagnosis-dropdown", "value"),
    Input("year-dropdown", "value"),
)
def update_charts(hospital, outcome, diagnosis, year):
    """
    Updates the summary cards, histograms, line chart, violin plot, and pie chart
    based on the selected hospital(s), outcome(s), diagnosis, and year(s).

    Parameters
    ----------
    hospital : list of str
        A list of hospital names to filter the data by.
    outcome : list of str
        A list of outcome names to filter the data by.
    diagnosis : list of str
        A list of diagnosis names to filter the data by.
    year : list of str
        A list of year strings to filter the data by.

    Returns
    -------
    summary_cards : list of dash.html.Div
        A list of Div components containing the summary stats.
    fig1 : dash.graph_objs.Figure
        A histogram of the outcome distribution by diagnosis.
    fig2 : dash.graph_objs.Figure
        A bar chart of the average length of stay by outcome.
    fig3 : dash.graph_objs.Figure
        A line chart of the monthly admissions by hospital.
    fig4 : dash.graph_objs.Figure
        A violin plot of the birth weight distribution by outcome.
    fig5 : dash.graph_objs.Figure
        A pie chart of the patient outcome proportions.
    """
    filtered = df.copy()
    if hospital:
        filtered = filtered[filtered["Hospital"].isin(hospital)]
    if outcome:
        filtered = filtered[filtered["Outcome"].isin(outcome)]
    if diagnosis:
        filtered = filtered[filtered["Diagnosis"].isin(diagnosis)]
    if year:
        filtered = filtered[filtered["Year"].isin(year)]

    # Summary stats
    total_admissions = len(filtered)
    num_deaths = (filtered["Outcome"] == "Died").sum()
    avg_los = filtered["Length_of_Stay_days"].mean().round(1)
    avg_bw = filtered["Birth_Weight_g"].mean().round(1)

    summary_cards = [
        html.Div(
            [html.H4("Total Admissions"), html.P(f"{total_admissions}")],
            style=card_style,
        ),
        html.Div([html.H4("Deaths"), html.P(f"{num_deaths}")], style=card_style),
        html.Div(
            [html.H4("Avg. Length of Stay"), html.P(f"{avg_los} days")],
            style=card_style,
        ),
        html.Div(
            [html.H4("Avg. Birth Weight"), html.P(f"{avg_bw} g")], style=card_style
        ),
    ]

    title_suffix = []
    if hospital:
        title_suffix.append(f"at {', '.join(hospital)}")
    if outcome:
        title_suffix.append(f"with outcome(s): {', '.join(outcome)}")
    if diagnosis:
        title_suffix.append(f"diagnosed as: {', '.join(diagnosis)}")
    if year:
        title_suffix.append(f"in {', '.join(year)}")
    suffix_text = " - " + ", ".join(title_suffix) if title_suffix else ""

    # Charts
    if hospital:
        fig1 = px.histogram(
            filtered,
            x="Diagnosis",
            color="Outcome",
            barmode="group",
            facet_col="Hospital",
            title=f"Outcomes by Diagnosis{suffix_text}",
        )
    else:
        fig1 = px.histogram(
            filtered,
            x="Diagnosis",
            color="Outcome",
            barmode="group",
            title=f"Outcomes by Diagnosis{suffix_text}",
        )

    if hospital:
        los_avg = (
            filtered.groupby(["Hospital", "Outcome"])["Length_of_Stay_days"]
            .mean()
            .reset_index()
        )
        fig2 = px.bar(
            los_avg,
            x="Outcome",
            y="Length_of_Stay_days",
            color="Hospital",
            barmode="group",
            title=f"Average Length of Stay by Outcome{suffix_text}",
            labels={"Length_of_Stay_days": "Avg Days"},
        )
    else:
        los_avg = (
            filtered.groupby("Outcome")["Length_of_Stay_days"].mean().reset_index()
        )
        fig2 = px.bar(
            los_avg,
            x="Outcome",
            y="Length_of_Stay_days",
            title=f"Average Length of Stay by Outcome{suffix_text}",
            labels={"Length_of_Stay_days": "Avg Days"},
        )

    admit_trend = (
        filtered.groupby(["Month", "Hospital"]).size().reset_index(name="Count")
    )
    fig3 = px.line(
        admit_trend,
        x="Month",
        y="Count",
        color="Hospital",
        markers=True,
        title=f"Monthly Admissions by Hospital{suffix_text}",
    )
    fig3.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=-45)

    if hospital:
        fig4 = px.violin(
            filtered,
            y="Birth_Weight_g",
            x="Hospital",
            color="Outcome",
            box=True,
            title=f"Birth Weight Distribution by Outcome{suffix_text}",
        )
    else:
        fig4 = px.violin(
            filtered,
            y="Birth_Weight_g",
            color="Outcome",
            box=True,
            title=f"Birth Weight Distribution by Outcome{suffix_text}",
        )

    fig5 = px.pie(
        filtered, names="Outcome", title=f"Patient Outcome Proportions{suffix_text}"
    )

    return summary_cards, fig1, fig2, fig3, fig4, fig5


if __name__ == "__main__":
    app.run(debug=True)
