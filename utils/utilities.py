from datetime import date, datetime
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st
from utils.calculate_taxes import (calculate_income_tax, calculate_state_tax, calculate_gain_tax)
from data.tax_rates import get_income_tax_rates, get_capital_gain_tax_rates
from data.state_taxrates import get_state_tax_rates
from data.ira_ssn_distribution import rmd_distribution


def read_fit_data(path):
    #path = "../data/equity_returns.csv"
    df = pd.read_csv(path)
    #print(df.columns) #['year', 'sp_tot_return', 'sp_cap_return', 'sp_div_yield', 'US_bond']
    df = df[['year', 'sp_cap_return', 'sp_div_yield', 'US_bond']]
    #print(df.head())
    mu_equity_cap, sigma_equity_cap = stats.norm.fit(df['sp_cap_return'])
    mu_equity_dividend, sigma_equity_dividend = stats.norm.fit(df['sp_div_yield'][-30:])
    mu_bond, sigma_bond = stats.norm.fit(df['US_bond'])
    return df, mu_equity_cap, sigma_equity_cap, mu_equity_dividend, sigma_equity_dividend, mu_bond, sigma_bond

def mortgage_interest(begin_balance, rate, monthly_payment, remaining_years):
    mortgage_interests = []
    end_balance = begin_balance
    for j in range(remaining_years):
        yearly_interest = 0
        for i in range(12):
            interest = end_balance * ((0.01*rate)/12)
            yearly_interest += interest
            end_balance -= (monthly_payment-interest)
        mortgage_interests.append(round(yearly_interest, 2))
    return mortgage_interests
#mort = mortgage_interest(889440.42, 2.25, 3605.35, 20)
#print(mort)


#simulation function
def monte_carlo_simulation(mu_equity, sigma_equity, mu_dividend, sigma_dividend, mu_bond, sigma_bond,
                           no_simulations, no_years):

    #np.random.seed(seed=4562)
    np.random.seed(45789)
    # Run simulation and return as Numpy 2D arrays
    simulation_returns = {'equity': np.random.normal(loc=mu_equity, scale=sigma_equity,
                                                            size=(no_simulations, no_years)),
                          'dividend': np.random.normal(loc=mu_dividend, scale=sigma_dividend,
                                                              size=(no_simulations, no_years)),
                          'bond': np.random.normal(loc=mu_bond, scale=sigma_bond,
                                                          size=(no_simulations, no_years))}
    #Find end balances for each simulation to find various percentile paths
    equity_simulated_balances = np.prod(1 + 0.01*simulation_returns['equity'], axis=1)
    dividend_simulated_total = np.sum(0.01 * simulation_returns['dividend'], axis=1)
    bond_simulated_total = np.sum(0.01 * simulation_returns['bond'], axis=1)
    # Find 10th, 25th ... percentiles and corresponding indexes of the market returns
    equity_index = {}
    dividend_index = {}
    bond_index = {}
    for percentile in [10, 25, 50, 75]:
        equity_percentile = np.percentile(equity_simulated_balances, percentile)
        equity_index[percentile] = np.argmin(np.abs(equity_simulated_balances - equity_percentile))
        div_percentile = np.percentile(dividend_simulated_total, percentile)
        dividend_index[percentile] = np.argmin(np.abs(dividend_simulated_total - div_percentile))
        bond_percentile = np.percentile(bond_simulated_total, percentile)
        bond_index[percentile] = np.argmin(np.abs(bond_simulated_total - bond_percentile))

    return simulation_returns, equity_index, dividend_index, bond_index

def return_by_scenarios(sim_returns, equity_index, dividend_index, bond_index, inflation):

    '''sig_below_avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[10],:],2),
                             'dividend': np.round(sim_returns['dividend'][dividend_index[10],:], 2),
                             'bond': np.round(sim_returns['bond'][bond_index[10],:], 2)}'''

    sig_below_avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[10]], 2),
                             'dividend': np.round(sim_returns['dividend'][dividend_index[10]], 2),
                             'bond': np.round(sim_returns['bond'][bond_index[10]], 2)}

    below_avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[25]],2),
                             'dividend': np.round(sim_returns['dividend'][dividend_index[25]], 2),
                             'bond': np.round(sim_returns['bond'][bond_index[25]], 2)}

    avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[50]],2),
                             'dividend': np.round(sim_returns['dividend'][dividend_index[50]], 2),
                             'bond': np.round(sim_returns['bond'][bond_index[50]], 2)}

    above_avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[75]],2),
                             'dividend': np.round(sim_returns['dividend'][dividend_index[75]], 2),
                             'bond': np.round(sim_returns['bond'][bond_index[75]], 2)}

    market_returns_future = {'sig_below_avg': sig_below_avg_returns,
                             'below_avg': below_avg_returns,
                             'average': avg_returns,
                             'above_avg': above_avg_returns}

    return market_returns_future



def plot_portfolio(portfolio, case, inCurrentDoller=True):
    current_year = date.today().year
    future_years = [current_year+i for i in range(len(portfolio))]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(future_years, portfolio, color='blue')
    ax.set_xlabel('Year')
    ax.set_ylabel('Portfolio Value')
    val = 'current($)' if inCurrentDoller else 'future($)'
    ax.set_title(f'Portfolio Value for {case} in {val}')
    st.pyplot(fig)


def calculate_taxes(income, ssn_earning, bond_interest, ira_distribution,
                    other_income, long_capital_gain, home_expense, est_donation,
                    residing_state, filing_choice, deferred_distribution, roth_conversion_amt,
                    short_term_gain=0, pension_income=0):
    #assumption : income is adjusted with 401 contribution if any

    gross_income = (income + 0.85 * ssn_earning + bond_interest + pension_income
                    + short_term_gain + ira_distribution['IRA-m'] + ira_distribution['IRA-p'] +
                    +ira_distribution['RMD-m'] + ira_distribution['RMD-p'] + other_income
                    + deferred_distribution + roth_conversion_amt)

    adjusted_gross_income = gross_income  # - contribution_401k - contribution_401k_p

    # Derive Gross Income for the State
    state_gross_income = adjusted_gross_income + long_capital_gain - 0.85 * ssn_earning

    # Calculate State Taxes(Assume itemized state deduction)
    state_taxable_income = state_gross_income - home_expense['property-tax'] - home_expense['interest']

    #st.write(f"State Taxable Income : {state_taxable_income}")
    if residing_state not in ['Florida', 'Texas']:
        state_tax_rate = get_state_tax_rates(state=residing_state, filing_as=filing_choice)
        tot_state_tax = 0
        for i in range(10):
            state_tax = calculate_state_tax(state_tax_rate, state_taxable_income - tot_state_tax)
            tot_state_tax = sum(state_tax)
        state_tax_total = tot_state_tax
    else:
        #state_tax = [0, 0]
        state_tax_total = 0
    # Derive Federal Taxable Income
    income_tax_rate, st_deduction, salt_cap = get_income_tax_rates(filing_choice)
    capital_gain_tax_rate = get_capital_gain_tax_rates(filing_choice)

    itemized_deduction = (home_expense['interest'] + est_donation +
                          min(home_expense['property-tax'] + state_tax_total, salt_cap))
    fed_taxable_income = adjusted_gross_income - max(st_deduction, itemized_deduction)

    # Calculate all the Federal taxes
    fed_income_tax = calculate_income_tax(income_tax_rate, fed_taxable_income)
    fed_gain_tax, rate = calculate_gain_tax(capital_gain_tax_rate, fed_taxable_income, long_capital_gain)

    return sum(fed_income_tax), sum(fed_gain_tax), state_tax_total, adjusted_gross_income

def calculate_end_balance(start_val, expenses, incomes, ssn_earnings, market_return, retirement_contribution,
                          filing_choice, capital_gain_percent, custom_distribution, home_expenses, rmd_index,
                          residing_state, roth_conversion, ages_m, ages_p, deferred_distributions):
    # start_val is a dictionary with IRA, ROTH_IRA, equity and bond as the keys
    # market_return is a dictionary with equity, dividend and bond as the keys
    end_balance ={'IRA-m': [], 'IRA-p': [], 'ROTH-m': [], 'ROTH-p': [], 'equity': []}
    total_tax =[]
    equity_returns = []
    dividend_returns = []
    roth_conversions = []
    roth_dividends = []
    roth_draws = {'roth-m-draw': [], 'roth-p-draw': []}
    bond_returns = []
    withdrawals = []
    adj_gross_incomes = []
    equity_draws = []
    ira_distributions = {'RMD-m': [], 'RMD-p': [], 'IRA-m': [], 'IRA-p': []}
    taxes = {'fed-tax': [], 'gain-tax': [], 'state-tax': []}
    # Initialize the investment starting balances
    equity_bal = start_val['equity']
    ira_m_bal = start_val['IRA-m']
    ira_p_bal = start_val['IRA-p']
    roth_m_bal = start_val['ROTH-m']
    roth_p_bal = start_val['ROTH-p']
    # Query the Required Minimum distribution rates:
    rmd_rates, rmd_start = rmd_distribution()
    rmd_m_index = rmd_start - rmd_index['rmd-m']
    rmd_p_index = rmd_start - rmd_index['rmd-p']

    # ratio of Ira balances. Withdrawal from iRA depends on ratio of IRA balances between partner and main person
    #ira_ratio = start_val['IRA-m'] / (start_val['IRA-m'] + start_val['IRA-p'] + 0.01)

    for i in range(market_return['equity'].size):
        ira_ratio = ira_m_bal / (ira_m_bal + ira_p_bal + 0.01)
        stock_return = market_return["equity"][i] + market_return["dividend"][i]
        ira_return_m = 0.01 * ira_m_bal * stock_return
        ira_return_p = 0.01 * ira_p_bal * stock_return
        #roth_return_m = 0.01 * stock_return * roth_m_bal
        #roth_return_p = 0.01 * stock_return * roth_p_bal

        equity_return = np.ceil(0.01 * market_return["equity"][i] * equity_bal)
        equity_dividend = 0.01 * market_return["dividend"][i] * equity_bal
        roth_return_m = np.ceil(0.01 * market_return["equity"][i] * roth_m_bal)
        roth_dividend_m = 0.01 * market_return["dividend"][i] * roth_m_bal
        roth_return_p = np.ceil(0.01 * market_return["equity"][i] * roth_p_bal)
        roth_dividend_p = 0.01 * market_return["dividend"][i] * roth_p_bal
        bond_return = 0.01 * market_return["bond"][i] * start_val['bond']
        home_expense = {'property-tax': home_expenses['property-tax'][i],
                        'interest': home_expenses['interest'][i]}
        equity_returns.append(equity_return)
        dividend_returns.append(equity_dividend)
        roth_dividends.append(roth_dividend_m + roth_dividend_p)
        bond_returns.append(bond_return)
        # Required minimum distribution:
        if i >= rmd_m_index:
            # print(i-rmd_m_index)
            rmd_m_distribution = np.ceil(ira_m_bal / rmd_rates[(i - rmd_m_index)])
            ira_m_bal -= rmd_m_distribution
            # st.write(f" RMD  {rmd_m_distribution}")
        else:
            rmd_m_distribution = 0
        if i > rmd_p_index:
            rmd_p_distribution = np.ceil(ira_p_bal / rmd_rates[i - rmd_p_index])
            ira_p_bal -= rmd_p_distribution
        else:
            rmd_p_distribution = 0
        # Estimate total_income
        est_total_income = (equity_dividend + roth_dividend_m + roth_dividend_p + bond_return + incomes[i] + ssn_earnings[i]
                            + deferred_distributions[i] + rmd_p_distribution + rmd_m_distribution)
        # iterate to match final total tax with initial assumption
        tax_expense = 0.25 * expenses[i]  # estimated to be 25% of expense

        # Expenses include core expense + Travel Expense + Mortgage + property Taxes
        roth_conversion_amt_m = min(ira_m_bal, roth_conversion*ira_ratio)
        roth_conversion_amt_p = min(ira_p_bal, roth_conversion*(1-ira_ratio))
        roth_conversion_amt = roth_conversion_amt_m + roth_conversion_amt_p
        roth_conversions.append(roth_conversion_amt)
        #update IRA balances
        ira_m_bal -= roth_conversion_amt_m
        ira_p_bal -= roth_conversion_amt_p
        for k in range(10):

            shortfall = tax_expense + expenses[i] - est_total_income

            # withdraw from IRA and Equity portfolio to support expense + estimated Tax (25%)
            # Withdraw from iRA and equity portfolio based on custom distribution and the ration of IRA balance between
            # you and your partner
            if shortfall > 0:
                # Now you need to withdraw from IRA and or Equity
                if ages_m[i] > 60:
                    if ira_m_bal > 0:
                        #you can withdraw from IRA
                        ira_m_withdraw = min(ira_m_bal, custom_distribution * shortfall * ira_ratio)
                        roth_m_withdraw = 0
                    else:
                        ira_m_withdraw = 0
                        roth_m_withdraw = min(roth_m_bal, custom_distribution * shortfall * ira_ratio)
                else:
                    ira_m_withdraw = 0
                    roth_m_withdraw = 0

                if ages_p[i] > 60:
                    if ira_p_bal > 0:
                        #you can withdraw from IRA
                        ira_p_withdraw = min(ira_p_bal, custom_distribution * shortfall * (1-ira_ratio))
                        roth_p_withdraw = 0
                    else:
                        ira_p_withdraw = 0
                        roth_p_withdraw = min(roth_p_bal, custom_distribution * shortfall * (1-ira_ratio))
                else:
                    ira_p_withdraw = 0
                    roth_p_withdraw = 0

                equity_withdrawal = shortfall - ira_m_withdraw - ira_p_withdraw - roth_m_withdraw - roth_p_withdraw
            else:
                ira_m_withdraw = 0
                ira_p_withdraw = 0
                roth_m_withdraw = 0
                roth_p_withdraw = 0
                equity_withdrawal = shortfall

            # Need to put the IRA withdrawal condition of age 60

            ira_distribution = {'IRA-m': ira_m_withdraw,
                                'IRA-p': ira_p_withdraw,
                                'RMD-m': rmd_m_distribution,
                                'RMD-p': rmd_p_distribution}

            long_capital_gain = equity_withdrawal * capital_gain_percent + equity_dividend
            other_income = 0
            #residing_state = 'California'
            est_donation = 0

            fed_tax, gain_tax, state_tax, adj_gross_income = calculate_taxes(incomes[i], ssn_earnings[i], bond_return, ira_distribution,
                                                           other_income, long_capital_gain, home_expense, est_donation,
                                                                             residing_state, filing_choice,
                                                                             deferred_distributions[i], roth_conversion_amt)
            tax_expense = fed_tax + gain_tax + state_tax
        #st.write(f" taxes : {state_tax, fed_tax, gain_tax}")
        withdrawals.append(shortfall)
        equity_draws.append(equity_withdrawal)
        roth_draws['roth-m-draw'].append(roth_m_withdraw)
        roth_draws['roth-p-draw'].append(roth_p_withdraw)
        ira_distributions['RMD-m'].append(rmd_m_distribution)
        ira_distributions['RMD-p'].append(rmd_p_distribution)
        ira_distributions['IRA-m'].append(ira_m_withdraw)
        ira_distributions['IRA-p'].append(ira_p_withdraw)
        total_tax.append(fed_tax + gain_tax + state_tax)
        taxes['fed-tax'].append(fed_tax)
        taxes['gain-tax'].append(gain_tax)
        taxes['state-tax'].append(state_tax)
        # Update the investment balances
        ira_m_bal = np.ceil(max(0,ira_return_m + ira_m_bal + retirement_contribution['ira-contrib-m'][i]
                                - ira_distribution['IRA-m']-ira_distribution['RMD-m']))
        ira_p_bal = np.ceil(max(0, ira_return_p + ira_p_bal + retirement_contribution['ira-contrib-p'][i]
                                - ira_distribution['IRA-p']-ira_distribution['RMD-p']))
        roth_m_bal = np.ceil(max(0, roth_return_m + roth_m_bal + roth_conversion_amt_m - roth_m_withdraw))
        roth_p_bal = np.ceil(max(0, roth_return_p + roth_p_bal + roth_conversion_amt_p - roth_p_withdraw))
        equity_bal = np.ceil(max(0, equity_return + equity_bal - equity_withdrawal))
        end_balance['IRA-m'].append(ira_m_bal)
        end_balance['IRA-p'].append(ira_p_bal)
        end_balance['ROTH-m'].append(roth_m_bal)
        end_balance['ROTH-p'].append(roth_p_bal)
        end_balance['equity'].append(equity_bal)
        end_balance['bond'] = start_val['bond']
        adj_gross_incomes.append(adj_gross_income)

    return (end_balance, total_tax, equity_returns, dividend_returns, withdrawals, bond_returns,
            adj_gross_incomes, ira_distributions, equity_draws, taxes, roth_dividends, roth_conversions, roth_draws)
def build_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, yearly_expenses, market_return,
                           starting_portfolio, home_expenses, retirement_contribution, filing_choice,
                           capital_gain_percent, custom_distribution, rmd_index, residing_state,
                           roth_conversion_amt, ages, deferred_distributions):
    current_year = datetime.now().year
    years = list(range(current_year, current_year + future_years))
    finance_df = pd.DataFrame(index=years)
    ages_m = list(range(ages['age-m'], ages['age-m'] + future_years))
    ages_p = list(range(ages['age-p'], ages['age-p'] + future_years))

    (end_balance, total_tax, eq_ret, dividend_returns, withdrawals,
     bond_returns, adj_gross_incomes, ira_distributions,
     equity_draws, taxes, roth_dividends,
     roth_conversions, roth_draws) = calculate_end_balance(starting_portfolio, yearly_expenses, total_incomes,
                                                            total_ssn_earnings, market_return, retirement_contribution,
                                                            filing_choice, capital_gain_percent, custom_distribution,
                                                            home_expenses, rmd_index, residing_state, roth_conversion_amt,
                                                            ages_m, ages_p, deferred_distributions)
    finance_df["Age"] = ages_m
    if filing_choice == "Married":
        finance_df["Partner Age"] = ages_p
    finance_df["Income"] = np.ceil(total_incomes)
    finance_df["Deferred Dist"] = np.ceil(deferred_distributions)
    finance_df["SSN"] = np.ceil(total_ssn_earnings)
    finance_df['Start IRA'] = end_balance['IRA-m']
    finance_df['Start IRA'] = finance_df['Start IRA'].shift(1).fillna(starting_portfolio['IRA-m'])
    finance_df['Start IRA-P'] = end_balance['IRA-p']
    finance_df['Start IRA-P'] = finance_df['Start IRA-P'].shift(1).fillna(starting_portfolio['IRA-p'])
    finance_df['Start Equity'] = end_balance['equity']
    finance_df['Start Equity'] = finance_df['Start Equity'].shift(1).fillna(starting_portfolio['equity'])
    finance_df["Cap yield %"] = market_return['equity']
    finance_df["Div yield %"] = market_return['dividend']
    finance_df["Bond yield %"] = market_return['bond']
    #finance_df['Capital Return'] = eq_ret
    finance_df['Dividend Pay'] = np.ceil(dividend_returns)
    finance_df['ROTH Dividend'] = np.ceil(roth_dividends)
    finance_df['Interest Pay'] = np.ceil(bond_returns)
    finance_df['Roth Conversion'] = np.ceil(roth_conversions)
    finance_df['Req. draw'] = np.ceil(withdrawals)
    finance_df['Equity draw'] = np.ceil(equity_draws)
    finance_df['IRA draw'] = np.ceil(ira_distributions['IRA-m'])
    finance_df['P-IRA draw'] = np.ceil(ira_distributions['IRA-p'])
    finance_df['Your RMD'] = np.ceil(ira_distributions['RMD-m'])
    finance_df['Partner RMD'] = np.ceil(ira_distributions['RMD-p'])
    finance_df['ROTH draw'] = np.ceil(roth_draws['roth-m-draw'])
    finance_df['ROTH-P draw'] = np.ceil(roth_draws['roth-p-draw'])
    finance_df['Adj Gross Income'] = np.ceil(adj_gross_incomes)
    #finance_df['div_ret'] = div_ret
    finance_df['Expense'] = np.ceil(yearly_expenses)
    #finance_df['propertyTax'] = np.ceil(home_expenses['property-tax'])
    finance_df['Fed Tax'] = taxes['fed-tax']
    finance_df['Gain Tax'] = taxes['gain-tax']
    finance_df['State Tax'] = taxes['state-tax']
    finance_df['Total Tax'] = total_tax
    finance_df['End IRA'] = end_balance['IRA-m']
    finance_df['End IRA-P'] = end_balance['IRA-p']
    finance_df['End ROTH'] = end_balance['ROTH-m']
    finance_df['End ROTH-P'] = end_balance['ROTH-p']
    finance_df['End Equity'] = end_balance['equity']
    #st.write(f"end IRA is {finance_df['End IRA'].iloc[-1]}")
    return finance_df

def final_outcomes(df1, df2, df3, df4, inflation):
    no_years = len(df1)-1
    current_factor = 1/((1+0.01*inflation)**no_years)
    data = {
        "Your IRA   ": [df1["End IRA"].iloc[-1], df2["End IRA"].iloc[-1], df3["End IRA"].iloc[-1], df4["End IRA"].iloc[-1]],
        "Spouse IRA": [df1["End IRA-P"].iloc[-1], df2["End IRA-P"].iloc[-1], df3["End IRA-P"].iloc[-1], df4["End IRA-P"].iloc[-1]],
        "ROTH total ": [df1['End ROTH-P'].iloc[-1]+ df1['End ROTH'].iloc[-1], df2['End ROTH-P'].iloc[-1]+df2['End ROTH'].iloc[-1],
                        df3['End ROTH-P'].iloc[-1]+df3['End ROTH'].iloc[-1], df4['End ROTH-P'].iloc[-1]+df4['End ROTH'].iloc[-1]],
        "Equity A/c": [df1['End Equity'].iloc[-1], df2['End Equity'].iloc[-1],df3['End Equity'].iloc[-1],df4['End Equity'].iloc[-1]],
        "Total Bal": [(df1["End IRA"].iloc[-1] + df1["End IRA-P"].iloc[-1] + df1['End Equity'].iloc[-1]
                          + df1['End ROTH'].iloc[-1] + df1['End ROTH-P'].iloc[-1]),
                          (df2["End IRA"].iloc[-1] + df2["End IRA-P"].iloc[-1] + df2['End Equity'].iloc[-1]
                          + df2['End ROTH'].iloc[-1] + df2['End ROTH-P'].iloc[-1]),
                          (df3["End IRA"].iloc[-1] + df3["End IRA-P"].iloc[-1] + df3['End Equity'].iloc[-1]
                          + df3['End ROTH'].iloc[-1] + df3['End ROTH-P'].iloc[-1]),
                          (df4["End IRA"].iloc[-1] + df4["End IRA-P"].iloc[-1] + df4['End Equity'].iloc[-1]
                         + df4['End ROTH'].iloc[-1] + df4['End ROTH-P'].iloc[-1])],
        "Fed Tax": [sum(df1['Total Tax'])-sum(df1['State Tax']), sum(df2['Total Tax'])-sum(df2['State Tax']),
                        sum(df3['Total Tax'])-sum(df3['State Tax']), sum(df4['Total Tax'])-sum(df4['State Tax'])],
        "State Tax": [sum(df1['State Tax']), sum(df2['State Tax']), sum(df3['State Tax']), sum(df4['State Tax'])]
    }
    data_current = data.copy()
    indexes = ["Significantly Below Avg", "Below Average", "Average Return", "Above Average"]
    df = pd.DataFrame(data, index=indexes)
    df = df.style.format("{:,.0f}")
    df.index.name = f"Market Condition"
    df_current = pd.DataFrame(data_current)
    #df_current.reset_index(drop=True, inplace=True)
    df_current = df_current*current_factor
    df_current = df_current.style.format("{:,.0f}")
    return df, df_current
