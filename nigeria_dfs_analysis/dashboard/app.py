from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ModuleNotFoundError:
    px = None
    go = None
    HAS_PLOTLY = False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import BRAND_COLORS, cfg
from src.data_loader import load_cbn_payments, load_competitors, load_efina_summary
from src.financial_model import project_income_statement, project_revenue, project_users
from src.market_sizing import compute_tam_sam_som
from src.risk_model import build_risk_registry, strategic_opportunities

st.set_page_config(
    page_title="Nigeria DFS Market Analysis",
    page_icon="NG",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2rem; font-weight: 700; color: #003087; }
    .section-header { font-size: 1.25rem; font-weight: 650; color: #003087; margin-top: 1rem; }
    .assumption-note { font-size: 0.85rem; color: #C0392B; font-style: italic; }
    .source-note { font-size: 0.8rem; color: #6B7280; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    *,
    horizontal: bool = False,
) -> None:
    if HAS_PLOTLY:
        if horizontal:
            fig = px.bar(df, x=y, y=x, orientation="h", title=title)
        else:
            fig = px.bar(df, x=x, y=y, title=title)
        fig.update_layout(height=380, plot_bgcolor="#F8F9FA", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    if horizontal:
        ax.barh(df[x], df[y], color="#003087")
        ax.set_xlabel(y)
        ax.set_ylabel(x)
    else:
        ax.bar(df[x], df[y], color="#003087")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.2)
    st.pyplot(fig, use_container_width=True)


def render_line_chart(
    df: pd.DataFrame,
    x: str,
    series: list[tuple[str, str]],
    title: str,
    yaxis_title: str,
) -> None:
    if HAS_PLOTLY:
        fig = go.Figure()
        for column, label in series:
            fig.add_trace(go.Scatter(x=df[x], y=df[column], mode="lines+markers", name=label))
        fig.update_layout(height=400, hovermode="x unified", yaxis_title=yaxis_title, xaxis_title=x)
        st.plotly_chart(fig, use_container_width=True)
        return

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for column, label in series:
        ax.plot(df[x], df[column], marker="o", label=label)
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(yaxis_title)
    ax.grid(alpha=0.2)
    ax.legend()
    st.pyplot(fig, use_container_width=True)


@st.cache_data(show_spinner=False)
def load_all_data() -> dict[str, pd.DataFrame]:
    return {
        "cbn": load_cbn_payments(),
        "efina": load_efina_summary(),
        "comp": load_competitors(),
        "risks": build_risk_registry(),
        "opps": strategic_opportunities(),
    }


data = load_all_data()

st.sidebar.markdown("## Nigeria DFS Dashboard")
page = st.sidebar.radio(
    "Navigate to",
    [
        "Executive Summary",
        "Financial Inclusion",
        "E-Payment Growth",
        "Market Sizing",
        "Financial Model",
        "Risk Assessment",
        "Competitive Landscape",
    ],
)

st.sidebar.markdown(
    "**Data sources:** CBN annual reports, EFInA, World Bank WDI, company press releases"
)
st.sidebar.markdown(
    '<p class="assumption-note">Market sizing and financial model values are assumptions '
    '(see configs/config.yaml)</p>',
    unsafe_allow_html=True,
)

if page == "Executive Summary":
    st.markdown('<p class="main-title">Nigeria Digital Financial Services - Market Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        "A consulting-style market assessment of Nigeria's digital financial services sector "
        "(2015-2023), built as a portfolio project for a management consulting analyst role."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Adult Population", "106M", help="World Bank 2023")
    with c2:
        st.metric("Formally Banked", "45%", "+5pp (2020-2023)", help="EFInA 2023")
    with c3:
        st.metric("NIP Volume 2023", "8,073M txns", help="CBN Annual Report 2023")
    with c4:
        st.metric("Mobile Money Wallets", "20M", help="CBN 2023")

    st.markdown("### Key Findings")
    st.markdown(
        """
        1. Financial inclusion still leaves a large underserved market.
        2. Payment infrastructure has scaled rapidly and can support new products.
        3. The market is competitive, but not closed to a focused entrant.
        4. FX and regulation are the highest-priority risks.
        5. USSD and agent networks are central to a realistic entry strategy.
        """
    )

    st.markdown("### Market Sizing Summary")
    r = compute_tam_sam_som()
    df_size = pd.DataFrame(
        {
            "Market": ["TAM", "SAM", "SOM Year 1", "SOM Year 3"],
            "Market Size (USD M)": [
                r["TAM"].market_size_usd_m,
                r["SAM"].market_size_usd_m,
                r["SOM_Y1"].market_size_usd_m,
                r["SOM_Y3"].market_size_usd_m,
            ],
        }
    )
    render_bar_chart(df_size, "Market", "Market Size (USD M)", "Market Sizing Funnel (Assumption)")
    st.markdown('<p class="assumption-note">All market size figures are assumptions.</p>', unsafe_allow_html=True)

elif page == "Financial Inclusion":
    st.markdown('<p class="section-header">Financial Inclusion Trend (EFInA 2008-2023)</p>', unsafe_allow_html=True)
    df_e = data["efina"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Banked % Change", f"+{df_e.iloc[-1]['banked_pct'] - df_e.iloc[0]['banked_pct']:.1f}pp")
    c2.metric("Excluded % Change", f"{df_e.iloc[-1]['excluded_pct'] - df_e.iloc[0]['excluded_pct']:.1f}pp")
    c3.metric("Mobile Money 2023", f"{df_e.iloc[-1]['mobile_money_pct']}%")
    render_line_chart(
        df_e,
        "year",
        [
            ("banked_pct", "Formally Banked (%)"),
            ("excluded_pct", "Financially Excluded (%)"),
            ("mobile_money_pct", "Mobile Money (%)"),
        ],
        "Financial Inclusion Trend (EFInA 2008-2023)",
        "% of Adults (15+)",
    )

elif page == "E-Payment Growth":
    st.markdown('<p class="section-header">E-Payment Growth (CBN Annual Reports 2015-2023)</p>', unsafe_allow_html=True)
    df_c = data["cbn"]
    metric = st.selectbox(
        "Select metric",
        ["NIP Volume (M txns)", "NIP Value (NGN Billions)", "POS Volume (M txns)", "Mobile Banking (M txns)", "Mobile Money Wallets (M)"],
    )
    col_map = {
        "NIP Volume (M txns)": "nip_volume_m",
        "NIP Value (NGN Billions)": "nip_value_bn_ngn",
        "POS Volume (M txns)": "pos_volume_m",
        "Mobile Banking (M txns)": "mobile_vol_m",
        "Mobile Money Wallets (M)": "mobile_money_wallets_m",
    }
    render_bar_chart(df_c, "year", col_map[metric], f"{metric} - Nigeria")

    start_v = float(df_c.iloc[0][col_map[metric]])
    end_v = float(df_c.iloc[-1][col_map[metric]])
    cagr = (end_v / start_v) ** (1 / 8) - 1 if start_v > 0 else 0
    st.metric("CAGR 2015-2023", f"{cagr * 100:.1f}%/yr")
    st.metric("Total Growth", f"{end_v / start_v:.0f}x" if start_v > 0 else "N/A")

elif page == "Market Sizing":
    st.markdown('<p class="section-header">Market Sizing Explorer - TAM / SAM / SOM</p>', unsafe_allow_html=True)
    st.markdown('<p class="assumption-note">All values below are assumptions. Adjust sliders to explore sensitivity.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        adults_m = st.slider("Nigerian adults (M)", 90, 120, 106)
        smartphone_p = st.slider("Smartphone penetration (%)", 20, 70, 40)
        arpu = st.slider("Average annual transaction value (USD/user)", 300, 2000, 850, step=50)
    with col2:
        som_y1_pct = st.slider("SOM Year 1 capture (% of SAM)", 1, 10, 2)
        som_y3_pct = st.slider("SOM Year 3 capture (% of SAM)", 2, 20, 7)

    sam_pop = adults_m * (smartphone_p / 100)
    tam_size = adults_m * 1e6 * arpu / 1e6
    sam_size = sam_pop * 1e6 * arpu / 1e6
    som_y1 = sam_size * som_y1_pct / 100
    som_y3 = sam_size * som_y3_pct / 100

    funnel_df = pd.DataFrame(
        {
            "Market": ["TAM", "SAM", "SOM Year 1", "SOM Year 3"],
            "Market Size (USD Millions)": [tam_size, sam_size, som_y1, som_y3],
        }
    )
    if HAS_PLOTLY:
        fig = px.bar(
            funnel_df,
            x="Market Size (USD Millions)",
            y="Market",
            orientation="h",
            text=[f"${v:,.0f}M" for v in funnel_df["Market Size (USD Millions)"]],
            title="Nigeria DFS Market Sizing Funnel",
        )
        fig.update_layout(height=350, xaxis_title="Market Size (USD Millions)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.barh(funnel_df["Market"], funnel_df["Market Size (USD Millions)"], color="#003087")
        ax.set_title("Nigeria DFS Market Sizing Funnel")
        ax.set_xlabel("Market Size (USD Millions)")
        ax.grid(axis="x", alpha=0.2)
        st.pyplot(fig, use_container_width=True)

elif page == "Financial Model":
    st.markdown('<p class="section-header">3-Year Financial Model (Interactive)</p>', unsafe_allow_html=True)
    st.markdown('<p class="assumption-note">Assumption-driven forward model. Adjust parameters to test scenarios.</p>', unsafe_allow_html=True)

    from src.config import FIN_MODEL_PARAMS

    col1, col2, col3 = st.columns(3)
    with col1:
        base_users = st.number_input("Year 1 user target", 100_000, 2_000_000, FIN_MODEL_PARAMS["user_base_y1"], step=50_000)
        arpu_y1 = st.slider("ARPU Year 1 (USD)", 4.0, 30.0, float(FIN_MODEL_PARAMS["arpu_usd_y1"]), 0.5)
    with col2:
        g2 = st.slider("Y2 user growth (%)", 20, 150, int(FIN_MODEL_PARAMS["user_growth_rate_y2"] * 100))
        g3 = st.slider("Y3 user growth (%)", 20, 120, int(FIN_MODEL_PARAMS["user_growth_rate_y3"] * 100))
    with col3:
        churn = st.slider("Annual churn (%)", 5, 40, int(FIN_MODEL_PARAMS["churn_rate"] * 100))
        cogs = st.slider("COGS (% of revenue)", 20, 60, 40)

    custom_params = {
        **FIN_MODEL_PARAMS,
        "user_base_y1": int(base_users),
        "user_growth_rate_y2": g2 / 100,
        "user_growth_rate_y3": g3 / 100,
        "churn_rate": churn / 100,
        "arpu_usd_y1": arpu_y1,
        "opex": {**FIN_MODEL_PARAMS["opex"], "cost_of_revenue_pct": cogs / 100},
    }

    df_u = project_users(custom_params)
    df_r = project_revenue(df_u, custom_params)
    df_p = project_income_statement(df_r, custom_params)

    col_a, col_b = st.columns(2)
    years = df_r.index.map({0: "Y1", 1: "Y2", 2: "Y3"})
    with col_a:
        if HAS_PLOTLY:
            fig1 = px.bar(df_r, x=years, y="total_revenue_usd_m", title="Revenue (USD M)")
            fig1.update_layout(height=280, xaxis_title="Year", plot_bgcolor="#F8F9FA")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            fig1, ax1 = plt.subplots(figsize=(7, 3))
            ax1.bar(years, df_r["total_revenue_usd_m"], color="#003087")
            ax1.set_title("Revenue (USD M)")
            ax1.set_xlabel("Year")
            ax1.set_ylabel("Revenue")
            ax1.grid(axis="y", alpha=0.2)
            st.pyplot(fig1, use_container_width=True)
    with col_b:
        if HAS_PLOTLY:
            fig2 = px.bar(df_p, x=years, y="ebitda_usd_m", title="EBITDA (USD M)")
            fig2.update_layout(height=280, xaxis_title="Year", plot_bgcolor="#F8F9FA", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            fig2, ax2 = plt.subplots(figsize=(7, 3))
            ax2.bar(years, df_p["ebitda_usd_m"], color="#1D4ED8")
            ax2.set_title("EBITDA (USD M)")
            ax2.set_xlabel("Year")
            ax2.set_ylabel("EBITDA")
            ax2.grid(axis="y", alpha=0.2)
            st.pyplot(fig2, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Y3 Active Users", f"{df_u.iloc[-1]['active_users']:,.0f}")
    c2.metric("Y3 Revenue", f"${df_r.iloc[-1]['total_revenue_usd_m']:.2f}M")
    c3.metric("Y3 EBITDA", f"${df_p.iloc[-1]['ebitda_usd_m']:.2f}M")
    c4.metric("Y3 EBITDA Margin", f"{df_p.iloc[-1]['ebitda_margin_pct']:.1f}%")

elif page == "Risk Assessment":
    st.markdown('<p class="section-header">Risk Assessment Matrix</p>', unsafe_allow_html=True)
    df_risks = data["risks"]
    tier_colors = {"Low": "#27AE60", "Medium": "#F39C12", "High": "#E67E22", "Critical": "#C0392B"}
    st.dataframe(df_risks[["Category", "Risk", "Probability", "Impact", "Risk Score", "Risk Tier", "Mitigation"]], use_container_width=True, height=350)
    col1, col2 = st.columns(2)
    with col1:
        tier_counts = df_risks["Risk Tier"].value_counts()
        if HAS_PLOTLY:
            fig = px.pie(values=tier_counts.values, names=tier_counts.index, title="Risks by Tier", color=tier_counts.index, color_discrete_map=tier_colors)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.pie(tier_counts.values, labels=tier_counts.index, autopct="%1.0f%%")
            ax.set_title("Risks by Tier")
            st.pyplot(fig, use_container_width=True)
    with col2:
        df_opps = data["opps"]
        if HAS_PLOTLY:
            fig2 = px.scatter(df_opps, x="Comp. Advantage Pot.", y="Market Attractiveness", size="Priority Score", text="Opportunity", title="Strategic Opportunity Matrix")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            ax2.scatter(df_opps["Comp. Advantage Pot."], df_opps["Market Attractiveness"], s=df_opps["Priority Score"] * 25, alpha=0.7, color="#003087")
            ax2.set_title("Strategic Opportunity Matrix")
            ax2.set_xlabel("Comp. Advantage Pot.")
            ax2.set_ylabel("Market Attractiveness")
            ax2.grid(alpha=0.2)
            st.pyplot(fig2, use_container_width=True)

elif page == "Competitive Landscape":
    st.markdown('<p class="section-header">Competitive Landscape - Nigeria DFS</p>', unsafe_allow_html=True)
    st.markdown('<p class="source-note">Source: Company press releases, Crunchbase, CBN licensed institutions. Caveat: user figures are self-reported.</p>', unsafe_allow_html=True)
    df_c = data["comp"]
    if HAS_PLOTLY:
        fig = px.scatter(
            df_c.dropna(subset=["funding_usd_m"]),
            x="funding_usd_m",
            y="reported_users_m",
            size="reported_users_m",
            color="type",
            text="company",
            hover_data=["revenue_model", "agent_network_k"],
            title="Funding vs. Reported Users",
            labels={"funding_usd_m": "Funding (USD M)", "reported_users_m": "Reported Users (M)"},
            height=480,
        )
        fig.update_traces(textposition="top center", textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)
    else:
        plot_df = df_c.dropna(subset=["funding_usd_m", "reported_users_m"]).copy()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(plot_df["funding_usd_m"], plot_df["reported_users_m"], s=plot_df["reported_users_m"] * 10, alpha=0.7, color="#003087")
        ax.set_title("Funding vs. Reported Users")
        ax.set_xlabel("Funding (USD M)")
        ax.set_ylabel("Reported Users (M)")
        ax.grid(alpha=0.2)
        st.pyplot(fig, use_container_width=True)
    st.dataframe(
        df_c[["company", "type", "reported_users_m", "funding_usd_m", "agent_network_k", "revenue_model", "monthly_txn_ngn_bn"]]
        .sort_values("reported_users_m", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )
