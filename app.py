import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from io import BytesIO

# Streamlit app configuration
st.set_page_config(page_title="📊 Financial Data Sweeper", layout="wide")
st.title("🚀 Financial Data Sweeper")

# Custom Modern Styling with Animations
st.markdown(
    """
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes pop {
            0% { transform: scale(0.9); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        body { font-family: 'Inter', sans-serif; }
        .stApp { background-color: #f0f2f6; color: #000000; }
        .css-18e3th9 { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 4px 4px 15px rgba(0,0,0,0.2); animation: fadeIn 1s ease-in-out; }
        .stButton>button { background: linear-gradient(to right, #ff416c, #ff4b2b); color: white; border-radius: 8px; padding: 12px; font-size: 16px; transition: 0.3s ease-in-out; animation: pop 0.5s ease-in-out; }
        .stButton>button:hover { background: linear-gradient(to right, #ff4b2b, #ff416c); transform: scale(1.1); }
        .stSidebar { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 2px 2px 12px rgba(0,0,0,0.1); animation: fadeIn 1s ease-in-out; }
        .stAlert { font-size: 18px; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar - File uploader with animation
st.sidebar.header("📂 Upload Financial Data")
with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], help="Supports CSV and Excel files")
    if uploaded_file:
        st.sidebar.success("✅ File uploaded!")
    else:
        st.sidebar.info("Awaiting file upload...")

if uploaded_file:
    try:
        # Detect file type and read data
        with st.spinner("Processing file..."):
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            time.sleep(1)
        
        st.success("🎉 File successfully uploaded!")
        
        # Display raw data
        st.subheader("📜 Raw Data")
        st.dataframe(df, use_container_width=True, height=350)
        
        # Data Cleaning
        df_cleaned = df.dropna().drop_duplicates()
        
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_cleaned, use_container_width=True, height=350)
        
        # Summary statistics
        with st.expander("📊 Data Summary - Click to Expand"):
            st.write(df_cleaned.describe())
        
        # Data Visualization
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("📈 Interactive Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(df_cleaned, x=selected_column, nbins=40, title=f"📊 {selected_column} Distribution", template="plotly_white", color_discrete_sequence=["#FF4B2B"])
                fig.update_layout(bargap=0.1)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(df_cleaned, y=selected_column, title=f"📦 {selected_column} Boxplot", template="plotly_white", color_discrete_sequence=["#FF4B2B"])
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(df_cleaned, y=selected_column, title=f"📈 {selected_column} Trend Line", template="plotly_white", markers=True, color_discrete_sequence=["#00C9A7"])
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 Q1, Q2, Q3 Comparison")
            q1 = df_cleaned[selected_column].quantile(0.25)
            q2 = df_cleaned[selected_column].median()
            q3 = df_cleaned[selected_column].quantile(0.75)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=["Q1", "Q2 (Median)", "Q3"], y=[q1, q2, q3], marker_color=["#FF4B2B", "#FFD700", "#00C9A7"], text=[q1, q2, q3], textposition="auto"))
            fig.update_layout(title=f"📊 Q1, Q2, Q3 Comparison for {selected_column}", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        # Download cleaned data
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            df.to_csv(output, index=False)
            return output.getvalue()
        
        csv = convert_df(df_cleaned)
        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv",
            help="Download the cleaned CSV file"
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")