from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_jobs(keyword="Python Developer", location="India", max_jobs=5):
    jobs = []

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # --- LinkedIn ---
    try:
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
        driver.get(linkedin_url)
        time.sleep(5)
        listings = driver.find_elements(By.CLASS_NAME, 'base-search-card__info')[:max_jobs]

        for job in listings:
            try:
                title = job.find_element(By.CLASS_NAME, 'base-search-card__title').text.strip()
                company = job.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text.strip()
                loc = job.find_element(By.CLASS_NAME, 'job-search-card__location').text.strip()
                link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')

                jobs.append({
                    "source": "LinkedIn",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link
                })
            except Exception:
                continue
    except Exception as e:
        print("LinkedIn Error:", e)

    # --- Naukri ---
    try:
        naukri_url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs-in-{location.lower()}"
        driver.get(naukri_url)
        time.sleep(5)
        naukri_jobs = driver.find_elements(By.CLASS_NAME, 'jobTuple')[:max_jobs]

        for job in naukri_jobs:
            try:
                title = job.find_element(By.CLASS_NAME, 'title').text.strip()
                link = job.find_element(By.CLASS_NAME, 'title').get_attribute('href')
                company = job.find_element(By.CLASS_NAME, 'companyName').text.strip()
                loc = job.find_element(By.CLASS_NAME, 'loc').text.strip()

                jobs.append({
                    "source": "Naukri",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link
                })
            except Exception:
                continue
    except Exception as e:
        print("Naukri Error:", e)

    # --- Indeed ---
    try:
        indeed_url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location}"
        driver.get(indeed_url)
        time.sleep(5)
        indeed_jobs = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')[:max_jobs]

        for job in indeed_jobs:
            try:
                title = job.find_element(By.CLASS_NAME, 'jobTitle').text.strip()
                company = job.find_element(By.CLASS_NAME, 'companyName').text.strip()
                loc = job.find_element(By.CLASS_NAME, 'companyLocation').text.strip()
                link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if link and not link.startswith("http"):
                    link = "https://www.indeed.com" + link

                jobs.append({
                    "source": "Indeed",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link
                })
            except Exception:
                continue
    except Exception as e:
        print("Indeed Error:", e)

    # --- Unstop ---
    try:
        unstop_url = f"https://unstop.com/jobs/search?search={keyword.replace(' ', '%20')}"
        driver.get(unstop_url)
        time.sleep(5)
        unstop_jobs = driver.find_elements(By.CLASS_NAME, 'job-card')[:max_jobs]

        for job in unstop_jobs:
            try:
                title = job.find_element(By.CLASS_NAME, 'job-title').text.strip()
                link = job.find_element(By.CLASS_NAME, 'job-title').get_attribute('href')
                company = job.find_element(By.CLASS_NAME, 'job-company-name').text.strip()
                loc = job.find_element(By.CLASS_NAME, 'job-location').text.strip()

                jobs.append({
                    "source": "Unstop",
                    "title": title,
                    "company": company,
                    "location": loc,
                    "link": link
                })
            except Exception:
                continue
    except Exception as e:
        print("Unstop Error:", e)

    driver.quit()
    return jobs
