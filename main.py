import datetime
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
    # TODO: Log context
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

    if call_type == 0:  # Called via task-scheduler, uses config.ini for report settings.

        print("...Loading data from config.ini...\n")

        # TODO: build config handler
        # Read pre-defined data file into df
        target_file = config_data['data_path']  # TODO: change to dynamic file selection from config
        destination_file = config_data['output_path']  # TODO: Review code, eliminate if unneeded.

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
            # print('Meter:', meter, '\nAccount:', customer.get_acc_party(), '\nDate:', date)
            meter_data = query_mdm_intervals(meter, date, str(customer.get_acc_party()))
            meter_obj = Meter(meter, 'Domestic', meter_data)

            customer.add_meter(current_meter_obj=meter_obj)

        # [IRRIGATION] Query usage data, return hourly reads, count violations
        irrig_meters = row.IrrigationMeters.split(', ')
        for meter in irrig_meters:
            # print('Meter:', meter, '\nAccount:', customer.get_acc_party(), '\nDate:', date)
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

    for i, customer in enumerate(customers):
        ws.cell(row=i + 2, column=1).value = customer.name
        ws.cell(row=i + 2, column=2).value = customer.get_acc_party()
        ws.cell(row=i + 2, column=3).value = customer.bug_viol
        ws.cell(row=i + 2, column=4).value = customer.irrig_viol
        ws.cell(row=i + 2, column=5).value = customer.mid_viol
        ws.cell(row=i + 2, column=6).value = customer.mon_viol
        ws.cell(row=i + 2, column=7).value = customer.allowance
        ws.cell(row=i + 2, column=8).value = customer.usage

    wb.save('output.xlsx')

    network_dump('output.xlsx', config_data['output_path'])

    logging.info("Process completed\n" + "=" * 50)


if __name__ == "__main__":
    main()
