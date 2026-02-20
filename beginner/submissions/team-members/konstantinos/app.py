### LIBRARIES AND APIS

import os
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv
#from IPython.display import display, Markdown
import gradio as gr

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

# check if API keys are set
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key")
if not HUGGINGFACE_API_KEY:
    raise ValueError("Missing HUGGINGFACE API key")
if not TAVILY_API_KEY:
    raise ValueError("Missing TAVILY API key")
if not ALPHAVANTAGE_API_KEY:
    raise ValueError("Missing ALPHAVANTAGE API key")

# clients
openai_client = OpenAI()
tavily_client = TavilyClient()

### TOOLS

## SEARCH TOOLS

import requests

def get_market_data(company_name):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={company_name}&apikey={ALPHAVANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    # get specific data
    result_n = data.get("Name", "Unknown")
    result_c = data.get("MarketCapitalization", "Unknown")
    result_p = data.get("PERatio", "Unknown")
    result_e = data.get("EPS", "Unknown")
    result_b = data.get("Beta", "Unknown")

    return {
        "company_name": result_n,
        "market_cap": result_c,
        "PE_ratio": result_p,
        "EPS": result_e,
        "Beta": result_b
    }

def get_revenue(company_name):
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={company_name}&apikey={ALPHAVANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()

    # get specific data
    result_r = data.get("annualReports", [{}])[0].get("totalRevenue")
    result_y = data.get("annualReports", [{}])[0].get("fiscalDateEnding")

    return {
        "total_revenue": result_r if result_r is not None else None,
        "fiscal_date_ending": result_y if result_y is not None else None
    }

def get_news_company(company_name: str, domains: list = None):
    result = tavily_client.search(company_name)
    return result

## PYDANTIC SCHEMA

from pydantic import BaseModel

class Financial_Summary_Schema(BaseModel):
    name: str
    sector: str
    market_position: str
    price: str
    market_cap: str
    price: str
    key_ratios: str
    recent_price_trend: str
    volatility: str
    revenue: str
    eps_trends: str
    top_headlines: str
    sentiment: str
    impact_rating: str
    opportunities: str
    risks: str
    neutral_uncertain_factors: str 

## EXPORTER FUNCTIONS

# JSON EXPORT

def my_export_json(data):
    print(data.model_dump_json(indent=2))
    with open("report.json", "w") as f:
        f.write(data.model_dump_json(indent=2))

# MARKDOWN EXPORT

def my_export_markdown(pydantic_obj):
    md = "### " + pydantic_obj.__class__.__name__ + "\n\n"
    for k, v in pydantic_obj.model_dump().items():
        md += f"- **{k}**: {v}\n"
    return md

### MAIN FUNCTION

def my_main_function(ticker):

    # run search tools

    try:
        market_data = get_market_data(ticker)
    except Exception as e:
        print("Market data failed:", e)
        market_data = {}

    try:
        news_data = get_news_company(ticker)
    except Exception as e:
        print("News data failed:", e)
        news_data = {}

    try:
        revenue_data = get_revenue(ticker)
    except Exception as e:
        print("Revenue data failed:", e)
        revenue_data = {}

    # call LLM for text summary

    summary_prompt = f"""
    You are a financial analyst. Summarize in 9-10 sentences for the given company the following:
    Market data: {market_data}
    News data: {news_data}
    Revenue figure: {revenue_data}
    """

    summary = openai_client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": summary_prompt}]
    )
    text_data = summary.output_text

    # call LLM for structured summary

    struct_summary = openai_client.responses.parse(
        model="gpt-4.1-mini",
        input=summary.output_text,
        text_format=Financial_Summary_Schema
    )
    structured_data = struct_summary.output[0].content[0].parsed

    #result = my_export_markdown(structured_data)

    return structured_data

    #display(Markdown(text_data))
    #print(my_export_markdown(structured_data))

### UI

with gr.Blocks() as demo:

    gr.Markdown("## Financial Summary Compiler")
    gr.Markdown("### Enter a company ticker and let AI collect information and create a financial summary for you:")

    with gr.Row(): 
        input_ticker = gr.Textbox(label="Input Ticker",placeholder="Enter a company ticker (e.g. IBM) and press 'Go!' ")

    with gr.Row():
        submit_btn  = gr.Button("Go!")
        export1_btn = gr.Button("Export JSON..")
        export2_btn = gr.Button("Export MARK..")        

    # OUTPUTS
    output = gr.Markdown(label="Financial Summary") # appears on screen
    output_state = gr.State()                       # saved state 

    gr.Markdown("created by Konstantinos Kazanas (to be used for test purposes only)")

    def on_submit(a_ticker):
        report_obj = my_main_function(a_ticker)   # creates pyd object
        md = my_export_markdown(report_obj)       # prints markdown on screen
        return md, report_obj

    def on_exp_1(report_obj):
        my_export_json(report_obj)
        return "JSON exported to report.json"

    def on_exp_2(report_obj):
        md = my_export_markdown(report_obj)
        return md

    submit_btn.click(on_submit, inputs=input_ticker, outputs=[output, output_state])
    export1_btn.click(on_exp_1, inputs=output_state, outputs=output)
    export2_btn.click(on_exp_2, inputs=output_state, outputs=output)

demo.launch()