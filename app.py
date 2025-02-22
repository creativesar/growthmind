import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from io import BytesIO
import numpy as np

# Streamlit app configuration
st.set_page_config(page_title="📊 Financial Data Sweeper", layout="wide", page_icon="🚀")
st.title("🚀 Financial Data Sweeper")

# Custom Styling for enhanced UI/UX
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #00C9A7; }
            50% { box-shadow: 0 0 20px #FF4B2B; }
            100% { box-shadow: 0 0 5px #00C9A7; }
        }
        @keyframes float {
            0% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0); }
        }
        body { font-family: 'Inter', sans-serif; }
        .stApp { background: linear-gradient(to right, #0f0c29, #302b63, #24243e); color: white; }
        .stButton>button { 
            background: linear-gradient(to right, #ff416c, #ff4b2b); 
            color: white; 
            border-radius: 12px; 
            padding: 12px 24px; 
            font-size: 16px; 
            transition: 0.3s ease-in-out; 
            animation: glow 2s infinite, pop 0.5s ease-in-out; 
        }
        .stButton>button:hover { transform: scale(1.1); }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px); 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 2px 2px 12px rgba(0,0,0,0.1); 
            animation: fadeIn 1s ease-in-out; 
        }
        .stHeader { color: white; font-size: 2.5rem; font-weight: bold; animation: float 3s infinite; }
        .stDataFrame { background: rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 10px; }
        .stExpander { background: rgba(255, 255, 255, 0.1); border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar - File uploader
st.sidebar.header("📂 Upload Financial Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV or Excel file", 
    type=["csv", "xlsx"], 
    help="Supports CSV and Excel files"
)

if uploaded_file:
    st.sidebar.success("✅ File uploaded!")
else:
    st.sidebar.info("Awaiting file upload...")

# Function to load data from file
def load_data(file):
    """Load data from uploaded CSV or Excel file."""
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# Function to clean data
def clean_data(df):
    """Remove missing values and duplicate records from the dataframe."""
    return df.dropna().drop_duplicates()

# Function to convert dataframe to downloadable CSV format
def convert_df(df):
    """Convert dataframe to CSV format for downloading."""
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

if uploaded_file:
    try:
        with st.spinner("🚀 Processing file..."):
            df = load_data(uploaded_file)  # Load data
            time.sleep(1)
        
        st.success("🎉 File successfully uploaded!")
        
        # Display raw data
        st.subheader("📜 Raw Data - Original dataset preview")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Clean data by removing NaN and duplicate values
        df_cleaned = clean_data(df)
        
        st.subheader("✨ Cleaned Data - Processed for accuracy")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Summary statistics
        with st.expander("📊 Data Summary - Click to Expand"):
            st.write("Statistical insights of the dataset:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="viridis"))
        
        # Data Visualization
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("📈 Interactive Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    df_cleaned, 
                    x=selected_column, 
                    nbins=40, 
                    title=f"📊 {selected_column} Distribution", 
                    template="plotly_dark", 
                    color_discrete_sequence=["#FF4B2B"]
                )
                fig.update_layout(bargap=0.1, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_cleaned, 
                    y=selected_column, 
                    title=f"📦 {selected_column} Boxplot", 
                    template="plotly_dark", 
                    color_discrete_sequence=["#00C9A7"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    df_cleaned, 
                    y=selected_column, 
                    title=f"📈 {selected_column} Trend Line", 
                    template="plotly_dark", 
                    markers=True, 
                    color_discrete_sequence=["#FFD700"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 Q1, Q2, Q3 Comparison - Understanding quartiles")
            q1, q2, q3 = df_cleaned[selected_column].quantile([0.25, 0.5, 0.75])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Q1", "Q2 (Median)", "Q3"], 
                y=[q1, q2, q3], 
                marker_color=["#FF4B2B", "#FFD700", "#00C9A7"], 
                text=[q1, q2, q3], 
                textposition="auto"
            ))
            fig.update_layout(
                title=f"📊 Q1, Q2, Q3 Comparison for {selected_column}", 
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Download cleaned data
        csv = convert_df(df_cleaned)
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            help="Download the cleaned CSV file for further analysis."
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")

# Add a futuristic footer
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 12px; margin-top: 20px;">
        <h3 style="color: white; animation: float 3s infinite;">Developed By Sarfraz Ahmad</h3>
        <p style="color: white;">Explore the future of financial data analysis!</p>
    </div>
    """,
    unsafe_allow_html=True,
)