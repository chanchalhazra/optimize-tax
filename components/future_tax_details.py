import streamlit as st
from utils.utilities import final_outcomes

def future_yearly_tables(df1, df2, df3, df4):

    with st.container():
        df = final_outcomes(df1, df2, df3, df4)
        cell1, cell2, cell3 = st.columns([1,6,1])
        with cell2:
            st.markdown(
                f"<p style='text-align: center;font-size:18px'><b>Portfolio Ending Balance & Detailed Table</b></p>",
                unsafe_allow_html=True)
            st.dataframe(df, use_container_width=False)

    with st.container():
        #st.markdown("#### Portfolio Detailed Table")
        tab1, tab2, tab3, tab4 = st.tabs(["Significantly Below Average Market", "Below Average Market Return",
                                          "Average Market Return", "Best Case Market Return"])
        with tab1:
            st.caption("In 90% of the simulations, results as good or better than the results shown.")
            st.dataframe(df1,use_container_width=True)
            #st.bar_chart(df1[["Ending Balance","Total Expense"]],use_container_width=True)

        with tab2:
            st.caption("In 75% of the simulations, results as good or better than the results shown.")
            st.dataframe(df2, use_container_width=True)
            #st.bar_chart(df2[["Ending Balance","Total Expense"]], use_container_width=True)

        with tab3:
            st.caption("In 50% of the simulations, results as good or better than the results shown.")
            st.dataframe(df3, use_container_width=True)
            #st.bar_chart(df3[["Ending Balance","Total Expense"]], use_container_width=True)

        with tab4:
            st.caption("In 25% of the simulations, results as good or better than the results shown.")
            st.dataframe(df4, use_container_width=True)
            '''st.bar_chart(df4[["Ending Balance","Total Expense"]], use_container_width=True,
                         x_label="Year", y_label="Portfolio Balance, Total Expense", color=["#1f77b4","#d62728"], height=700)'''
