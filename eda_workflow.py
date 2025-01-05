import streamlit as st
import seaborn as sns
import altair as alt

def eda_workflow(dataset):
    st.header("Exploratory Data Analysis (EDA)")

    if dataset is None:
        st.warning("Please upload a dataset before proceeding.")
        return

    st.subheader("Summary Statistics")
    if st.button("Show Summary Statistics"):
        st.dataframe(dataset.describe(include="all").transpose())

    st.subheader("Data Visualizations")
    col1, col2 = st.columns(2)

    with col1:
        column_to_plot = st.selectbox("Select column for Histogram:", options=dataset.columns)
        if st.button("Generate Histogram"):
            st.bar_chart(dataset[column_to_plot])

    with col2:
        x_axis = st.selectbox("Select X-axis for Scatter Plot:", options=dataset.columns)
        y_axis = st.selectbox("Select Y-axis for Scatter Plot:", options=dataset.columns)
        if st.button("Generate Scatter Plot"):
            st.altair_chart(
                alt.Chart(dataset).mark_circle().encode(
                    x=x_axis, y=y_axis
                ).interactive(), use_container_width=True
            )

    st.subheader("Correlation Matrix")
    if st.checkbox("Show Correlation Matrix"):
        corr_matrix = dataset.corr()
        st.dataframe(corr_matrix)
        fig = sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
        st.pyplot(fig.figure)