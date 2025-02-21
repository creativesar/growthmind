import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout="wide")

st.markdown(
    """
    <style>
        .main { background-color: #121212; }
        .block-container { padding: 2rem; background-color: #1e1e1e; border-radius: 12px; }
        h1, h2, h3, h4, h5, h6, p, label, .stText { color: white !important; } /* Text White */
        .stButton>button { background-color: #0078D7; color: white; border-radius: 8px; }
        .stButton>button:hover { background-color: #005a9e; }
        .stDownloadButton>button { background-color: #28a745; color: white; }
        .stDownloadButton>button:hover { background-color: #218838; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚀 Advanced Financial Data Sweeper")
st.write("Upload and clean your financial data, visualize trends, and convert between formats.")

uploaded_files = st.file_uploader("Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        df = pd.read_csv(file) if file_extension == ".csv" else pd.read_excel(file)

        st.write(f"**📄 File:** {file.name} ({file.size / 1024:.2f} KB)")
        st.dataframe(df.head())
        
        st.subheader("📊 Data Insights")
        st.write(df.describe())
        
        st.subheader("🛠️ Data Cleaning")
        if st.checkbox(f"Remove Duplicates from {file.name}"):
            df.drop_duplicates(inplace=True)
            st.write("Duplicates Removed!")

        if st.checkbox(f"Fill Missing Values for {file.name}"):
            df.fillna(df.mean(), inplace=True)
            st.write("Missing Values Filled with Mean!")
        
        st.subheader("📈 Visualization")
        chart_type = st.selectbox(f"Choose a Chart Type for {file.name}", ["Bar", "Line", "Pie", "Histogram"], key=file.name)
        numeric_columns = df.select_dtypes(include=['number']).columns
        selected_column = st.selectbox("Select Column to Visualize", numeric_columns, key=file.name + "_col")

        if chart_type == "Bar":
            fig = px.bar(df, x=df.index, y=selected_column, title=f"Bar Chart of {selected_column}")
        elif chart_type == "Line":
            fig = px.line(df, x=df.index, y=selected_column, title=f"Line Chart of {selected_column}")
        elif chart_type == "Pie":
            fig = px.pie(df, names=selected_column, title=f"Pie Chart of {selected_column}")
        else:
            fig = px.histogram(df, x=selected_column, title=f"Histogram of {selected_column}")

        st.plotly_chart(fig)
        
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio("Convert to:", ["CSV", "Excel"], key=file.name + "_conv")
        buffer = BytesIO()
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            mime_type = "text/csv"
        else:
            df.to_excel(buffer, index=False, engine='openpyxl')
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        buffer.seek(0)
        
        st.download_button(
            label=f"⬇️ Download {file.name} as {conversion_type}",
            data=buffer,
            file_name=file.name.replace(file_extension, ".csv" if conversion_type == "CSV" else ".xlsx"),
            mime=mime_type
        )

st.success("🎉 Processing Complete!")
