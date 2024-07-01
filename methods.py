import pyodbc
from sqlalchemy import create_engine, text
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def query_mdm_intervals(meter_id, date, acc_num):
    odm = (
        'mssql+pyodbc:///?odbc_connect='
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.95.56\\UCENTRA;'
        'DATABASE=ODMReporting;'
        'UID=odmreport;'
        'PWD=odmreport;'
    )

    odm_1 = text("""
        SELECT 
                ReadValue,
				ReadDate
            FROM
                ODM.IntervalReads
            WHERE
                AccountNumber = :acc_num
			AND
				MeterIdentifier = :meter_id
            AND
                ReadDate >= :date AND ReadDate < DATEADD(DAY, 7, :date)
    """)

    odm_engine = create_engine(odm)
    dataframe = pd.read_sql(odm_1, odm_engine, params={'acc_num': acc_num, 'meter_id': meter_id, 'date': date})
    odm_engine.dispose()
    return dataframe


def calculate_budget(acres, dcp_num):
    if dcp_num == 0:
        return (acres * (1 / 12) * 7.48) / 1000
    elif dcp_num == 1:
        return (acres * (0.75 / 12) * 7.48) / 1000
    elif dcp_num == 2:
        return (acres * (0.5 / 12) * 7.48) / 1000
    else:
        return 0


# Returns most recent Monday prior to date entered (returns same date if already Monday)
def calculate_monday(date):
    # Returning datetime or timestamp object causes query to run indefinitely, so return as str
    return str(pd.Timestamp(date) - pd.Timedelta(days=pd.Timestamp(date).dayofweek))


def irrigation_violations(df):
    # Create a deep copy of the dataframe to prevent any modifications to the original
    irr_df = df.copy(deep=True)
    # Strip all times from the datetimes - we want only dates
    irr_df.ReadDate = pd.to_datetime(irr_df.ReadDate).dt.date
    # Group all reads by their date, and sum all 24 ReadValue values for each of the 7 days of week
    irr_df = irr_df.groupby('ReadDate')['ReadValue'].sum().reset_index()
    # If the irrigation meter displays any non-zero reads at any point, return the number of days in violation
    return len(irr_df[irr_df.ReadValue > 0].index)


def midday_violations(df, dcp):
    # Start times are one hour ahead of actual times
    if dcp == 1:
        start = pd.to_datetime('10:00:00').time()
        end = pd.to_datetime('19:00:00').time()
    elif dcp == 2:
        start = pd.to_datetime('08:00:00').time()
        end = pd.to_datetime('19:00:00').time()
    midday_df = df.copy()
    midday_df.ReadDate = pd.to_datetime(midday_df.ReadDate)
    midday_df = midday_df[(midday_df.ReadDate.dt.time >= start) & (midday_df.ReadDate.dt.time <= end)]
    midday_df.ReadDate = midday_df.ReadDate.dt.date
    # Group all values by day and sum of all day reads
    midday_df = midday_df.groupby('ReadDate')['ReadValue'].sum().reset_index()
    return len(midday_df[midday_df.ReadValue > 0])


def monday_violations(df):
    # Will return 1 if any row found where the day is Monday and the hourly read is greater than 0
    if len(df[(pd.to_datetime(df.ReadDate).dt.day_name() == 'Monday') & (df.ReadValue > 0)]) > 0:
        return 1
    else:
        return 0


def file_explorer():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()
