import joblib
import pandas as pd
import streamlit as st


@st.cache_resource
def load_resources():
    model = joblib.load("best_rf_model.pkl")
    df_ref = pd.read_csv("client_counselor_dataset.csv")

    return model, df_ref
