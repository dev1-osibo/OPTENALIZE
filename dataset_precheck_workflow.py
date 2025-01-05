import streamlit as st

def dataset_precheck_workflow(dataset):
    """
    Scans the uploaded dataset for inconsistencies and issues.
    """
    st.subheader("Dataset Pre-check")

    issues_detected = False

    # Detect missing values
    missing_summary = dataset.isnull().sum()
    total_missing_cells = missing_summary.sum()
    missing_columns = missing_summary[missing_summary > 0].index.tolist()

    if total_missing_cells > 0:
        issues_detected = True
        st.warning(f"Missing values found in {len(missing_columns)} columns, affecting {total_missing_cells} cells.")
        with st.expander("View Missing Value Details"):
            st.dataframe(missing_summary[missing_summary > 0])

    # Detect mixed types
    mixed_columns = []
    for col in dataset.columns:
        unique_types = dataset[col].apply(type).nunique()
        if unique_types > 1:
            mixed_columns.append(col)

    if mixed_columns:
        issues_detected = True
        st.warning(f"Mixed types detected in {len(mixed_columns)} columns.")
        with st.expander("View Mixed Type Columns"):
            st.write(mixed_columns)

    # Check for duplicate rows
    duplicate_count = dataset.duplicated().sum()
    if duplicate_count > 0:
        issues_detected = True
        st.warning(f"Your dataset contains {duplicate_count} duplicate rows.")

    # Final Summary
    if issues_detected:
        st.error("Issues detected in the dataset. Please resolve them before proceeding.")
        return False
    else:
        st.success("No issues detected. Your dataset is ready for analysis!")
        return True