import re
from chainbreaker_api import ChainBreakerScraper
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
import datetime
import bot.constants as ct

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)

import ipfshttpclient
ipfs_client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')


def clean_string(string, no_space = False):   
    """
    Clean String.
    """
    if no_space:
        string = string.replace("  ","")
    string = string.strip()
    string = string.lower()
    string = string.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    string = string.replace("\n"," ")
    return string

def getId(link) -> str:
    m = re.search("/[0-9]+", link)
    return m.group(0)[1:]

def getPhone(driver: Chrome) -> str:
    # Click all reveal buttons until it works.
    reveal_buttons = driver.find_elements(By.CLASS_NAME, "reveal-button")
    for button in reveal_buttons:
        try:
            button.click()
        except:
            pass

    # Wait a second.
    MAX_TRIES = 100
    tries = 0
    while tries < MAX_TRIES:
        time.sleep(10)

        # Get all class names with phone number title
        numbers = driver.find_elements(By.CLASS_NAME, "seller-phone-number-title")
        for n in numbers:
            if len(n.text) > 0:
                phonenumber = n.text
                if "X" not in phonenumber:
                    return phonenumber
                else:
                    tries += 1
                    break
    return ""

def getExternalWebsite(driver: Chrome) -> str:
    links = driver.find_elements(By.CLASS_NAME, "link")
    for l in links:
        if l.get_attribute("data-q") == "seller-websiteUrl":
            return l.get_attribute("href")
    return ""

def getTitle(driver: Chrome) -> str:
    title = driver.find_element(By.TAG_NAME, "h1")
    return title.text

def getText(driver: Chrome) -> str:
    p_tags = driver.find_elements(By.TAG_NAME, "P")
    for p in p_tags:
        if p.get_attribute("itemprop") == "description":
            return p.text.replace("\n", " ")

def getLocation(driver: Chrome):
    locations = driver.find_elements(By.TAG_NAME, "h4")
    for l in locations:
        if l.get_attribute("itemprop") == "addressLocality":
            values = l.text.split()
            region = values[1]
            city = values[0]
            return region, city, ""

def getCountry() -> str:
    return ct.COUNTRY

def getCategory() -> str:
    return ct.CATEGORY

def getAge() -> str:
    return ""

def getEthnicity() -> str:
    return ct.ETHNICITY

def getNationality() -> str:
    return ct.NATIONALITY

def getPostDate(driver: Chrome) -> datetime.datetime:
    dds = driver.find_elements(By.TAG_NAME, "dd")
    for dd in dds:
        if dd.get_attribute("data-testid") == "attribute-value":
            string = dd.text
            if "days" in string:
                days = int(string.split(" ")[0])
                tod = datetime.datetime.today()
                d = datetime.timedelta(days = days)
                return dateToString(tod - d)
            return dateToString(datetime.datetime.now())

def getDateScrape() -> datetime.datetime:
    return dateToString(datetime.datetime.now())

def dateToString(date: datetime.datetime):
    return datetime.datetime.strftime(date, "%Y-%m-%d")

def getScreenshot(driver: Chrome):
    driver.execute_script("window.scrollTo(0,0)")
    driver.save_screenshot("ss.png")
    res = ipfs_client.add("ss.png")
    return res["Hash"]

def scrap_ad_link(client: ChainBreakerScraper, driver: Chrome, dicc: dict):
    phone = getPhone(driver)
    email = ""
    if phone == "" or "X" in phone:
        logger.warning("Phone not found! Skipping this ad.")
        return None

    author = ct.AUTHOR
    language = ct.LANGUAGE
    link = dicc["url"]
    id_page = getId(dicc["url"])
    title = getTitle(driver)
    text = getText(driver)
    category = ct.CATEGORY
    first_post_date = getPostDate(driver)

    date_scrap = getDateScrape()
    website = ct.SITE_NAME

    external_website = getExternalWebsite(driver)
    reviews_website = ""
    country = ct.COUNTRY
    region, city, place = getLocation(driver)
    
    comments = []
    latitude = ""
    longitude = ""

    ethnicity = getEthnicity()
    nationality = getNationality()

    age = getAge()
    screenshot = getScreenshot()
    #print(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email, verified_ad, prepayment, promoted_ad)
    #        external_website, reviews_website, comments, latitude, longitude, ethnicity, nationality, age)
    # Upload ad in database.
    data, res = client.insert_ad(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email,
            external_website, reviews_website, comments, latitude, longitude, ethnicity, nationality, age, screenshot) # Eliminar luego

    # Log results.
    logger.info("Data sent to server: ")
    logger.info(data)
    logger.info(res.status_code)
    print(res.text)
    if res.status_code != 200: 
        logger.error("Algo salió mal...")
    else: 
        logger.info("Éxito!")