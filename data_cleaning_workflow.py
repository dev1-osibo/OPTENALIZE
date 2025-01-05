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
        if total_missing > 0:
            st.warning(f"Your dataset contains {total_missing} missing values.")
            st.dataframe(missing_summary.rename("Missing Values"))

            action = st.radio(
                "Select an action to handle missing values:",
                ["Fill with Mean", "Fill with Random Values", "Drop Rows"]
            )
            if st.button("Apply Missing Value Handling"):
                with st.spinner("Applying changes..."):
                    for col in dataset.columns:
                        if dataset[col].isnull().any():
                            if action == "Fill with Mean":
                                dataset[col].fillna(dataset[col].mean(), inplace=True)
                            elif action == "Fill with Random Values":
                                col_min, col_max = dataset[col].min(), dataset[col].max()
                                dataset[col].fillna(pd.Series([col_min, col_max]).sample(1).values[0], inplace=True)
                            elif action == "Drop Rows":
                                dataset.dropna(subset=[col], inplace=True)
                    st.success("Missing value handling applied successfully.")

    # Handle Duplicates
    st.subheader("Handle Duplicates")
    with st.spinner("Checking for duplicates..."):
        duplicate_count = dataset.duplicated().sum()
        if duplicate_count > 0:
            st.warning(f"Your dataset contains {duplicate_count} duplicate rows.")
            if st.button("Remove Duplicates"):
                with st.spinner("Removing duplicates..."):
                    dataset.drop_duplicates(inplace=True)
                    st.success(f"Removed {duplicate_count} duplicate rows.")

    st.session_state["dataset"] = dataset