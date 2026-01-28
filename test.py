import datetime
from openpyxl import Workbook
from methods import *
from customer import Customer
from meter import Meter
from formatting import *

today = datetime.date.today()
date = (pd.Timestamp(today) - pd.Timedelta(days=pd.Timestamp(today).dayofweek + 7)).date()

meter_data = query_dh(str('33361'), date, str('68561'))

meter_data.to_csv('data/test_output.csv', index=False)