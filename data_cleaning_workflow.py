import streamlit as st
import pandas as pd

def data_cleaning_workflow(dataset):
    st.header("Data Cleaning")

    if dataset is None:
        st.warning("Please upload a dataset to start cleaning.")
        return

    # Handle Missing Values
    st.subheader("Handle Missing Values")
    with st.spinner("Analyzing missing values..."):
        missing_summary = dataset.isnull().sum()
        total_missing = missing_summary.sum()
        affected_columns = missing_summary[missing_summary > 0].count()

        if total_missing > 0:
            st.warning(f"Your dataset contains {total_missing} missing values in {affected_columns} columns.")
            if st.checkbox("View details of missing values"):
                st.dataframe(missing_summary[missing_summary > 0].rename("Missing Values"))

            action = st.radio(
                "Select an action to handle missing values:",
                ["Fill with Mean", "Fill with Random Values", "Drop Rows"]
            )
            if st.button("Apply Missing Value Handling"):
                with st.spinner("Applying changes..."):
                    for col in missing_summary[missing_summary > 0].index:
                        if pd.api.types.is_numeric_dtype(dataset[col]):
                            if action == "Fill with Mean":
                                dataset[col].fillna(dataset[col].mean(), inplace=True)
                            elif action == "Fill with Random Values":
                                col_min, col_max = dataset[col].min(), dataset[col].max()
                                dataset[col].fillna(pd.Series([col_min, col_max]).sample(1).values[0], inplace=True)
                            elif action == "Drop Rows":
                                dataset.dropna(subset=[col], inplace=True)
                        else:
                            st.warning(f"Column '{col}' is non-numeric and cannot be handled with the selected option.")
                    st.success("Missing value handling applied successfully.")

    # Handle Non-Numeric Values in Numeric Columns
    st.subheader("Handle Non-Numeric Values in Numeric Columns")
    non_numeric_in_numeric_cols = []
    for col in dataset.columns:
        if pd.api.types.is_numeric_dtype(dataset[col]):
            non_numeric = dataset[col][~dataset[col].apply(lambda x: isinstance(x, (int, float, type(None))))]
            if not non_numeric.empty:
                non_numeric_in_numeric_cols.append(col)

    if non_numeric_in_numeric_cols:
        st.warning(f"Non-numeric values detected in {len(non_numeric_in_numeric_cols)} numeric columns.")
        if st.checkbox("View details of non-numeric values"):
            for col in non_numeric_in_numeric_cols:
                st.write(f"Non-numeric values in '{col}':")
                st.write(dataset[col][~dataset[col].apply(lambda x: isinstance(x, (int, float, type(None))))])

        action = st.radio(
            "How should non-numeric values in numeric columns be handled?",
            ["Convert to NaN", "Drop Rows", "Replace with 0"]
        )
        if st.button("Apply Non-Numeric Value Handling"):
            with st.spinner("Processing non-numeric values..."):
                for col in non_numeric_in_numeric_cols:
                    if action == "Convert to NaN":
                        dataset[col] = pd.to_numeric(dataset[col], errors="coerce")
                    elif action == "Drop Rows":
                        dataset = dataset[pd.to_numeric(dataset[col], errors="coerce").notnull()]
                    elif action == "Replace with 0":
                        dataset[col] = pd.to_numeric(dataset[col], errors="coerce").fillna(0)
                st.success("Non-numeric value handling applied successfully.")

    # Handle Duplicates
    st.subheader("Handle Duplicates")
    duplicate_count = dataset.duplicated().sum()
    if duplicate_count > 0:
        st.warning(f"Your dataset contains {duplicate_count} duplicate rows.")
        if st.button("Remove Duplicates"):
            with st.spinner("Removing duplicates..."):
                dataset.drop_duplicates(inplace=True)
                st.success(f"Removed {duplicate_count} duplicate rows.")

    # Update the session state with the cleaned dataset
    st.session_state["dataset"] = dataset

    # Display Cleaned Dataset
    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head(10))  # Show only the first 10 rows for preview

    # Allow Dataset Download
    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )