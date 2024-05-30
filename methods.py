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
				ReadDate, 
				MeterIdentifier
            FROM
                ODM.IntervalReads
            WHERE
                AccountNumber = :acc_num
			AND
				MeterIdentifier = :meter_id
            AND
                ReadDate BETWEEN :date AND DATEADD(DAY, 7, :date)
    """)

    odm_engine = create_engine(odm)

    return pd.read_sql(odm_1, odm_engine, params={'acc_num': acc_num, 'meter_id': meter_id, 'date': date})


def calculate_budget(acres, dcp_num):
    if dcp_num == 0:
        return (acres * 1 * 7.48) / 1000
    elif dcp_num == 1:
        return (acres * 0.75 * 7.48 * dcp_num) / 1000
    elif dcp_num == 2:
        return (acres * 0.5 * 7.48 * dcp_num) / 1000
    else:
        return 1


# Returns most recent Monday prior to date entered (returns same date if already Monday)
def calculate_monday(date):
    return pd.Timestamp(date) - pd.Timedelta(days=pd.Timestamp(date).dayofweek)


def irrigation_violations(df):
    df.ReadDate = pd.to_datetime(df.ReadDate).dt.date
    df = df.groupby('ReadDate')['ReadValue'].sum().reset_index()
    return len(df[df.ReadValue > 0].index)


def midday_violations(df, dcp):
    if dcp == 1:
        start = pd.to_datetime('09:00:00').time()
        end = pd.to_datetime('20:00:00').time()
    if dcp == 2:
        start = pd.to_datetime('07:00:00').time()
        end = pd.to_datetime('12:00:00').time()
    df.ReadDate = pd.to_datetime(df.ReadDate)
    midday_df = df[(df.ReadDate.dt.time >= start) & (df.ReadDate.dt.time <= end)]
    midday_df.ReadDate = pd.to_datetime(midday_df.ReadDate).dt.date
    midday_df = midday_df.groupby('ReadDate')['ReadValue'].sum().reset_index()
    return len(midday_df[midday_df.ReadValue > 0].index)

def file_explorer():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()