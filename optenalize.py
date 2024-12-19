import streamlit as st
import pandas as pd

st.title("Optenalize: Data Cleaning and Forecasting")
st.write("Welcome to the Optenalize platform! Upload your dataset to get started.")

# File upload widget
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Show file name
    st.write(f"Uploaded file: {uploaded_file.name}")

    try:
        # Handle CSV and Excel files
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)

        # Display the data
        st.write("Here's a preview of your data:")
        st.dataframe(data.head())

    except Exception as e:
        st.error(f"Error loading file: {e}")