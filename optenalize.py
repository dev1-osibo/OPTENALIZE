import streamlit as st
import pandas as pd

# Define data cleaning workflow
def data_cleaning_workflow():
    """Implements the data cleaning workflow."""
    st.header("Data Cleaning")

    # Load dataset from session state
    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload a dataset to start cleaning.")
        return
    
    dataset = st.session_state["dataset"]

    # Missing Value Summary
    st.subheader("Missing Values Summary")
    missing_summary = dataset.isnull().sum().sort_values(ascending=False)
    missing_percentage = (missing_summary / len(dataset)) * 100
    st.write(pd.DataFrame({"Missing Values": missing_summary, "Percentage": missing_percentage}))

    # Handle Missing Values
    st.subheader("Advanced Missing Value Handling")

    # Select Essential Columns
    essential_columns = st.multiselect(
        "Select essential columns (rows with missing values here will be deleted):",
        options=dataset.columns,
        default=[],
        help="Choose columns that are critical for your analysis."
    )

    # Drop Columns with High Missing Values
    missing_threshold = st.slider(
        "Drop columns with more than this % missing values:", 0, 100, 50, 5
    )

    if st.button("Apply Missing Value Threshold"):
        cols_to_drop = missing_percentage[missing_percentage > missing_threshold].index
        cols_to_warn = [col for col in essential_columns if col in cols_to_drop]

        if cols_to_warn:
            st.warning(f"The following essential columns exceed the threshold and will NOT be dropped: {cols_to_warn}")
            cols_to_drop = [col for col in cols_to_drop if col not in essential_columns]

        dataset = dataset.drop(columns=cols_to_drop)
        st.session_state["dataset"] = dataset  # Update in session state
        st.success(f"Dropped columns: {list(cols_to_drop)}")

    # Handle Rows with Missing Values
    if essential_columns:
        dataset = dataset.dropna(subset=essential_columns)
        st.session_state["dataset"] = dataset  # Update in session state
        st.success("Dropped rows with missing values in essential columns.")

    # Impute Remaining Missing Values
    dataset = dataset.fillna(dataset.mean(numeric_only=True))
    st.session_state["dataset"] = dataset  # Update in session state
    st.success("Imputed numeric missing values with column means.")

    # Handle Duplicates
    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        before = len(dataset)
        dataset = dataset.drop_duplicates()
        st.session_state["dataset"] = dataset
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

    # Standardize Column Names
    st.subheader("Standardize Column Names")
    if st.button("Standardize Columns"):
        dataset.columns = dataset.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("[^a-zA-Z0-9_]", "")
        st.session_state["dataset"] = dataset
        st.success("Column names standardized.")

    # Preview Cleaned Dataset
    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head())


# Centralized App Heading
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>Welcome to Optenalize</h1>
        <h3>Your One-Stop Tool for Data Cleaning, Forecasting, and Machine Learning Insights</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

# Goal Selection
st.subheader("What would you like to do today?")
selected_goal = st.selectbox(
    "Select your goal:",
    [
        "Clean the dataset",
        "Perform exploratory data analysis (EDA)",
        "Train a predictive model",
        "Perform general ML tasks",
        "Other (specify custom goal)"
    ]
)
st.session_state["selected_goal"] = selected_goal

# File Upload Section
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
        st.dataframe(st.session_state["dataset"].head())

# Branch into workflows
if st.session_state["selected_goal"] == "Clean the dataset":
    data_cleaning_workflow()
elif st.session_state["selected_goal"] == "Perform exploratory data analysis (EDA)":
    st.info("EDA workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Train a predictive model":
    st.info("Predictive modeling workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Perform general ML tasks":
    st.info("General ML workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Other (specify custom goal)":
    st.info("Custom workflow will be implemented next.")