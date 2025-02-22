import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from io import BytesIO
from sklearn.ensemble import IsolationForest
from streamlit_lottie import st_lottie
import requests
import base64
import random

# App Configuration
st.set_page_config(page_title="🌌 Financial Data Sweeper 2050", layout="wide", page_icon="⚡️", initial_sidebar_state="collapsed")

# Cyberpunk Styling with Animations
st.markdown(
    """
    <style>
        @keyframes neonPulse { 0% { text-shadow: 0 0 5px #00ffcc, 0 0 10px #ff00cc; } 50% { text-shadow: 0 0 20px #00ffcc, 0 0 30px #ff00cc; } 100% { text-shadow: 0 0 5px #00ffcc, 0 0 10px #ff00cc; } }
        @keyframes float { 0% { transform: translateY(0); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0); } }
        @keyframes bgShift { 0% { background-position: 0% 0%; } 100% { background-position: 100% 100%; } }
        body { font-family: 'Orbitron', sans-serif; }
        .stApp { 
            background: linear-gradient(45deg, #1a0d2e, #0f2b63, #1a0d2e); 
            background-size: 200% 200%; 
            animation: bgShift 15s infinite; 
            color: #fff; 
        }
        .stButton>button { 
            background: linear-gradient(45deg, #ff00cc, #00ffcc); 
            color: #000; 
            border: none; 
            border-radius: 15px; 
            padding: 15px 30px; 
            font-size: 18px; 
            animation: neonPulse 1.5s infinite; 
            transition: transform 0.3s ease; 
        }
        .stButton>button:hover { transform: scale(1.15); }
        .stSidebar { 
            background: rgba(0, 0, 0, 0.7); 
            backdrop-filter: blur(15px); 
            border: 2px solid #00ffcc; 
            border-radius: 20px; 
            padding: 25px; 
        }
        h1, h2, h3 { animation: neonPulse 2s infinite; }
        .data-container { 
            background: rgba(0, 255, 204, 0.1); 
            border: 1px solid #ff00cc; 
            border-radius: 10px; 
            padding: 20px; 
            margin: 10px 0; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Lottie Animation Loader (Cyberpunk City)
def load_lottie_url(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

lottie_city = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_tows2oda.json")  # Cyberpunk city animation

# Initialize Session State
if "score" not in st.session_state:
    st.session_state.score = 0
if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"

# Sidebar: Mission Control
with st.sidebar:
    st.title("⚡️ Mission Control")
    uploaded_file = st.file_uploader("Upload Data Core (CSV/Excel)", type=["csv", "xlsx"], key="uploader")
    st.session_state.theme = st.selectbox("Select Holo-Theme", ["Cyberpunk", "Neon Dark", "Quantum Glow"])
    theme_styles = {
        "Cyberpunk": "background: linear-gradient(45deg, #1a0d2e, #0f2b63, #1a0d2e); color: #fff;",
        "Neon Dark": "background: linear-gradient(45deg, #0f0c29, #302b63); color: #00ffcc;",
        "Quantum Glow": "background: linear-gradient(45deg, #000428, #004e92); color: #ffd700;"
    }
    st.markdown(f"<style>.stApp {{{theme_styles[st.session_state.theme]}}}</style>", unsafe_allow_html=True)
    st.write(f"🛡️ Agent Score: {st.session_state.score}")

# Cached Functions
@st.cache_data
def load_data(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

@st.cache_data
def clean_data(df, method="drop", remove_outliers=False):
    methods = {"drop": df.dropna, "mean": lambda x: x.fillna(x.mean()), "median": lambda x: x.fillna(x.median())}
    numeric_cols = df.select_dtypes(include=['number']).columns
    df_clean = methods.get(method, df.dropna)()
    if method in ["mean", "median"]:
        df_clean[numeric_cols] = methods[method](df[numeric_cols])
    if remove_outliers:
        for col in numeric_cols:
            Q1, Q3 = df_clean[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df_clean = df_clean[~((df_clean[col] < (Q1 - 1.5 * IQR)) | (df_clean[col] > (Q3 + 1.5 * IQR)))]
    return df_clean.drop_duplicates()

def convert_df(df, format="csv"):
    if format == "csv":
        return df.to_csv(index=False).encode()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Main App
st.title("🌌 Financial Data Sweeper 2050")
st_lottie(lottie_city, height=200, key="city")

if uploaded_file:
    with st.spinner("⚡️ Initializing Data Core..."):
        df = load_data(uploaded_file)
        st.session_state.score += 10  # Reward for uploading
    
    st.success("⚡️ Data Core Activated!")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", start_time=0)  # Sci-fi sound

    # Cleaning & Transformation
    st.markdown("<div class='data-container'>", unsafe_allow_html=True)
    st.subheader("🧠 Data Core Processor")
    cleaning_method = st.selectbox("Select Purification Protocol", ["Drop", "Mean", "Median"])
    remove_outliers = st.checkbox("Enable Anomaly Shield")
    df_cleaned = clean_data(df, method=cleaning_method.lower(), remove_outliers=remove_outliers)
    
    transform = st.selectbox("Quantum Transformation", ["None", "Log", "Normalize"])
    if transform != "None":
        numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
        if transform == "Log":
            df_cleaned[numeric_cols] = np.log1p(df_cleaned[numeric_cols])
        elif transform == "Normalize":
            df_cleaned[numeric_cols] = (df_cleaned[numeric_cols] - df_cleaned[numeric_cols].min()) / (df_cleaned[numeric_cols].max() - df_cleaned[numeric_cols].min())
        st.session_state.score += 5  # Reward for transformation
    st.dataframe(df_cleaned.head(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # AI Anomaly Detection
    st.markdown("<div class='data-container'>", unsafe_allow_html=True)
    st.subheader("🤖 AI Sentinel")
    if st.button("Scan for Anomalies"):
        numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomalies = iso_forest.fit_predict(df_cleaned[numeric_cols])
            df_cleaned["Anomaly"] = anomalies == -1
            st.write(f"Detected {df_cleaned['Anomaly'].sum()} anomalies!")
            fig = px.scatter(df_cleaned, x=numeric_cols[0], y=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0], 
                             color="Anomaly", title="Anomaly Scan", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.score += 20  # Big reward for AI use
    st.markdown("</div>", unsafe_allow_html=True)

    # Immersive Visualizations
    st.markdown("<div class='data-container'>", unsafe_allow_html=True)
    st.subheader("🌐 Holo-Visor")
    numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
    if len(numeric_columns) >= 3:
        x_3d, y_3d, z_3d = st.selectbox("X Axis", numeric_columns), st.selectbox("Y Axis", numeric_columns, index=1), st.selectbox("Z Axis", numeric_columns, index=2)
        fig_3d = px.scatter_3d(df_cleaned, x=x_3d, y=y_3d, z=z_3d, color=z_3d, title="Quantum Data Globe", 
                               template="plotly_dark", size_max=10, opacity=0.7)
        fig_3d.update_layout(scene=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_3d, use_container_width=True)
        st.session_state.score += 15

    # Real-Time Simulation
    if st.button("Activate Real-Time Feed"):
        st.subheader("📡 Data Stream Simulation")
        placeholder = st.empty()
        for _ in range(10):
            simulated_data = df_cleaned[numeric_columns].apply(lambda x: x * (1 + random.uniform(-0.05, 0.05)))
            fig_stream = px.line(simulated_data, title="Live Financial Stream", template="plotly_dark")
            placeholder.plotly_chart(fig_stream, use_container_width=True)
            time.sleep(0.5)
        st.session_state.score += 25

    # Augmented Insights
    st.subheader("🔍 Augmented Insights")
    if len(numeric_columns) > 1:
        fig_rad = go.Figure(data=go.Scatterpolar(r=df_cleaned[numeric_columns].mean(), theta=numeric_columns, fill='toself'))
        fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, template="plotly_dark")
        st.plotly_chart(fig_rad, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Export
    st.subheader("💾 Data Vault")
    export_format = st.selectbox("Export Protocol", ["CSV", "Excel"])
    export_data = convert_df(df_cleaned, export_format.lower())
    st.download_button(f"Download {export_format}", export_data, f"data_sweep.{export_format.lower()}",
                       mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.markdown("<h2 style='text-align: center;'>⚡️ Awaiting Data Core Insertion...</h2>", unsafe_allow_html=True)
    st_lottie(load_lottie_url("https://assets8.lottiefiles.com/packages/lf20_yppqjrfw.json"), height=300)  # Loading animation

# Leaderboard & Footer
st.markdown("<div class='data-container'>", unsafe_allow_html=True)
st.subheader("🏆 Agent Leaderboard")
leaderboard = {"Agent X": 150, "CyberGhost": 120, f"You": st.session_state.score}
st.write(pd.DataFrame(leaderboard.items(), columns=["Agent", "Score"]).sort_values("Score", ascending=False))
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align: center; padding: 20px; background: rgba(0, 255, 204, 0.1); border: 2px solid #ff00cc; border-radius: 15px;'>
        <h3 style='animation: float 3s infinite;'>Crafted by Sarfraz in 2050</h3>
        <p>Sweep the Future of Finance!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Holo-Feedback
with st.expander("📡 Transmit Feedback"):
    feedback = st.text_area("Send Signal to HQ")
    if st.button("Transmit"):
        st.success("Signal Received!")
        st.session_state.score += 5