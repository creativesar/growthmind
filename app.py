import streamlit as st
import pandas as pd
from io import BytesIO

# Streamlit app title
st.set_page_config(page_title="Financial Data Sweeper", layout="wide")
st.title("🚀 Financial Data Sweeper")

# Custom Styling
st.markdown("""
    <style>
        .stApp { background-color: #f4f4f4; font-family: 'Arial', sans-serif; }
        .css-18e3th9 { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
        .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; padding: 10px; font-size: 16px; }
        .stSidebar { background-color: #f8f9fa; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# File uploader
st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Detect file type and read data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.subheader("📜 Raw Data")
        st.dataframe(df, use_container_width=True, height=300)

        # Cleaning the data
        df_cleaned = df.dropna()  # Remove missing values
        df_cleaned = df_cleaned.drop_duplicates()  # Remove duplicate rows
        
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_cleaned, use_container_width=True, height=300)
        
        # Summary statistics
        st.subheader("📊 Data Summary")
        st.write(df_cleaned.describe())
        
        # Download cleaned data
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            df.to_csv(output, index=False)
            processed_data = output.getvalue()
            return processed_data
        
        csv = convert_df(df_cleaned)
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            help="Click to download the cleaned CSV file."
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.info("Please upload a CSV or Excel file to proceed.")
