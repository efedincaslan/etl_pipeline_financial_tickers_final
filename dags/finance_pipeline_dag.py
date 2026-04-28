from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='finance_pipeline', # Unique identifier in the UI
    start_date=datetime(2026, 4, 28),
    schedule="@daily",    # How often to run
    catchup=False         # Prevents running all past intervals
) as dag:
    # 4. Define Tasks
    task_1 = BashOperator(task_id="main", bash_command="python /opt/airflow/dags/main.py")
    

    # 5. Set Dependencies
    task_1  