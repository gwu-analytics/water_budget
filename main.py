import datetime
from openpyxl import Workbook
from methods import *
from customer import Customer
from meter import Meter
from formatting import *


def main():
    logging.info("Process Started")

    input_file = 'L:/Division/Water Utility/4_UTILITY_SUPPORT/Analytics/Products/Large Property Variance/data_file/sample_book.xlsx'
    output_file = 'L:/Division/Water Utility/4_UTILITY_SUPPORT/Analytics/Products/Large Property Variance/output_files/'

    # Instantiate data df
    data = init_df(input_file)

    # Perform date calc, get calculated monday from previous week
    today = datetime.date.today()
    date = (pd.Timestamp(today) - pd.Timedelta(days=pd.Timestamp(today).dayofweek + 7)).date()

    # Instantiate dcp manually
    dcp = 1

    customers = []
    for row in data.itertuples(index=True, name='Customer'):
        # Create customer obj and set object variables from data file
        customer = Customer(name=row.CustomerName, footage=row.IrrigatableArea)
        customer.set_acc_party(acc_party=row.CustomerNumber)
        customer.set_allowance(allowance=calculate_budget(row.IrrigatableArea, dcp))

        # [IRRIGATION] Query usage data, return hourly reads, count violations
            # print('Meter:', meter, '\nAccount:', customer.get_acc_party(), '\nDate:', date)
        if row.Type == 'MDM':
            meter_data = query_mdm_intervals(row.IrrigationMeters, date, str(customer.get_acc_party()))
        else:
            # VariableID is hard-coded with the assumption that there is only one variable ID. If another
            # customer were added with multiple meters, they would also have multiple VIDs. Would need update
            meter_data = query_dh(str(int(row.IrrigationMeters)), date, str(int(row.VariableID)))

            meter_obj = Meter(row.IrrigationMeters, 'Irrigation', meter_data)

        # Give customer object the meter and type
        customer.add_meter(current_meter_obj=meter_obj)
        customer.type == row.Type
        # Add all usage from current meter to running usage total
        customer.add_usage(meter_data.ReadValue.sum())

        customer.mon_viol = monday_violations(meter_data)

        # Calculate midday or Monday violations given DCP
        # These are only done on irrigation meters b/c it is impossible to separate
        # domestic usage from irrigation due to sheer volume of usage in large multi-fam properties
        if dcp < 3:
            customer.mid_viol = midday_violations(meter_data, dcp)
        elif dcp >= 3:
            customer.irrig_viol = irrigation_violations(meter_data)

        # If total usage from all meters exceeds customer budget, add violation
        if customer.usage > customer.allowance and dcp < 3:
            customer.bug_viol = 1

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

    wb.save(output_file + 'output.xlsx')

    logging.info("Process completed\n" + "=" * 50)


if __name__ == "__main__":
    main()
