import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text
import openpyxl


odm = (
    'mssql+pyodbc:///?odbc_connect='
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.95.56\\UCENTRA;'
    'DATABASE=ODMReporting;'
    'UID=odmreport;'
    'PWD=odmreport;'
)

odm_query = text("""
    SELECT QUERY HERE
""")


class Customer:
    def __init__(self, name, acreage):
        self.name, self.acreage, self.allowance, self.meters, self.usage = name, acreage, None, None, None
        self.__acc_party = acc_party

    def set_acc_party(self, acc_party):
        self.__acc_party = acc_party

    def set_allowance(self, allowance):
        self.allowance = allowance

    def set_meters(self, meters):
        self.meters = meters

    def set_usage(self, usage):
        self.usage = usage


def calculate_budget(acres):
    return (acres * 43560 * 0.83 * 7.48) / 1000


if __name__ == "__main__":
    # file = file picker
    customers = pd.read_csv(file)

    odm_engine = create_engine(odm)

    # Get analysis period
    # - Get last full week?
    # - Get last seven days?

    for index, row in customers.iterrows():
        customer = Customer(name=row['name'], acreage=row['acres'])
        customer.set_acc_party(acc_party=row['acc_party'])
        customer.set_allowance(allowance=calculate_budget(row['acres']))

        customer.set_meters(pd.read_sql(odm_query, odm_engine))
