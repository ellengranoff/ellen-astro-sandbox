from airflow.sdk import dag, task, chain
from pendulum import datetime

@dag(schedule="@daily", start_date=datetime(2025, 1, 1), tags=["dag_versioning"])
def af3_dag_versioning_example():

    # V1 of this dag runs the first 3 tasks!

    @task
    def task_1():
        print("Hello from task 1!")

    @task
    def task_2():
        print("Hello from task 2!")

    @task
    def task_3():
        print("Hello from task 3!")

    @task
    def task_4():
        print("Hello from task 4!")

    chain(
        # task_1(),
        task_2(),
        # task_3(),
        task_4(),
    )

af3_dag_versioning_example()