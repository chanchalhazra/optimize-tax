import pandas as pd

def download_data():
    # Sample data
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "San Francisco", "Los Angeles"]
    })

    # Show the table
    #st.write("#### Save Data")
    #st.write("Save Data")
    #st.dataframe(df)

    # Convert DataFrame to CSV
    csv = df.to_csv(index=False).encode("utf-8")

    # Download button
    st.download_button(
        label="📥 **Save Input data for future**",
        data=csv,
        file_name="sample_data.csv",
        mime="text/csv"
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
    if st.button("📤 **Click to Upload input File**"):
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "json", "xlsx"])

        if uploaded_file:
            st.success(f"Uploaded file: {uploaded_file.name}")