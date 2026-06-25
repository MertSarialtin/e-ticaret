#dag_products.py
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

# DAG'ı tanımlıyoruz
with DAG(
    dag_id='gunluk_products_calistirici', #apache airflow da görünür 
    description='Her gun saat 12:00de harici scripti calistirir', # kendine aciklama
    
    # 1. ZAMANLAMA: Her gün saat 12:00'de çalışması için iCal/Cron mantığı kullanıyoruz
    schedule_interval='0 9 * * *', 
    
    # DAG'ın aktif olacağı başlangıç tarihi
    start_date=datetime(2026, 6, 22), 
    catchup=False, #bugunden itibaren calismaya baslar, gecmis tarihleri calistirmaya calismaz
) as dag:

    # 2. GÖREV: BashOperator kullanarak terminale komut veriyoruz
    urunleri_listele = BashOperator(
        task_id='seed_products_scriptini_tetikle', #Görevin Airflow arayüzündeki (UI) adı
        
        #BashOperator siyah ekranı açtıktan sonra buraya yazdığın metni kopyalar, 
        #terminale yapıştırır ve Enter tuşuna basar
        bash_command='python3 /opt/airflow/scripts/seed_products.py',
    )
    urunleri_kaydet = BashOperator(
        task_id='add_products_scriptini_tetikle', 
        bash_command='python3 /opt/airflow/scripts/add_products.py',
    )
    # Tek bir görevimiz olduğu için oklarla (>>) bir sıra belirtmemize gerek yok.
    urunleri_listele >> urunleri_kaydet