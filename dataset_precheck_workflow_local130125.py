import pandas as pd
import streamlit as st

# Initialize session state for action log
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []

# Function to handle precheck
def run_precheck(dataset):
    """
    Performs dataset precheck and displays issues.
    """
    st.subheader("Dataset Pre-check")
    issue_summary = {
        "Blank Cells": dataset.isnull().sum().sum(),
        "Whitespace Issues": sum(
            dataset[col].astype(str).str.contains(r"^\s|\s$", na=False).sum()
            for col in dataset.columns
        ),
        "Numeric in Non-Numeric Columns": sum(
            dataset[col].apply(lambda x: isinstance(x, (int, float))).sum()
            for col in dataset.select_dtypes(exclude=["number"]).columns
        ),
        "Non-Numeric in Numeric Columns": sum(
            dataset[col].apply(lambda x: not isinstance(x, (int, float)) and pd.notnull(x)).sum()
            for col in dataset.select_dtypes(include=["number"]).columns
        )
    }

    # Display issues summary
    if any(issue_summary.values()):
        for issue, count in issue_summary.items():
            if count > 0:
                st.warning(f"{issue}: {count} affected cells.")
        if st.checkbox("View detailed issues"):
            st.write("Detailed Issue Breakdown:")
            for col in dataset.columns:
                if dataset[col].isnull().any():
                    st.write(f"Blank Cells in {col}: {dataset[col].isnull().sum()}")
                if dataset[col].astype(str).str.contains(r"^\s|\s$", na=False).any():
                    st.write(f"Whitespace Issues in {col}")
                if dataset[col].apply(lambda x: isinstance(x, (int, float))).any():
                    st.write(f"Numeric in Non-Numeric Column {col}")
                if dataset[col].apply(lambda x: not isinstance(x, (int, float)) and pd.notnull(x)).any():
                    st.write(f"Non-Numeric in Numeric Column {col}")
    else:
        st.success("No issues detected in the dataset.")

# Function to handle cleaning
def run_cleaning_workflow(dataset):
    """
    Handles dataset cleaning based on user-selected options.
    """
    st.subheader("Dataset Cleaning Workflow")

    # Horizontal checkboxes for cleaning options
    cleaning_actions = {
        "Handle Blank Cells": False,
        "Fix Whitespace Issues": False,
        "Fix Numeric in Non-Numeric Columns": False,
        "Fix Non-Numeric in Numeric Columns": False,
        "Validate and Fix Date/Year Columns": False,
    }

    selected_options = []
    cols = st.columns(len(cleaning_actions))
    for i, action in enumerate(cleaning_actions):
        cleaning_actions[action] = cols[i].checkbox(action)
        if cleaning_actions[action]:
            selected_options.append(action)

    # Action log
    st.subheader("Action Log")
    st.write("Actions taken:", st.session_state["action_log"])

    # Handle blank cells
    if "Handle Blank Cells" in selected_options:
        st.write("How would you like to handle blank cells?")
        blank_options = st.radio(
            "Select an option:",
            ["Fill with Random Values", "Fill with Mean/Average", "Leave as NaN"],
            horizontal=True,
            key="blank_options"
        )
        if st.button("Execute Cleaning for Blank Cells"):
            if blank_options == "Fill with Random Values":
                for col in dataset.columns:
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        col_min, col_max = dataset[col].min(), dataset[col].max()
                        dataset[col].fillna(
                            pd.Series([col_min, col_max]).sample(1).values[0],
                            inplace=True
                        )
                st.session_state["action_log"].append("Blank cells filled with random values.")
            elif blank_options == "Fill with Mean/Average":
                for col in dataset.columns:
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        dataset[col].fillna(dataset[col].mean(), inplace=True)
                st.session_state["action_log"].append("Blank cells filled with mean/average.")
            elif blank_options == "Leave as NaN":
                st.session_state["action_log"].append("Blank cells left as NaN.")
            st.success("Blank cells handled successfully!")

    # Handle whitespace issues
    if "Fix Whitespace Issues" in selected_options:
        st.write("How would you like to handle whitespace issues?")
        whitespace_options = st.radio(
            "Select an option:",
            ["Trim Whitespaces", "Remove Rows with Whitespaces"],
            horizontal=True,
            key="whitespace_options"
        )
        if st.button("Execute Cleaning for Whitespace Issues"):
            if whitespace_options == "Trim Whitespaces":
                for col in dataset.columns:
                    dataset[col] = dataset[col].astype(str).str.strip()
                st.session_state["action_log"].append("Whitespaces trimmed.")
            elif whitespace_options == "Remove Rows with Whitespaces":
                for col in dataset.columns:
                    dataset = dataset[
                        ~dataset[col].astype(str).str.contains(r"^\s|\s$", na=False)
                    ]
                st.session_state["action_log"].append("Rows with whitespaces removed.")
            st.success("Whitespace issues handled successfully!")

    # Handle numeric in non-numeric columns
    if "Fix Numeric in Non-Numeric Columns" in selected_options:
        st.write("Handling Numeric in Non-Numeric Columns:")
        if st.button("Execute Cleaning for Numeric in Non-Numeric"):
            for col in dataset.select_dtypes(exclude=["number"]).columns:
                dataset[col] = dataset[col].apply(lambda x: "N/A" if isinstance(x, (int, float)) else x)
            st.session_state["action_log"].append("Numeric values in non-numeric columns replaced with 'N/A'.")
            st.success("Numeric values in non-numeric columns handled successfully!")

    # Handle non-numeric in numeric columns
    if "Fix Non-Numeric in Numeric Columns" in selected_options:
        st.write("Handling Non-Numeric in Numeric Columns:")
        if st.button("Execute Cleaning for Non-Numeric in Numeric"):
            for col in dataset.select_dtypes(include=["number"]).columns:
                dataset[col] = pd.to_numeric(dataset[col], errors='coerce')
            st.session_state["action_log"].append("Non-numeric values in numeric columns converted to NaN.")
            st.success("Non-numeric values in numeric columns handled successfully!")

    # Validate and fix date/year columns
    if "Validate and Fix Date/Year Columns" in selected_options:
        st.write("Validating and Fixing Date/Year Columns:")
        date_options = st.radio(
            "Choose a date format to validate:",
            ["%Y-%m-%d", "%Y/%m/%d", "Custom"],
            horizontal=True,
            key="date_options"
        )
        if date_options == "Custom":
            custom_format = st.text_input("Enter custom date format (e.g., '%d-%m-%Y'):")
        if st.button("Execute Cleaning for Date/Year Columns"):
            for col in dataset.columns:
                if "date" in col.lower() or "year" in col.lower():
                    try:
                        if date_options == "Custom" and custom_format:
                            dataset[col] = pd.to_datetime(dataset[col], format=custom_format, errors="coerce")
                        else:
                            dataset[col] = pd.to_datetime(dataset[col], format=date_options, errors="coerce")
                        st.session_state["action_log"].append(f"Validated and fixed date/year column: {col}.")
                    except Exception as e:
                        st.error(f"Error fixing {col}: {e}")

    # Preview cleaned dataset
    st.subheader("Preview Cleaned Dataset")
    st.dataframe(dataset.head(10))

    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

# Simulate dataset upload
st.title("Dataset Pre-check and Cleaning Workflow")

uploaded_file = st.file_uploader("Upload your file (CSV or Excel):", type=["csv", "xlsx"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        dataset = pd.read_csv(uploaded_file)
    elif file_type == "xlsx":
        dataset = pd.read_excel(uploaded_file)

    # Checkbox to preview dataset
    if st.checkbox("Preview dataset"):
        st.dataframe(dataset.head(10))

    # Run precheck
    run_precheck(dataset)

    # Run cleaning workflow
    run_cleaning_workflow(dataset)
else:
    st.warning("Upload a dataset to start the workflow.")