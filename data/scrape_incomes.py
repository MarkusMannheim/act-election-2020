import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# use a headless browser (saves time)
chrome_options = Options()
chrome_options.add_argument("--headless")

# set up the browser
driver = webdriver.Chrome(options=chrome_options)

# read in postcodes
postcodes = pd.read_csv("./filtered_postcodes.csv")
postcodes = list(postcodes["0"])

# empty list to capture scraped income data
median_incomes = []
household_incomes = pd.DataFrame(index=postcodes)

# begin scraping loop
for postcode in postcodes:
    # convert postcode to correct string format
    postcode = "0" * (4 - len(str(postcode))) + str(postcode)

    # ABS QuickStats search home page
    driver.get("https://www.abs.gov.au/websitedbs/censushome.nsf/home/quickstats?opendocument&navpos=220")

    # input postcode to search field
    search_field = driver.find_element_by_css_selector(".gwt-SearchWidget-Container input")
    search_field.clear()
    search_field.send_keys(postcode[0])
    time.sleep(.25)
    search_field.send_keys(postcode[1])
    time.sleep(.25)
    search_field.send_keys(postcode[2])
    time.sleep(.25)
    search_field.send_keys(postcode[3])
    time.sleep(.25)

    # get postcode pop-up suggestion
    try:
        suggested_postcode = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".suggestion-hilite-prefix"))
        )
        if suggested_postcode.get_attribute("innerText") == postcode:
            # refill search input and submit
            suggested_postcode.click()
            driver.find_element_by_class_name("gwt-SearchWidget-Button").click()
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".qsDwelling tbody tr:nth-child(3) td"))
                )
                income = element.get_attribute("innerText")
                print(postcode, "—", income)
                median_incomes.append(income)
            except:
                print("failure 2:", postcode, "— null")
                median_incomes.append("NaN")
        else:
            print("failure 3:", postcode, "— null")
            median_incomes.append("NaN")
    except:
        print("failure 1:", postcode, "— null")
        median_incomes.append("NaN")

# end scraping, save data
driver.close()
household_incomes["income"] = median_incomes
household_incomes.to_csv("./solarData/medianIncomes.csv", index_label="postcode")
