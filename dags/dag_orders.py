#dag_orders.py
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='saatlik_orders_calistirici',
    description='Her 1 saatte bir harici scripti calistirir',

    schedule_interval='0 * * * *',
    
    start_date=datetime(2026, 6, 22), 
    catchup=False, 
) as dag:
    urunleri_listele = BashOperator(
        task_id='order_management_scriptini_tetikle', 
        bash_command='python3 /opt/airflow/scripts/order_management.py',
    )
