import pyodbc
from sqlalchemy import create_engine, text
import pandas as pd


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

    data = pd.read_sql(odm_1, odm_engine, params={'acc_num': acc_num, 'meter_id': meter_id, 'date': date})
