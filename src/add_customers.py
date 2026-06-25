#add_customers.py
import os
import sys
import pandas as pd

#-->bu kodları bulamazsan gir şuraya bak: /opt/airflow/project/Scripts
# sys.path.append('/opt/airflow/project/Scripts')
from db_connection import get_db_engine

from dotenv import load_dotenv
load_dotenv()
CSV_YOLU = os.getenv("CUSTOMER_DATA_YOLU")
df = pd.read_csv(CSV_YOLU)

orijinal_sutunlar = ["Name", "City", "Gender"] 
df = df[orijinal_sutunlar]

sutun_haritasi = {"Name": "name", "City": "city", "Gender": "gender"}
df = df.rename(columns=sutun_haritasi)

# BAĞLANTIYI MERKEZDEN ALIYORUZ
engine = get_db_engine()

df.to_sql(name="customers", con=engine, if_exists="append", index=False)
print("Müşteri verileri AWS PostgreSQL'e yüklendi!")