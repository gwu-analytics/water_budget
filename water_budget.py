'''
water_budget.py is a command line tool for determining the water budget for a list of customers.
It uses the inputs from a csv file to provide the requisite argument data (irrigation and regular meters, irrigatable land in acres, etc.)
And finally, it returns an iterable with visualizations for each customer as well as any violations they have incurred.

See readme.md for more details
'''

# Dependencies
import pandas as pd
import pyodbc
import openpyxl

# Pseudocode breakdown

# Class instantiation
    # A Class: Customer is instantiated to contain the following:
    # A dictionary with each of the customer's meters by type {"potable": [...], "irrigation": [...]}
    # The customer's irrigatable land in acres as float
    # The customer's budget volume allowance in kgals over tier 1 consumption calculated as 1" of water over their acres of irrigatable land
    # A Pandas dataframe for the customer's water use over the previous x days (specified at runtime, default of seven.)

# User specifies the target CSV

# For each row in target CSV, water_budget.py creates a Customer object

# Set analysis_period variable; starting date (user input or take today's date and calculate)
    # Default to last complete Monday-to-Monday week, or accept arg for start date

# By default, export the data into a excel sheet using openpyxl
    # For each customer, create a sheet which displays the customer usage profile visual, budget capacity visual, and details