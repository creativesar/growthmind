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

# Dark mode toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

theme = "plotly_dark" if dark_mode else "plotly"
background = "#0f0c29" if dark_mode else "#f4f4f4"

# Sidebar - File uploader
st.sidebar.header("📂 Upload Financial Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], help="Supports CSV and Excel files")

if uploaded_file:
    st.sidebar.success("✅ File uploaded!")
else:
    st.sidebar.info("Awaiting file upload...")

def load_data(file):
    """Load data from uploaded CSV or Excel file."""
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

def clean_data(df):
    """Remove missing values and duplicate records from the dataframe."""
    df = df.dropna().drop_duplicates()
    return df

def convert_df(df):
    """Convert dataframe to CSV format for downloading."""
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

if uploaded_file:
    try:
        with st.spinner("🚀 Processing file..."):
            df = load_data(uploaded_file)
            time.sleep(1)
        
        st.success("🎉 File successfully uploaded!")
        
        st.subheader("📜 Raw Data")
        st.dataframe(df, use_container_width=True)
        
        df_cleaned = clean_data(df)
        
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_cleaned, use_container_width=True)
        
        with st.expander("📊 Data Summary"):
            st.write(df_cleaned.describe())
        
        # Correlation Heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            fig = px.imshow(df_cleaned[numeric_columns].corr(), text_auto=True, template=theme, title="📊 Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)
        
        # Visualization
        if not numeric_columns.empty:
            st.subheader("📈 Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(df_cleaned, x=selected_column, nbins=40, template=theme, title=f"📊 {selected_column} Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(df_cleaned, y=selected_column, template=theme, title=f"📦 {selected_column} Boxplot")
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(df_cleaned, y=selected_column, template=theme, title=f"📈 {selected_column} Trend Line")
                st.plotly_chart(fig, use_container_width=True)
        
        # Download cleaned data
        csv = convert_df(df_cleaned)
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")
