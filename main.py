import datetime
from openpyxl import Workbook
from methods import *
from customer import Customer
from meter import Meter


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
    while dcp not in range(0, 4):
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
            # Convert dates to weekdays only, filter for Mondays and any value exists
            if dcp in range(1, 2):
                customer.mid_viol = midday_violations(meter_data)
            elif dcp >= 3:
                customer.irrig_viol = irrigation_violations(meter_data)

        # If total usage from all meters exceeds customer budget, add violation
        if customer.usage > customer.allowance:
            customer.bug_viol = 1

        # Parsing reads and counting number of violations by type
        customers.append(customer)

    print('=' * 50)
    for customer in customers:
        print('Generated data for', customer.name)
        print('Budget violations:', customer.bug_viol)
        print('Irrigation violations:', customer.irrig_viol)
        print('Customer Usage:', customer.usage)
        print('=' * 50)
        """
        wb = Workbook()
        ws = wb.active
        ws.title = 'Summary'
        ws['A1'] = 'Summary'
        ws['A2'] = 'Week of ' + date
        ws['A3'] = customer.bug_viol
        ws['A4'] = customer.irrig_viol
        """
