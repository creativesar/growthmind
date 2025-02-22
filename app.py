import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
import datetime

# Streamlit app configuration
st.set_page_config(page_title="📊 Financial Data Sweeper", layout="wide", page_icon="🚀")
st.title("🚀 Financial Data Sweeper - Next Gen")

# Enhanced Custom Styling with Better Color Contrast
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
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        body { font-family: 'Inter', sans-serif; }
        .stApp { background: linear-gradient(135deg, #1a1a1a, #2a2a2a, #3a3a3a); color: #E0E0E0; }
        .stButton>button { 
            background: linear-gradient(to right, #FF416C, #FF4B2B); 
            color: #FFFFFF; 
            border-radius: 12px; 
            padding: 12px 24px; 
            font-size: 16px; 
            transition: 0.3s ease-in-out; 
            animation: glow 2s infinite, pulse 1.5s infinite; 
        }
        .stButton>button:hover { transform: scale(1.15); }
        .stSidebar { 
            background: rgba(50, 50, 50, 0.9); 
            backdrop-filter: blur(15px); 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); 
            animation: fadeIn 1s ease-in-out; 
            color: #E0E0E0; 
        }
        .stHeader { color: #FFD700; font-size: 2.5rem; font-weight: bold; animation: float 3s infinite; }
        .stDataFrame { background: rgba(60, 60, 60, 0.8); border-radius: 12px; padding: 15px; }
        .stExpander { background: rgba(60, 60, 60, 0.8); border-radius: 12px; color: #E0E0E0; }
        .dashboard-card { 
            background: rgba(50, 50, 50, 0.9); 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
            animation: fadeIn 1s ease-in-out; 
            color: #E0E0E0; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar - File uploader and customization
st.sidebar.header("📂 Upload & Customize")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV or Excel file", 
    type=["csv", "xlsx"], 
    help="Supports CSV and Excel files"
)
theme = st.sidebar.radio("🎨 Select Theme", ["Dark", "Light"])
accent_color = st.sidebar.color_picker("🎨 Pick Accent Color", "#FF4B2B")

# Theme-specific adjustments
if theme == "Light":
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #F5F5F5, #E8ECEF, #DDE1E4); color: #333333; }
            .stSidebar { background: rgba(255, 255, 255, 0.9); color: #333333; }
            .stHeader { color: #FF4B2B; }
            .stDataFrame { background: rgba(255, 255, 255, 0.9); }
            .stExpander { background: rgba(255, 255, 255, 0.9); color: #333333; }
            .dashboard-card { background: rgba(255, 255, 255, 0.9); color: #333333; }
        </style>
    """, unsafe_allow_html=True)

if uploaded_file:
    st.sidebar.success("✅ File uploaded!")
else:
    st.sidebar.info("Awaiting file upload...")

# Cached function to load data
@st.cache_data
def load_data(file):
    """Load data from uploaded CSV or Excel file."""
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# Function to clean data
def clean_data(df, method="drop", custom_fill=None):
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
    elif method == "zero":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        return df.drop_duplicates()
    elif method == "custom" and custom_fill is not None:
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(custom_fill)
        return df.drop_duplicates()

# Function to detect outliers
def detect_outliers(df, column):
    """Detect outliers using IQR method."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)][column]
    return outliers

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

# Function to detect date columns
def detect_date_column(df):
    """Detect potential date columns."""
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            try:
                pd.to_datetime(df[col])
                return col
            except:
                continue
    return None

if uploaded_file:
    try:
        # Progress bar for loading
        progress_bar = st.progress(0)
        with st.spinner("🚀 Processing file..."):
            df = load_data(uploaded_file)
            for i in range(100):
                progress_bar.progress(i + 1)
            progress_bar.empty()
        
        st.success("🎉 File successfully uploaded!")
        
        # Dashboard Layout
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("📜 Raw Data - Original dataset preview")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clean data
        cleaning_method = st.selectbox("🧹 Select cleaning method", ["Drop Missing Values", "Fill with Mean", "Fill with Median", "Fill with Zero", "Custom Fill"])
        custom_fill = None
        if cleaning_method == "Custom Fill":
            custom_fill = st.number_input("Enter custom fill value", value=0.0)
        cleaning_method_map = {
            "Drop Missing Values": "drop",
            "Fill with Mean": "mean",
            "Fill with Median": "median",
            "Fill with Zero": "zero",
            "Custom Fill": "custom"
        }
        df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method], custom_fill=custom_fill)
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("✨ Cleaned Data - Processed for accuracy")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary statistics
        with st.expander("📊 Data Summary - Click to Expand"):
            st.write("Statistical insights of the dataset:")
            st.write(df_cleaned.describe().style.background_gradient(cmap="viridis"))
        
        # Correlation Heatmap
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.subheader("🔥 Correlation Heatmap")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap", template="plotly_dark", color_continuous_scale="viridis")
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("📥 Download Heatmap", data=fig.to_image(format="png"), file_name="heatmap.png", mime="image/png")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Visualization
        if not numeric_columns.empty:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
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
                    color_discrete_sequence=[accent_color]
                )
                fig.update_layout(bargap=0.1, hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 Download Histogram", data=fig.to_image(format="png"), file_name="histogram.png", mime="image/png")
            
            with col2:
                fig = px.box(
                    df_cleaned, 
                    y=selected_column, 
                    title=f"📦 {selected_column} Boxplot", 
                    template="plotly_dark", 
                    color_discrete_sequence=[accent_color]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 Download Boxplot", data=fig.to_image(format="png"), file_name="boxplot.png", mime="image/png")
            
            with col3:
                fig = px.line(
                    df_cleaned, 
                    y=selected_column, 
                    title=f"📈 {selected_column} Trend Line", 
                    template="plotly_dark", 
                    markers=True, 
                    color_discrete_sequence=[accent_color]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 Download Trend Line", data=fig.to_image(format="png"), file_name="trendline.png", mime="image/png")
            
            # Time Series Detection
            date_column = detect_date_column(df_cleaned)
            if date_column and st.checkbox("Analyze as Time Series"):
                df_cleaned[date_column] = pd.to_datetime(df_cleaned[date_column])
                fig = px.line(
                    df_cleaned, 
                    x=date_column, 
                    y=selected_column, 
                    title=f"⏳ Time Series: {selected_column} over {date_column}", 
                    template="plotly_dark", 
                    color_discrete_sequence=[accent_color]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 Download Time Series", data=fig.to_image(format="png"), file_name="timeseries.png", mime="image/png")
            
            # Scatter Plot Option
            if st.checkbox("Show Scatter Plot"):
                x_col = st.selectbox("Select X-axis column", numeric_columns)
                y_col = st.selectbox("Select Y-axis column", numeric_columns, index=1)
                fig = px.scatter(
                    df_cleaned, 
                    x=x_col, 
                    y=y_col, 
                    title=f"Scatter Plot: {x_col} vs {y_col}", 
                    template="plotly_dark", 
                    color_discrete_sequence=[accent_color]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 Download Scatter Plot", data=fig.to_image(format="png"), file_name="scatter.png", mime="image/png")
            
            # Outlier Detection
            if st.checkbox("Detect Outliers"):
                outliers = detect_outliers(df_cleaned, selected_column)
                st.write(f"Outliers in {selected_column}:")
                if not outliers.empty:
                    st.write(outliers)
                else:
                    st.write("No outliers detected.")
            
            # Quartile Comparison
            st.subheader("📊 Q1, Q2, Q3 Comparison")
            q1, q2, q3 = df_cleaned[selected_column].quantile([0.25, 0.5, 0.75])
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Q1", "Q2 (Median)", "Q3"], 
                y=[q1, q2, q3], 
                marker_color=[accent_color, "#FFD700", "#00C9A7"], 
                text=[f"{q1:.2f}", f"{q2:.2f}", f"{q3:.2f}"], 
                textposition="auto"
            ))
            fig.update_layout(title=f"📊 Q1, Q2, Q3 Comparison for {selected_column}", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.download_button("📥 Download Quartile Chart", data=fig.to_image(format="png"), file_name="quartile.png", mime="image/png")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Integration Placeholder
        with st.expander("🤖 Ask Grok - AI Insights"):
            question = st.text_input("Ask a question about your data (e.g., 'What’s the trend in this column?')")
            if question:
                st.write(f"Grok’s response: Analyzing '{question}' - [Imagine I’m diving into your data here!]")
        
        # Download cleaned data
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        export_format = st.selectbox("📤 Select export format", ["CSV", "Excel"])
        export_data = convert_df(df_cleaned, format=export_format.lower())
        st.download_button(
            label=f"📥 Download Cleaned Data ({export_format})",
            data=export_data,
            file_name=f"cleaned_data.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the cleaned file for further analysis."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")

# Futuristic Footer
st.markdown(
    f"""
    <div style="text-align: center; padding: 20px; background: rgba(50, 50, 50, 0.9); border-radius: 12px; margin-top: 20px;">
        <h3 style="color: {accent_color}; animation: float 3s infinite;">Developed By Sarfraz</h3>
        <p style="color: #E0E0E0;">Unleash the future of financial data analysis! 🚀</p>
        <p style="color: #B0B0B0; font-size: 0.9rem;">Powered by xAI’s Grok - {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
