import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
import time

# Streamlit app configuration
st.set_page_config(page_title="🌌 Financial Data Sweeper", layout="wide", page_icon="🚀")
st.title("🌠 Financial Data Sweeper V4.0")

# Enhanced Light Theme Styling with a refined cosmic twist
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #a1c4fd, 0 0 10px #c3e0ff; }
            50% { box-shadow: 0 0 15px #a1c4fd, 0 0 20px #c3e0ff; }
            100% { box-shadow: 0 0 5px #a1c4fd, 0 0 10px #c3e0ff; }
        }
        @keyframes float {
            0% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        body { font-family: 'Poppins', sans-serif; }
        .stApp { 
            background: linear-gradient(135deg, #eef2ff, #dbe9ff, #f5faff); 
            color: #1e2a44; 
            animation: fadeIn 1s ease-in-out; 
        }
        .stButton>button { 
            background: linear-gradient(45deg, #a1c4fd, #c3e0ff); 
            color: #1e2a44; 
            border-radius: 12px; 
            padding: 10px 25px; 
            font-size: 16px; 
            font-weight: 600; 
            transition: all 0.3s ease; 
            animation: pulse 2s infinite; 
            border: none;
            box-shadow: 0 2px 8px rgba(161, 196, 253, 0.4);
        }
        .stButton>button:hover { 
            transform: scale(1.08); 
            background: linear-gradient(45deg, #c3e0ff, #a1c4fd); 
            box-shadow: 0 4px 12px rgba(161, 196, 253, 0.6);
        }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.95); 
            backdrop-filter: blur(12px); 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05); 
            animation: fadeIn 1s ease-in-out; 
        }
        .stHeader { 
            color: #a1c4fd; 
            font-size: 2.5rem; 
            font-weight: 700; 
            animation: float 3s infinite; 
            text-shadow: 0 2px 4px rgba(161, 196, 253, 0.3);
        }
        .stSubheader { 
            color: #3b5998; 
            font-weight: 600; 
            margin-top: 20px; 
        }
        .stDataFrame { 
            background: rgba(255, 255, 255, 0.98); 
            border-radius: 12px; 
            padding: 10px; 
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03); 
        }
        .stExpander { 
            background: rgba(255, 255, 255, 0.98); 
            border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03); 
            padding: 10px; 
        }
        .feedback-box { 
            background: rgba(195, 224, 255, 0.15); 
            border-radius: 12px; 
            padding: 15px; 
            box-shadow: 0 2px 10px rgba(161, 196, 253, 0.2); 
        }
        .stSelectbox, .stTextInput, .stTextArea { 
            background: rgba(255, 255, 255, 0.9); 
            border-radius: 8px; 
            padding: 8px; 
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.02);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.header("🌌 Data Nexus")
uploaded_file = st.sidebar.file_uploader(
    "Upload your cosmic data (CSV/Excel)", 
    type=["csv", "xlsx"], 
    help="Supports CSV and Excel data streams"
)

if uploaded_file:
    st.sidebar.success("🌠 Data stream online!")
else:
    st.sidebar.info("🌀 Awaiting cosmic data...")

# Cached data loading
@st.cache_data
def load_data(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# Data cleaning function
def clean_data(df, method="drop"):
    if method == "drop":
        return df.dropna().drop_duplicates()
    elif method == "mean":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        return df.drop_duplicates()
    elif method == "median":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        return df.drop_duplicates()
    elif method == "zero":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df.drop_duplicates()

# Outlier detection
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    return outliers

# Data export
def convert_df(df, format="csv"):
    if format == "csv":
        output = BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    elif format == "excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output.read()

if uploaded_file:
    try:
        # Loading animation
        progress_bar = st.progress(0)
        with st.spinner("🌌 Engaging hyperdrive..."):
            df = load_data(uploaded_file)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            progress_bar.empty()
        
        st.success("✨ Data hyperspace jump complete!")
        
        # Raw data display
        st.subheader("📜 Cosmic Raw Data")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(245, 250, 255, 0.7);"), use_container_width=True, height=400)
        
        # Data cleaning
        cleaning_method = st.selectbox("🧠 Data Flux Purification", ["Purge Anomalies", "Mean Convergence", "Median Stabilization", "Zero Flux"])
        cleaning_method_map = {
            "Purge Anomalies": "drop",
            "Mean Convergence": "mean",
            "Median Stabilization": "median",
            "Zero Flux": "zero"
        }
        df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method])
        
        st.subheader("✨ Stabilized Data Core")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(245, 250, 255, 0.7);"), use_container_width=True, height=400)
        
        # Summary stats
        with st.expander("📊 Quantum Data Insights", expanded=False):
            st.write("Analyzing data dimensions:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="Blues"))
        
        # Correlation heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("🔥 Interstellar Correlation Map")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Map", template="plotly_white", color_continuous_scale="Blues")
            fig.update_layout(hovermode="x unified", font=dict(color="#1e2a44"))
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualizations
        if not numeric_columns.empty:
            st.subheader("🌌 Galactic Visualizations")
            selected_column = st.selectbox("Select data singularity", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    df_cleaned, x=selected_column, nbins=50, title=f"📊 {selected_column} Nebula Histogram", 
                    template="plotly_white", color_discrete_sequence=["#a1c4fd"]
                )
                fig.update_layout(bargap=0.1, hovermode="x unified", font=dict(color="#1e2a44"))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_cleaned, y=selected_column, title=f"📦 {selected_column} Quantum Flux", 
                    template="plotly_white", color_discrete_sequence=["#c3e0ff"]
                )
                fig.update_layout(font=dict(color="#1e2a44"))
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    df_cleaned, y=selected_column, title=f"📈 {selected_column} Temporal Rift", 
                    template="plotly_white", markers=True, color_discrete_sequence=["#ffcc99"]
                )
                fig.update_layout(font=dict(color="#1e2a44"))
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if st.checkbox("Engage Scatter Warp"):
                x_col = st.selectbox("X-axis singularity", numeric_columns)
                y_col = st.selectbox("Y-axis singularity", numeric_columns, index=1)
                fig = px.scatter(
                    df_cleaned, x=x_col, y=y_col, title=f"Warp Field: {x_col} vs {y_col}", 
                    template="plotly_white", color_discrete_sequence=["#c3e0ff"], 
                    animation_frame=None if 'Date' not in df_cleaned.columns else 'Date'
                )
                fig.update_layout(font=dict(color="#1e2a44"))
                st.plotly_chart(fig, use_container_width=True)
            
            # Outlier detection
            if st.checkbox("Probe for Cosmic Anomalies"):
                outliers = detect_outliers(df_cleaned, selected_column)
                st.write(f"Anomalies in {selected_column}:")
                if not outliers.empty:
                    st.write(outliers)
                else:
                    st.write("No anomalies detected in this singularity.")
            
            # Quartile visualization
            st.subheader("📊 Stellar Quartile Array")
            q1, q2, q3 = df_cleaned[selected_column].quantile([0.25, 0.5, 0.75])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Q1", "Q2 (Core)", "Q3"], y=[q1, q2, q3], 
                marker_color=["#a1c4fd", "#ffcc99", "#c3e0ff"], 
                text=[f"{q1:.2f}", f"{q2:.2f}", f"{q3:.2f}"], textposition="auto"
            ))
            fig.update_layout(title=f"Quartile Array for {selected_column}", template="plotly_white", font=dict(color="#1e2a44"))
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Integration
        with st.expander("🤖 AI Core", expanded=False):
            question = st.text_input("Query the neural core (e.g., 'What’s the trend in this singularity?')")
            if question:
                with st.spinner("🤖 Neural net engaging..."):
                    time.sleep(1)
                trend = "rising" if df_cleaned[selected_column].iloc[-1] > df_cleaned[selected_column].iloc[0] else "falling" if df_cleaned[selected_column].iloc[-1] < df_cleaned[selected_column].iloc[0] else "stable"
                st.write(f"🧠 Response (Feb 24, 2025): Analyzing '{question}'. For {selected_column}, the temporal rift suggests a {trend} trend based on recent data shifts.")
        
        # Download section
        export_format = st.selectbox("📤 Data Extraction Protocol", ["CSV", "Excel"])
        export_data = convert_df(df_cleaned, format=export_format.lower())
        st.download_button(
            label=f"📥 Extract Data ({export_format})",
            data=export_data,
            file_name=f"stabilized_data_{export_format.lower()}.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Extract stabilized data for intergalactic analysis."
        )

        # Feedback Section
        st.subheader("🌠 Feedback Cosmos")
        st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
        with st.form(key="feedback_form"):
            st.write("Rate this cosmic experience:")
            feedback_rating = st.slider("Stellar Rating (1-5)", 1, 5, 3, format="%d ⭐")
            feedback_text = st.text_area("Transmit your cosmic thoughts", height=120, placeholder="Tell us how we can enhance this galaxy!")
            submit_feedback = st.form_submit_button(label="Send Across the Universe")
            if submit_feedback:
                st.success(f"🌌 Feedback beamed! Rating: {feedback_rating}/5 ⭐\nMessage: {feedback_text}")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Hyperdrive malfunction: {e}")
else:
    st.sidebar.warning("⚠ Engage data upload to activate the cosmos.")

# Footer
st.markdown(
    """
    <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.95); border-radius: 12px; margin-top: 25px; box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);">
        <h3 style="color: #a1c4fd; animation: float 3s infinite; font-size: 1.8rem; font-weight: 600;">Developed by Sarfraz</h3>
        <p style="color: #1e2a44; font-size: 1rem;">Navigating the financial multiverse</p>
        <div style="margin-top: 8px;">
            <span style="font-size: 1.2rem; animation: rotate 12s linear infinite;">🪐</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)