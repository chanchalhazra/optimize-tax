import numpy as np
import pandas as pd


def get_state_tax_rates(state, filing_as):
    state_taxes = {}

    state_taxes[("California",'Single')] = pd.DataFrame({
            "from": [0, 10757, 25500, 40246, 55867, 70607,360660, 432788, 721315],
            "to": [10756, 25499, 40245, 55866, 70606,360659, 432787, 721314, np.inf],
            "rate": [1, 2, 4, 6, 8, 9.3, 10.3, 11.3, 12.3]
        })
    state_taxes[("California", 'Married')] = pd.DataFrame({
        "from": [0, 21513, 50999, 80491, 111733, 141213, 721319, 865575, 1442629],
        "to": [21512, 50998, 80490, 111732, 141212, 721318, 865574, 1442628, np.inf],
        "rate": [1, 2, 4, 6, 8, 9.3, 10.3, 11.3, 12.3]
    })
    state_taxes[("California", 'Head')] = pd.DataFrame({
        "from": [0, 21528, 51001, 65745, 81365, 96108, 490494, 588594, 980988],
        "to": [21527, 51000, 65744, 81364, 96107, 490493, 588593, 980987, np.inf],
        "rate": [1, 2, 4, 6, 8, 9.3, 10.3, 11.3, 12.3]
    })
    #Oregon
    state_taxes[("Oregon", 'Single')] = pd.DataFrame({
        "from": [0, 4301, 10751, 125001],
        "to": [4300, 10750, 125000, np.inf],
        "rate": [4.75, 6.75, 8.75, 9.9]
    })
    state_taxes[("Oregon", 'Married')] = pd.DataFrame({
        "from": [0, 8601, 21501, 250001],
        "to": [8600, 21500, 250000, np.inf],
        "rate": [4.75, 6.75, 8.75, 9.9]
    })
    state_taxes[("Oregon", 'Married')] = pd.DataFrame({
        "from": [0, 8601, 21501, 250001],
        "to": [8600, 21500, 250000, np.inf],
        "rate": [4.75, 6.75, 8.75, 9.9]
    })


    #state_standard_deduction['CA'] = {'Single': 15000, 'Married': 30000, 'Head': 21000}

    return state_taxes[(state, filing_as)]

#rate = get_state_tax_rates("California",'Single')
#print(rate)