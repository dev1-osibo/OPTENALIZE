import streamlit as st

st.title("Optenalize: Data Cleaning and Forecasting")
st.write("Welcome to the Optenalize platform!")

uploaded_file = st.file_uploader("Upload your dataset (CSV, Excel, etc.)")
if uploaded_file is not None:
    st.write("File uploaded successfully!")
    # Additional processing can go here.