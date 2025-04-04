import streamlit as st
import pandas as pd
import seaborn as sns
import altair as alt

# Dataset Pre-check Functionality
def dataset_precheck_workflow(dataset):
    """
    Performs a quick scan of the uploaded dataset for common issues
    and provides user choices for resolution.
    """
    st.subheader("Dataset Pre-check")

    issues_detected = False

    # Check for missing values
    missing_summary = dataset.isnull().sum()
    total_missing_cells = missing_summary.sum()
    if total_missing_cells > 0:
        issues_detected = True
        st.warning(f"Your dataset contains {missing_summary[missing_summary > 0].count()} columns with {total_missing_cells} missing cells.")
        if st.checkbox("Show missing values details"):
            st.dataframe(missing_summary[missing_summary > 0])

    # Check for mixed or inconsistent data types
    inconsistent_columns = []
    for col in dataset.columns:
        if not pd.api.types.is_numeric_dtype(dataset[col]) and dataset[col].str.isnumeric().any():
            inconsistent_columns.append(col)
    if inconsistent_columns:
        issues_detected = True
        st.warning(f"{len(inconsistent_columns)} columns contain mixed or inconsistent types.")
        if st.checkbox("Show inconsistent columns"):
            st.write(inconsistent_columns)

    # Check for duplicate rows
    duplicate_count = dataset.duplicated().sum()
    if duplicate_count > 0:
        issues_detected = True
        st.warning(f"Your dataset contains {duplicate_count} duplicate rows.")

    # Outcome summary
    if not issues_detected:
        st.success("No issues detected in the dataset. Ready to proceed.")