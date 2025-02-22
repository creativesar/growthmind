import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
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

# Sidebar - File uploader and theme switcher
st.sidebar.header("📂 Upload Financial Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV or Excel file", 
    type=["csv", "xlsx"], 
    help="Supports CSV and Excel files"
)
theme = st.sidebar.radio("🎨 Select Theme", ["Dark", "Light"])

if theme == "Light":
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(to right, #ffffff, #f0f8ff); color: black; }
        </style>
    """, unsafe_allow_html=True)

# Function to load data from file
def load_data(file):
    """Load data from uploaded CSV or Excel file."""
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# Function to clean data
def clean_data(df, method="drop"):
    """Handle missing values based on user preference."""
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

# Function to convert dataframe to downloadable format
def convert_df(df, format="csv"):
    """Convert dataframe to CSV or Excel format for downloading."""
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
        with st.spinner("🚀 Processing file..."):
            df = load_data(uploaded_file)  # Load data
        
        st.success("🎉 File successfully uploaded!")
        
        # Display raw data
        st.subheader("📜 Raw Data - Original dataset preview")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Clean data by removing NaN and duplicate values
        cleaning_method = st.selectbox("🧹 Select cleaning method", ["Drop Missing Values", "Fill with Mean", "Fill with Median"])
        cleaning_method_map = {
            "Drop Missing Values": "drop",
            "Fill with Mean": "mean",
            "Fill with Median": "median"
        }
        df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method])
        
        st.subheader("✨ Cleaned Data - Processed for accuracy")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Summary statistics
        with st.expander("📊 Data Summary - Click to Expand"):
            st.write("Statistical insights of the dataset:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="viridis"))
        
        # Correlation Heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("🔥 Correlation Heatmap")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap", template="plotly_dark", color_continuous_scale="viridis")
            st.plotly_chart(fig, use_container_width=True)
        
        # Interactive Filters
        st.subheader("🔍 Interactive Filters")
        filter_column = st.selectbox("Select a column to filter", df_cleaned.columns)
        if df_cleaned[filter_column].dtype in [np.int64, np.float64]:
            min_val, max_val = st.slider(f"Filter {filter_column} range", float(df_cleaned[filter_column].min()), float(df_cleaned[filter_column].max()), (float(df_cleaned[filter_column].min()), float(df_cleaned[filter_column].max())))
            filtered_df = df_cleaned[(df_cleaned[filter_column] >= min_val) & (df_cleaned[filter_column] <= max_val)]
        else:
            unique_values = df_cleaned[filter_column].unique()
            selected_values = st.multiselect(f"Select values for {filter_column}", unique_values, default=unique_values)
            filtered_df = df_cleaned[df_cleaned[filter_column].isin(selected_values)]
        
        st.dataframe(filtered_df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Data Visualization
        if not numeric_columns.empty:
            st.subheader("📈 Interactive Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig = px.histogram(
                    filtered_df, 
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
                    filtered_df, 
                    y=selected_column, 
                    title=f"📦 {selected_column} Boxplot", 
                    template="plotly_dark", 
                    color_discrete_sequence=["#00C9A7"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                fig = px.line(
                    filtered_df, 
                    y=selected_column, 
                    title=f"📈 {selected_column} Trend Line", 
                    template="plotly_dark", 
                    markers=True, 
                    color_discrete_sequence=["#FFD700"]
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # AI-Powered Insights
        st.subheader("🤖 AI-Powered Insights")
        if len(numeric_columns) > 1:
            kmeans_clusters = st.slider("Number of Clusters for K-Means", 2, 10, 3)
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(filtered_df[numeric_columns])
            kmeans = KMeans(n_clusters=kmeans_clusters, random_state=42)
            filtered_df["Cluster"] = kmeans.fit_predict(scaled_data)
            
            fig = px.scatter_matrix(
                filtered_df,
                dimensions=numeric_columns,
                color="Cluster",
                title="K-Means Clustering",
                template="plotly_dark",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Download cleaned data
        export_format = st.selectbox("📤 Select export format", ["CSV", "Excel"])
        export_data = convert_df(filtered_df, format=export_format.lower())
        st.download_button(
            label=f"📥 Download Filtered Data ({export_format})",
            data=export_data,
            file_name=f"filtered_data.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the filtered file for further analysis."
        )
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")

# Add a futuristic footer
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 12px; margin-top: 20px;">
        <h3 style="color: white; animation: float 3s infinite;">Developed By Sarfraz</h3>
        <p style="color: white;">Explore the future of financial data analysis!</p>
    </div>
    """,
    unsafe_allow_html=True,
)