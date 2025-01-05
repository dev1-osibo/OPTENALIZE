import streamlit as st
import pandas as pd
from dataset_precheck import dataset_precheck
from data_cleaning_workflow import data_cleaning_workflow
from eda_workflow import eda_workflow

# Initialize session state for goal selection
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

st.subheader("Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        dataset = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        dataset = pd.read_excel(uploaded_file)
    elif file_type == "json":
        dataset = pd.read_json(uploaded_file)

    st.session_state["dataset"] = dataset

    # Dataset Precheck
    issues_detected = dataset_precheck(dataset)

    # Tabs for Workflow Navigation
    tab1, tab2 = st.tabs(["Clean Dataset", "EDA"])

    with tab1:
        if issues_detected:
            st.warning("Dataset has issues. Please clean it first.")
        else:
            st.success("No issues detected. Ready to clean data.")
            st.session_state["dataset"] = data_cleaning_workflow(dataset)

    with tab2:
        if not issues_detected:
            eda_workflow(dataset)
        else:
            st.warning("Please resolve dataset issues before performing EDA.")