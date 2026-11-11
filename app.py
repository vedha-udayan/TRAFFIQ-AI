import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="TRAFFIQ AI | Mauritius Mobility",
    page_icon="🚦",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "length-and-density-of-road-network.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
    data["Category"] = data["Category"].astype(str).str.strip()
    data["Subcategory"] = (
        data["Subcategory"].fillna("Overall").astype(str).str.strip()
    )

    return data.dropna(
        subset=["Year", "Value"]
    ).sort_values(["Year", "Category", "Subcategory"])


data = load_data()

years = sorted(data["Year"].astype(int).unique())

if not years:
    st.error("No valid year data was found in the CSV file.")
    st.stop()

latest_year = int(max(years))
latest = data[data["Year"] == latest_year]


def metric_value(year, category, subcategory=None):
    rows = data[
        (data["Year"] == year) &
        (data["Category"] == category)
    ]

    if subcategory is not None:
        rows = rows[rows["Subcategory"] == subcategory]

    if rows.empty:
        return None

    return float(rows.iloc[0]["Value"])


road_latest = latest[latest["Category"] == "Length of road"]
total_road = road_latest["Value"].sum()

vehicles_km = metric_value(
    latest_year, "Vehicles per KM of road"
)

density = metric_value(
    latest_year, "Density of Road Network"
)


# ---------------- PAGE HEADER ----------------

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 1.2rem 1.4rem;
    border-radius: 14px;
    background: linear-gradient(110deg, #10243a, #174b61);
    color: white;
    margin-bottom: 1rem;
}

.hero h1 {
    margin: 0;
    font-size: 2.15rem;
}

.hero p {
    margin: .35rem 0 0 0;
    opacity: .88;
}

.note {
    padding: .8rem 1rem;
    border-left: 4px solid #e5a93d;
    background: rgba(230, 170, 55, .10);
    border-radius: 6px;
}

.small {
    font-size: .85rem;
    opacity: .75;
}
</style>

<div class="hero">
    <h1>🚦 TRAFFIQ AI</h1>
    <p>
        Mauritius mobility intelligence · Evidence-led road network
        analysis and journey scenario planning
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Hackathon prototype · Track 5: Traffic and Metro Express optimisation"
)

st.markdown("""
<div class="note">
<b>Data honesty:</b> Historical road-network indicators below come
from the Mauritius Open Data Portal. They are island-wide annual
statistics, not live traffic speeds or Port Louis–Curepipe measurements.
Journey scenarios are planning calculations using values entered
by the user; they are not predictions from observed corridor traffic.
</div>
""", unsafe_allow_html=True)


# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Network overview",
    "📈 Historical trends",
    "🧭 Journey scenario lab",
    "ℹ️ Data & methodology"
])


# ---------------- TAB 1: NETWORK OVERVIEW ----------------

with tab1:

    st.subheader(
        f"Latest published year in dataset: {latest_year}"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total road length",
        f"{total_road:,.0f} km"
    )

    c2.metric(
        "Vehicles per km of road",
        f"{vehicles_km:,.0f}" if vehicles_km is not None else "N/A"
    )

    c3.metric(
        "Road network density",
        f"{density:.2f}" if density is not None else "N/A"
    )

    st.caption(
        "Total road length is calculated by summing the four published "
        "road categories for the selected year."
    )

    left, right = st.columns([1.15, 1])

    with left:

        st.markdown("*Road length by category*")

        chart = px.bar(
            road_latest,
            x="Subcategory",
            y="Value",
            color="Subcategory",
            labels={
                "Subcategory": "Road category",
                "Value": "Length (km)"
            },
            title=f"Road network composition · {latest_year}"
        )

        chart.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Kilometres"
        )

        st.plotly_chart(chart, width="stretch")

    with right:

        st.markdown("*Latest available indicators*")

        summary = latest[
            latest["Category"] != "Length of road"
        ][["Category", "Value"]].copy()

        summary["Value"] = summary["Value"].round(2)

        st.dataframe(
            summary.rename(columns={
                "Category": "Indicator",
                "Value": "Published value"
            }),
            width="stretch",
            hide_index=True
        )

    st.markdown("*Explore a year*")

    selected = st.slider(
        "Select year",
        min_value=min(years),
        max_value=max(years),
        value=latest_year,
        step=1
    )

    year_rows = data[data["Year"] == selected]

    st.dataframe(
        year_rows[
            ["Category", "Subcategory", "Value"]
        ].rename(columns={
            "Category": "Indicator",
            "Subcategory": "Road type / detail",
            "Value": "Value"
        }),
        width="stretch",
        hide_index=True
    )


# ---------------- TAB 2: HISTORICAL TRENDS ----------------

with tab2:

    st.subheader(
        "How Mauritius' road network indicators changed over time"
    )

    road = data[
        data["Category"] == "Length of road"
    ].copy()

    fig = px.area(
        road,
        x="Year",
        y="Value",
        color="Subcategory",
        labels={
            "Year": "Year",
            "Value": "Road length (km)",
            "Subcategory": "Road category"
        },
        title="Road length by category (1980–2024)"
    )

    st.plotly_chart(fig, width="stretch")

    indicators = data[
        data["Category"].isin([
            "Vehicles per KM of road",
            "Density of Road Network"
        ])
    ].copy()

    l, r = st.columns(2)

    with l:

        v = indicators[
            indicators["Category"] == "Vehicles per KM of road"
        ]

        st.plotly_chart(
            px.line(
                v,
                x="Year",
                y="Value",
                markers=True,
                title="Vehicles per kilometre of road",
                labels={
                    "Value": "Vehicles per km",
                    "Year": "Year"
                }
            ),
            width="stretch"
        )

    with r:

        v = indicators[
            indicators["Category"] == "Density of Road Network"
        ]

        st.plotly_chart(
            px.line(
                v,
                x="Year",
                y="Value",
                markers=True,
                title="Density of road network",
                labels={
                    "Value": "Published density value",
                    "Year": "Year"
                }
            ),
            width="stretch"
        )

    st.info(
        "These are descriptive national statistics. They do not identify "
        "congestion hotspots or explain the cause of changes."
    )


# ---------------- TAB 3: JOURNEY SCENARIO LAB ----------------

with tab3:

    st.subheader("Door-to-door journey scenario planner")

    st.write(
        "Enter journey times from your own observation, a published "
        "timetable, or a clearly labelled planning assumption. Compare "
        "a current journey with a proposed coordinated feeder connection."
    )

    st.markdown("*Scenario inputs (minutes)*")

    a, b = st.columns(2)

    with a:

        st.markdown("*Current / uncoordinated journey*")

        road_now = st.number_input(
            "Road or feeder travel",
            min_value=0.0,
            max_value=300.0,
            value=18.0,
            step=1.0,
            key="rn"
        )

        wait_now = st.number_input(
            "Feeder / interchange waiting",
            min_value=0.0,
            max_value=180.0,
            value=14.0,
            step=1.0,
            key="wn"
        )

        metro_now = st.number_input(
            "Metro Express travel",
            min_value=0.0,
            max_value=180.0,
            value=24.0,
            step=1.0,
            key="mn"
        )

        transfer_now = st.number_input(
            "Transfer / walking time",
            min_value=0.0,
            max_value=120.0,
            value=8.0,
            step=1.0,
            key="tn"
        )

    with b:

        st.markdown("*Proposed coordinated journey*")

        road_new = st.number_input(
            "Road or feeder travel ",
            min_value=0.0,
            max_value=300.0,
            value=18.0,
            step=1.0,
            key="rnew"
        )

        wait_new = st.number_input(
            "Feeder / interchange waiting ",
            min_value=0.0,
            max_value=180.0,
            value=5.0,
            step=1.0,
            key="wnew"
        )

        metro_new = st.number_input(
            "Metro Express travel ",
            min_value=0.0,
            max_value=180.0,
            value=24.0,
            step=1.0,
            key="mnew"
        )

        transfer_new = st.number_input(
            "Transfer / walking time ",
            min_value=0.0,
            max_value=120.0,
            value=5.0,
            step=1.0,
            key="tnew"
        )

    total_now = (
        road_now + wait_now + metro_now + transfer_now
    )

    total_new = (
        road_new + wait_new + metro_new + transfer_new
    )

    delta = total_now - total_new

    x, y, z = st.columns(3)

    x.metric(
        "Current total",
        f"{total_now:.0f} min"
    )

    y.metric(
        "Proposed total",
        f"{total_new:.0f} min"
    )

    z.metric(
        "Time difference",
        f"{delta:+.0f} min",
        delta_color="normal"
    )

    comparison = pd.DataFrame({
        "Journey": [
            "Current / uncoordinated",
            "Proposed / coordinated"
        ],
        "Total minutes": [
            total_now,
            total_new
        ]
    })

    st.plotly_chart(
        px.bar(
            comparison,
            x="Journey",
            y="Total minutes",
            text_auto=True,
            title="Door-to-door journey comparison",
            color="Journey"
        ),
        width="stretch"
    )

    if delta > 0:

        reduction = (
            delta / total_now * 100
            if total_now > 0 else 0
        )

        st.success(
            f"Under these inputs, the proposed scenario is "
            f"{delta:.0f} minutes shorter "
            f"({reduction:.1f}% reduction)."
        )

    elif delta < 0:

        st.warning(
            f"Under these inputs, the proposed scenario is "
            f"{abs(delta):.0f} minutes longer."
        )

    else:

        st.info(
            "Both scenarios have the same total journey time."
        )

    st.caption(
        "This is a transparent what-if calculator, not a machine-learning "
        "prediction. Replace the default example values with measured "
        "journey observations or verified timetable values before "
        "presenting a real-world saving."
    )

    out = pd.DataFrame([
        {
            "scenario": "Current / uncoordinated",
            "road_or_feeder_min": road_now,
            "waiting_min": wait_now,
            "metro_min": metro_now,
            "transfer_min": transfer_now,
            "total_min": total_now
        },
        {
            "scenario": "Proposed / coordinated",
            "road_or_feeder_min": road_new,
            "waiting_min": wait_new,
            "metro_min": metro_new,
            "transfer_min": transfer_new,
            "total_min": total_new
        }
    ])

    st.download_button(
        "⬇️ Download scenario results (CSV)",
        out.to_csv(index=False).encode("utf-8"),
        file_name="traffiq_journey_scenarios.csv",
        mime="text/csv"
    )


# ---------------- TAB 4: DATA & METHODOLOGY ----------------

with tab4:

    st.subheader("Data provenance")

    st.markdown("""
    *Primary dataset:* Length and density of road network for the Island of Mauritius

    *Publisher:* Mauritius Digital Promotion Agency / Mauritius Open Data Portal

    *Coverage:* 1980–2024

    *Licence:* CC-BY-SA-4.0

    *Fields used:* Year, Category, Subcategory, Value

    *What the dataset supports*
    - Historical road length by motorways, main roads, secondary roads and other roads.
    - Published vehicles-per-kilometre-of-road indicator.
    - Published road-network density indicator.

    *What it does not contain*
    - GPS road geometry or individual road segments.
    - Live traffic speed, congestion, vehicle counts by corridor or time of day.
    - Feeder-bus arrival times or a complete bus timetable.
    - Port Louis–Curepipe observed door-to-door journey times.

    *How the prototype uses it*
    - Loads the downloaded CSV directly.
    - Calculates total road length from the four road categories.
    - Visualises historical changes and the latest available indicators.
    - Provides an editable scenario calculator for a proposed feeder/Metro connection.

    *Responsible-use note:* Do not describe the scenario outputs as measured savings, AI forecasts or live traffic results. They are conditional calculations based on the input values.
    """)

    st.markdown("*Source links*")

    st.markdown(
        "- [Mauritius Open Data dataset page]"
        "(https://data.govmu.org/dataset/length-density-road-network-island-mauritius)"
    )

    st.markdown(
        "- [CSV resource page]"
        "(https://data.govmu.org/dataset/length-density-road-network-island-mauritius/resource/71f65b85-9061-4062-97d9-a0a1c3ff153d)"
    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    '<p class="small">TRAFFIQ AI · Hackathon prototype · '
    'Source data: Mauritius Open Data Portal · '
    'Scenario outputs depend on user-entered inputs.</p>',
    unsafe_allow_html=True
)