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
    mu_equity_cap, sigma_equity_cap = stats.norm.fit(df['sp_cap_return'][-30:])
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

    np.random.seed(seed=4562)
    # initialize simulation returns as Numpy arrays
    simulation_returns = {'equity': np.zeros((no_years, no_simulations)),
                          'dividend': np.zeros((no_years, no_simulations)),
                          'bond': np.zeros((no_years, no_simulations))}
    equity_simulated = []
    dividend_simulated = []
    bond_simulated = []
    for i in range(no_simulations):
        simulation_returns['equity'][:, i] = np.transpose(
            np.random.normal(loc=mu_equity, scale=sigma_equity, size=no_years))
        # print(simulation_returns['equity'])
        simulation_returns['dividend'][:, i] = np.transpose(
            np.random.normal(loc=mu_dividend, scale=sigma_dividend, size=no_years))
        simulation_returns['bond'][:, i] = np.transpose(np.random.normal(loc=mu_bond, scale=sigma_bond, size=no_years))
        equity_bal = 1
        dividend_received = 0
        bond_return = 0
        for k in range(no_years):
            equity_bal *= (1 + 0.01 * simulation_returns['equity'][k, i])
            dividend_received += 0.01 * simulation_returns['dividend'][k, i]
            bond_return += 0.01 * simulation_returns['bond'][k, i]
        equity_simulated.append(equity_bal)
        dividend_simulated.append(dividend_received)
        bond_simulated.append(bond_return)
    # Find 10th, 25th ... percentiles
    equity_index = {}
    dividend_index = {}
    bond_index = {}
    for percentile in [10, 25, 50, 75]:
        equity_percentile = np.percentile(equity_simulated, percentile)
        equity_index[percentile] = np.argmin(np.abs(equity_simulated - equity_percentile))
        div_percentile = np.percentile(dividend_simulated, percentile)
        dividend_index[percentile] = np.argmin(np.abs(dividend_simulated - div_percentile))
        bond_percentile = np.percentile(bond_simulated, percentile)
        bond_index[percentile] = np.argmin(np.abs(bond_simulated - bond_percentile))

    return simulation_returns, equity_index, dividend_index, bond_index

def return_by_scenarios(sim_returns, equity_index, dividend_index, bond_index, inflation):

    sig_below_avg_returns = {'equity': np.round(sim_returns['equity'][:, equity_index[10]],2),
                             'dividend': np.round(sim_returns['dividend'][:, dividend_index[10]], 2),
                             'bond': np.round(sim_returns['bond'][:, bond_index[10]], 2)}

    below_avg_returns = {'equity': np.round(sim_returns['equity'][:, equity_index[25]],2),
                             'dividend': np.round(sim_returns['dividend'][:, dividend_index[25]], 2),
                             'bond': np.round(sim_returns['bond'][:, bond_index[25]], 2)}

    avg_returns = {'equity': np.round(sim_returns['equity'][:, equity_index[50]],2),
                             'dividend': np.round(sim_returns['dividend'][:, dividend_index[50]], 2),
                             'bond': np.round(sim_returns['bond'][:, bond_index[50]], 2)}

    above_avg_returns = {'equity': np.round(sim_returns['equity'][:, equity_index[75]],2),
                             'dividend': np.round(sim_returns['dividend'][:, dividend_index[75]], 2),
                             'bond': np.round(sim_returns['bond'][:, bond_index[75]], 2)}

    sig_below_avg_returns_c = {
        'equity': np.round([sig_below_avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                            for i in range(len(sig_below_avg_returns['equity']))], 2),
        'dividend': np.round([sig_below_avg_returns['dividend'][i] / ((1 + inflation * 0.01) ** (i))
                              for i in range(len(sig_below_avg_returns['dividend']))], 2),
        'bond': np.round([sig_below_avg_returns['bond'][i] / ((1 + inflation * 0.01) ** (i))
                          for i in range(len(sig_below_avg_returns['bond']))], 2)}

    avg_returns_c = {
        'equity': np.round([avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                            for i in range(len(avg_returns['equity']))], 2),
        'dividend': np.round([avg_returns['dividend'][i] / ((1 + inflation * 0.01) ** (i))
                              for i in range(len(avg_returns['dividend']))], 2),
        'bond': np.round([avg_returns['bond'][i] / ((1 + inflation * 0.01) ** (i))
                          for i in range(len(avg_returns['bond']))], 2)}

    below_avg_returns_c = {
        'equity': np.round([below_avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                            for i in range(len(below_avg_returns['equity']))], 2),
        'dividend': np.round([below_avg_returns['dividend'][i] / ((1 + inflation * 0.01) ** (i))
                              for i in range(len(below_avg_returns['dividend']))], 2),
        'bond': np.round([below_avg_returns['bond'][i] / ((1 + inflation * 0.01) ** (i))
                          for i in range(len(below_avg_returns['bond']))], 2)}
    above_avg_returns_c = {
        'equity': np.round([above_avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                            for i in range(len(above_avg_returns['equity']))], 2),
        'dividend': np.round([above_avg_returns['dividend'][i] / ((1 + inflation * 0.01) ** (i))
                              for i in range(len(above_avg_returns['dividend']))], 2),
        'bond': np.round([above_avg_returns['bond'][i] / ((1 + inflation * 0.01) ** (i))
                          for i in range(len(above_avg_returns['bond']))], 2)}

    market_returns_future = {'sig_below_avg': sig_below_avg_returns,
                             'below_avg': below_avg_returns,
                             'average': avg_returns,
                             'above_avg': above_avg_returns}

    market_returns_current = {'sig_below_avg': sig_below_avg_returns_c,
                              'below_avg': below_avg_returns_c,
                              'average': avg_returns_c,
                              'above_avg': above_avg_returns_c}

    return market_returns_current, market_returns_future



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
                    residing_state, filing_choice, short_term_gain=0, pension_income=0):
    #assumption : income is adjusted with 401 contribution if any

    gross_income = (income + 0.85 * ssn_earning + bond_interest + pension_income
                    + short_term_gain + ira_distribution['IRA-m'] + ira_distribution['IRA-p'] +
                    +ira_distribution['RMD-m'] + ira_distribution['RMD-m'] + other_income)

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
                          filing_choice, capital_gain_percent, custom_distribution, home_expenses, rmd_index):
    # start_val is a dictionary with IRA, ROTH_IRA, equity and bond as the keys
    # market_return is a dictionary with equity, dividend and bond as the keys
    end_balance ={'IRA-m': [], 'IRA-p': [], 'ROTH-m': [], 'ROTH-p': [], 'equity': []}
    total_tax =[]
    equity_returns = []
    dividend_returns = []
    bond_returns = []
    withdrawals = []
    adj_gross_incomes = []
    equity_draws = []
    ira_distributions = {'RMD-m': [], 'RMD-p': [], 'IRA-m': [], 'IRA-p': []}
    #start_val = start_portfolio
    equity_bal = start_val['equity']
    ira_m_bal = start_val['IRA-m']
    ira_p_bal = start_val['IRA-p']
    roth_m_bal = start_val['ROTH-m']
    roth_p_bal = start_val['ROTH-p']
    #Required Minimum distribution rates:
    rmd_rates, rmd_start = rmd_distribution()
    rmd_m_index = rmd_start - rmd_index['rmd-m']
    rmd_p_index = rmd_start - rmd_index['rmd-p']
    for i in range(market_return['equity'].size):
        #st.write(f"index is {i}")
        ira_return_m = 0.01*market_return["equity"][i]*ira_m_bal+ 0.01*market_return["dividend"][i]*ira_m_bal
        ira_return_p = 0.01 * market_return["equity"][i] * ira_p_bal + 0.01 * market_return["dividend"][i] * ira_p_bal
        roth_return_m = (0.01 * market_return["equity"][i] * roth_m_bal
                         + 0.01 * market_return["dividend"][i] * roth_m_bal)
        roth_return_p = (0.01 * market_return["equity"][i] * roth_p_bal
                         + 0.01 * market_return["dividend"][i] * roth_p_bal)
        equity_return = np.ceil(0.01 * market_return["equity"][i] * equity_bal)
        equity_dividend = 0.01 * market_return["dividend"][i] * equity_bal
        bond_return = 0.01 * market_return["bond"][i] * start_val['bond']
        # Multiplying expense by 1.25 so that we included an estimated tax payment
        home_expense = {'property-tax': home_expenses['property-tax'][i],
                        'interest': home_expenses['interest'][i]}
        shortfall = max(0,(1.25 * expenses[i] - (equity_dividend+bond_return + incomes[i] + ssn_earnings[i])))
        equity_returns.append(equity_return)
        dividend_returns.append(equity_dividend)
        bond_returns.append(bond_return)
        withdrawals.append(shortfall)
        # withdraw from IRA and Equity portfolio to support expense + estimated Tax (25%)
        # Withdraw from iRA and equity portfolio based on custom distribution and teh ration of IRA balance between
        # you and your partner
        if i >= rmd_m_index:
            #print(i-rmd_m_index)
            rmd_m_distribution = np.ceil(ira_m_bal/rmd_rates[(i-rmd_m_index)])
            #st.write(f" RMD  {rmd_m_distribution}")
        else:
            rmd_m_distribution = 0
        if i > rmd_p_index:
            rmd_p_distribution = np.ceil(ira_p_bal/rmd_rates[i-rmd_m_index])
        else:
            rmd_p_distribution = 0

        shortfall = (shortfall - rmd_m_distribution - rmd_p_distribution)

        equity_withdrawal = max(0, (1-custom_distribution) * shortfall)
        ira_ratio = start_val['IRA-m']/(start_val['IRA-m']+start_val['IRA-p']+0.01)
        ira_m_withdraw = max(0, (shortfall-equity_withdrawal)*ira_ratio)
        ira_p_withdraw = max(0,(shortfall - equity_withdrawal - ira_m_withdraw))
        ira_distribution = {'IRA-m': ira_m_withdraw,
                            'IRA-p': ira_p_withdraw,
                            'RMD-m': rmd_m_distribution,
                            'RMD-p': rmd_p_distribution}
        equity_draws.append(equity_withdrawal)
        ira_distributions['RMD-m'].append(rmd_m_distribution)
        ira_distributions['RMD-p'].append(rmd_p_distribution)
        ira_distributions['IRA-m'].append(ira_m_withdraw)
        ira_distributions['IRA-p'].append(ira_p_withdraw)
        #add to IRA distribution the RMD part for both m snd p

        long_capital_gain = equity_withdrawal * capital_gain_percent + equity_dividend
        other_income = 0
        residing_state = 'California'
        est_donation = 0

        fed_tax, gain_tax, state_tax, adj_gross_income = calculate_taxes(incomes[i], ssn_earnings[i], bond_return, ira_distribution,
                                                       other_income,long_capital_gain,home_expense,est_donation,
                                                       residing_state, filing_choice)
        #st.write(f" taxes : {state_tax, fed_tax, gain_tax}")
        total_tax.append(fed_tax + gain_tax + state_tax)
        # Update the investment balances
        ira_m_bal = np.ceil(max(0,ira_return_m + ira_m_bal - ira_distribution['IRA-m']-ira_distribution['RMD-m']))
        ira_p_bal = np.ceil(max(0, ira_return_p + ira_p_bal - ira_distribution['IRA-p']-ira_distribution['RMD-p']))
        roth_m_bal = np.ceil(max(0,roth_return_m + roth_m_bal))
        roth_p_bal = np.ceil(max(0,roth_return_p + roth_p_bal))
        equity_bal = np.ceil(max(0, equity_return + equity_bal - equity_withdrawal))
        end_balance['IRA-m'].append(ira_m_bal)
        end_balance['IRA-p'].append(ira_p_bal)
        end_balance['ROTH-m'].append(roth_m_bal)
        end_balance['ROTH-p'].append(roth_p_bal)
        end_balance['equity'].append(equity_bal)
        end_balance['bond'] = start_val['bond']
        adj_gross_incomes.append(adj_gross_income)

    return (end_balance, total_tax, equity_returns, dividend_returns, withdrawals, bond_returns,
            adj_gross_incomes, ira_distributions, equity_draws)
def build_yearly_dataframe(future_years, total_ssn_earnings, total_incomes, yearly_expenses, market_return,
                           starting_portfolio, home_expenses, retirement_contribution, filing_choice,
                           capital_gain_percent, custom_distribution, rmd_index):
    current_year = datetime.now().year
    years = list(range(current_year, current_year + future_years))
    finance_df = pd.DataFrame(index=years)

    (end_balance, total_tax, eq_ret, dividend_returns, withdrawals,
     bond_returns, adj_gross_incomes, ira_distributions, equity_draws) = calculate_end_balance(starting_portfolio, yearly_expenses, total_incomes,
                                                            total_ssn_earnings, market_return, retirement_contribution,
                                                            filing_choice, capital_gain_percent, custom_distribution,
                                                            home_expenses, rmd_index)
    finance_df["Income"] = np.ceil(total_incomes)
    finance_df["SSN"] = np.ceil(total_ssn_earnings)
    finance_df['Start IRA'] = end_balance['IRA-m']
    finance_df['Start IRA'] = finance_df['Start IRA'].shift(1).fillna(starting_portfolio['IRA-m'])
    finance_df['Start IRA-p'] = end_balance['IRA-p']
    finance_df['Start IRA-p'] = finance_df['Start IRA-p'].shift(1).fillna(starting_portfolio['IRA-p'])
    finance_df['Start Equity'] = end_balance['equity']
    finance_df['Start Equity'] = finance_df['Start Equity'].shift(1).fillna(starting_portfolio['equity'])
    finance_df["Cap yield"] = market_return['equity']
    finance_df["Div yield"] = market_return['dividend']
    finance_df["bond yield"] = market_return['bond']
    finance_df['Capital Return'] = eq_ret
    finance_df['Dividend Pay'] = np.ceil(dividend_returns)
    finance_df['Interest Pay'] = np.ceil(bond_returns)
    finance_df['Total draw'] = np.ceil(withdrawals)
    finance_df['Equity draw'] = np.ceil(equity_draws)
    finance_df['IRA draw'] = np.ceil(ira_distributions['IRA-m'])
    finance_df['P-IRA draw'] = np.ceil(ira_distributions['IRA-p'])
    finance_df['Your RMD'] = np.ceil(ira_distributions['RMD-m'])
    finance_df['Partner RMD'] = np.ceil(ira_distributions['RMD-p'])
    finance_df['Adj Gross Income'] = np.ceil(adj_gross_incomes)
    #finance_df['div_ret'] = div_ret
    finance_df['Expense'] = np.ceil(yearly_expenses)
    finance_df['propertyTax'] = np.ceil(home_expenses['property-tax'])
    finance_df['Total Tax'] = total_tax
    finance_df['End IRA'] = end_balance['IRA-m']
    finance_df['End IRA-p'] = end_balance['IRA-p']
    finance_df['End Equity'] = end_balance['equity']
    #st.write(f"end IRA is {finance_df['End IRA'].iloc[-1]}")
    return finance_df

def final_outcomes(df1, df2, df3, df4):
    data = {
        "Your IRA": [df1["End IRA"].iloc[-1], df2["End IRA"].iloc[-1], df3["End IRA"].iloc[-1], df4["End IRA"].iloc[-1]],
        "Partner IRA": [df1["End IRA-p"].iloc[-1], df2["End IRA-p"].iloc[-1], df3["End IRA-p"].iloc[-1], df4["End IRA-p"].iloc[-1]],
        "Equity Portfolio": [df1['End Equity'].iloc[-1], df2['End Equity'].iloc[-1],df3['End Equity'].iloc[-1],df4['End Equity'].iloc[-1]],
        "Total Tax": [sum(df1['Total Tax']), sum(df2['Total Tax']), sum(df3['Total Tax']), sum(df4['Total Tax'])]
    }
    data["Your IRA"] = [f"{val:,.0f}" for val in data["Your IRA"]]
    data["Partner IRA"] = [f"{val:,.0f}" for val in data["Partner IRA"]]
    data["Equity Portfolio"] = [f"{val:,.0f}" for val in data["Equity Portfolio"]]
    data["Total Tax"] = [f"{val:,.0f}" for val in data["Total Tax"]]
    indexes = ["Significantly Below Average Market Return", "Below Average Market Return", "Average Market Return", "Best Case Market Return"]
    df = pd.DataFrame(data, index=indexes)
    df.index.name = f"Market Condition"
    #df = df.round(0)
    return df
