import os
import csv
import dotenv
import asyncio
from crawl4ai import AsyncWebCrawler

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables from .env file
dotenv.load_dotenv('./.env')

# Get the OpenAI API key from environment variables
# openai_api_key = os.getenv("OPENAI_API_KEY")
# google_api_key = os.getenv("GOOGLE_API_KEY")

conf_list = [
    "SIGGRAPH",
    "CVPR",
    "ICIP",
    # "IEEE Vis",
    # "SIGGRAPH_ASIA",
    # "ECCV",
    # "ICCV",
    # "HPG",
    # "EuroVis",
    # "IEEE VR",
    # "ACM MM",
    # "WACV",
    # "Eurographics",
    # "ISMAR",
    # "3DV",
    # "ACCV",
]

def get_conference_websites(conferences):
    llm = GoogleGenerativeAI(model="gemini-pro")
    prompt_template = PromptTemplate(
        input_variables=["conference"],
        template="Find the url to important deadline dates page from the website of the latest edition of the {conference} conference. Only provide the url and nothing extra in text."
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    conference_websites = {}
    for conference in conferences:
        response = chain.run(conference=conference)
        conference_websites[conference] = response.strip()

    return conference_websites

async def crawl_websites(websites):
    mdowns = {}
    async with AsyncWebCrawler() as crawler:
        for conference, url in websites.items():
            print(f"Crawling {conference} website: {url}")
            try:
                result = await crawler.arun(url=url)
                mdowns[conference] = result.markdown
                print(f"Successfully crawled for {conference}.")
            except Exception as e:
                mdowns[conference] = None
                print(f"Failed to crawl {conference} website: {e}")

    return mdowns

def get_conference_dates(conf_list, mdowns):
    llm = GoogleGenerativeAI(model="gemini-pro")
    prompt_template = PromptTemplate(
        input_variables=["markdown"],
        template="Extract the final paper submission deadlines of the full papers from the following conference webpage content and format the dates in DD-MM-YYYY format. Only keep a single date in the answer and nothing extra in text. If the date is not available write N/A:\n\n{markdown}"
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    conference_dates = {}
    for conference, markdown in mdowns.items():
        if markdown:
            response = chain.run(markdown=markdown)
            conference_dates[conference] = response.strip()
        else:
            conference_dates[conference] = "N/A"

    return conference_dates

def update_csv(dates):
    csv_path = 'dl.csv'
    existing_dates = {}

    if os.path.exists(csv_path):
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    conference, date = row
                    existing_dates[conference] = date

    # Update the existing dates with new dates if they are different
    for conference, date in dates.items():
        if date != "N/A":
            existing_dates[conference] = date

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for conference, date in existing_dates.items():
            writer.writerow([conference, date])

    


if __name__ == "__main__":
    # Collate all the websites
    websites = get_conference_websites(conf_list)
    for conf, site in websites.items():
        print(f"{conf}: {site}")

    # Crawl the websites and capture the returned mdowns
    mdowns = asyncio.run(crawl_websites(websites))

    # Get the dates from the markdowns
    dates = get_conference_dates(conf_list, mdowns)
    print(dates)

    # Update the CSV with the new dates
    update_csv(dates)