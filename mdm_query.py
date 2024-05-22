import pyodbc
import datetime

def query_mdm_intervals(serial_id, start_date):
    # Instantiate connection as cnxn
    cnxn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                          "SERVER=192.168.95.56\\UCENTRA;"
                          "DATABASE=ODMReporting;"
                          "UID=odmreport;"
                          "PWD=odmreport;")

    # Instantiate cursor as cursor...
    cursor = cnxn.cursor()

    # Instantiate query
    # TODO Convert the start_date argument to a datetime object, then do some maths on it to get the seven day range...
    query = f"""
            SELECT 
                SUM(ReadValue)
            FROM
                ODM.IntervalReads
            WHERE
                MeterIdentifier = {serial_id}
            AND
                ReadDate BETWEEN {start_date} AND DATEADD(DAY, 7, {start_date})
            """

    # execute query
    cursor.execute(query)
    print(cursor.fetchall(), type(cursor.fetchall()))

    # Close cursor and connection
    cursor.close()
    cnxn.close()
