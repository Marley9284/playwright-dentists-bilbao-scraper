#  Asynchronous Playwright Scraper - Dentists in Bilbao, Spain

This is a robust and asynchronous scraper made in Python with the library **Playwright**, which automatically extracts dental clinics and dentists in Bilbao from the Yellow Pages of Spain.

##  Characteristics

* **Asynchronous:** Utilizes (`asyncio`) and the *Playwright Async API* for efficient, non-blocking network requests.

* **Data Sanitization and Filtering:** 
Sanitizes and validates based on whitelist of location and activity using Unicode normalization (`unicodedata`) and deletes duplicated entries.

* **Human Behavior Simulation:** 
It has built-in delays between navigation actions and *headless=False*, to mitigate ban risks.

* **Error Handling:** 
Equipped with error handling: if an extraction fails, the main flow continues uninterrupted.

* **Logging:** 
Use of (`logging`) for a clean and real-time console reading. 

##  Technologies used

* **Python 3.10+**
* **Playwright (Async API)**
* **Pandas**
* **Asyncio**

## How to use

1. **Clone the repository**
   ```bash
   git clone https://github.com/Marley9284/playwright-dentists-bilbao-scraper.git
   cd playwright-dentists-bilbao-scraper

2. **Install dependencies** 
   ```bash
   pip install -r requirements.txt

3. **Install Playwright browsers**
   ```bash
   playwright install chromium

4. **Run the scraper**
   ```bash
   python src/main.py

## Output

Upon successful completion, the script generates a file named **Dentists.csv** structured with ";" as delimiter and UTF-8 encoding (for compatibility with Microsoft Excel) which includes the following fields:

| Field | Description |
| --- | --- | 
| **title** | Name of the dental clinic or practitioner.| 
| **activity** | The specialization listed. | 
| **number** | The contact phone number (formatted as text to prevent data corruption).|
| **address** | The physical street address.|
| **location** | The specific city/municipality *(filtered for Bilbao).* |   

<img width="1127" height="288" alt="Demo" src="https://github.com/user-attachments/assets/49c91bc6-dbcc-400d-8da1-afb5c6f66bcb" />
(Numbers and locations fields are not shown in the image)


