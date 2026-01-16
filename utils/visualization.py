import matplotlib.pyplot as plt
import streamlit as st

def visualize_missing(df):
    fig, ax = plt.subplots()
    df.isnull().sum().plot(kind="bar", ax=ax)
    ax.set_title("Missing Values by Column")
    st.pyplot(fig)

def visualize_distributions(df):
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        fig, ax = plt.subplots()
        df[col].plot(kind="hist", ax=ax)
        ax.set_title(f"Distribution of {col}")
        st.pyplot(fig)

def visualize_grouped(df, group_col, value_col):
    fig, ax = plt.subplots()
    df.groupby(group_col)[value_col].mean().plot(kind="bar", ax=ax)
    ax.set_title(f"Average {value_col} by {group_col}")
    st.pyplot(fig)
