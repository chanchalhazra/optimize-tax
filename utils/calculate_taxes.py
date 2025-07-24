import numpy as np
import pandas as pd

from data import tax_rates
from data.tax_rates import get_income_tax_rates, get_capital_gain_tax_rates
from data.state_taxrates import get_state_tax_rates

inc_tax_rates = get_income_tax_rates(filing_as='Single')
gain_tax_rates = get_capital_gain_tax_rates(filing_as='Single')
state_tax_rates = get_state_tax_rates(state='California', filing_as='Single', )
#print(state_tax_rates)
taxable_income = 12000000

def calculate_income_tax(tax_rates, taxable_income):
    tax=[]
    if taxable_income > 0:
        for i in range(tax_rates.shape[0]):
            to_amt = tax_rates.iloc[i]['to']
            from_amt = tax_rates.iloc[i]['from']
            rate = tax_rates.iloc[i]['rate']
            if taxable_income >= to_amt:
                tax.append(np.ceil((to_amt-from_amt)*rate*0.01))
            else:
                tax.append(np.ceil((taxable_income-from_amt)*rate*0.01))
                break
    #print(tax)
    return tax

def calculate_gain_tax(tax_rates, taxable_income, long_gain):
    gain_tax = []
    rate = 0
    gross_income = taxable_income+long_gain
    if gross_income > 0:
        for i in range(tax_rates.shape[0]):
            to_amt = tax_rates.iloc[i]['to']
            from_amt = tax_rates.iloc[i]['from']
            rate = tax_rates.iloc[i]['rate']
            if gross_income <= to_amt:
                gain_tax.append(np.ceil(long_gain*rate*0.01))
                break
            else:
                gain_tax.append(0)

    #print(gain_tax)
    return gain_tax, rate
'''
W-2 Box 1 = Gross Salary
            - Pre-tax 401(k) contributions
            - Pre-tax health/dental/vision insurance
            - HSA/FSA contributions
            - Other pre-tax deductions
            + Taxable benefits (if any)
'''
def calculate_state_tax(tax_rates, taxable_income):
    state_tax = []
    if taxable_income > 0:
        for i in range(tax_rates.shape[0]):
            to_amt = tax_rates.iloc[i]['to']
            from_amt = tax_rates.iloc[i]['from']
            rate = tax_rates.iloc[i]['rate']
            if taxable_income >= to_amt:
                state_tax.append(np.ceil((to_amt-from_amt)*rate*0.01))
            else:
                state_tax.append(np.ceil((taxable_income-from_amt)*rate*0.01))
                break
    #print(state_tax)
    return state_tax

#calculate_income_tax(inc_tax_rates, taxable_income=50000)
#calculate_gain_tax(gain_tax_rates, taxable_income=0, long_gain=50000)
calculate_state_tax(state_tax_rates, taxable_income=50000)