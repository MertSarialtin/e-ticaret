#seed_customers.py
import os
import pandas as pd
import random
from faker import Faker

fake = Faker('tr_TR')
veri_sayisi = random.randint(10, 20) 

veri_listesi = []

for i in range(veri_sayisi):
    gender = random.choice(["Erkek", "Kadın"])
    
    if gender == "Erkek":
        name = fake.name_male()
    else:
        name = fake.name_female()
        
    city = fake.city()
    
    # ID alanını tamamen kaldırdık, sadece veritabanındaki diğer sütunları gönderiyoruz
    veri_listesi.append({
        "Name": name,
        "City": city,
        "Gender": gender
    })

df = pd.DataFrame(veri_listesi)

from dotenv import load_dotenv
load_dotenv()
# Bilgisayardaysan .env'deki C:/... yolunu alır, Docker'daysan yaml'daki /opt/... yolunu alır:
CSV_YOLU = os.getenv("CUSTOMER_DATA_YOLU")

df.to_csv(CSV_YOLU, index=False, encoding="utf-8")
print(df.head())
print(f"{veri_sayisi} yeni kişi kayıt oldu")