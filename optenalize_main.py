import streamlit as st
import pandas as pd
from dataset_precheck_workflow import dataset_precheck_workflow
from data_cleaning_workflow import data_cleaning_workflow
from eda_workflow import eda_workflow

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>Welcome to Optenalize</h1>
        <h3>Your One-Stop Tool for Data Cleaning, Forecasting, and Machine Learning Insights</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

if "dataset" not in st.session_state:
    st.session_state["dataset"] = None

uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        st.session_state["dataset"] = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        st.session_state["dataset"] = pd.read_excel(uploaded_file)
    elif file_type == "json":
        st.session_state["dataset"] = pd.read_json(uploaded_file)

    dataset_precheck_workflow(st.session_state["dataset"])

tab1, tab2 = st.tabs(["Clean Dataset", "EDA"])
with tab1:
    if st.session_state["dataset"] is not None:
        data_cleaning_workflow(st.session_state["dataset"])
    else:
        st.warning("Please upload a dataset first.")

with tab2:
    if st.session_state["dataset"] is not None:
        eda_workflow(st.session_state["dataset"])
    else:
        st.warning("Please upload a dataset first.")