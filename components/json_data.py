import streamlit as st
import pandas

def download_data(data_json):

    # Convert jsondatae to CSV


    # Download button
    st.download_button(
        label="📥 **Click here to save your input data for future use**",
        data=json_str,
        file_name="optimize_tax_inputs.json",
        mime="application/json"
    )

def upload_data():
    '''
    uploaded_file = st.file_uploader("📤 Upload data saved previously", type="csv",)

    # If a file is uploaded
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Show data
        st.dataframe(df)'''
    # Button to trigger upload
    if st.button("📤 **Click to upload your previously saved input data**"):
        uploaded_file = st.file_uploader("Choose a file", type=["csv"])
        # Load JSON and store in session state

    data = json.load(data2)
    for key, value in data.items():
        print(key, value)
        st.session_state[key] = value

upload_data()