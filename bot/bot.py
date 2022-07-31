import bot.constants as ct
import sys
import time 
import re
import bot.scrape

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from chainbreaker_api import ChainBreakerScraper
import warnings
warnings.filterwarnings("ignore")

from utils.env import get_config
config = get_config()

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)


def enterGumTree(driver: Chrome):
    # Enter GumTree
    driver.get(ct.LOGIN_SITE)
    logger.info("Current URL: " + driver.current_url)
    time.sleep(4)

    locator = (By.ID, "email")
    email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    #locator = (By.ID, "onetrust-accept-btn-handler")
    #accept_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    
    # Accept cookies.
    #accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    #accept_button.click()

    # Get email and password inputs.
    #email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "fld-password")

    # Fill inputs.
    email_input.send_keys(config["USERNAME"])
    password_input.send_keys(config["GUMTREE_PASSWORD"])

    # Press login button.
    login_button = driver.find_elements(By.TAG_NAME, "button")
    for b in login_button:
        if b.text == "Login":
            b.click()
            break
        
    # Wait.
    #time.sleep(5)
    return driver

def getDriver(debug: str):

    # Crear driver.
    logger.info("Open Chrome")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    if debug == "TRUE":
        driver = webdriver.Chrome(executable_path="./chromedriver.exe", options = options)
    else:
        options.binary_location = config["GOOGLE_CHROME_BIN"]
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path= config["CHROMEDRIVER_PATH"], chrome_options= options)
    return driver

def isThereNextPage(driver: Chrome):
    li = driver.find_element(By.CLASS_NAME, "pagination-next")
    a = li.find_element(By.TAG_NAME, "a")
    if a.get_attribute("class") != "pagination-disabled":
        return True
    return False

def main():
    endpoint = config["ENDPOINT"]
    user = config["USERNAME"]
    password = config["PASSWORD"]

    logger.warning("Scraper initialized.")

    client = None
    client = ChainBreakerScraper(endpoint)
    res = client.login(user, password)
    if type(res) != str:
        logger.critical("Login was not successful.")
        sys.exit()
    else: 
        logger.warning("Login was successful.")

    driver = getDriver(config["DEBUG"])
    time.sleep(4)
    driver = enterGumTree(driver)

    count_announcement = 1
    nextPage = True
    page = 0
    
    while nextPage:
        # Load list of ads.
        page += 1
        logger.warning("# Page: " + str(page))
        driver.get(ct.SITE + f"/page{page}")

        # Wait.
        time.sleep(5)

        # Get ads.
        ads = driver.find_elements(By.CLASS_NAME, "listing-link")
        for ad in ads: 
            url = ad.get_attribute("href") 
            if client.get_status() != 200:
                logger.error("Endpoint is offline. Service stopped.", exc_info = True)
                driver.quit()
                sys.exit()

            info_ad = ct.SITE_NAME + ", #ad " + str(count_announcement) + ", page_link " + url
            id_ad = bot.scrape.getId(url)

            if client.does_ad_exist(id_ad, ct.SITE_NAME, ct.COUNTRY):
                logger.warning("Ad already in database. Link: " + url)
                continue
            else:
                logger.warning("New Ad. " + info_ad)
            
            # Enter to the ad.
            original_window = driver.current_window_handle
            assert len(driver.window_handles) == 1

            # Click the link which opens in a new window
            driver.execute_script("window.open('');")

            # Wait for the new window or tab
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            driver.get(url)
            
            # Wait
            time.sleep(4)
            logger.warning("Ad correctly loaded.")

            # Save values in dictionary
            dicc = {}
            dicc["url"] = url

            # Scrap ad.
            ad_record = bot.scrape.scrap_ad_link(client, driver, dicc)
            count_announcement += 1

            # Return to pagination.
            driver.close()
            driver.switch_to.window(original_window)
        
        nextPage = isThereNextPage(driver)

    # Close everything!
    driver.quit()

def execute_scraper():
    MAX_TRIES = 5
    tries = 0
    error = True

    while error and tries < MAX_TRIES:
        try:
            main()
            error = False
            break
        except Exception as e:
            error = True
            logger.exception(str(e))
            tries += 1