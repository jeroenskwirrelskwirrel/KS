import streamlit as st
import requests
import json

st.title("ETIM Prediction Interface")

# Input fields
description = st.text_area("Description", height=100)
top_k = st.number_input("Top K", min_value=1, value=10)
temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
s3_prefix = st.text_input("S3 Prefix", value="71")

# When the user clicks the button
if st.button("Predict ETIM"):
    payload = {
        "description": description,
        "top_k": top_k,
        "temperature": temperature,
        "s3_prefix": s3_prefix
    }

    try:
        response = requests.post(
            "http://79.116.198.30:12030/predict_etim",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 200:
            st.success("Prediction received!")
            st.json(response.json())
        else:
            st.error(f"Error: {response.status_code}\n{response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")

