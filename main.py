import tkinter as tk
from tkinter import filedialog
import yaml
from mdm_query import *
import datetime
import openpyxl


class Customer:
    def __init__(self, name, footage):
        self.name, self.footage, self.allowance, self.meters = name, footage, None, None
        self.mon_viol, self.mid_viol, self.bug_viol = None, None, None
        self.water, self.irrigation = [], []
        self.__acc_party = None

    def set_acc_party(self, acc_party):
        self.__acc_party = acc_party

    def set_allowance(self, allowance):
        self.allowance = allowance

    def set_meters(self, meters):
        self.meters = meters

    def set_viols(self, mon, mid, bug):
        self.mon_viol, self.mid_viol, self.bug_viol = mon, mid, bug

    def get_acc_party(self):
        return self.__acc_party


class Meter:
    def __init__(self):
        self.type, self.data = None, None

    def set_meters(self, meter_type, meter_data):
        self.type, self.data = meter_type, meter_data


def calculate_budget(acres, dcp):
    return (acres * 0.83 * 7.48 * dcp) / 1000


def file_explorer():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()


if __name__ == "__main__":

    print('=' * 50)
    print('Master-Metered Community Violation Application\nWater Analytics 2024')
    print('=' * 50 + '\n- Select your data file.\n')

    file_selected = file_explorer()
    data = pd.read_excel(file_selected)

    while True:  # needs date conversion to past monday or something
        try:
            date = input('- Enter target date like YYYY-MM-DD: ')
            datetime.date.fromisoformat(date)
            break
        except ValueError:
            print('Date format is YYYY-MM-DD.')

    cust_choice = input('- Enter 1 for a full report, or 2 for a single customer report: ')
    while cust_choice != '1' and cust_choice != '2':
        cust_choice = input(' > Enter only a 1 or 2, please:')
    if cust_choice == '2':
        cust_choice = input('- Enter the account number for your customer: ')  # needs error handling

    dcp = int(input('- Enter the current DCP stage, from 0 to 4: '))
    while dcp not in range(0, 4):
        dcp = int(input('- It has to be 0, 1, 2, 3, or 4, please: '))

    print('Thank you! Please hold while we generate your data.')

    customers = []
    for row in data.itertuples(index=True, name='Customer'):
        customer = Customer(name=row.CustomerName, footage=row.IrrigatableArea)
        customer.set_acc_party(acc_party=row.CustomerNumber)
        customer.set_allowance(allowance=calculate_budget(row.IrrigatableArea, dcp))
        

        # Querying usage data and returning hourly reads


        # Parsing reads and counting number of violations by type
        customers.append(customer)

    print('=' * 50)
    for customer in customers:
        print('Generated data for', customer.name)
        # Excel output
