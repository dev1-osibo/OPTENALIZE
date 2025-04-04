import pandas as pd
import streamlit as st

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
    else:
        st.success("No issues detected in the dataset.")

# Function to handle cleaning
def run_cleaning_workflow(dataset):
    """
    Handles dataset cleaning based on user-selected options.
    """
    st.subheader("Dataset Cleaning Workflow")

    # Horizontal checkboxes for cleaning options
    options = ["Handle Blank Cells", "Fix Whitespace Issues", "Fix Numeric in Non-Numeric Columns",
               "Fix Non-Numeric in Numeric Columns", "Validate and Fix Date/Year Columns"]
    columns = st.columns(len(options))

    selected_options = []
    for col, option in zip(columns, options):
        if col.checkbox(option):
            selected_options.append(option)

    if "Handle Blank Cells" in selected_options:
        st.write("Handle Blank Cells:")
        sub_columns = st.columns(3)
        with sub_columns[0]:
            fill_random = st.radio("Fill with Random Values", ["Off", "On"], horizontal=True)
        with sub_columns[1]:
            fill_mean = st.radio("Fill with Mean/Average", ["Off", "On"], horizontal=True)
        with sub_columns[2]:
            leave_na = st.radio("Leave as NaN", ["Off", "On"], horizontal=True)
        if st.button("Execute Cleaning for Blank Cells"):
            if fill_random == "On":
                for col in dataset.columns:
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        col_min, col_max = dataset[col].min(), dataset[col].max()
                        dataset[col] = dataset[col].fillna(
                            pd.Series([col_min, col_max]).sample(1).values[0]
                        )
                st.success("Blank cells filled with random values successfully!")
            elif fill_mean == "On":
                for col in dataset.columns:
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        dataset[col] = dataset[col].fillna(dataset[col].mean())
                st.success("Blank cells filled with mean/average successfully!")
            elif leave_na == "On":
                st.success("Blank cells left as NaN successfully!")

    if "Fix Whitespace Issues" in selected_options:
        st.write("Handle Whitespace Issues:")
        whitespace_trim = st.radio("Trim Whitespaces", ["Off", "On"], horizontal=True)
        whitespace_remove = st.radio("Remove Rows with Whitespaces", ["Off", "On"], horizontal=True)
        if st.button("Execute Cleaning for Whitespace Issues"):
            if whitespace_trim == "On":
                for col in dataset.columns:
                    dataset[col] = dataset[col].astype(str).str.strip()
                st.success("Whitespaces trimmed successfully!")
            elif whitespace_remove == "On":
                for col in dataset.columns:
                    dataset = dataset[
                        ~dataset[col].astype(str).str.contains(r"^\s|\s$", na=False)
                    ]
                st.success("Rows with whitespaces removed successfully!")

    # Additional cleaning options for numeric/non-numeric and date/year can be added here similarly.

    # Final dataset preview and download
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