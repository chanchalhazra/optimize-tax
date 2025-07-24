import streamlit as st


def component_yearly_taxes(df1, df2, df3):
    with st.container():
        tab1, tab2, tab3, tab4 = st.tabs(["Wait till RMD at 73", "Yearly ROTH conversion",
                                          "Proportional withdrawal"])
        with tab1:
            st.caption("In 90% of the simulations, results as good or better than the results shown.")
            st.dataframe(df1,use_container_width=True)
            st.bar_chart(df1[["Ending Balance","Total Expense"]],use_container_width=True)

        with tab2:
            st.caption("In 75% of the simulations, results as good or better than the results shown.")
            st.dataframe(df2, use_container_width=True)
            st.bar_chart(df2[["Ending Balance","Total Expense"]], use_container_width=True)

        with tab3:
            st.caption("In 50% of the simulations, results as good or better than the results shown.")
            st.dataframe(df3, use_container_width=True)
            st.bar_chart(df3[["Ending Balance","Total Expense"]], use_container_width=True)
