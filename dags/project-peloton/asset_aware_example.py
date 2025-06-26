from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
import requests
from datetime import datetime
import json


with DAG(
    dag_id="get_peloton_data",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["peloton"]
) as dag:
    
    # Get the connection securely at DAG parse time + construct auth payload
    def get_login_payload():
        conn = BaseHook.get_connection("ellen_peloton_connection_new")
        return {
            "username_or_email": conn.login,
            "password": conn.password,
        }
    
    auth_payload = get_login_payload()

    # Authenticate with Peloton
    login_task = HttpOperator(
        task_id="login_task",
        http_conn_id="ellen_peloton_connection_new",
        method="POST",
        endpoint="/auth/login",
        data=json.dumps(auth_payload),
        headers={"Content-Type": "application/json"},
        response_filter=lambda r: r.json()["session_id"],
        do_xcom_push=True,
        log_response=True,
    )

    # Use session id from login_task to access profile data
    def get_profile(**context):
        session_id = context["ti"].xcom_pull(task_ids="login_task")
        if not session_id:
            raise ValueError("No session_id found in XCom.")
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"peloton_session_id={session_id}"
        }
        resp = requests.get("https://api.onepeloton.com/api/me", headers=headers)
        resp.raise_for_status()
        profile_data = resp.json()
        return profile_data

    # get user data
    profile_task = PythonOperator(
        task_id="get_peloton_profile",
        python_callable=get_profile
    )



    login_task >> profile_task


