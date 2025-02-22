import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import time

# App Configuration
st.set_page_config(page_title="🔥 Financial Data Sweeper Elite", layout="wide", page_icon="💰", initial_sidebar_state="expanded")

# Bold Styling
st.markdown(
    """
    <style>
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
        body { font-family: 'Montserrat', sans-serif; }
        .stApp { 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: #fff; 
        }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.15); 
            backdrop-filter: blur(12px); 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); 
            animation: fadeIn 0.8s ease; 
        }
        .stButton>button { 
            background: linear-gradient(45deg, #ff6b6b, #feca57); 
            color: #fff; 
            border: none; 
            border-radius: 10px; 
            padding: 12px 25px; 
            font-weight: bold; 
            transition: all 0.3s ease; 
            animation: pulse 2s infinite; 
        }
        .stButton>button:hover { 
            background: linear-gradient(45deg, #feca57, #ff6b6b); 
            transform: translateY(-3px); 
            box-shadow: 0 6px 15px rgba(255, 107, 107, 0.5); 
        }
        .panel { 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 15px; 
            padding: 20px; 
            margin: 15px 0; 
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); 
            animation: fadeIn 0.5s ease; 
        }
        h1, h2, h3 { color: #feca57; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar: Controls
st.sidebar.title("🔥 Sweeper Controls")
uploaded_file = st.sidebar.file_uploader("Upload Financial Data", type=["csv", "xlsx"], help="CSV or Excel files")
view_mode = st.sidebar.selectbox("View Mode", ["Snapshot", "Forecast", "Clusters"])
show_preview = st.sidebar.checkbox("Preview Data", value=True)

# Cached Functions
@st.cache_data
def load_data(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

@st.cache_data
def clean_data(df, method="median", remove_outliers=False):
    numeric_cols = df.select_dtypes(include=['number']).columns
    if method == "median":
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif method == "mean":
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    elif method == "drop":
        df = df.dropna()
    if remove_outliers:
        for col in numeric_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df = df[~((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR)))]
    return df.drop_duplicates()

def convert_df(df, format="csv"):
    if format == "csv":
        return df.to_csv(index=False).encode()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Main App
st.title("🔥 Financial Data Sweeper Elite")
st.markdown("<p style='color: #dfe6e9;'>Ignite your financial insights with blazing speed and style.</p>", unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("🔄 Sweeping data..."):
        df = load_data(uploaded_file)
        time.sleep(0.5)
    
    # Data Cleaning
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("🛠️ Data Forge")
    cleaning_method = st.selectbox("Cleaning Protocol", ["Median Fill", "Mean Fill", "Drop Missing"], key="clean")
    remove_outliers = st.checkbox("Eliminate Outliers", key="outliers")
    df_cleaned = clean_data(df, method=cleaning_method.split()[0].lower(), remove_outliers=remove_outliers)
    st.success(f"Data forged: {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns")
    if show_preview:
        st.write("Data Snapshot:")
        st.dataframe(df_cleaned.head(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
    date_cols = df_cleaned.select_dtypes(include=['datetime']).columns

    # View Modes
    if view_mode == "Snapshot":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("📊 Data Snapshot")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Core Metrics:")
            metrics = df_cleaned[numeric_cols].agg(["mean", "median", "std"]).T
            st.dataframe(metrics.style.format("{:.2f}"), height=200)
        with col2:
            if len(numeric_cols) > 1:
                fig_corr = px.imshow(df_cleaned[numeric_cols].corr(), text_auto=".2f", title="Correlation Heatmap", 
                                     color_continuous_scale="Viridis", height=400)
                st.plotly_chart(fig_corr, use_container_width=True)
        if len(numeric_cols) > 0:
            hist_col = st.selectbox("Histogram Column", numeric_cols, key="hist")
            fig_hist = px.histogram(df_cleaned, x=hist_col, nbins=40, title=f"{hist_col} Distribution", 
                                    color_discrete_sequence=["#ff6b6b"])
            st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    elif view_mode == "Forecast":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("⏳ Forecasting Engine")
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            time_col = st.selectbox("Time Axis", date_cols, key="time")
            value_col = st.selectbox("Value to Forecast", numeric_cols, key="value")
            periods = st.slider("Forecast Periods", 5, 30, 10)
            model = ExponentialSmoothing(df_cleaned[value_col], trend="add", seasonal=None).fit()
            forecast = model.forecast(periods)
            forecast_df = pd.DataFrame({
                time_col: pd.date_range(start=df_cleaned[time_col].max(), periods=periods + 1, freq="D")[1:],
                value_col: forecast
            })
            full_df = pd.concat([df_cleaned[[time_col, value_col]], forecast_df])
            fig_forecast = px.line(full_df, x=time_col, y=value_col, title=f"{value_col} Forecast", 
                                   color_discrete_sequence=["#feca57"])
            fig_forecast.add_scatter(x=forecast_df[time_col], y=forecast_df[value_col], mode="lines", 
                                     name="Forecast", line=dict(dash="dash", color="#ff6b6b"))
            st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.warning("Need a datetime and numeric column for forecasting!")
        st.markdown("</div>", unsafe_allow_html=True)

    elif view_mode == "Clusters":
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("🌐 Cluster Analysis")
        if len(numeric_cols) >= 2:
            n_clusters = st.slider("Number of Clusters", 2, 10, 3)
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df_cleaned[numeric_cols])
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_data)
            df_cleaned["Cluster"] = clusters
            x_col = st.selectbox("X Axis", numeric_cols, key="x_cluster")
            y_col = st.selectbox("Y Axis", numeric_cols, index=1, key="y_cluster")
            fig_cluster = px.scatter(df_cleaned, x=x_col, y=y_col, color="Cluster", title="Cluster Map", 
                                     color_continuous_scale="Rainbow")
            st.plotly_chart(fig_cluster, use_container_width=True)
            st.write("Cluster Centers:")
            st.dataframe(pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=numeric_cols))
        else:
            st.warning("Need at least 2 numeric columns for clustering!")
        st.markdown("</div>", unsafe_allow_html=True)

    # Dynamic Dashboard
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("🎛️ Dynamic Dashboard")
    dash_cols = st.multiselect("Select Dashboard Metrics", numeric_cols, default=list(numeric_cols)[:3])
    if dash_cols:
        fig_dash = go.Figure()
        colors = ["#ff6b6b", "#feca57", "#48dbfb"]
        for i, col in enumerate(dash_cols):
            fig_dash.add_trace(go.Scatter(x=df_cleaned.index, y=df_cleaned[col], name=col, 
                                          mode="lines+markers", line=dict(color=colors[i % len(colors)])))
        fig_dash.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig_dash, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Export
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("📥 Export Suite")
    export_format = st.selectbox("Export Format", ["CSV", "Excel"], key="export")
    export_data = convert_df(df_cleaned, export_format.lower())
    st.download_button(f"Download {export_format}", export_data, f"sweeper_elite.{export_format.lower()}",
                       mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<div style='text-align: center; color: #dfe6e9;'>Drop your data to ignite the sweep!</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div style='text-align: center; padding: 20px; color: #dfe6e9;'>
        <p>Built by Sarfraz | Powered by xAI | Unleash the Elite</p>
    </div>
    """,
    unsafe_allow_html=True,
)