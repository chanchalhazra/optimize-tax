import numpy as np
import pandas as pd

def get_income_tax_rates(filing_as):
    income_tax_rate_single = pd.DataFrame({
            "from":[0,11601,47151,100526,191951,243726,609351],
            "to":[11601,47151,100526,191951,243726,609351,np.inf],
            "rate":[10,12,22,24,32,35,37]
        })
    income_tax_rate_married = pd.DataFrame({
        "from": [0, 23201, 94301, 201051, 383901, 487451, 731201],
        "to": [23201, 94301, 201051, 383901, 487451, 731201, np.inf],
        "rate": [10, 12, 22, 24, 32, 35, 37]
    })

    income_tax_rate_head = pd.DataFrame({
        "from": [0, 11601, 47151, 100526, 191951, 243726, 609351],
        "to": [11601, 47151, 100526, 191951, 243726, 609351, np.inf],
        "rate": [10, 12, 22, 24, 32, 35, 37]
    })
    standard_deduction = {'Single': 15000, 'Married': 30000, 'Head': 21000}
    salt_cap = {'Single': 40000, 'Married': 40000, 'Head': 40000}
    if filing_as == "Single":
        income_tax_rate = income_tax_rate_single
    elif filing_as == "Married":
        income_tax_rate = income_tax_rate_married
    else:
        income_tax_rate = income_tax_rate_head
    return income_tax_rate, standard_deduction[filing_as], salt_cap[filing_as]

def get_capital_gain_tax_rates(filing_as):
    capital_gain_tax_rate_single = pd.DataFrame({
            "from":[0,48350,533400],
            "to":[48350,533400,np.inf],
            "rate":[0, 15, 20]
        })
    capital_gain_tax_rate_married = pd.DataFrame({
        "from": [0, 96700, 600050],
        "to": [96700, 600050, np.inf],
        "rate": [0, 15, 20]
    })

    capital_gain_tax_rate_head = pd.DataFrame({
        "from": [0, 64750, 566700],
        "to": [64750, 566700, np.inf],
        "rate": [0, 15, 20]
    })
    if filing_as == "Single":
        capital_gain_tax_rate = capital_gain_tax_rate_single
    elif filing_as == "Married":
        capital_gain_tax_rate = capital_gain_tax_rate_married
    else:
        capital_gain_tax_rate = capital_gain_tax_rate_head
    return capital_gain_tax_rate

