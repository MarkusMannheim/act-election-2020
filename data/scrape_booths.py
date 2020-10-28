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

# set up scrape
driver.get("https://www.elections.act.gov.au/elections_and_voting/past_act_legislative_assembly_elections/2016-election/2016-election-results/polling-place-results")

electorates = driver.find_element(By.CLASS_NAME, "group-heading").find_elements(By.TAG_NAME, "a")
electorate_names = []
for electorate in electorates:
    electorate_names.append(electorate.get_attribute("innerText"))

booths = driver.find_elements(By.CSS_SELECTOR, ".data-row, .total-row")
booth_names = []
booth_index = 0
for booth in booths:
    booth = booth.get_attribute("innerText").split("\t")[0]
    booth_names.append(booth)
booth_names[-5] = "Amalgamated"

candidate_votes = pd.DataFrame(columns=["booth", "electorate", "party", "candidate", "votes"])

# begin scraping loop
root_electorate = 0
for index, booth in enumerate(booth_names):
    booth_alias = "-".join(booth.replace("(", "").replace(")", "").lower().split())
    if (index > 0) and (booth < booth_names[index - 1]):
        root_electorate = root_electorate + 1
    print(f"Scraping {booth} results ...")    
    for electorate in electorate_names:
        print(f"Analysing {electorate} votes ...")
        
        # go to results page
        driver.get(f"https://www.elections.act.gov.au/elections_and_voting/past_act_legislative_assembly_elections/2016-election/2016-election-results/polling-place-results/{electorate_names[root_electorate].lower().replace('(', '').replace(')', '') if root_electorate < 5 else 'central-scrutiny'}/{booth_alias}?electorate={electorate}")
        
        # iterate through each row
        rows = driver.find_elements(By.TAG_NAME, "tr")        
        for row in rows:
            type = row.get_attribute("class")
            
            # sort and collate data
            if type == "group-heading":
                party = row.find_element(By.TAG_NAME, "a").get_attribute("innerText")
            elif type == "data-row":
                candidate = row.find_element(By.TAG_NAME, "td").get_attribute("innerText").strip()
                votes = int(row.find_element(By.CLASS_NAME, "text-right").get_attribute("innerText").strip().replace(",", ""))
                vote = {
                    "booth": booth,
                    "electorate": electorate,
                    "party": party,
                    "candidate": candidate,
                    "votes": votes
                }
                candidate_votes.loc[booth_index] = pd.Series(vote)
                booth_index = booth_index + 1
    candidate_votes.to_csv("candidate_votes.csv")