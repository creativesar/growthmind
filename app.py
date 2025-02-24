import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
import time

# Streamlit app configuration
st.set_page_config(page_title="✨ Cosmic Financial Portal", layout="wide", page_icon="🌠")
st.title("🌌 Cosmic Financial Portal V4.0")

# Out-of-this-World Light Theme Styling
st.markdown(
    """
    <style>
        @keyframes cosmicPulse {
            0% { transform: scale(1); opacity: 0.8; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(1); opacity: 0.8; }
        }
        @keyframes orbit {
            0% { transform: rotate(0deg) translateX(10px) rotate(0deg); }
            100% { transform: rotate(360deg) translateX(10px) rotate(-360deg); }
        }
        @keyframes supernova {
            0% { box-shadow: 0 0 5px #ffd700, 0 0 15px #ff80bf; }
            50% { box-shadow: 0 0 20px #ffd700, 0 0 30px #ff80bf; }
            100% { box-shadow: 0 0 5px #ffd700, 0 0 15px #ff80bf; }
        }
        @keyframes starFade {
            0% { opacity: 0; transform: translateY(50px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        body { font-family: 'Exo 2', sans-serif; }
        .stApp { 
            background: linear-gradient(135deg, #f5faff, #e0f0ff, #fef8e6); 
            color: #1e1e4a; 
            animation: starFade 1.5s ease-in-out; 
            position: relative; 
            overflow: hidden; 
        }
        .stApp::before {
            content: '✨';
            position: absolute;
            font-size: 4rem;
            color: rgba(255, 215, 0, 0.3);
            top: 20px;
            left: 20px;
            animation: orbit 8s infinite linear;
        }
        .stApp::after {
            content: '🌠';
            position: absolute;
            font-size: 3rem;
            color: rgba(255, 128, 191, 0.3);
            bottom: 20px;
            right: 20px;
            animation: orbit 10s infinite linear reverse;
        }
        .stButton>button { 
            background: linear-gradient(90deg, #ffd700, #ff80bf, #80dfff); 
            color: #1e1e4a; 
            border-radius: 25px; 
            padding: 15px 40px; 
            font-size: 18px; 
            font-weight: bold;
            transition: all 0.5s ease; 
            animation: supernova 3s infinite; 
            border: none;
            text-transform: uppercase;
        }
        .stButton>button:hover { 
            transform: scale(1.2) translateY(-5px); 
            background: linear-gradient(90deg, #80dfff, #ff80bf, #ffd700); 
        }
        .stSidebar { 
            background: linear-gradient(180deg, rgba(255, 250, 240, 0.9), rgba(224, 240, 255, 0.9)); 
            backdrop-filter: blur(10px); 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 5px 25px rgba(0,0,0,0.05); 
            border: 1px solid rgba(255, 215, 0, 0.3);
        }
        .stHeader { color: #ff80bf; font-size: 3.5rem; font-weight: 900; animation: cosmicPulse 2s infinite; }
        .stDataFrame { 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 20px; 
            padding: 20px; 
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.2); 
            border: 1px dashed #80dfff;
        }
        .stExpander { 
            background: rgba(255, 255, 255, 0.95); 
            border-radius: 20px; 
            box-shadow: 0 5px 15px rgba(255, 128, 191, 0.2); 
            border: 1px dashed #ffd700;
        }
        .feedback-box { 
            background: linear-gradient(45deg, rgba(255, 215, 0, 0.2), rgba(128, 223, 255, 0.2)); 
            border-radius: 20px; 
            padding: 25px; 
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.5); 
            border: 2px solid #ff80bf;
        }
        .cosmic-title { 
            text-align: center; 
            font-size: 2.5rem; 
            color: #ffd700; 
            text-shadow: 0 0 10px #ff80bf; 
            margin-bottom: 20px; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.header("🌠 Dimensional Gateway")
uploaded_file = st.sidebar.file_uploader(
    "Teleport your data (CSV/Excel)", 
    type=["csv", "xlsx"], 
    help="Supports CSV and Excel transmissions"
)

if uploaded_file:
    st.sidebar.success("🌟 Data vortex activated!")
else:
    st.sidebar.info("🌀 Awaiting dimensional data...")

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
        # Cosmic loading animation
        progress_bar = st.progress(0)
        with st.spinner("🌌 Warping through hyperspace..."):
            df = load_data(uploaded_file)
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.008)  # Faster for a snappier feel
            progress_bar.empty()
        
        st.success("✨ Portal stabilized!")
        
        # Raw data display
        st.markdown("<h2 class='cosmic-title'>📡 Raw Data Nebula</h2>", unsafe_allow_html=True)
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 245, 230, 0.6);"), use_container_width=True, height=400)
        
        # Data cleaning
        cleaning_method = st.selectbox("🧪 Quantum Purification Matrix", ["Void Collapse", "Astral Mean", "Nebula Median", "Zero Gravity"])
        cleaning_method_map = {
            "Void Collapse": "drop",
            "Astral Mean": "mean",
            "Nebula Median": "median",
            "Zero Gravity": "zero"
        }
        df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method])
        
        st.markdown("<h2 class='cosmic-title'>🌟 Stabilized Data Constellation</h2>", unsafe_allow_html=True)
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 245, 230, 0.6);"), use_container_width=True, height=400)
        
        # Summary stats
        with st.expander("📊 Galactic Data Codex"):
            st.write("Decoding cosmic metrics:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="YlOrRd"))
        
        # Correlation heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.markdown("<h2 class='cosmic-title'>🌈 Celestial Correlation Grid</h2>", unsafe_allow_html=True)
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Grid", template="plotly_white", color_continuous_scale="YlOrRd")
            fig.update_layout(hovermode="x unified", margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualizations
        if not numeric_columns.empty:
            st.markdown("<h2 class='cosmic-title'>🌌 Interdimensional Visuals</h2>", unsafe_allow_html=True)
            selected_column = st.selectbox("Select cosmic vector", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    df_cleaned, x=selected_column, nbins=50, title=f"🌠 {selected_column} Starfield", 
                    template="plotly_white", color_discrete_sequence=["#ff80bf"]
                )
                fig.update_layout(bargap=0.2, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_cleaned, y=selected_column, title=f"🪐 {selected_column} Gravity Well", 
                    template="plotly_white", color_discrete_sequence=["#80dfff"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    df_cleaned, y=selected_column, title=f"✨ {selected_column} Lightwave", 
                    template="plotly_white", markers=True, color_discrete_sequence=["#ffd700"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if st.checkbox("Activate Warp Field"):
                x_col = st.selectbox("X-axis vector", numeric_columns)
                y_col = st.selectbox("Y-axis vector", numeric_columns, index=1)
                fig = px.scatter(
                    df_cleaned, x=x_col, y=y_col, title=f"🌌 Warp: {x_col} vs {y_col}", 
                    template="plotly_white", color_discrete_sequence=["#ffd700"], 
                    animation_frame=None if 'Date' not in df_cleaned.columns else 'Date'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Outlier detection
            if st.checkbox("Scan for Cosmic Aberrations"):
                outliers = detect_outliers(df_cleaned, selected_column)
                st.write(f"Aberrations in {selected_column}:")
                if not outliers.empty:
                    st.write(outliers)
                else:
                    st.write("No aberrations detected in this vector.")
            
            # Quartile visualization
            st.markdown("<h2 class='cosmic-title'>🌟 Quantum Quartile Nexus</h2>", unsafe_allow_html=True)
            q1, q2, q3 = df_cleaned[selected_column].quantile([0.25, 0.5, 0.75])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Q1", "Q2 (Core)", "Q3"], y=[q1, q2, q3], 
                marker_color=["#ff80bf", "#ffd700", "#80dfff"], 
                text=[f"{q1:.2f}", f"{q2:.2f}", f"{q3:.2f}"], textposition="auto"
            ))
            fig.update_layout(title=f"Quartile Nexus for {selected_column}", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Integration
        with st.expander("🤖 Neural Star Core"):
            question = st.text_input("Ask the cosmic oracle (e.g., 'What’s the flux in this vector?')")
            if question:
                with st.spinner("🤖 Accessing star core..."):
                    time.sleep(1)
                st.write(f"🌠 Oracle Response (Feb 24, 2025): Decoding '{question}'. For {selected_column}, the lightwave indicates a [rising/falling/stable] flux based on interdimensional shifts.")
        
        # Download section
        export_format = st.selectbox("📡 Data Teleport Protocol", ["CSV", "Excel"])
        export_data = convert_df(df_cleaned, format=export_format.lower())
        st.download_button(
            label=f"🌌 Teleport Data ({export_format})",
            data=export_data,
            file_name=f"cosmic_data_{export_format.lower()}.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Teleport stabilized data across dimensions."
        )

        # Feedback Section
        st.markdown("<h2 class='cosmic-title'>🌠 Intergalactic Feedback</h2>", unsafe_allow_html=True)
        st.markdown("<div class='feedback-box'>", unsafe_allow_html=True)
        with st.form(key="feedback_form"):
            st.write("Rate this cosmic voyage:")
            feedback_rating = st.slider("Star Rating (1-5)", 1, 5, 3, format="%d 🌟")
            feedback_text = st.text_area("Send a cosmic signal", height=120, placeholder="How can we amplify this portal?")
            submit_feedback = st.form_submit_button(label="Transmit to the Cosmos")
            if submit_feedback:
                st.success(f"🌌 Signal received! Rating: {feedback_rating}/5 🌟\nMessage: {feedback_text}")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Dimensional rift detected: {e}")
else:
    st.sidebar.warning("⚠ Open the data gateway to begin the voyage.")

# Cosmic Footer
st.markdown(
    """
    <div style="text-align: center; padding: 40px; background: linear-gradient(45deg, rgba(255, 245, 230, 0.9), rgba(224, 240, 255, 0.9)); border-radius: 20px; margin-top: 40px; box-shadow: 0 5px 25px rgba(255, 215, 0, 0.2);">
        <h3 style="color: #ff80bf; animation: cosmicPulse 2s infinite; font-size: 2.5rem;">Crafted by Sarfraz</h3>
        <p style="color: #1e1e4a; font-size: 1.3rem;">Explorer of the Financial Cosmos</p>
        <div style="margin-top: 15px;">
            <span style="font-size: 2rem; animation: orbit 12s infinite linear;">🌍</span>
            <span style="font-size: 1.5rem; animation: orbit 8s infinite linear reverse;">✨</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)