import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from io import BytesIO
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# App Configuration
st.set_page_config(page_title="📊 Financial Data Sweeper", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# Theme Persistence
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# Custom Styling
st.markdown(
    """
    <style>
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes glow { 0% { box-shadow: 0 0 5px #00C9A7; } 50% { box-shadow: 0 0 20px #FF4B2B; } 100% { box-shadow: 0 0 5px #00C9A7; } }
        @keyframes float { 0% { transform: translateY(0); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0); } }
        body { font-family: 'Inter', sans-serif; }
        .stButton>button { 
            background: linear-gradient(to right, #ff416c, #ff4b2b); 
            color: white; 
            border-radius: 12px; 
            padding: 12px 24px; 
            font-size: 16px; 
            transition: 0.3s ease-in-out; 
            animation: glow 2s infinite; 
        }
        .stButton>button:hover { transform: scale(1.1); }
        .stSidebar { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px); 
            padding: 20px; 
            border-radius: 12px; 
            animation: fadeIn 1s ease-in-out; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Theme Selection
theme_styles = {
    "Dark": ".stApp { background: linear-gradient(to right, #0f0c29, #302b63, #24243e); color: white; }",
    "Light": ".stApp { background: linear-gradient(to right, #ffffff, #f0f8ff); color: black; }",
    "Cyberpunk": ".stApp { background: linear-gradient(to right, #1a0d2e, #ff00cc, #00ffcc); color: #fff; }"
}
st.sidebar.title("📂 Control Panel")
theme = st.sidebar.selectbox("🎨 Theme", ["Dark", "Light", "Cyberpunk"], key="theme_selector")
st.session_state.theme = theme
st.markdown(f"<style>{theme_styles[st.session_state.theme]}</style>", unsafe_allow_html=True)

# Sidebar: File Upload & Navigation
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"], help="Supports CSV and Excel files")
page = st.sidebar.radio("Go to", ["Home", "Visualizations", "Insights"])

# Cached Functions
@st.cache_data
def load_data(file):
    """Load data from uploaded CSV or Excel file."""
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

@st.cache_data
def clean_data(df, method="drop", remove_outliers=False):
    """Handle missing values and outliers."""
    if method == "drop":
        df_clean = df.dropna().drop_duplicates()
    elif method == "mean":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        df_clean = df.drop_duplicates()
    elif method == "median":
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        df_clean = df.drop_duplicates()
    elif method == "ffill":
        df_clean = df.fillna(method="ffill").drop_duplicates()
    elif method == "bfill":
        df_clean = df.fillna(method="bfill").drop_duplicates()
    
    if remove_outliers:
        numeric_cols = df_clean.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            Q1, Q3 = df_clean[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df_clean = df_clean[~((df_clean[col] < (Q1 - 1.5 * IQR)) | (df_clean[col] > (Q3 + 1.5 * IQR)))]
    return df_clean

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

# Main App Logic
if uploaded_file:
    with st.spinner("🚀 Processing file..."):
        df = load_data(uploaded_file)
        time.sleep(1)
    
    st.title("🚀 Financial Data Sweeper")
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
    progress.empty()
    st.success("🎉 Data loaded successfully!")

    # Cleaning Options
    cleaning_method = st.selectbox("🧹 Select cleaning method", 
                                   ["Drop Missing Values", "Fill with Mean", "Fill with Median", "Forward Fill", "Backward Fill"])
    remove_outliers = st.checkbox("Remove Outliers (IQR Method)")
    cleaning_method_map = {
        "Drop Missing Values": "drop", "Fill with Mean": "mean", "Fill with Median": "median",
        "Forward Fill": "ffill", "Backward Fill": "bfill"
    }
    df_cleaned = clean_data(df, method=cleaning_method_map[cleaning_method], remove_outliers=remove_outliers)

    # Page Navigation
    if page == "Home":
        st.subheader("📜 Raw Data")
        st.dataframe(df.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        st.subheader("✨ Cleaned Data")
        st.dataframe(df_cleaned.style.applymap(lambda x: "background-color: rgba(255, 255, 255, 0.1);"), use_container_width=True, height=350)
        
        # Data Transformation
        st.subheader("🔧 Data Transformation")
        transform_option = st.selectbox("Apply Transformation", ["None", "Log", "Normalize", "Standardize"])
        if transform_option != "None":
            numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
            if transform_option == "Log":
                df_cleaned[numeric_cols] = np.log1p(df_cleaned[numeric_cols])
            elif transform_option == "Normalize":
                df_cleaned[numeric_cols] = (df_cleaned[numeric_cols] - df_cleaned[numeric_cols].min()) / (df_cleaned[numeric_cols].max() - df_cleaned[numeric_cols].min())
            elif transform_option == "Standardize":
                df_cleaned[numeric_cols] = (df_cleaned[numeric_cols] - df_cleaned[numeric_cols].mean()) / df_cleaned[numeric_cols].std()
            st.write("Transformed Data Preview:")
            st.dataframe(df_cleaned.head())

        # Download Cleaned Data
        export_format = st.selectbox("📤 Select export format", ["CSV", "Excel"])
        export_data = convert_df(df_cleaned, format=export_format.lower())
        st.download_button(
            label=f"📥 Download Cleaned Data ({export_format})",
            data=export_data,
            file_name=f"cleaned_data.{export_format.lower()}",
            mime="text/csv" if export_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif page == "Visualizations":
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("📈 Interactive Data Visualizations")
            selected_column = st.selectbox("Select a column to visualize", numeric_columns)
            chart_style = st.selectbox("Chart Style", ["Default", "Minimal", "Bold"])
            style_map = {"Default": "plotly_dark", "Minimal": "simple_white", "Bold": "seaborn"}

            col1, col2, col3 = st.columns(3)
            with col1:
                fig = px.histogram(df_cleaned, x=selected_column, nbins=40, title=f"📊 {selected_column} Distribution", 
                                   template=style_map[chart_style], color_discrete_sequence=["#FF4B2B"])
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.box(df_cleaned, y=selected_column, title=f"📦 {selected_column} Boxplot", 
                             template=style_map[chart_style], color_discrete_sequence=["#00C9A7"])
                st.plotly_chart(fig, use_container_width=True)
            with col3:
                fig = px.line(df_cleaned, y=selected_column, title=f"📈 {selected_column} Trend Line", 
                              template=style_map[chart_style], markers=True, color_discrete_sequence=["#FFD700"])
                st.plotly_chart(fig, use_container_width=True)

            # 3D Plot
            if len(numeric_columns) >= 3:
                st.subheader("🌐 3D Visualization")
                x_3d = st.selectbox("X Axis", numeric_columns)
                y_3d = st.selectbox("Y Axis", numeric_columns, index=1)
                z_3d = st.selectbox("Z Axis", numeric_columns, index=2)
                fig = px.scatter_3d(df_cleaned, x=x_3d, y=y_3d, z=z_3d, title="3D Financial Data", template=style_map[chart_style])
                st.plotly_chart(fig, use_container_width=True)

            # Animated Trend
            date_col = df_cleaned.select_dtypes(include=['datetime', 'object']).columns
            if len(date_col) > 0:
                st.subheader("⏳ Animated Trend")
                fig = px.scatter(df_cleaned, x=date_col[0], y=selected_column, animation_frame=date_col[0], 
                                 title="Animated Trend Over Time", template=style_map[chart_style])
                st.plotly_chart(fig, use_container_width=True)

    elif page == "Insights":
        numeric_columns = df_cleaned.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.subheader("🔥 Correlation Heatmap")
            corr_matrix = df_cleaned[numeric_columns].corr()
            fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap", template="plotly_dark", color_continuous_scale="viridis")
            st.plotly_chart(fig, use_container_width=True)

            # Summary Statistics
            with st.expander("📊 Data Summary"):
                st.write(df_cleaned.describe().style.background_gradient(cmap="viridis"))

            # Predictive Insights
            st.subheader("🔮 Predictive Insights")
            if st.checkbox("Enable Forecasting") and len(numeric_columns) >= 2:
                x_col = st.selectbox("Select X (Feature)", numeric_columns)
                y_col = st.selectbox("Select Y (Target)", numeric_columns, index=1)
                X = df_cleaned[[x_col]].values
                y = df_cleaned[y_col].values
                model = LinearRegression().fit(X, y)
                preds = model.predict(X)
                fig = px.scatter(df_cleaned, x=x_col, y=y_col, trendline="ols", template="plotly_dark")
                st.plotly_chart(fig)
                st.write(f"Predicted {y_col} = {model.coef_[0]:.2f} * {x_col} + {model.intercept_:.2f}")

    # Tips
    tips = {
        "Drop Missing Values": "Good for small datasets but may lose data.",
        "Fill with Mean": "Best for normally distributed data.",
        "Fill with Median": "Robust to outliers.",
        "Forward Fill": "Great for time-series data.",
        "Backward Fill": "Fills gaps with future values."
    }
    st.info(f"💡 Tip: {tips.get(cleaning_method, 'Choose wisely!')}")

    # PDF Report
    st.subheader("📜 Generate Report")
    if st.button("Download PDF Report"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"Financial Data Summary:<br/>{df_cleaned.describe().to_string()}", styles['Normal'])]
        doc.build(story)
        st.download_button("Download Report", buffer.getvalue(), "report.pdf", "application/pdf")

else:
    st.sidebar.warning("⚠ Please upload a file to proceed.")
    st.write("Welcome to Financial Data Sweeper! Upload a file to begin.")

# Footer
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 12px; margin-top: 20px;">
        <h3 style="color: white; animation: float 3s infinite;">Developed By Sarfraz</h3>
        <p style="color: white;">Explore the future of financial data analysis!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Feedback
with st.sidebar.expander("💬 Feedback"):
    feedback = st.text_area("Tell us what you think!")
    if st.button("Submit Feedback"):
        st.success("Thanks for your feedback!")