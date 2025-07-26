import numpy as np

def monte_carlo_simulation(mu_equity, sigma_equity, no_simulations, no_years):

    np.random.seed(4562)

    # initialize simulation returns as Numpy arrays
    simulation_returns_1 = {'equity': np.zeros((no_simulations, no_years))}
    equity_simulated_1 = []
    for i in range(no_simulations):
        simulation_returns_1['equity'][i, :] = np.random.normal(loc=mu_equity, scale=sigma_equity, size=no_years)
        end_bal = np.prod([(0.01*a+1) for a in simulation_returns_1['equity'][i]])
        equity_simulated_1.append(end_bal)


    # Find 10th, 25th ... percentiles
    equity_index = {}

    for percentile in [10, 25, 50, 75]:
        equity_percentile_1 = np.percentile(equity_simulated_1, percentile)
        equity_index[percentile] = np.argmin(np.abs(equity_simulated_1 - equity_percentile_1))


    return simulation_returns_1, equity_index, equity_simulated_1

sim_returns, equity_index, equity_simulated_1 = monte_carlo_simulation(10,18,10,
                                          5)
print(sim_returns)
print(equity_index)


sig_below_avg_returns = {'equity': np.round(sim_returns['equity'][equity_index[25],:],2),}


print(sig_below_avg_returns)

inflation = 2.5
sig_below_avg_returns_current = {'equity': np.round([sig_below_avg_returns['equity'][i] / ((1 + inflation * 0.01) ** (i))
                                     for i in range(len(sig_below_avg_returns['equity']))],2)}


#print(sig_below_avg_returns_current)
data = np.array([105, 150, 91, 95, 200, 170, 90, 130])
percentile_value = np.percentile(data, 10)

# Get index of the closest value
index = np.argmin(np.abs(data - percentile_value))
print(percentile_value)
print(index)

lst = [2, 3, 4]
result = np.prod([x + 1 for x in lst])
print(result)