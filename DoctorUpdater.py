import os
import re

import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys

from google.oauth2 import service_account
from googleapiclient.discovery import build

import time

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/documents']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=scope)
service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
client = gspread.authorize(credentials)

sheet = client.open('Doctors Sheet').sheet1
values = sheet.get_all_values()

os.environ['PATH'] += "C:\\Users\\Yahya Al-Azhary\\Documents\\Selenium Driver\\chromedriver-win64"
driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://www.npidataservices.com/npi-lookup")
driver.maximize_window()


rownum = 1108
for value in values[1107:]:
    print(value)
    npiField = driver.find_element(By.ID, 'npi_id')
    startUrl = driver.current_url
    npiField.clear()
    npiField.send_keys(value[4])
    npiField.send_keys(Keys.ENTER)
    if startUrl == driver.current_url:
        print(f"Doctor not found {value[4]}")
    else:
        doctorInfo = driver.find_element(By.ID, "pp_add_copy_text")
        doctorInfo = doctorInfo.text.split("\n")

        statePattern = re.compile("[^a-z0-9][a-z]{2}[^a-z0-9]", re.IGNORECASE)
        dradd2 = doctorInfo[1].title()
        stateAddress = doctorInfo[2].split("-")[0].replace(",", "").title()
        state = statePattern.search(stateAddress)
        stateAddress = statePattern.sub(state.upper(), stateAddress)
        dradd3 = stateAddress.replace(" ", ", ")
        dradd4 = stateAddress.replace(" ", "/ ")
        dradd1 = f"{dradd2}, {dradd3}"

        drphone = doctorInfo[3].split(":")[1].replace("-", ".")

        columns = {'B': state, 'F': dradd1, 'G': dradd2, 'H': dradd3, 'I': dradd4, 'J': drphone}
        for column in columns:
            print(columns[column], end=" ")
        for column in columns:
            sheet.update(f"{column}{rownum}", [[columns[column]]])
        driver.back()
    rownum += 1

