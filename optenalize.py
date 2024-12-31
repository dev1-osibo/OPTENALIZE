import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dataset Pre-check Functionality
def dataset_precheck():
    """
    Performs a quick scan of the uploaded dataset for common issues
    and provides user choices for resolution.
    """
    st.subheader("Dataset Pre-check")
    
    dataset = st.session_state["dataset"]
    issues_detected = False

    # Check for missing values
    missing_summary = dataset.isnull().sum()
    total_missing = missing_summary.sum()
    if total_missing > 0:
        issues_detected = True
        st.warning(f"Your dataset contains {total_missing} missing values.")
    
    # Check for duplicate rows
    duplicate_count = dataset.duplicated().sum()
    if duplicate_count > 0:
        issues_detected = True
        st.warning(f"Your dataset contains {duplicate_count} duplicate rows.")

    # Check for non-standard column names
    non_standard_cols = [
        col for col in dataset.columns if not col.isidentifier()
    ]
    if non_standard_cols:
        issues_detected = True
        st.warning(f"The following column names are non-standard: {non_standard_cols}")

    # Redirect Options
    if issues_detected:
        st.error("Issues detected in the dataset. Proceed with caution.")
        action = st.radio(
            "How would you like to proceed?",
            options=[
                "Clean the dataset now",
                "Proceed with warnings",
            ],
            index=0,
        )
        if action == "Clean the dataset now":
            st.session_state["redirect_to_cleaning"] = True
        elif action == "Proceed with warnings":
            st.session_state["proceed_with_warnings"] = True
    else:
        st.success("No issues detected in the dataset. Ready to proceed.")

# Exploratory Data Analysis Workflow
def eda_workflow():
    """
    Implements the Exploratory Data Analysis (EDA) workflow.
    """
    st.header("Exploratory Data Analysis (EDA)")
    dataset = st.session_state["dataset"]

    # Summary Statistics
    st.subheader("Summary Statistics")
    st.write(dataset.describe())

    # Data Visualization Options
    st.subheader("Generate Visualizations")
    visualization_type = st.selectbox(
        "Select Visualization Type",
        ["Histogram", "Scatter Plot", "Correlation Matrix"]
    )

    if visualization_type == "Histogram":
        column = st.selectbox("Select Column", dataset.select_dtypes(include=['float', 'int']).columns)
        if st.button("Generate Histogram"):
            fig, ax = plt.subplots()
            sns.histplot(dataset[column], kde=True, ax=ax)
            st.pyplot(fig)

    elif visualization_type == "Scatter Plot":
        col1, col2 = st.columns(2)
        x_col = col1.selectbox("Select X-Axis Column", dataset.columns)
        y_col = col2.selectbox("Select Y-Axis Column", dataset.columns)
        if st.button("Generate Scatter Plot"):
            fig, ax = plt.subplots()
            sns.scatterplot(data=dataset, x=x_col, y=y_col, ax=ax)
            st.pyplot(fig)

    elif visualization_type == "Correlation Matrix":
        if st.button("Generate Correlation Matrix"):
            fig, ax = plt.subplots()
            sns.heatmap(dataset.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            st.pyplot(fig)

# Data Cleaning Workflow
def data_cleaning_workflow():
    st.header("Data Cleaning")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload a dataset to start cleaning.")
        return

    dataset = st.session_state["dataset"]

    # Handle Missing Value Placeholders
    st.subheader("Handle Missing Value Placeholders")
    placeholders = st.text_input(
        "Enter placeholder values to treat as missing (comma-separated):",
        value="None,null,NA",
        help="Provide a list of placeholders (e.g., None, null, NA) to convert to missing values (NaN)."
    )
    if st.button("Apply Placeholder Replacement"):
        placeholder_list = [x.strip() for x in placeholders.split(",")]
        dataset.replace(placeholder_list, pd.NA, inplace=True)
        st.session_state["dataset"] = dataset
        st.success(f"Replaced placeholders {placeholder_list} with NaN.")

    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        before = len(dataset)
        dataset = dataset.drop_duplicates()
        st.session_state["dataset"] = dataset
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head())

    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

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

if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

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

    # Dataset Precheck
    dataset_precheck()

    # Redirect or Proceed
    if st.session_state.get("redirect_to_cleaning"):
        data_cleaning_workflow()
    elif st.session_state.get("proceed_with_warnings"):
        eda_workflow()

if st.session_state["selected_goal"] == "Clean the dataset":
    data_cleaning_workflow()
elif st.session_state["selected_goal"] == "Perform exploratory data analysis (EDA)":
    eda_workflow()
elif st.session_state["selected_goal"] == "Train a predictive model":
    st.info("Predictive modeling workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Perform general ML tasks":
    st.info("General ML workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Other (specify custom goal)":
    st.info("Custom workflow will be implemented next.")