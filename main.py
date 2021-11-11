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

def tag_cleanup(html):
    html = str(html)
    cleanr = re.compile('<.*?>')
    string = (re.sub(cleanr, '', html))
    string = string.replace('\n', '')
    string = string.replace('\t', '')
    string = string.replace(' ', '')
    return string

def main():
    url = r'https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Fsearch%2Fresults%2Fcompanies%2F%3FcompanyHqGeo%3D%255B%2522106057199%2522%255D%26companySize%3D%255B%2522C%2522%252C%2522D%2522%255D%26industry%3D%255B%252296%2522%255D%26origin%3DFACETED_SEARCH%26sid%3DKhR&fromSignIn=true&trk=cold_join_sign_in'
    CUR_DIR = Path(__file__).parent
    PROGRAM = 'chromedriver.exe'
    PATH = CUR_DIR / PROGRAM
    
    OPTIONS = webdriver.ChromeOptions()
    #OPTIONS.add_argument('--headless')
    #OPTIONS.add_argument('--user-data-dir=chrome-data')
    
    try:
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        
    except WebDriverException:
        BINARY = 'D:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        OPTIONS.binary_location = BINARY
        OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(PATH, options=OPTIONS)
        
    try:
        with open ('login.json') as f:
            login_info = json.load(f)
        browser.get(url)
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'card-layout')))
        username = browser.find_element_by_id('username')
        password = browser.find_element_by_id('password')
        username.send_keys(login_info['username'])
        password.send_keys(login_info['password'])
        browser.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[3]/button').click()
        WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'artdeco-card')))
        executor_url = browser.command_executor._url
        session_id = browser.session_id
        #pickle.dump(browser.get_cookies(), open('cookies.pkl', 'wb'))
        
        all = []
        
        #for i in range(1, 101):
        for i in range(1):
            # cookies = pickle.load(open("cookies.pkl", "rb"))
            # for cookie in cookies:
            #     browser.add_cookie(cookie)
            #html = browser.find_element_by_tag_name('html')
            #html.send_keys(Keys.END)
            #time.sleep(2)
            #next = browser.find_element_by_xpath('//button[@aria-label="Avançar"]')
            source = browser.page_source
            
            soup = BeautifulSoup(source, 'html.parser')
            for company in soup.find_all('a', class_ = 'app-aware-link'):
                link = company['href']
                if link.startswith('https://www.linkedin.com/company/'):
                    name = tag_cleanup(company)
                    if name and company and (name != ' '):
                        row = {'Nome': name, 'LinkedIn': link}
                        all.append(row)
            #pickle.dump(browser.get_cookies(), open('cookies.pkl', 'wb'))
            #next.click()
                    
        browser.quit()
        
        for d in all:
            link = d['LinkedIn'] + 'about'
            browser2 = webdriver.Remote(options=OPTIONS, command_executor=executor_url, desired_capabilities={})
            browser2.session_id = session_id
            print(link)
            browser2.get(link)
            WebDriverWait(browser2, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'card-layout')))
            browser2.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[3]/button').click()
            page = browser2.page_source
            soup = BeautifulSoup(page, 'html.parser')
            print(page, soup)
            
            for row in soup.find_all('dt', class_ = ['mb1', 'text-heading-small']):
                alo = tag_cleanup(row)
                print(row)
    
    
    except TimeoutException:
        try:
            browser.quit()
        finally:
            sys.exit()


if __name__ == '__main__':
    main()