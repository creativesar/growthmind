import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import time

# Streamlit app title
st.set_page_config(page_title="Financial Data Sweeper", layout="wide")
st.title("🚀 Financial Data Sweeper")

# Custom Styling
st.markdown("""
    <style>
        .stApp { background-color: #f4f4f4; font-family: 'Arial', sans-serif; }
        .css-18e3th9 { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
        .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; padding: 10px; font-size: 16px; transition: 0.3s ease-in-out; }
        .stButton>button:hover { background-color: #0056b3; }
        .stSidebar { background-color: #f8f9fa; padding: 20px; border-radius: 10px; }
        .stAlert { font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Sidebar - File uploader with animation
st.sidebar.header("📂 Upload Data")
with st.sidebar:
    with st.spinner("Waiting for file upload..."):
        uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
        time.sleep(1)

if uploaded_file:
    try:
        # Detect file type and read data
        with st.spinner("Processing file..."):
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            time.sleep(1)

        st.success("✅ File uploaded successfully!")
        st.subheader("📜 Raw Data")
        st.dataframe(df, use_container_width=True, height=300)

        # Cleaning the data
        df_cleaned = df.dropna()  # Remove missing values
        df_cleaned = df_cleaned.drop_duplicates()  # Remove duplicate rows
        
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_cleaned, use_container_width=True, height=300)
        
        # Summary statistics with expander
        with st.expander("📊 Data Summary - Click to Expand"):
            st.write(df_cleaned.describe())
        
        # Data Visualization
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("📈 Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            
            # Histogram
            fig, ax = plt.subplots()
            sns.histplot(df_cleaned[selected_column], bins=20, kde=True, ax=ax)
            ax.set_title(f"Distribution of {selected_column}")
            st.pyplot(fig)
            
            # Boxplot
            fig, ax = plt.subplots()
            sns.boxplot(y=df_cleaned[selected_column], ax=ax)
            ax.set_title(f"Boxplot of {selected_column}")
            st.pyplot(fig)
        
        # Download cleaned data with success message
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            df.to_csv(output, index=False)
            processed_data = output.getvalue()
            return processed_data
        
        csv = convert_df(df_cleaned)
        if st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            help="Click to download the cleaned CSV file."
        ):
            st.success("🎉 Download successful! Enjoy your cleaned data!")
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.info("Please upload a CSV or Excel file to proceed.")
