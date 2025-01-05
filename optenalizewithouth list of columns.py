import streamlit as st
import pandas as pd
import seaborn as sns
import altair as alt

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

    # Redirect Options Based on Goal
    if issues_detected:
        if "selected_goal" in st.session_state and st.session_state["selected_goal"] == "Perform exploratory data analysis (EDA)":
            st.error("Issues detected in the dataset. EDA requires a clean dataset.")
            st.info("Please return to the goal selection and choose 'Clean the dataset' to resolve these issues.")
            st.session_state["redirect_to_cleaning"] = True
        else:
            st.error("Issues detected in the dataset. Please resolve them before proceeding.")
    else:
        st.success("No issues detected in the dataset. Ready to proceed.")

# EDA Workflow
def eda_workflow():
    """Perform Exploratory Data Analysis."""
    st.header("Exploratory Data Analysis (EDA)")

    # Ensure a dataset is loaded
    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload and clean the dataset before proceeding with EDA.")
        return

    dataset = st.session_state["dataset"]

    # Trigger EDA functionalities only if dataset is clean
    st.info("Your dataset is clean. You can now perform EDA.")

    if st.button("Show Summary Statistics"):
        st.subheader("Summary Statistics")
        st.dataframe(dataset.describe(include="all").transpose())

    st.subheader("Data Visualizations")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            column_to_plot = st.selectbox(
                "Select column for Histogram:",
                options=dataset.columns,
                help="Choose a column to plot its histogram."
            )
            if st.button("Generate Histogram"):
                st.bar_chart(dataset[column_to_plot].dropna())

        with col2:
            x_axis = st.selectbox("Select X-axis for Scatter Plot:", options=dataset.columns)
            y_axis = st.selectbox("Select Y-axis for Scatter Plot:", options=dataset.columns)
            if st.button("Generate Scatter Plot"):
                st.altair_chart(
                    alt.Chart(dataset).mark_circle().encode(
                        x=x_axis, y=y_axis
                    ).interactive(),
                    use_container_width=True
                )

    st.subheader("Correlation Matrix")
    if st.checkbox("Show Correlation Matrix"):
        try:
            corr_matrix = dataset.corr(numeric_only=True)
            if corr_matrix.empty:
                st.warning("Correlation matrix is empty. Please check your data.")
            else:
                st.dataframe(corr_matrix)
                st.write("Heatmap:")
                corr_matrix = corr_matrix.fillna(0)
                fig = sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
                st.pyplot(fig.figure)
        except Exception as e:
            st.error(f"An error occurred while generating the heatmap: {e}")

# Data Cleaning Workflow
def data_cleaning_workflow():
    st.header("Data Cleaning")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload a dataset to start cleaning.")
        return

    dataset = st.session_state["dataset"]

    st.subheader("Handle Missing Value Placeholders")
    placeholders = st.text_input(
        "Enter placeholder values to treat as missing (comma-separated):",
        value="None,null,NA",
        key="missing_placeholder_key_cleaning",
        help="Provide a list of placeholders (e.g., None, null, NA) to convert to missing values (NaN)."
    )
    if st.button("Apply Placeholder Replacement", key="apply_placeholder_key_cleaning"):
        placeholder_list = [x.strip() for x in placeholders.split(",")]
        dataset.replace(placeholder_list, pd.NA, inplace=True)
        st.session_state["dataset"] = dataset
        st.success(f"Replaced placeholders {placeholder_list} with NaN.")

        # Ask user what to do with NaN values
        st.subheader("Handle Missing Values")
        for col in dataset.columns:
            if dataset[col].isnull().any():
                col_type = dataset[col].dtype
                if pd.api.types.is_numeric_dtype(col_type):
                    action = st.selectbox(
                        f"How should missing values in '{col}' be handled?",
                        ["Fill with Random Values", "Fill with Mean", "Leave as NaN"],
                        key=f"missing_action_{col}"
                    )
                    if action == "Fill with Random Values":
                        col_min, col_max = dataset[col].min(), dataset[col].max()
                        dataset[col].fillna(pd.Series([col_min, col_max]).sample(1).values[0], inplace=True)
                    elif action == "Fill with Mean":
                        dataset[col].fillna(dataset[col].mean(), inplace=True)
                else:
                    action = st.selectbox(
                        f"How should missing values in '{col}' (non-numerical) be handled?",
                        ["Fill with 'Missing'", "Leave as NaN"],
                        key=f"missing_action_{col}"
                    )
                    if action == "Fill with 'Missing'":
                        dataset[col].fillna("Missing", inplace=True)

        st.session_state["dataset"] = dataset
        st.success("Missing value handling applied successfully.")

    st.subheader("Handle Non-Numeric Values in Numeric Columns")
    for col in dataset.select_dtypes(include="number").columns:
        if dataset[col].dtype != float and dataset[col].dtype != int:
            action = st.selectbox(
                f"Non-numeric values detected in numeric column '{col}'. How should they be handled?",
                ["Convert to NaN", "Drop Rows", "Replace with 0"],
                key=f"non_numeric_action_{col}"
            )
            if st.button(f"Apply for {col}", key=f"apply_non_numeric_{col}"):
                if action == "Convert to NaN":
                    dataset[col] = pd.to_numeric(dataset[col], errors="coerce")
                elif action == "Drop Rows":
                    dataset = dataset[pd.to_numeric(dataset[col], errors="coerce").notnull()]
                elif action == "Replace with 0":
                    dataset[col] = pd.to_numeric(dataset[col], errors="coerce").fillna(0)

    st.session_state["dataset"] = dataset
    st.success("Non-numeric value handling applied successfully.")

    st.subheader("Handle Duplicates")
    columns_for_duplicates = st.multiselect(
        "Select columns to check for duplicates (leave blank to check all):",
        options=dataset.columns,
        help="Choose specific columns to identify duplicate rows."
    )
    if st.button("Remove Duplicates"):
        before = len(dataset)
        if columns_for_duplicates:
            dataset = dataset.drop_duplicates(subset=columns_for_duplicates)
        else:
            dataset = dataset.drop_duplicates()
        st.session_state["dataset"] = dataset
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head(10))  # Limited to first 10 rows

    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

# Main App Logic
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

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
        st.dataframe(st.session_state["dataset"].head(10))  # Limited to first 10 rows

    # Dataset Precheck
    dataset_precheck()

# Tabs for Workflow Navigation
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