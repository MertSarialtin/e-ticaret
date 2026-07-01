#dag_customers.py
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='customers_calistirici',
    description='Her 3 dakikada bir harici scripti calistirir',

    schedule_interval='*/3 * * * *',
    
    start_date=datetime(2026, 6, 22), 
    catchup=False, 
) as dag:
    
    urunleri_listele = BashOperator(
        task_id='seed_customers_scriptini_tetikle', 
        bash_command='python3 /opt/airflow/scripts/seed_customers.py',
    )
    urunleri_kaydet = BashOperator(
        task_id='add_customers_scriptini_tetikle', 
        bash_command='python3 /opt/airflow/scripts/add_customers.py',
    )
    urunleri_listele >> urunleri_kaydet
