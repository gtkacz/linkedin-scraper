import re, sys, html, requests, os, mechanize, pandas as pd, requests, time, pickle, json
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from itertools import zip_longest

def main():
    url = r'https://www.linkedin.com/company/buserbrasil/about/'
    url2 = r'https://www.linkedin.com/company/pda-international/about/'
    CUR_DIR = Path(__file__).parent
    PROGRAM = 'chromedriver.exe'
    PATH = CUR_DIR / PROGRAM
    
    OPTIONS = webdriver.ChromeOptions()
    #OPTIONS.add_argument('--headless')
    
    with open('data.json', 'r', encoding='utf-8-sig') as read_file:
        infos = json.load(read_file)
    
    try:
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        
    except WebDriverException:
        BINARY = 'D:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        OPTIONS.binary_location = BINARY
        OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        
    with open ('login.json') as f:
        login_info = json.load(f)
    browser.get(url)
    WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'card-layout')))
    username = browser.find_element_by_id('username')
    password = browser.find_element_by_id('password')
    username.send_keys(login_info['username'])
    password.send_keys(login_info['password'])
    browser.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[3]/button').click()
    time.sleep(5)
    browser.get(url2)
    
if __name__ == '__main__':
    main()