import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import airflow_ai_sdk as ai_sdk

model = OpenAIModel(
    model_name="llama3.1",
    provider=OpenAIProvider(
        base_url="http://host.docker.internal:11434/v1"
    ),
)

@task
def get_companies() -> list[dict]:
    return [
        {"name": "Chewy"},
        {"name": "Whoop"},
        {"name": "Stripe"},
    ]

class CompanyInfo(ai_sdk.BaseModel):
    name: str
    summary: str

@task.llm(
    model=model,
    result_type=CompanyInfo,
    system_prompt="""
You are an experienced researcher with a great deal of expertise in Airflow. 
You have a great understanding of what types of problems can be solved with Airflow. 
You are also an expert in research; you do a great job succinctly summarizing what companies do.
You will be given a company name and have been tasked with generating a 100-200 word summary that covers what a company does / what their product(s) do, how many people work there, where they are headquarted and what they might use Airflow for.
Input will be a  dictionary with a "name" key representing the name of the company.
Return a JSON object with exactly two keys: "name" and "summary". Do not include any additional text or commentary.
"""
)
def generate_company_summary(company: dict | None = None):
    if company is None:
        raise AirflowSkipException("No company provided")
    # Return the prompt input string, which will be templated internally
    return f"Company Name: {company['name']}"

@task
def display_summaries(company_summaries: list[dict]):
    from pprint import pprint
    summaries_list = [{"Company": company["name"], "summary": company["summary"]} for company in company_summaries]
    pprint(summaries_list)
    return summaries_list

@dag(schedule=None, start_date=pendulum.datetime(2025, 3, 1, tz="UTC"), catchup=False)
def ollama_company_summary_generation():
    companies = get_companies()
    company_summaries = generate_company_summary.expand(company=companies)
    display_summaries(company_summaries)

ollama_company_summary_generation_dag = ollama_company_summary_generation()

if __name__ == "__main__":
    ollama_company_summary_generation_dag.test()