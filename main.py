import datetime
import time #TODO: Is this import deprecated?
from openpyxl import Workbook
from methods import *
from customer import Customer
from meter import Meter
from formatting import *


def main():

    logging.info("Process Started")

    args = parse_call_arguments()

    if args.context_override != 0:
        context = args.context_override
    else:
        context = check_execution_context()
    #TODO: Log context
    check_for_config()

    call_type = 1

    # Testing feature: call_type switch on override
    if context == 1:
        call_type = 0
    
    config_data = read_config()

    logging.info(f"call_type = {call_type}")

    logging.info("Config elements")
    logging.info("=" * 50)
    for k in config_data:
        logging.info(f"{k}: {config_data[k]}")

    if call_type == 1:

        print('=' * 50)
        print('Master-Metered Community Violation Application\nWater Analytics 2024')
        print('=' * 50)


        # Setup job
        print('\n- Select your data file.')

        # Display file explorer, get data file, convert meter lists to str
        file_selected = file_explorer()
        data = init_df(file_selected)

        # Collect target date from user, check for correct format.
        while True:
            try:
                date = input('- Enter target date like YYYY-MM-DD: ')
                datetime.date.fromisoformat(date)
                break
            except ValueError:
                print('Date format is YYYY-MM-DD.')
        # Grab closest prior Monday
        date = str(calculate_monday(date))

        cust_choice = input('- Enter 1 for a full report, or 2 for a single customer report: ')
        while cust_choice != '1' and cust_choice != '2':
            cust_choice = input(' > Enter only a 1 or 2, please:')
        if cust_choice == '2':
            cust_acc = int(input('- Enter the account number for your customer: '))
            data = data[data.CustomerNumber == cust_acc]

        dcp = int(input('- Enter the current DCP stage, from 0 to 4: '))
        while dcp not in range(5):
            dcp = int(input('- It has to be 0, 1, 2, 3, or 4, please: '))

        print('Thank you! Please hold...')
    
    elif call_type == 0: # Called via task-scheduler, uses config.ini for report settings.

        print("...Loading data from config.ini...\n")

        #TODO: build config handler
        # Read pre-defined data file into df
        target_file = config_data['data_path'] #TODO: change to dynamic file selection from config
        destination_file = config_data['output_path'] #TODO: Review code, eliminate if unneeded.

        # Instantiate data df
        data = init_df(target_file)

        # Perform date calc, get calculated monday from previous week
        today = datetime.date.today()
        delta = datetime.timedelta(weeks=1)
        date = today - delta
        date = str(calculate_monday(date))


        # For the automated report, we always use cust_choice 1
        cust_choice = 1

        # Instantiate dcp
        dcp = int(config_data['dcp_value'])

        print("Report variables:")
        print('=' * 50)
        print(f"Start Date:\t{date}")
        print(f"DCP:\t\t{dcp}")
        print(f"Target Path:\t{target_file}")
        print(f"Output Dir:\t{config_data['output_path']}")

        
        logging.info("Report variables:")
        logging.info('=' * 50)
        logging.info(f"Start Date:\t{date}")
        logging.info(f"DCP:\t\t\t{dcp}")
        logging.info(f"Target Path:\t{target_file}")
        logging.info(f"Output Dir:\t{config_data['output_path']}")
        logging.info("=" * 50)

    else:
        raise RuntimeError(f"Water Budget encountered a fatal error: invalid call_type; {call_type}")

    customers = []
    for row in data.itertuples(index=True, name='Customer'):
        # Create customer obj and set object variables from data file
        customer = Customer(name=row.CustomerName, footage=row.IrrigatableArea)
        customer.set_acc_party(acc_party=row.CustomerNumber)
        customer.set_allowance(allowance=calculate_budget(row.IrrigatableArea, dcp))

        # [WATER] Query usage data, return hourly reads, count violations
        water_meters = row.WaterMeters.split(', ')
        for meter in water_meters:
            #print('Meter:', meter, '\nAccount:', customer.get_acc_party(), '\nDate:', date)
            meter_data = query_mdm_intervals(meter, date, str(customer.get_acc_party()))
            meter_obj = Meter(meter, 'Domestic', meter_data)

            customer.add_meter(current_meter_obj=meter_obj)

        # [IRRIGATION] Query usage data, return hourly reads, count violations
        irrig_meters = row.IrrigationMeters.split(', ')
        for meter in irrig_meters:
            #print('Meter:', meter, '\nAccount:', customer.get_acc_party(), '\nDate:', date)
            meter_data = query_mdm_intervals(meter, date, str(customer.get_acc_party()))
            meter_obj = Meter(meter, 'Irrigation', meter_data)

            customer.add_meter(current_meter_obj=meter_obj)
            customer.add_usage(meter_data.ReadValue.sum())

            customer.mon_viol = monday_violations(meter_data)

            if dcp < 3:

                customer.mid_viol = midday_violations(meter_data, dcp)
            elif dcp >= 3:
                customer.irrig_viol = irrigation_violations(meter_data)

        # If total usage from all meters exceeds customer budget, add violation

        # Only use irrigation usage
        if customer.usage > customer.allowance and dcp < 3:
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
        ws.cell(row=i + 2, column=1).value = customer.name
        ws.cell(row=i + 2, column=2).value = customer.get_acc_party()
        ws.cell(row=i + 2, column=3).value = customer.bug_viol
        ws.cell(row=i + 2, column=4).value = customer.irrig_viol
        ws.cell(row=i + 2, column=5).value = customer.mid_viol
        ws.cell(row=i + 2, column=6).value = customer.mon_viol
        ws.cell(row=i + 2, column=7).value = customer.allowance
        ws.cell(row=i + 2, column=8).value = customer.usage

    if cust_choice == '2':

        if len(customers) == 0:
            print('Failed to locate customer! Ensure account number is correct.')

        for customer in customers:
            for i, meter in enumerate(customer.meters):
                ws = wb.create_sheet(meter.type, i+1)

                meter.data['day'] = meter.data['ReadDate']
                meter.data['day'] = pd.to_datetime(meter.data['day']).dt.day_name()

                ws['B1'] = 'Mon'
                ws['B1'].font, ws['B1'].border = bold_font, thin_border
                ws['C1'] = 'Tues'
                ws['C1'].font, ws['C1'].border = bold_font, thin_border
                ws['D1'] = 'Wed'
                ws['D1'].font, ws['D1'].border = bold_font, thin_border
                ws['E1'] = 'Thur'
                ws['E1'].font, ws['E1'].border = bold_font, thin_border
                ws['F1'] = 'Fri'
                ws['F1'].font, ws['F1'].border = bold_font, thin_border
                ws['G1'] = 'Sat'
                ws['G1'].font, ws['G1'].border = bold_font, thin_border
                ws['H1'] = 'Sun'
                ws['H1'].font, ws['H1'].border = bold_font, thin_border

                ws['A2'], ws['A3'], ws['A4'], ws['A5'] = '12:00 AM', '1:00 AM', '2:00 AM', '3:00 AM'
                ws['A6'], ws['A7'], ws['A8'], ws['A9']  = '4:00 AM', '5:00 AM', '6:00 AM', '7:00 AM'
                ws['A10'], ws['A11'], ws['A12'], ws['A13'] = '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM'
                ws['A14'], ws['A15'], ws['A16'], ws['A17'] = '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM'
                ws['A18'], ws['A19'], ws['A20'], ws['A21'] = '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM'
                ws['A22'], ws['A23'], ws['A24'], ws['A25'] = '8:00 PM', '9:00 PM', '10:00 PM', '11:00 PM'

                # Make start and end times for mid-day schedule gray
                if meter.type == 'Irrigation':
                    for k in range(1, 9):
                        ws.cell(row=21, column=k).fill = gray_fill
                        if dcp == 1:
                            ws.cell(row=11, column=k).fill = gray_fill
                        elif dcp == 2:
                            ws.cell(row=9, column=k).fill = gray_fill
                    for l in range(2, 26):
                        ws.cell(row=l, column=2).fill = orange_fill

                ws['K1'] = 'Meter'
                ws['K1'].font, ws['K1'].border = bold_font, thin_border
                ws['K2'] = meter.meter_id
                ws['L1'] = 'Type'
                ws['L1'].font, ws['L1'].border = bold_font, thin_border
                ws['L2'] = meter.type
                ws['M1'] = 'Sum of Usage (kgals)'
                ws['M1'].font, ws['M1'].border = bold_font, thin_border
                ws['M2'] = meter.data['ReadValue'].sum()

                ws['K9'] = 'Bold text indicates where an irrigation violation occurred'
                ws['K10'] = 'Gray cells mark the prohibited mid-day watering window'

                for j, row in meter.data.iterrows():
                    ws.cell(row=row.ReadDate.hour+2, column=row.ReadDate.weekday()+2).value = row.ReadValue

                    if dcp >= 3 and row.ReadValue > 0 and meter.type == 'Irrigation':
                        ws.cell(row=row.ReadDate.hour+2, column=row.ReadDate.weekday()+2).font = bold_font

    wb.save('output.xlsx')

    network_dump('output.xlsx', config_data['output_path'])

    logging.info("Process completed\n" + "=" * 50)

if __name__ == "__main__":
    main()
