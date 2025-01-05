import streamlit as st
import pandas as pd

def data_cleaning_workflow(dataset):
    st.header("Data Cleaning")

    st.subheader("Handle Missing Value Placeholders")
    placeholders = st.text_input(
        "Enter placeholder values to treat as missing (comma-separated):",
        value="None,null,NA",
        key="missing_placeholder_key_cleaning"
    )
    if st.button("Apply Placeholder Replacement", key="apply_placeholder_key_cleaning"):
        placeholder_list = [x.strip() for x in placeholders.split(",")]
        dataset.replace(placeholder_list, pd.NA, inplace=True)
        st.success(f"Replaced placeholders {placeholder_list} with NaN.")

    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        before = len(dataset)
        dataset = dataset.drop_duplicates()
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head(10))  # Limit to first 10 rows

    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

    return dataset