import math

import streamlit as st
import pandas as pd
from data.tax_rates import get_income_tax_rates, get_capital_gain_tax_rates
from data.state_taxrates import get_state_tax_rates
from utils.calculate_taxes import calculate_income_tax, calculate_gain_tax, calculate_state_tax

def tax_tables(income_tax, gain_tax, state_tax, filing_choice, residing_state):
    '''
    filing_choice = st.sidebar.radio("**Filing Taxes as**", ["Single", "Married", "Head"],
                                                      horizontal=True, key="filing_choice")
    states = {'California': 3.0, 'Florida': 0.0, 'Texas': 0.0, 'Oregon': 2.0, 'Arizona': 2.0}
    residing_state = st.sidebar.selectbox("Residing State", states.keys(), key="residing_state")'''
    income_tax_rate, standard_deduction, salt_cap = get_income_tax_rates(filing_as=st.session_state.filing_choice)
    capital_gain_tax_rate = get_capital_gain_tax_rates(st.session_state.filing_choice)
    st.sidebar.subheader("Federal Level")
    with st.sidebar.expander('**Income Tax Tables**', expanded=True):
        col1, col2, col3, col4 = st.columns([2,2,1,2])
        with col1:
            st.markdown(f"<span style='font-size:13px'><u>From $</u></span>", unsafe_allow_html=True)
            for i in range(income_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'><b>{income_tax_rate['from'][i]:,}</b></span>",
                            unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='font-size:13px'><u>To $</u></span>", unsafe_allow_html=True)
            for i in range(income_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'><b>{income_tax_rate['to'][i]:,}</b></span>",
                            unsafe_allow_html=True)

        with col3:
            st.markdown(f"<span style='font-size:13px'><u>%</u></span>", unsafe_allow_html=True)
            for i in range(income_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'><b>{income_tax_rate['rate'][i]:,}</b></span>",
                            unsafe_allow_html=True)
        with col4:
            st.markdown(f"<span style='font-size:13px'><u>Tax Amt</u></span>", unsafe_allow_html=True)
            #taxable_income = st.session_state.taxable_income

            #tax = calculate_income_tax(income_tax_rate,taxable_income)
            #tax_amt = 3000
            for i in range(len(income_tax)):
                st.markdown(f"<span style='font-size:12px'><b>{income_tax[i]}</b></span>", unsafe_allow_html=True)

        st.markdown(f"<span style='font-size:12px'><b>Total Income Tax : {sum(income_tax)}</b></span>", unsafe_allow_html=True)
    with st.sidebar.expander('**Capital Gain Tax Tables**', expanded=False):
        col1, col2, col3, col4 = st.columns([2,2,1,3])
        with col1:
            st.markdown(f"<span style='font-size:13px'><u>From $</u></span>", unsafe_allow_html=True)
            for i in range(capital_gain_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'>{capital_gain_tax_rate['from'][i]:,}</span>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<span style='font-size:13px'><u>To $</u></span>", unsafe_allow_html=True)
            for i in range(capital_gain_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'>{capital_gain_tax_rate['to'][i]:,}</span>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"<span style='font-size:13px'><u>%</u></span>", unsafe_allow_html=True)
            for i in range(capital_gain_tax_rate.shape[0]):
                st.markdown(f"<span style='font-size:12px'>{capital_gain_tax_rate['rate'][i]:,}</span>", unsafe_allow_html=True)

        with col4:
            st.markdown(f"<span style='font-size:13px'><u>Tax Amt</u></span>", unsafe_allow_html=True)
            for i in range(len(gain_tax)):
                st.markdown(f"<span style='font-size:12px'><b>{gain_tax[i]:,}</b></span>", unsafe_allow_html=True)

        st.markdown(f"<span style='font-size:12px'><b>Total Capital Gain Tax : {sum(gain_tax):,}</b></span>", unsafe_allow_html=True)
    st.sidebar.subheader(f"State Level: {residing_state}")
    if residing_state not in ['Florida','Texas']:
        state_tax_rate = get_state_tax_rates(state=residing_state, filing_as=filing_choice, )
        no_tax_rows = state_tax_rate.shape[0]
        with st.sidebar.expander('**State income Tax Tables**', expanded=False):
            col1, col2, col3, col4 = st.columns([2,2,1,2])
            with col1:
                st.markdown(f"<span style='font-size:13px'><u>From $</u></span>", unsafe_allow_html=True)
                for i in range(no_tax_rows):
                    st.markdown(f"<span style='font-size:12px'><b>{state_tax_rate['from'][i]:,}</b></span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span style='font-size:13px'><u>To $</u></span>", unsafe_allow_html=True)
                for i in range(no_tax_rows):
                    st.markdown(f"<span style='font-size:12px'><b>{state_tax_rate['to'][i]:,}</b></span>",
                                unsafe_allow_html=True)
            with col3:
                st.markdown(f"<span style='font-size:13px'><u>%</u></span>", unsafe_allow_html=True)
                for i in range(no_tax_rows):
                    st.markdown(f"<span style='font-size:12px'><b>{state_tax_rate['rate'][i]}</b></span>", unsafe_allow_html=True)

            with col4:
                st.markdown(f"<span style='font-size:13px'><u>Tax Amt</u></span>", unsafe_allow_html=True)
                #state_tax = calculate_state_tax(state_tax_rate, taxable_income)
                for i in range(len(state_tax)):
                    st.markdown(f"<span style='font-size:12px'><b>{state_tax[i]:,}</b></span>",
                                unsafe_allow_html=True)
            st.session_state.total_state_tax = sum(state_tax)
            st.markdown(f"<span style='font-size:12px'><b>Total State Income Tax :{st.session_state.total_state_tax:,}</b></span>",
                        unsafe_allow_html=True)
    else:
        st.sidebar.write(f"The state {residing_state} has not state income tax")

