import streamlit as st
from components.main_body import main_content
from components.tax_sidebar import tax_tables
st.set_page_config(layout="wide")

if 'filing_choice' not in st.session_state:
    st.session_state.filing_choice = 'Single'
if 'residing_state' not in st.session_state:
    st.session_state.residing_state = 'California'

if 'state_tax_total' not in st.session_state:
    st.session_state.state_tax_total = 0.0


income_tax, gain_tax, state_tax, filing_choice, residing_state = main_content()
tax_tables(income_tax, gain_tax, state_tax, filing_choice, residing_state)

