import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
import time

# Streamlit app configuration
st.set_page_config(page_title="🌌 Financial Data Sweeper", layout="wide", page_icon="🚀")
st.title("🌠 Financial Data Sweeper V3.0")

# Enhanced Light Theme Styling with a cosmic twist
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #ff80bf, 0 0 10px #80dfff; }
            50% { box-shadow: 0 0 15px #ff80bf, 0 0 20px #80dfff; }
            100% { box-shadow: 0 0 5px #ff80bf, 0 0 10px #80dfff; }
        }
        @keyframes float {
            0% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        body { font-family: 'Orbitron', sans-serif; }
        .stApp { 
            background: linear-gradient(135deg, #f0f4ff, #d9e8ff, #e6f0ff); 
            color: #2a2a5e; 
            animation: fadeIn 1.2s ease-in-out; 
        }
        .stButton>button { 
            background: linear-gradient(45deg, #ff80bf, #80dfff); 
            color: #ffffff; 
            border-radius: 15px; 
            padding: 12px 30px; 
            font-size: 16px; 
            transition: all 0.4s ease; 
            animation: glow 2s infinite, pulse 1.5s infinite; 
            border: none;
        }
        .stButton>button:hover { 
            transform: scale(1.15) rotate(3deg); 
            background: linear-gradient(45deg, #80dfff, #ff80bf); 
        }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.8); 
            backdrop-filter: blur(15px); 
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            animation: fadeIn 1.2s ease-in-out; 
        }
        .stHeader { color: #ff4d94; font-size: 3rem; font-weight: 700; animation: float 3s infinite; }
        .stDataFrame { 
            background: rgba(255, 255, 255, 0.9); 
            border-radius: 15px; 
            padding: 15px; 
            box-shadow: 0 3px 12px rgba(0,0,0,0.1); 
        }
        .stExpander { 
            background: rgba(255, 255, 255, 0.9); 
            border-radius: 15px; 
            box-shadow: 0 3px 12px rgba(0,0,0,0.1); 
        }
        .feedback-box { 
            background: rgba(128, 223, 255, 0.2); 
            border-radius: 15px; 
            padding: 20px; 
            box-shadow: 0 0 12px rgba(128, 223, 255, 0.5); 
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
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(240, 244, 255, 0.5);"), use_container_width=True, height=400)
        
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
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(240, 244, 255, 0.5);"), use_container_width=True, height=400)
        
        # Summary stats
        with st.expander("📊 Quantum Data Insights"):
            st.write("Analyzing data dimensions:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="Blues"))
        
        # Correlation heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("🔥 Interstellar Correlation Map")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Map", template="plotly_white", color_continuous_scale="Blues")
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualizations
        if not numeric_columns.empty:
            st.subheader("🌌 Galactic Visualizations")
            selected_column = st.selectbox("Select data singularity", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    df_cleaned, x=selected_column, nbins=50, title=f"📊 {selected_column} Nebula Histogram", 
                    template="plotly_white", color_discrete_sequence=["#ff80bf"]
                )
                fig.update_layout(bargap=0.1, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_cleaned, y=selected_column, title=f"📦 {selected_column} Quantum Flux", 
                    template="plotly_white", color_discrete_sequence=["#80dfff"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    df_cleaned, y=selected_column, title=f"📈 {selected_column} Temporal Rift", 
                    template="plotly_white", markers=True, color_discrete_sequence=["#ffcc00"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if st.checkbox("Engage Scatter Warp"):
                x_col = st.selectbox("X-axis singularity", numeric_columns)
                y_col = st.selectbox("Y-axis singularity", numeric_columns, index=1)
                fig = px.scatter(
                    df_cleaned, x=x_col, y=y_col, title=f"Warp Field: {x_col} vs {y_col}", 
                    template="plotly_white", color_discrete_sequence=["#80dfff"], 
                    animation_frame=None if 'Date' not in df_cleaned.columns else 'Date'
                )
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
                marker_color=["#ff80bf", "#ffcc00", "#80dfff"], 
                text=[f"{q1:.2f}", f"{q2:.2f}", f"{q3:.2f}"], textposition="auto"
            ))
            fig.update_layout(title=f"Quartile Array for {selected_column}", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Integration
        with st.expander("🤖 AI Core"):
            question = st.text_input("Query the neural core (e.g., 'What’s the trend in this singularity?')")
            if question:
                with st.spinner("🤖 Neural net engaging..."):
                    time.sleep(1)
                st.write(f"🧠 Response (Feb 24, 2025): Analyzing '{question}'. For {selected_column}, the temporal rift suggests a [rising/falling/stable] trend based on recent data shifts.")
        
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
    <div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.9); border-radius: 15px; margin-top: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <h3 style="color: #ff80bf; animation: float 3s infinite; font-size: 2rem;">Developed by Sarfraz</h3>
        <p style="color: #2a2a5e; font-size: 1.2rem;">Navigating the financial multiverse</p>
        <div style="margin-top: 10px;">
            <span style="font-size: 1.5rem; animation: rotate 10s linear infinite;">🪐</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)