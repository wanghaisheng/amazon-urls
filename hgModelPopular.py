import requests
import os
import hashlib
import concurrent.futures
from DataRecorder import Recorder
from getbrowser import setup_chrome
from dotenv import load_dotenv
from save_app_profile import *
load_dotenv()

# Constants for D1 Database
D1_DATABASE_ID = os.getenv('D1_APP_DATABASE_ID')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')

CLOUDFLARE_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/d1/database/{D1_DATABASE_ID}"

# Initialize Browser
browser = setup_chrome()

def getcounts(url):
    """
    Scrape app information from the provided URL.
    """
    if url:
        try:
            tab = browser.new_tab()
            tab.get(url)
            
            # Extract app details
            articles = tab.ele('.pt-8 border-gray-100 col-span-full lg:col-span-6 xl:col-span-7 pb-12').eles("t:article")
            items = []
            for a in articles:
                model_url = "https://huggingface.co/models/" + a.ele('t:a').link
                run_count = "https://huggingface.co/models/" + a.ele('t:a').eles("t:svg")[1].text
                

                item = {
                    "model_url": model_url,
                    "run_count": run_count
                }
                items.append(item)
            return items
        except Exception as e:
            print(f"Error fetching info for {url}: {e}")
            return []

def bulk_scrape_and_save_model_urls():
    """
    Scrape app information for multiple URLs concurrently and save to D1 database.
    """
    total = []
    # Generate URLs for pages 1 to 100
    urls=[]
    for i in range(1, 101):
        url = f"https://huggingface.co/models?p={i}&sort=trending"
        urls.append(url)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(getcounts, urls))
        
    # Flatten the results and extend the total list
    for result in results:
        total.extend(result)

    # Process the total list of items
    batch_process_in_chunks(total, process_function=batch_process_updated_model_count)

if __name__ == "__main__":
    # Create the table before scraping
    # create_app_profiles_table()

    # List of URLs to scrape (initial URLs if any)
    urls = []

    # Perform scraping and save to D1
    # bulk_scrape_and_save_model_urls(urls)