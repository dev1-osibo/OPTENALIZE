import streamlit as st
import pandas as pd

def data_cleaning_workflow():
    st.header("Data Cleaning")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload a dataset to start cleaning.")
        return

    dataset = st.session_state["dataset"]

    st.subheader("Missing Values Summary")
    with st.expander("View Missing Values Summary"):
        missing_summary = dataset.isnull().sum().sort_values(ascending=False)
        missing_percentage = (missing_summary / len(dataset)) * 100
        st.write(pd.DataFrame({"Missing Values": missing_summary, "Percentage": missing_percentage}))

    st.subheader("Advanced Missing Value Handling")
    essential_columns = st.multiselect(
        "Select essential columns:", options=dataset.columns, help="Columns critical for analysis.")

    if essential_columns:
        st.write("How would you like to handle rows with missing values in essential columns?")
        col1, col2 = st.columns(2)
        with col1:
            missing_value_action = st.radio(
                "Action:",
                options=["Impute with column mean", "Impute with random values", "Delete rows"]
            )

        if st.button("Apply Missing Values Action"):
            if missing_value_action == "Impute with column mean":
                dataset[essential_columns] = dataset[essential_columns].fillna(dataset[essential_columns].mean())
                st.success("Imputed missing values with column means.")
            elif missing_value_action == "Impute with random values":
                for col in essential_columns:
                    col_min, col_max = dataset[col].min(), dataset[col].max()
                    dataset[col] = dataset[col].apply(
                        lambda x: pd.Series([col_min, col_max]).sample(1).values[0] if pd.isnull(x) else x
                    )
                st.success("Imputed missing values with random values.")
            elif missing_value_action == "Delete rows":
                dataset = dataset.dropna(subset=essential_columns)
                st.success("Dropped rows with missing values.")

            st.session_state["dataset"] = dataset

    st.subheader("Drop Columns with High Missing Values")
    col3, col4 = st.columns(2)
    with col3:
        missing_threshold = st.number_input(
            "Set missing values threshold (%):",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="Drop columns exceeding this threshold."
        )

    if st.button("Apply Missing Value Threshold"):
        cols_to_drop = missing_percentage[missing_percentage > missing_threshold].index
        cols_to_warn = [col for col in essential_columns if col in cols_to_drop]

        if cols_to_warn:
            st.warning(f"Essential columns not dropped: {cols_to_warn}")
            cols_to_drop = [col for col in cols_to_drop if col not in essential_columns]

        dataset = dataset.drop(columns=cols_to_drop)
        st.session_state["dataset"] = dataset

        if len(cols_to_drop) > 0:
            with st.expander("View dropped columns"):
                st.write(list(cols_to_drop))
            st.success(f"Dropped {len(cols_to_drop)} columns.")
        else:
            st.info("No columns were dropped.")

    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        before = len(dataset)
        dataset = dataset.drop_duplicates()
        st.session_state["dataset"] = dataset
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

    st.subheader("Standardize Column Names")
    if st.button("Standardize Columns"):
        dataset.columns = dataset.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("[^a-zA-Z0-9_]", "")
        st.session_state["dataset"] = dataset
        st.success("Standardized column names.")

    st.subheader("Preview Cleaned Dataset")
    if st.checkbox("Show Cleaned Dataset"):
        st.dataframe(dataset.head())

    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>Welcome to Optenalize</h1>
        <h3>Your One-Stop Tool for Data Cleaning, Forecasting, and Machine Learning Insights</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

st.subheader("What would you like to do today?")
selected_goal = st.selectbox(
    "Select your goal:",
    [
        "Clean the dataset",
        "Perform exploratory data analysis (EDA)",
        "Train a predictive model",
        "Perform general ML tasks",
        "Other (specify custom goal)"
    ]
)
st.session_state["selected_goal"] = selected_goal

st.subheader("Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        st.session_state["dataset"] = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        st.session_state["dataset"] = pd.read_excel(uploaded_file)
    elif file_type == "json":
        st.session_state["dataset"] = pd.read_json(uploaded_file)

    if st.checkbox("Preview the dataset"):
        st.dataframe(st.session_state["dataset"].head())

if st.session_state["selected_goal"] == "Clean the dataset":
    data_cleaning_workflow()
elif st.session_state["selected_goal"] == "Perform exploratory data analysis (EDA)":
    st.info("EDA workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Train a predictive model":
    st.info("Predictive modeling workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Perform general ML tasks":
    st.info("General ML workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Other (specify custom goal)":
    st.info("Custom workflow will be implemented next.")
