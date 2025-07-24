import numpy as np

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

sim_returns, equity_index, dividend_index, bond_index = monte_carlo_simulation(10,18,1.9,
                                          2.3,3.5,1.4,1000,20)
#print(sim_ret['equity'][:,x[50]])

sig_below_avg_returns = {'equity': np.round(sim_returns['equity'][:,equity_index[10]],2),
                             'dividend': np.round(sim_returns['dividend'][:, dividend_index[10]],2),
                             'bond': np.round(sim_returns['bond'][:, bond_index[10]],2)}


#print(sig_below_avg_returns)
inflation = 2.5
sig_below_avg_returns_current = {'equity': np.round([sig_below_avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                                     for i in range(len(sig_below_avg_returns['equity']))],2),
                           'dividend': np.round([sig_below_avg_returns['dividend'][i] / ((1 + inflation * 0.01) ** (i))
                                     for i in range(len(sig_below_avg_returns['dividend']))],2),
                           'bond': np.round([sig_below_avg_returns['bond'][i] / ((1 + inflation * 0.01) ** (i))
                                     for i in range(len(sig_below_avg_returns['bond']))],2)}

#print(sig_below_avg_returns_current)
data = np.array([105, 150, 91, 95, 200, 170, 90, 130])
percentile_value = np.percentile(data, 10)

# Get index of the closest value
index = np.argmin(np.abs(data - percentile_value))
print(percentile_value)
print(index)