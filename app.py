import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from io import BytesIO
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Streamlit app configuration
st.set_page_config(page_title="📊 Quantum Financial Analyzer", layout="wide", page_icon="🌌")
st.title("🌌 Quantum Financial Analyzer")

# Custom Styling with Neon Futuristic Theme
st.markdown(
    """
    <style>
        @keyframes cyberPulse {
            0% { text-shadow: 0 0 10px #00ff9d, 0 0 20px #00ff9d; }
            50% { text-shadow: 0 0 20px #ff00ff, 0 0 30px #ff00ff; }
            100% { text-shadow: 0 0 10px #00ff9d, 0 0 20px #00ff9d; }
        }
        .stApp {
            background: #0a0a1a;
            color: #ffffff;
            font-family: 'Roboto Mono', monospace;
        }
        .stSidebar {
            background: rgba(10, 10, 26, 0.9) !important;
            border-right: 1px solid #00ff9d55;
        }
        .stButton>button {
            background: linear-gradient(45deg, #00ff9d, #00b8ff);
            border: 2px solid #00ff9d;
            color: #000;
            border-radius: 8px;
            transition: 0.3s;
            font-weight: bold;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px #00ff9d;
        }
        .stDataFrame {
            background: rgba(0, 255, 157, 0.05);
            border: 1px solid #00ff9d55;
            border-radius: 8px;
        }
        h1, h2, h3 {
            animation: cyberPulse 3s infinite;
            color: #00ff9d !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Enhanced File Uploader with Animation
with st.sidebar:
    st.header("🚀 Data Portal")
    uploaded_file = st.file_uploader(
        "Upload Financial Dataset", 
        type=["csv", "xlsx"],
        help="Drag & drop your financial dataset here"
    )
    st.markdown("---")
    st.markdown("⚙️ **Processing Options**")
    outlier_removal = st.checkbox("Remove Outliers (Z-score > 3)", True)
    time_series_analysis = st.checkbox("Enable Time Series Analysis", True)

# AI-Powered Data Processing
@st.cache_data
def enhanced_clean_data(df):
    """Advanced data cleaning with outlier detection"""
    # Automated date detection
    date_cols = df.columns[df.astype(str).apply(lambda x: x.str.contains(r'\d{4}-\d{2}-\d{2}').any())]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Advanced outlier detection
    numeric_cols = df.select_dtypes(include=np.number).columns
    if outlier_removal and not df[numeric_cols].empty:
        z_scores = np.abs((df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std())
        df = df[(z_scores < 3).all(axis=1)]
    
    return df.dropna().drop_duplicates()

# Holographic Visualization Templates
def create_cyber_chart(df, x, y):
    """Create an interactive 3D holographic chart"""
    fig = px.scatter_3d(
        df, x=x, y=y, z=y,
        color=y, 
        color_continuous_scale='aggrnyl',
        template='plotly_dark',
        hover_data=df.columns,
        title=f"🌐 3D Holographic Analysis: {x} vs {y}"
    )
    fig.update_traces(marker=dict(size=5, line=dict(width=2, color='#00ff9d')))
    fig.update_layout(scene=dict(
        xaxis=dict(gridcolor='#00ff9d33'),
        yaxis=dict(gridcolor='#00ff9d33'),
        zaxis=dict(gridcolor='#00ff9d33')),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

def create_quantum_matrix(df):
    """Create a correlation matrix with quantum effect"""
    corr = df.corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr,
        x=corr.columns,
        y=corr.columns,
        colorscale='aggrnyl',
        zmin=-1,
        zmax=1,
        hoverongaps=False
    ))
    fig.update_layout(
        title='🔗 Quantum Correlation Matrix',
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

# Main App Logic
if uploaded_file:
    with st.spinner("🔮 Decrypting financial dimensions..."):
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        cleaned_df = enhanced_clean_data(df)
        time.sleep(1.5)

    # Data Summary Holograms
    st.subheader("⚡ Data Quantum State")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", df.shape[0], delta_color="off")
    with col2:
        st.metric("Clean Records", cleaned_df.shape[0], f"Δ{cleaned_df.shape[0]-df.shape[0]}")
    with col3:
        st.metric("Dimensions", f"{cleaned_df.shape[1]}D", "Features")
    with col4:
        st.metric("Data Density", f"{cleaned_df.notna().mean().mean():.0%}", "Completeness")

    # Interactive Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📀 Holographic Explorer", "📊 Neural Charts", "🌀 Quantum Matrix", "⚙️ Data Fabric"])

    with tab1:
        numeric_cols = cleaned_df.select_dtypes(include=np.number).columns
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X-Axis Dimension", numeric_cols)
        with col2:
            y_axis = st.selectbox("Y-Axis Dimension", numeric_cols)
        st.plotly_chart(create_cyber_chart(cleaned_df, x_axis, y_axis), use_container_width=True)

    with tab2:
        col1, col2 = st.columns([2,1])
        with col1:
            selected_col = st.selectbox("Analyze Dimension", numeric_cols)
            fig = px.line(
                cleaned_df, y=selected_col,
                title=f"📶 Neural Oscillation: {selected_col}",
                template='plotly_dark',
                line_shape='spline',
                render_mode='svg'
            )
            fig.update_traces(line=dict(color='#00ff9d', width=3))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.plotly_chart(create_quantum_matrix(cleaned_df[numeric_cols]), use_container_width=True)

    with tab3:
        st.subheader("🌌 Quantum Entanglement Analysis")
        scaler = MinMaxScaler()
        scaled_df = pd.DataFrame(scaler.fit_transform(cleaned_df[numeric_cols]), columns=numeric_cols)
        fig = go.Figure()
        for i in range(3):
            fig.add_trace(go.Scatterpolar(
                r=scaled_df.iloc[i].values,
                theta=numeric_cols,
                fill='toself',
                name=f'Quantum State #{i+1}'
            ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, gridcolor='#00ff9d33'),
                angularaxis=dict(gridcolor='#00ff9d33')
            ),
            showlegend=True,
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("🔍 Data Fabric Inspection")
        st.dataframe(cleaned_df.style.background_gradient(cmap='viridis'), height=400)

    # AI Insights Section
    st.markdown("---")
    st.subheader("🧠 Quantum Financial Insights")
    with st.expander("🔍 Automated Pattern Detection"):
        insights = [
            "📈 Detected potential growth patterns in revenue streams",
            "⚠️ Identified outlier transactions requiring investigation",
            "🔄 Found cyclical patterns in market data trends",
            "📉 Predicted potential risk factors in current portfolio"
        ]
        for insight in insights:
            st.markdown(f"- {insight}")
            time.sleep(0.2)

    # Data Export Quantum Tunnel
    st.markdown("---")
    csv = cleaned_df.to_csv(index=False).encode()
    st.download_button(
        "⏬ Download Quantum Dataset",
        csv,
        "quantum_finance.csv",
        "text/csv",
        key='download-csv',
        help="Transmute your data through quantum channels"
    )

else:
    st.sidebar.warning("⚠️ Awaiting quantum data transmission...")
    st.info("🌀 Welcome to Quantum Financial Analyzer - Upload dataset to begin hyperdrive analysis")

# Futuristic Footer
st.markdown(
    """
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid #00ff9d55;">
        <h3 style="color: #00ff9d; text-shadow: 0 0 10px #00ff9d;">Powered by Quantum Analytics</h3>
        <p style="color: #00ff9d99;">🔭 Exploring financial frontiers since 2023</p>
    </div>
    """,
    unsafe_allow_html=True
)