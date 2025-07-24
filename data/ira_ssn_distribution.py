

def rmd_distribution():
    rmd = [26.5, 25.5, 24.6, 23.7, 22.9, 22.0, 21.1, 20.2, 19.4, 18.5, 17.7, 16.8, 16.0,
           15.2, 14.4, 13.7, 12.9, 12.2, 11.5, 10.8, 10.1, 9.5, 8.9, 8.4, 7.8, 7.3, 6.8, 6.4]
    rmd_start = 75
    return rmd, rmd_start

def ssn_tax_factor(agi):
    #if AGI is more than $ then 50% is taxable, if more than 100000, 85% is taxable
    if agi > 100000:
        tax_factor = 0.85
    elif 50000 < agi < 100000:
        tax_factor = 0.5
    else:
        tax_factor = 0
    return tax_factor
