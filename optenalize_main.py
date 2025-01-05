import streamlit as st
import pandas as pd
from dataset_precheck_workflow import dataset_precheck_workflow
from data_cleaning_workflow import data_cleaning_workflow
from eda_workflow import eda_workflow

# Main App Heading
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>Welcome to Optenalize</h1>
        <h3>Your One-Stop Tool for Data Cleaning, Forecasting, and Machine Learning Insights</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State for Goal Selection
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

# Step 1: Upload Dataset
st.subheader("Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        st.session_state["dataset"] = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        st.session_state["dataset"] = pd.read_excel(uploaded_file)
    elif file_type == "json":
        st.session_state["dataset"] = pd.read_json(uploaded_file)

    if st.checkbox("Preview the dataset"):
        st.dataframe(st.session_state["dataset"].head(10))  # Preview limited to first 10 rows

    # Perform Dataset Pre-check
    dataset_precheck_workflow()

# Tabs for Navigation
st.subheader("Navigate Through Workflows")
tab1, tab2 = st.tabs(["Clean Dataset", "EDA"])

with tab1:
    if "dataset" in st.session_state:
        data_cleaning_workflow()
    else:
        st.warning("No dataset uploaded yet.")

with tab2:
    if "dataset" in st.session_state and not st.session_state.get("redirect_to_cleaning"):
        eda_workflow()
    elif "dataset" in st.session_state:
        st.warning("Please return to the 'Clean Dataset' tab to resolve issues.")
    else:
        st.warning("No dataset uploaded yet.")