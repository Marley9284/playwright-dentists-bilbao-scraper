import asyncio
import pandas as pd
import os
import logging
import unicodedata
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CATALOGUE_URL = "https://www.paginasamarillas.es/search/dentista/all-ma/bizkaia/all-is/bilbao/all-ba/all-pu/all-nc/"
START_URL = "https://www.paginasamarillas.es/search/dentista/all-ma/bizkaia/all-is/bilbao/all-ba/all-pu/all-nc/1"
WHITELIST_LOCATIONS = ["bilbao" ]
WHITELIST_ACTIVITIES = ["clinicas dentales", "dentista", "odontol", "estomatol", "dentistas"]

def clean_text(text:str) -> str:
    if not text:
        return ""
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return text.lower().strip()

async def scrape_page(page, browser, url):
    await page.goto(url)
    dentist_data = []

    dentist_links = await page.query_selector_all("a[data-omniclick='name']")
    for link in dentist_links:
        href = await link.get_attribute("href")
        if href:
            await asyncio.sleep(2)
            details = await scrape_dentist_details(browser, href)
            if details:
                dentist_data.append(details)


    next_page = await page.query_selector("a:has(i.icon-flecha-derecha)")
    next_url = await next_page.get_attribute("href") if next_page else None

    return dentist_data, next_url

async def scrape_dentist_details(browser, dentist_url):
    page = await browser.new_page()
    try:
        await page.goto(dentist_url, timeout=10000)

        title, address, number, activity, location = None, None, None, None, None

        title_locator = page.locator("h1[itemprop='name'][data-yext='name']")
        number_locator = page.locator("span[itemprop='telephone']").first
        address_locator = page.locator("span[itemprop='streetAddress']")
        activity_locator = page.locator("div.actividades p")


        if await title_locator.is_visible(timeout=5000):
            full_text = await title_locator.text_content()
            location_span = title_locator.locator("span.localidad")   

            if await location_span.is_visible(timeout=1000):
                location = await location_span.text_content()
                title = full_text.replace(location, "").strip()
            else:
                title = full_text.strip()


        if await number_locator.is_visible(timeout=5000):
            number = await number_locator.text_content()


        if await address_locator.is_visible(timeout=5000):
            address = await address_locator.text_content()
 

        if await activity_locator.is_visible(timeout=5000):
            activity = await activity_locator.text_content()
            activity = activity.lower().title()


        return {
            "title": title.strip() if title else None,
            "activity": activity.strip() if activity else None,
            "number": number.strip() if number else None,
            "address": address.strip() if address else None,
            "location": location.strip() if location else None
        }
    
    except Exception as e:
        logging.error(f"Error scrapping details on {dentist_url}: {e}")
        return {}

    finally:
        await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = START_URL
        all_dentists = []

        while url:
            logging.info(f"Scraping page: {url}")
            try:
                dentists, next_url = await scrape_page(page, browser, url)
                all_dentists.extend(dentists)
                url = next_url
            except Exception as e:
                logging.error(f"Failed to scrape page {url}: {e}")
                break

        logging.info(f"Total before removing duplicates and aplying filters: {len(all_dentists)}")

        filtered_Dentist = []
        for row in all_dentists:
            loc_clean = clean_text(row.get("location"))
            act_clean = clean_text(row.get("activity"))


            if WHITELIST_LOCATIONS and not any(c in loc_clean for c in WHITELIST_LOCATIONS):
                continue

            if WHITELIST_ACTIVITIES and not any (a in act_clean for a in WHITELIST_ACTIVITIES):
                continue


            cleaned_row = {
                k: (v.replace("\n", " ").replace("\r", " ").strip() if isinstance(v, str) else v)
                for k, v in row.items()
            }    
            filtered_Dentist.append(cleaned_row)

        logging.info(f"Total dentists after aplying the filters: {len(filtered_Dentist)}")

        df = pd.DataFrame(filtered_Dentist)
        df.drop_duplicates(subset=["title", "number"], keep="first", inplace=True)

        logging.info(f"Total dentists after removing duplicates: {len(df)}")

        if "number" in df.columns:
            df["number"] = df["number"].astype(str).str.replace(r"\s+", "", regex=True)
            df["number"] = '="' + df["number"] + '"'


        script_dir = os.path.dirname(os.path.abspath(__file__))

        output_path = os.path.join(script_dir, "Dentists.csv")

        df.to_csv(
            output_path, 
            sep=";", 
            index=False, 
            encoding="utf_8_sig", 
            columns=["title", "activity", "number", "address", "location"]
        )


        logging.info("Process completed. Dentist have been saved to Dentist.csv")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())