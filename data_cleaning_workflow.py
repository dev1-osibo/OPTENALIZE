# Data Cleaning Workflow
def data_cleaning_workflow(dataset):
    """
    Perform data cleaning operations.
    """
    st.header("Data Cleaning")

    # Handle Missing Value Placeholders
    st.subheader("Handle Missing Value Placeholders")
    placeholder_options = ["None", "null", "NA", "N/A", "-"]
    selected_placeholders = st.multiselect(
        "Select placeholder values to treat as missing:", placeholder_options, default=placeholder_options
    )
    with st.spinner("Replacing placeholder values..."):
        for placeholder in selected_placeholders:
            dataset.replace(placeholder, pd.NA, inplace=True)
        st.session_state["dataset"] = dataset
    st.success("Placeholder values replaced successfully.")

    # Handle Missing Values
    st.subheader("Handle Missing Values")
    if dataset.isnull().any().any():
        handling_option = st.radio(
            "Select how to handle missing values:",
            ["Fill with Random Values", "Fill with Mean (numerical only)", "Leave as NaN", "Drop Rows"]
        )
        with st.spinner("Handling missing values..."):
            for col in dataset.columns:
                if dataset[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(dataset[col]):
                        if handling_option == "Fill with Random Values":
                            col_min, col_max = dataset[col].min(), dataset[col].max()
                            dataset[col].fillna(pd.Series([col_min, col_max]).sample(1).values[0], inplace=True)
                        elif handling_option == "Fill with Mean (numerical only)":
                            dataset[col].fillna(dataset[col].mean(), inplace=True)
                        elif handling_option == "Drop Rows":
                            dataset.dropna(subset=[col], inplace=True)
                    else:
                        if handling_option == "Drop Rows":
                            dataset.dropna(subset=[col], inplace=True)
    st.success("Missing value handling completed.")

    # Handle Duplicates
    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        with st.spinner("Removing duplicate rows..."):
            before = len(dataset)
            dataset.drop_duplicates(inplace=True)
            after = len(dataset)
            st.session_state["dataset"] = dataset
        st.success(f"Removed {before - after} duplicate rows.")

    # Preview Cleaned Dataset
    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head(10))  # Limited to first 10 rows

    # Download Cleaned Dataset
    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )