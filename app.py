import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np

# Streamlit app configuration
st.set_page_config(page_title="📊 Financial Data Sweeper", layout="wide", page_icon="🚀")
st.title("🚀 Financial Data Sweeper V2.0")

# Enhanced Custom Styling with futuristic flair
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #00C9A7, 0 0 10px #FF4B2B; }
            50% { box-shadow: 0 0 20px #FF4B2B, 0 0 30px #00C9A7; }
            100% { box-shadow: 0 0 5px #00C9A7, 0 0 10px #FF4B2B; }
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
        body { font-family: 'Orbitron', sans-serif; }
        .stApp { 
            background: linear-gradient(135deg, #1a0b2e, #3b1e5e, #2e2a6b); 
            color: #e0e0ff; 
            animation: fadeIn 1s ease-in-out; 
        }
        .stButton>button { 
            background: linear-gradient(45deg, #ff2b6c, #ff8e53); 
            color: white; 
            border-radius: 15px; 
            padding: 15px 30px; 
            font-size: 18px; 
            transition: all 0.4s ease; 
            animation: glow 2s infinite, pulse 1.5s infinite; 
            border: none;
        }
        .stButton>button:hover { 
            transform: scale(1.15); 
            background: linear-gradient(45deg, #ff8e53, #ff2b6c); 
        }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(15px); 
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
            animation: fadeIn 1.2s ease-in-out; 
        }
        .stHeader { color: #ffd700; font-size: 3rem; font-weight: 700; animation: float 3s infinite; }
        .stDataFrame { 
            background: rgba(255, 255, 255, 0.08); 
            border-radius: 15px; 
            padding: 15px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.15); 
        }
        .stExpander { 
            background: rgba(255, 255, 255, 0.08); 
            border-radius: 15px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.15); 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar - Enhanced with futuristic elements
st.sidebar.header("📂 Data Portal")
uploaded_file = st.sidebar.file_uploader(
    "Upload your data matrix (CSV/Excel)", 
    type=["csv", "xlsx"], 
    help="Compatible with CSV and Excel data streams"
)
theme = st.sidebar.radio("🌌 Theme Matrix", ["Cosmic Dark", "Quantum Light"])

if theme == "Quantum Light":
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #f0f8ff, #e6e6fa); color: #1a0b2e; }
            .stHeader { color: #ff2b6c; }
        </style>
    """, unsafe_allow_html=True)

if uploaded_file:
    st.sidebar.success("✅ Data stream activated!")
else:
    st.sidebar.info("🌀 Awaiting data transmission...")

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
        # Enhanced loading animation
        progress_bar = st.progress(0)
        with st.spinner("🌀 Initializing data stream..."):
            df = load_data(uploaded_file)
            for i in range(100):
                progress_bar.progress(i + 1)
            progress_bar.empty()
        
        st.success("🌌 Data matrix successfully integrated!")
        
        # Raw data display
        st.subheader("📜 Raw Data Matrix")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=400)
        
        # Data cleaning options
        cleaning_method = st.selectbox("🧠 Data Purification", ["Drop Anomalies", "Mean Imputation", "Median Imputation", "Zero Fill"])
        cleaning_method_map = {
            "Drop Anomalies": "drop",
            "Mean Imputation": "mean",
            "Median Imputation": "median",
            "Zero Fill": "zero"
        }
        df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method])
        
        st.subheader("✨ Purified Data Matrix")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=400)
        
        # Summary stats
        with st.expander("📊 Data Insights Portal"):
            st.write("Quantum statistical analysis:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="plasma"))
        
        # Correlation heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("🔥 Correlation Nebula")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Nebula", template="plotly_dark", color_continuous_scale="inferno")
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualizations
        if not numeric_columns.empty:
            st.subheader("🌠 Visualization Galaxy")
            selected_column = st.selectbox("Select data vector", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    df_cleaned, x=selected_column, nbins=50, title=f"📊 {selected_column} Distribution Field", 
                    template="plotly_dark", color_discrete_sequence=["#ff8e53"]
                )
                fig.update_layout(bargap=0.2, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_cleaned, y=selected_column, title=f"📦 {selected_column} Quantum Box", 
                    template="plotly_dark", color_discrete_sequence=["#00C9A7"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    df_cleaned, y=selected_column, title=f"📈 {selected_column} Temporal Stream", 
                    template="plotly_dark", markers=True, color_discrete_sequence=["#ffd700"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if st.checkbox("Activate Scatter Dimension"):
                x_col = st.selectbox("X-axis vector", numeric_columns)
                y_col = st.selectbox("Y-axis vector", numeric_columns, index=1)
                fig = px.scatter(
                    df_cleaned, x=x_col, y=y_col, title=f"Scatter Dimension: {x_col} vs {y_col}", 
                    template="plotly_dark", color_discrete_sequence=["#ff2b6c"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Outlier detection
            if st.checkbox("Scan for Anomalies"):
                outliers = detect_outliers(df_cleaned, selected_column)
                st.write(f"Anomalies in {selected_column}:")
                if not outliers.empty:
                    st.write(outliers)
                else:
                    st.write("No anomalies detected in this vector.")
            
            # Quartile visualization
            st.subheader("📊 Quartile Constellation")
            q1, q2, q3 = df_cleaned[selected_column].quantile([0.25, 0.5, 0.75])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Q1", "Q2 (Median)", "Q3"], y=[q1, q2, q3], 
                marker_color=["#ff8e53", "#ffd700", "#00C9A7"], 
                text=[f"{q1:.2f}", f"{q2:.2f}", f"{q3:.2f}"], textposition="auto"
            ))
            fig.update_layout(title=f"Quartile Constellation for {selected_column}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Integration with AI
        with st.expander("🤖 AI"):
            question = st.text_input("Query the AI core (e.g., 'What’s the trend in this vector?')")
            if question:
                st.write("🤖 AI core processing...")
                # Example response (integrated with an AI model)
                st.write(f"Analysis: As of Feb 22, 2025, I'm analyzing your data. For '{question}', I'd need to see the specific trend in {selected_column}. Based on the line chart, it appears to [describe trend].")

        # Download section
        export_format = st.selectbox("📤 Export Protocol", ["CSV", "Excel"])
        export_data = convert_df(df_cleaned, format=export_format.lower())
        st.download_button(
            label=f"📥 Extract Data ({export_format})",
            data=export_data,
            file_name=f"purified_data.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Extract purified data for external analysis."
        )

        # Feedback Section
        st.subheader("🌟 Feedback Matrix")
        with st.form(key="feedback_form"):
            feedback_rating = st.slider("Rate your experience (1-5)", 1, 5, 3)
            feedback_text = st.text_area("Share your thoughts on this dashboard")
            submit_feedback = st.form_submit_button(label="Transmit Feedback")
            if submit_feedback:
                st.success(f"Feedback transmitted! Rating: {feedback_rating}/5\nMessage: {feedback_text}")
        
    except Exception as e:
        st.error(f"❌ System error in data processing: {e}")
else:
    st.sidebar.warning("⚠ Initiate data upload to activate dashboard.")

# Futuristic Footer
st.markdown(
    """
    <div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; margin-top: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
        <h3 style="color: #ffd700; animation: float 3s infinite; font-size: 2rem;">Engineered by Sarfraz</h3>
        <p style="color: #e0e0ff; font-size: 1.2rem;">Unleashing the future of financial data exploration</p>
        <p style="color: #00C9A7; font-size: 0.9rem;">Powered by xAI • Deployed on Feb 22, 2025</p>
    </div>
    """,
    unsafe_allow_html=True,
)