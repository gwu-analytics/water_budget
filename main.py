import datetime
from openpyxl import Workbook
from methods import *
from customer import Customer
from meter import Meter
from formatting import *

if __name__ == "__main__":

    print('=' * 50)
    print('Master-Metered Community Violation Application\nWater Analytics 2024')
    print('=' * 50 + '\n- Select your data file.\n')

    file_selected = file_explorer()
    data = pd.read_excel(file_selected)
    data.WaterMeters = data.WaterMeters.astype(str)
    data.IrrigationMeters = data.IrrigationMeters.astype(str)

    while True:
        try:
            date = input('- Enter target date like YYYY-MM-DD: ')
            datetime.date.fromisoformat(date)
            break
        except ValueError:
            print('Date format is YYYY-MM-DD.')
    date = calculate_monday(date)

    cust_choice = input('- Enter 1 for a full report, or 2 for a single customer report: ')
    while cust_choice != '1' and cust_choice != '2':
        cust_choice = input(' > Enter only a 1 or 2, please:')
    if cust_choice == '2':
        cust_choice = input('- Enter the account number for your customer: ')
        while len(cust_choice) != 8:
            cust_choice = input('- Number must be 8 characters long: ')

    dcp = int(input('- Enter the current DCP stage, from 0 to 4: '))
    while dcp not in range(5):
        dcp = int(input('- It has to be 0, 1, 2, 3, or 4, please: '))

    print('Thank you! Please hold while we generate your data.')

    customers = []
    for row in data.itertuples(index=True, name='Customer'):
        customer = Customer(name=row.CustomerName, footage=row.IrrigatableArea)
        customer.set_acc_party(acc_party=row.CustomerNumber)
        customer.set_allowance(allowance=calculate_budget(row.IrrigatableArea, dcp))

        # [WATER] Query usage data, return hourly reads, count violations
        water_meters = row.WaterMeters.split(', ')
        for meter in water_meters:
            meter_data = query_mdm_intervals(meter, date, str(customer.get_acc_party()))
            meter_obj = Meter(meter, 'water', meter_data)

            customer.add_meter(current_meter_obj=meter_obj)
            customer.add_usage(meter_data.ReadValue.sum())

        # [IRRIGATION] Query usage data, return hourly reads, count violations
        irrig_meters = row.IrrigationMeters.split(', ')
        for meter in irrig_meters:
            meter_data = query_mdm_intervals(meter, date, str(customer.get_acc_party()))
            meter_obj = Meter(meter, 'water', meter_data)

            customer.add_meter(current_meter_obj=meter_obj)
            customer.add_usage(meter_data.ReadValue.sum())

            customer.mon_viol = monday_violations(meter_data)
            if dcp in range(1, 2):
                customer.mid_viol = midday_violations(meter_data, dcp)
            elif dcp >= 3:
                customer.irrig_viol = irrigation_violations(meter_data)

        # If total usage from all meters exceeds customer budget, add violation
        if customer.usage > customer.allowance:
            customer.bug_viol = 1

        # Parsing reads and counting number of violations by type
        customers.append(customer)

    # Create workbook
    wb = Workbook()
    ws = wb.active

    # Manually set column widths of output file
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 20
    ws.column_dimensions['G'].width = 20
    ws.column_dimensions['H'].width = 18
    ws.column_dimensions['J'].width = 18
    ws.column_dimensions['L'].width = 10

    # Manually set column names,
    ws.cell(row=1, column=1).value = 'Customer Name'
    ws.cell(row=1, column=1).border = thin_border
    ws.cell(row=1, column=1).font = bold_font
    ws.cell(row=1, column=2).value = 'Customer Number'
    ws.cell(row=1, column=2).border = thin_border
    ws.cell(row=1, column=2).font = bold_font
    ws.cell(row=1, column=3).value = 'Budget Violation'
    ws.cell(row=1, column=3).border = thin_border
    ws.cell(row=1, column=3).font = bold_font
    ws.cell(row=1, column=4).value = 'Irrigation Violations'
    ws.cell(row=1, column=4).border = thin_border
    ws.cell(row=1, column=4).font = bold_font
    ws.cell(row=1, column=5).value = 'Mid-day Violations'
    ws.cell(row=1, column=5).border = thin_border
    ws.cell(row=1, column=5).font = bold_font
    ws.cell(row=1, column=6).value = 'Monday Violations'
    ws.cell(row=1, column=6).border = thin_border
    ws.cell(row=1, column=6).font = bold_font
    ws.cell(row=1, column=7).value = 'Customer Budget'
    ws.cell(row=1, column=7).border = thin_border
    ws.cell(row=1, column=7).font = bold_font
    ws.cell(row=1, column=8).value = 'Customer Usage'
    ws.cell(row=1, column=8).border = thin_border
    ws.cell(row=1, column=8).font = bold_font
    ws['J1'] = 'Week Of'
    ws['J1'].border = thin_border
    ws['J1'].font = bold_font
    ws['J2'] = date
    ws['L1'] = 'DCP Stage'
    ws['L1'].border = thin_border
    ws['L1'].font = bold_font
    ws['L2'] = dcp

    print('=' * 50)
    for i, customer in enumerate(customers):
        print('Generated data for', customer.name)
        if dcp < 3:
            print('Budget violations:', customer.bug_viol)
            print('Irrigation violations: N/A')
        else:
            print('Budget violations: N/A')
            print('Irrigation violations:', customer.irrig_viol)
        print('Mid-day violations:', customer.mid_viol)
        print('Monday violations:', customer.mon_viol)
        print('Customer Budget:', customer.allowance)
        print('Customer Usage:', customer.usage)
        print('=' * 50)

        ws.cell(row=i + 2, column=1).value = customer.name
        ws.cell(row=i + 2, column=2).value = customer.get_acc_party()
        ws.cell(row=i + 2, column=3).value = customer.bug_viol
        ws.cell(row=i + 2, column=4).value = customer.irrig_viol
        ws.cell(row=i + 2, column=5).value = customer.mid_viol
        ws.cell(row=i + 2, column=6).value = customer.mon_viol
        ws.cell(row=i + 2, column=7).value = customer.allowance
        ws.cell(row=i + 2, column=8).value = customer.usage

    while True:
        try:
            wb.save('output.xlsx')
            break
        except PermissionError:
            print('Please save output file if file is already open! Please close file now.')
            print('Attempting to save output file...')
