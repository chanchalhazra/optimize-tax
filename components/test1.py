import numpy as np

def monte_carlo_simulation(mu_equity, sigma_equity, no_simulations, no_years):

    np.random.seed(4562)

    # initialize simulation returns as Numpy arrays

    equity_simulated_1 = []
    #simulation_returns = {}
    simulation_returns = {'equity': 0.01 * np.random.normal(loc=mu_equity, scale=sigma_equity,
                                                            size=(no_simulations, no_years))}
    #growth_factor = 1 + simulation_returns['equity']
    end_balances = np.prod(1 + simulation_returns['equity'], axis=1)



    # Find 10th, 25th ... percentiles
    equity_index = {}

    for percentile in [10, 25, 50, 75]:
        equity_percentile_1 = np.percentile(end_balances, percentile)
        equity_index[percentile] = np.argmin(np.abs(end_balances - equity_percentile_1))


    return simulation_returns, equity_index, end_balances

sim_returns, equity_index, end_balances = monte_carlo_simulation(10,18,10,
                                          5)
print(sim_returns)
print(end_balances)
print(equity_index)

print(f"10th percentile returns are {sim_returns['equity'][equity_index[10]]}")

lst = np.array([-0.1152631 ,  0.14114392,  0.38237757,  0.10902725,  0.20513148])
lst_1 = 1+lst
print(lst_1)
print(np.prod(lst_1, axis=0))

