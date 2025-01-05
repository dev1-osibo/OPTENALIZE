import streamlit as st

def dataset_precheck_workflow(dataset):
    """
    Performs a quick scan of the uploaded dataset for common issues
    and provides user choices for resolution.
    """
    st.subheader("Dataset Pre-check")
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

    # Return result
    return issues_detected