import tkinter as tk
from tkinter import filedialog
import yaml
from mdm_query import *


class Customer:
    def __init__(self, name, acreage):
        self.name, self.acreage, self.allowance, self.meters, self.usage = name, acreage, None, None, None
        self.__acc_party = None

    def set_acc_party(self, acc_party):
        self.__acc_party = acc_party

    def set_allowance(self, allowance):
        self.allowance = allowance

    def set_meters(self, meters):
        self.meters = meters

    def set_usage(self, usage):
        self.usage = usage

    def get_acc_party(self):
        return self.__acc_party


def calculate_budget(acres):
    return (acres * 0.83 * 7.48) / 1000


def file_explorer():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()


if __name__ == "__main__":
    file_selected = file_explorer()  # needs error handling
    with open(file_selected, 'r') as file:
        data = yaml.safe_load(file)

    date = input('Enter target date like YYYY-MM-DD: ')

    customers = []
    for i in data:
        customer = Customer(name=i['customerName'], acreage=i['irrigatableArea'])
        customer.set_acc_party(acc_party=i['customerNumber'])
        customer.set_allowance(allowance=calculate_budget(i['irrigatableArea']))
        customer.set_meters(meters=i['meters'])
        customer.set_usage(usage=query_mdm_intervals(customer.get_acc_party(), date))
        customers.append(customer)

    for customer in customers:
        print(customer.name)
        print(customer.allowance, 'kgals')
        print(customer.usage)

# Deliverables?
# Can we just have the query return a sum of usage between the dates
# what happens if its not equitable
#