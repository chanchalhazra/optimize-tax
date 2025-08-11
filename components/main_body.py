#import streamlit
import streamlit as st
from data.tax_rates import get_income_tax_rates, get_capital_gain_tax_rates
from data.state_taxrates import get_state_tax_rates
from utils.calculate_taxes import calculate_income_tax, calculate_gain_tax, calculate_state_tax
from utils.utilities import (read_fit_data, mortgage_interest, monte_carlo_simulation,
                             build_yearly_dataframe, return_by_scenarios)
from components.future_tax_details import future_yearly_tables
import pandas as pd

def main_content():
    #np.random.seed(seed=4562)
    col1, col2, col3, col4, col5 = st.columns([1,4, 2,1, 6])
    with col2:
        filing_choice = st.radio("**File Taxes as**", ["Single", "Married", "Head"],
                                        horizontal=True, key="filing_choice")
    with col3:
        states = {'California': 3.0, 'Florida': 0.0, 'Texas': 0.0, 'Oregon': 2.0, 'Arizona': 2.0}
        residing_state = st.selectbox("**Residing State**", states.keys(), key="residing_state")
    with col5:
       tax_choice = st.radio("**Estimate Taxes for**", ["Current Year", "Future Years",],
                                 horizontal=True, key="tax_choice", index=1)
    if tax_choice == "Current Year":
        income_tax_rate, st_deduction, salt_cap = get_income_tax_rates(st.session_state.filing_choice)
        capital_gain_tax_rate = get_capital_gain_tax_rates(st.session_state.filing_choice)
        st.markdown("```")
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center;font-size:20px'><b>Tax Estimation for Current Year</b></p>",
                        unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(["Wages & Income", "adjustments to Income",
                                              "Itemized Deductions & Tax Credits"])
            with tab1:
                cell1, cell2, cell3, cell4 = st.columns(4)
                with cell1:
                    wage_income_m = st.number_input("Your Wages & Salaries", min_value=0, max_value=100000000,
                                                  value=0, step=1000)
                    if filing_choice == "Married":
                        wage_income_p = st.number_input("Partner Wages & Salaries", min_value=0, max_value=10000000, value=0)
                    else:
                        wage_income_p = st.number_input("Partner Wages & Salaries", min_value=0, max_value=1000000, value=0, disabled=True)
                        wage_income_p = 0
                    rental_income = st.number_input("Rental Income", min_value=0, max_value=100000, value=0)

                with cell2:
                    business_income = st.number_input("Business Income", min_value=0, max_value=10000000, value=0)
                    interest_taxable = st.number_input("Taxable Interest(bond,CD etc) Est", min_value=0, max_value=100000, value=0)
                    interest_notax = st.number_input("Estimated Tax-exempt interest", min_value=0, max_value=100000, value=0)

                with cell3:
                    ssn_earning = st.number_input("Social security benefits", min_value=0, max_value=100000, value=0)
                    pension_income = st.number_input("Pensions and Annuity", min_value=0, max_value=1000000, value=0)
                    ira_distribution = st.number_input("IRA Distributions", min_value=0, max_value=10000000, value=0)

                with cell4:
                    qualified_dividend = st.number_input("Estimated Qualified Dividend", min_value=0, max_value=100000,
                                                         value=0)
                    short_term_gain = st.number_input("Short Term Capital gain", min_value=0, max_value=1000000, value=0)
                    long_capital_gain = st.number_input("Long Term Capital gain", min_value=0, max_value=10000000, value=0)

            with tab2:
                cell1, cell2, cell3, cell4 = st.columns(4)
                with cell1:
                    unemployment_benefit = st.number_input("Unemployment Benefits", min_value=0, max_value=100000000,
                                                    value=0, step=1000)
                    other_income = st.number_input("Other Income", min_value=0, max_value=25000, value=0)
                with cell2:
                    contribution_401k = st.number_input("Contribution to 401K IRA", min_value=0,
                                                        max_value=1000000, value=0)
                    contribution_401k_p = st.number_input("Partner contribution to 401K IRA", min_value=0, max_value=35000, value=0)
                with cell3:
                    student_interest_deduction = st.number_input("Student loan interest deduction", min_value=0,
                                                                 max_value=100000, value=0)
                    self_health_deduction = st.number_input("Self employed health Insurance", min_value=0,
                                                                 max_value=100000, value=0)
                with cell4:
                    alimony_pay_deduction = st.number_input("Alimony Paid", min_value=0, max_value=100000000,
                                                            value=0, step=1000)
                    alimony_pay_received = st.number_input("Alimony received", min_value=0, max_value=100000000,
                                                            value=0, step=1000)

            with tab3:
                cell1, cell2, cell3, cell4 = st.columns(4)
                with cell1:
                    interest_mortgage = st.number_input("Yearly Mortgage(<1M) Interest", min_value=0, max_value=1000000,
                                                        value=0)
                    property_tax = st.number_input("Yearly Property Taxes", min_value=0, max_value=25000, value=0)

                    # Your actual deduction is only for the amount that exceeds 7.5 %of your Adjusted Gross Income (AGI).
                    # include Health Insurance premiums
                with cell2:
                    est_donation = st.number_input("Total planned donation", min_value=0, max_value=1000000, value=00)
                    med_expenses = st.number_input("Medical & Dental Expense", min_value=0, max_value=100000, value=0)
                with cell3:
                    investment_interest_expense = st.number_input("Investment Interest Expense", min_value=0, max_value=100000,value=0)
                    child_care=st.number_input("Child Care, adoption, Income Credit", min_value=0,max_value=25000, value=0)
                with cell4:

                    other_credit = st.number_input("Any sort of Income Credit", min_value=0, max_value=25000, value=0)
                    foreign_tax_credit = st.number_input("Foreign Tax Credit", min_value=0, max_value=25000, value=0)
            '''
            # This section to save and upload input data file
            input_data = {
                'filing_choice': filing_choice,
                'residing_state': residing_state,
                'wage_income': wage_income,
                
            }
            col1, col2 = st.columns([2,2])
            with col1:
                download_data(input_data)
            with col2:
                upload_data()
        #st.divider()'''
            #Derive Adjusted Gross Income - Federal Income
            gross_income = (wage_income_m+wage_income_p+0.85*ssn_earning+interest_taxable+pension_income
                            + short_term_gain+ira_distribution+rental_income+business_income
                            + unemployment_benefit+other_income)
            adjusted_gross_income = gross_income-contribution_401k-contribution_401k_p
            fed_long_capital_gain = long_capital_gain+qualified_dividend

            #Derive Gross Income for the State
            state_gross_income = adjusted_gross_income + fed_long_capital_gain - 0.85*ssn_earning

            # Calculate State Taxes(Assume itemized state deduction)
            state_taxable_income = state_gross_income-property_tax-interest_mortgage
            if residing_state not in ['Florida', 'Texas']:
                state_tax_rate = get_state_tax_rates(state=residing_state, filing_as=filing_choice)
                tot_state_tax = 0
                for i in range(10):
                    state_tax = calculate_state_tax(state_tax_rate, state_taxable_income-tot_state_tax)
                    #state_taxable_income = state_taxable_income - state_tax
                    tot_state_tax = sum(state_tax)
                st.session_state.state_tax_total = tot_state_tax
            else:
                state_tax = [0, 0]
                st.session_state.state_tax_total = 0

            #st.write(f"Total state tax {tot_state_tax}")
            #Derive Federal Taxable Income
            #itemized_deduction = interest_mortgage+property_tax
            itemized_deduction = interest_mortgage + est_donation + min(property_tax + sum(state_tax), salt_cap)
            fed_taxable_income = adjusted_gross_income - max(st_deduction,itemized_deduction)

            #Calcuate all the taxes
            #income_tax_rate, st_deduction = get_income_tax_rates(st.session_state.filing_choice)
            #capital_gain_tax_rate = get_capital_gain_tax_rates(st.session_state.filing_choice)
            fed_income_tax = calculate_income_tax(income_tax_rate, fed_taxable_income)
            fed_gain_tax, rate = calculate_gain_tax(capital_gain_tax_rate, fed_taxable_income, fed_long_capital_gain)

            data = {
                "Federal Income": ["Adjusted Gross Income", "Taxable Income", "Federal Income Tax"],
                "Fed $": [f"{adjusted_gross_income:,}", f"{fed_taxable_income:,}", f"{sum(fed_income_tax):,}"],
                "Capital Gain": ["Long Term Gain", "Gain Tax Rate %", "Capital Gain Tax"],
                "Gain $": [f"{fed_long_capital_gain:,}", f"{rate}", f"{sum(fed_gain_tax):,}"],
                "State Level": ["Adjusted Gross Income", "Taxable Income", "State Tax"],
                "State $": [f"{state_gross_income:,}", f"{state_taxable_income:,}", f"{sum(state_tax):,}"],
            }

            df = pd.DataFrame(data)
            # Display table in Streamlit

            st.write("")
            st.markdown(f"<span style='font-size:18px'><i>Tax Estimates</b></span>", unsafe_allow_html=True)
            #st.table(df.reset_index(drop=True))
            st.dataframe(df)
            col1, col2, col3 = st.columns([2,2,2])
            with col1:
                st.write(f"  Standard Deduction  =  {st_deduction}")
            with col2:
                st.write(f"  Itemized Deduction = {itemized_deduction:,}")
            with col3:
                if itemized_deduction > st_deduction:
                    st.write(f" Itemized deduction is selected")
    st.markdown("~~~")

    if tax_choice == "Future Years":
        # populate fed_income_tax, fed_gain_tax, state_tax with 00
        fed_income_tax = []
        fed_gain_tax = []
        state_tax = []
        path = './data/equity_bond_returns.csv'
        (_, mu_fitted_equity_cap, sigma_fitted_equity_cap, mu_fitted_equity_dividend, sigma_fitted_equity_dividend,
         mu_fitted_bond, sigma_fitted_bond) = read_fit_data(path)
        with st.container(border=True):
            cell1, cell2, cell3, cell4 = st.columns([1,3,2,1])
            with cell2:
                st.markdown(f"<p style='text-align: center;font-size:20px'><b>Tax Estimates for Future Years In Retirement</b></p>",
                        unsafe_allow_html=True)
            with cell3:
                input_mode = st.radio("Input data or simulate ", ['Input', 'Simulate'], index=0, horizontal=True)
            #st.markdown("---")
            # create details dataframes
            # Estimate taxes for future years
        #with st.container(border=True):
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Your Retirement plan","Partner Retirement plan","Expense budget",
                                              "Savings & Investment", "Deferred Income Distribution"])
            RMD_age = 75
            with tab1:
                cell1, cell2, cell3, cell4 = st.columns(4)
                with cell1:
                    age_m = st.number_input("Current Age", min_value=0, max_value=129, value=50)
                    retire_age_m = st.number_input("Retiring age", min_value=0, max_value=129, value=60)
                    #rmd_m_index = RMD_age - age_m
                with cell2:

                    ssn_age_m = st.number_input("SSN start age", min_value=0, max_value=129, value=62)
                    plan_to_age_m = st.number_input("Plan to age", min_value=0, max_value=129, value=90)

                with cell3:
                    income_m = st.number_input("Gross Income", min_value=0, max_value=30000000,
                                               value=0)
                    ssn_earning_m = st.number_input("SSN Earnings", min_value=0, max_value=100000, value=36000)
                with cell4:
                    ira_contribution_m = st.number_input("IRA/401k Contribution", min_value=0,
                                                        max_value=1000000, value=0)
                    #rmd_index = {'rmd-m': age_m, 'rmd-p': age_p}

            with tab2:
                cell1, cell2, cell3, cell4 = st.columns(4)
                with cell1:
                    if filing_choice == 'Married':
                        age_p = st.number_input("Partner Age", min_value=0, max_value=129, value=50)
                        retire_age_p = st.number_input("Partner Retiring age", min_value=0, max_value=129, value=60)
                    else:
                        age_p = st.number_input("Partner Age", min_value=0, max_value=129, value=0, disabled=True)
                        retire_age_p = st.number_input("Partner Retiring at", min_value=0, max_value=129, value=0,
                                                       disabled=True)

                    rmd_index = {'rmd-m': age_m, 'rmd-p': age_p}
                with cell2:
                    if filing_choice == 'Married':
                        ssn_age_p = st.number_input("Partner SSN start age", min_value=0, max_value=129, value=62)
                        plan_to_age_p = st.number_input("Partner Plan to age", min_value=0, max_value=129, value=90)
                    else:
                        ssn_age_p = st.number_input("Partner drawing SSN at", min_value=0, max_value=129, value=0,
                                                    disabled=True)
                        plan_to_age_p = st.number_input("Partner Plan to age", min_value=0, max_value=129,
                                                        value=0, disabled=True)
                with cell3:
                    if filing_choice == 'Married':
                        income_p = st.number_input("Partner Gross Income", min_value=0, max_value=30000000,
                                                   value=0)
                        ssn_earning_p = st.number_input("Partner SSN earning", min_value=0, max_value=100000, value=36000)
                    else:
                        income_p = st.number_input("Partner annual Income", min_value=0, max_value=30000000, value=0, disabled=True)
                        ssn_earning_p = st.number_input("Partner SSN benefits", min_value=0, max_value=100000, value=0,
                                                        disabled=True)
                with cell4:
                    if filing_choice == 'Married':
                        ira_contribution_p = st.number_input("Partner IRA/401k Contribution", min_value=0,
                                                             max_value=1000000, value=0)
                    else:
                        ira_contribution_p = st.number_input("Partner IRA/401k Contribution", min_value=0,
                                                             max_value=1000000, value=0, disabled=True)



                #Estimate the future years based on age and plan to age
                future_years = max((plan_to_age_m-age_m)+1,(plan_to_age_p-age_p)+1)
                #Estimate future SSN earnings
                COLA_rate = 1.5
                yrs_before_ssn_m = ssn_age_m - age_m
                yrs_before_ssn_p = ssn_age_p - age_p
                ssn_earnings_m = [round(ssn_earning_m*((1+0.01*COLA_rate)**(i-yrs_before_ssn_m)),2)
                                   if i >= yrs_before_ssn_m else 0 for i in range(future_years)]
                ssn_earnings_p = [round(ssn_earning_p * ((1 + 0.01 * COLA_rate) ** (i - yrs_before_ssn_p)), 2)
                                  if i >= yrs_before_ssn_p else 0 for i in range(future_years)]
                combined_ssn_earnings = [a+b for a,b in zip(ssn_earnings_m, ssn_earnings_p)]
                incomes_m = [(income_m-ira_contribution_m) if i <= (retire_age_m - age_m)
                             else 0 for i in range(future_years)]
                incomes_p = [(income_p-ira_contribution_p) if i <= (retire_age_p - age_p) else 0 for i in
                             range(future_years)]
                combined_incomes = [a+b for a, b in zip(incomes_m, incomes_p)]
                ira_contributions_m = [ira_contribution_m if i <= (retire_age_m - age_m) else 0 for i in
                                       range(future_years)]
                ira_contributions_p = [ira_contribution_p if i <= (retire_age_m - age_m) else 0 for i in
                                       range(future_years)]
                retirement_contribution = {'ira-contrib-m': ira_contributions_m, 'ira-contrib-p': ira_contributions_p}
            with tab3:
                # st.write("enter your planned expenses including teh ones which can give tax credit like donations")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    rent_expense = st.number_input("Rent per Yr", min_value=0, max_value=30000000, value=0)
                    property_tax_2 = st.number_input("Property Tax per yr", min_value=0, max_value=30000000,
                                                     value=0)
                with col2:
                    mortgage_balance = st.number_input("Mortgage Balance", min_value=0, max_value=3000000, value=0)
                    mortgage_rate = st.number_input("Mortgage Rate", min_value=0.0, max_value=15.0, value=3.0)

                with col3:
                    mortgage_years = st.number_input("Mortgage years left", min_value=0, max_value=30)
                    monthly_mortgage_pay = st.number_input("Mortgage pay $/Mon", min_value=0, max_value=120000)


                with col4:
                    core_expense = st.number_input("Core Expenses $/yr", min_value=0, max_value=1200000)
                    travel_expense = st.number_input("Travel Expense $/yr", min_value=0, max_value=1200000)
                inflation = 2.5
                total_expense = core_expense + travel_expense
                expenses_no_mortgage = [total_expense * (1 + 0.01 * inflation) ** i for i in range(future_years)]
                mortgage_expenses = [monthly_mortgage_pay*12 if i < mortgage_years else 0 for i in range(future_years)]
                yearly_expenses_1 = [a + b for a, b in zip(expenses_no_mortgage, mortgage_expenses)]

                # Calculate yearly mortgage interests
                mortgage_yearly_interests = mortgage_interest(mortgage_balance, mortgage_rate,
                                                              monthly_mortgage_pay, mortgage_years)
                mortgage_yearly_interests.extend([0]*(future_years-mortgage_years))
                property_taxes = [round(property_tax_2 * (1+0.01*inflation)**i,0) for i in range(future_years)]
                yearly_expenses = [a + b for a, b in zip(yearly_expenses_1, property_taxes)]
                home_expenses = {'rent': rent_expense, 'interest': mortgage_yearly_interests,
                                 'property-tax': property_taxes, 'monthly-pay': monthly_mortgage_pay}
            with tab4:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ira_m = st.number_input("401K/IRA Balance", min_value=0, max_value=100000000, value=0)
                    ira_p = st.number_input("Partner 401K/IRA Balance", min_value=0, max_value=100000000, value=0)

                with col2:
                    roth_m = st.number_input("ROTH IRA Balance", min_value=0, max_value=100000000, value=0)
                    roth_p = st.number_input("Partner ROTH IRA", min_value=0, max_value=100000000, value=0)

                with col3:
                    combined_portfolio = st.number_input("Taxable Investment Portfolio", min_value=0, max_value=100000000, value=0)
                    other_income = st.number_input("Net Business $ Rent Income", min_value=0, max_value=3000000,
                                                   value=0)

                with col4:
                    pension_income_m = st.number_input("Pension $/yr", min_value=0, max_value=100000, value=0)
                    pension_income_p = st.number_input("Partner Pension $/yr", min_value=0, max_value=100000,
                                                       value=0)

            with tab5:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    deferred_amt_m = st.number_input("Total deferred balance", min_value=0, max_value=3000000, value=0)
                    def_withdraw_age_m = st.number_input("Withdraw start age", min_value=0, max_value=129, value=retire_age_m)

                with col2:
                    def_withdraw_duration_m = st.number_input("No of year", min_value=0, max_value=20, value=0)
                    def_distributions_m = []
                    #st.write("enter year by year")
                    with st.expander("Enter Distributions by Year", expanded=True):
                        for i in range(def_withdraw_duration_m):
                            val = st.number_input(f"Year {i+1} distribution", min_value=0.0, max_value=1000000.0,
                                                  value=deferred_amt_m/def_withdraw_duration_m)
                            def_distributions_m.append(val)

                with col3:
                    deferred_amt_p = st.number_input("Partner Total deferred balance", min_value=0, max_value=3000000,
                                                     value=0)
                    def_withdraw_age_p = st.number_input("Partner - Withdraw start age", min_value=0, max_value=129,
                                                         value=retire_age_p)

                with col4:

                    def_withdraw_duration_p = st.number_input("Partner - no of years", min_value=0, max_value=20,
                                                            value=0)
                    # st.write("enter year by year")
                    def_distributions_p = []
                    with st.expander("Partner - Distributions by Year", expanded=True):
                        for i in range(def_withdraw_duration_p):
                            val = st.number_input(f"Partner Year {i+1} distribution", min_value=0.0, max_value=1000000.0,
                                                  value=deferred_amt_p/def_withdraw_duration_p)
                            def_distributions_p.append(val)
                # create the deferred comp distribution series
                years_before_m = def_withdraw_age_m-age_m
                years_after_m = future_years - years_before_m - def_withdraw_duration_m
                def_distributions_m[:0] = [0]*years_before_m
                def_distributions_m[years_before_m+def_withdraw_duration_m:] = [0]*years_after_m
                years_before_p = def_withdraw_age_p - age_p
                years_after_p = future_years - years_before_p - def_withdraw_duration_p
                def_distributions_p[:0] = [0] * years_before_p
                def_distributions_p[years_before_p + def_withdraw_duration_p:] = [0] * years_after_p
                deferred_distributions = [a+b for a, b in zip(def_distributions_m,
                                                              def_distributions_p)]
                #st.write(len(def_distributions_m), len(def_distributions_p), len(deferred_distributions))
            ages = {'age-m': age_m, 'age-p': age_p}
            st.markdown('---')
            #Control room
            col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1, 3, 1, 2, 2, 2])
            with col1:
                capital_gain_percent = st.slider("Avg Capital gain % of portfolio", min_value=0.0, max_value=1.0,
                                                 value=0.3, step=0.1)
                roth_conversion_amt = st.number_input("ROTH conversion $/yr", min_value=0, max_value=1000000, value=0)

            with col3:
                custom_distribution = st.slider("IRA % of withdrawal", min_value=0.0, max_value=1.0, value=0.4,
                                                step=0.01)
                equity_distribution = st.slider("Equity Distribution %", min_value=0.0, max_value=1.0, value=0.8,
                                                step=0.1)
            with col5:
                mu_equity = st.number_input("Equity return", 0.0, 20.0, mu_fitted_equity_cap, step=0.1)
                sigma_equity = st.number_input("Equity return spread", 0.0, 20.0, sigma_fitted_equity_cap, step=0.1)
            with col6:
                mu_dividend = st.number_input("Dividend yield", 0.0, 20.0, mu_fitted_equity_dividend, step=0.1)
                sigma_dividend = st.number_input("Div. Yield spread", 0.0, 20.0, sigma_fitted_equity_dividend,
                                                 step=0.1)
            with col7:
                mu_bond = st.number_input("Bond return", 0.0, 20.0, mu_fitted_bond, step=0.1)
                sigma_bond = st.number_input("Bond return spread", 0.0, 20.0, sigma_fitted_bond, step=0.1)
            st.markdown('---')
            '''col1, col2 = st.columns([2,3])
            with col2:
                st.markdown(f"<span style='font-size:10px'><i>Equity dividend yield is modelled based on last "
                        f"30 years as market dynamics changed: more stock buybacks than dividend payout</i></span>",
                        unsafe_allow_html=True)'''
            # Calculate Portfolio combination:
            equity_portfolio = combined_portfolio * equity_distribution
            bond_portfolio = combined_portfolio * (1 - equity_distribution)
            portfolio = {'IRA-m': ira_m, 'IRA-p': ira_p, 'ROTH-m': roth_m,
                         'ROTH-p': roth_p, 'equity': equity_portfolio, 'bond': bond_portfolio}

            #Calculate returns and taxes:
            if input_mode == 'Simulate':
                simulation_returns,equity_index, dividend_index, bond_index = monte_carlo_simulation(mu_equity, sigma_equity, mu_dividend, sigma_dividend,
                                                            mu_bond, sigma_bond,2000, no_years=future_years)
                market_returns_future = return_by_scenarios(simulation_returns,equity_index,
                                                                                    dividend_index, bond_index, 2.5)

                df1 = build_yearly_dataframe(future_years, combined_ssn_earnings, combined_incomes, yearly_expenses,
                                             market_returns_future['sig_below_avg'], portfolio, home_expenses,
                                             retirement_contribution, filing_choice, capital_gain_percent,
                                             custom_distribution, rmd_index, residing_state, roth_conversion_amt,
                                             ages, deferred_distributions)
                df2 = build_yearly_dataframe(future_years, combined_ssn_earnings, combined_incomes,yearly_expenses,
                                             market_returns_future['below_avg'], portfolio,home_expenses,
                                             retirement_contribution, filing_choice, capital_gain_percent,
                                             custom_distribution, rmd_index, residing_state, roth_conversion_amt,
                                             ages, deferred_distributions)
                df3 = build_yearly_dataframe(future_years, combined_ssn_earnings, combined_incomes,yearly_expenses,
                                             market_returns_future['average'], portfolio,home_expenses,
                                             retirement_contribution, filing_choice, capital_gain_percent,
                                             custom_distribution, rmd_index, residing_state, roth_conversion_amt,
                                             ages, deferred_distributions)
                df4 = build_yearly_dataframe(future_years, combined_ssn_earnings, combined_incomes,yearly_expenses,
                                             market_returns_future['above_avg'], portfolio,home_expenses,
                                             retirement_contribution, filing_choice, capital_gain_percent,
                                             custom_distribution, rmd_index, residing_state, roth_conversion_amt,
                                             ages, deferred_distributions)

                future_yearly_tables(df1, df2, df3, df4, inflation)

    return fed_income_tax, fed_gain_tax, state_tax, filing_choice, residing_state, tax_choice
