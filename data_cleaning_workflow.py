import pandas as pd
import streamlit as st

def data_cleaning_workflow(dataset):
    """
    Implements the data cleaning workflow, including handling missing values and duplicates.
    """
    st.header("Data Cleaning")

    # Handle Missing Values
    st.subheader("Handle Missing Values")
    missing_columns = dataset.columns[dataset.isnull().any()].tolist()
    total_missing_cells = dataset.isnull().sum().sum()

    if total_missing_cells > 0:
        st.warning(f"Missing values detected in {len(missing_columns)} columns, affecting {total_missing_cells} cells.")
        handling_option = st.radio(
            "Choose how to handle missing values:",
            ["Fill with Random Values", "Fill with Mean", "Leave as NaN"]
        )

        if st.button("Apply Missing Value Handling"):
            with st.spinner("Applying missing value handling..."):
                for col in missing_columns:
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        if handling_option == "Fill with Random Values":
                            col_min, col_max = dataset[col].min(), dataset[col].max()
                            dataset[col].fillna(
                                pd.Series([col_min, col_max]).sample(1).values[0], inplace=True
                            )
                        elif handling_option == "Fill with Mean":
                            dataset[col].fillna(dataset[col].mean(), inplace=True)
                    else:
                        if handling_option == "Fill with Random Values":
                            dataset[col].fillna("Missing", inplace=True)

                st.session_state["dataset"] = dataset
                st.success("Missing value handling completed successfully!")

    # Handle Duplicates
    st.subheader("Handle Duplicates")
    duplicate_count = dataset.duplicated().sum()
    if duplicate_count > 0:
        st.warning(f"{duplicate_count} duplicate rows detected.")
        if st.button("Remove Duplicates"):
            with st.spinner("Removing duplicates..."):
                dataset = dataset.drop_duplicates()
                st.session_state["dataset"] = dataset
                st.success(f"Removed {duplicate_count} duplicate rows.")

    # Preview Cleaned Dataset
    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head(10))

    # Download Cleaned Dataset
    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )