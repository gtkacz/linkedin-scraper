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

def tag_cleanup(html):
    html = str(html)
    cleanr = re.compile('<.*?>')
    string = (re.sub(cleanr, '', html))
    #string = string.replace('\n', '')
    #string = string.replace('\t', '')
    string = string.strip()
    return string

def main():
    #url = r'https://www.linkedin.com/company/buserbrasil/about/'
    CUR_DIR = Path(__file__).parent
    PROGRAM = 'chromedriver.exe'
    PATH = CUR_DIR / PROGRAM
    
    OPTIONS = webdriver.ChromeOptions()
    #OPTIONS.add_argument('--headless')
    #OPTIONS.add_argument('--window-size=%s' % '1920,1080')
    
    with open('data.json', 'r', encoding='utf-8-sig') as read_file:
        infos = json.load(read_file)
    
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
        df = pd.DataFrame()
        logou = False
        for e in tqdm(infos):
            row = e.copy()
            url = row['LinkedIn'] + 'about'
            browser.get(url)
            if not logou:
                WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'card-layout')))
                username = browser.find_element_by_id('username')
                password = browser.find_element_by_id('password')
                username.send_keys(login_info['username'])
                password.send_keys(login_info['password'])
                browser.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[3]/button').click()
                logou = True
            page = browser.page_source
            soup = BeautifulSoup(page, 'html.parser')
            
            for tabela in soup.find_all('section', class_ = ['artdeco-card', 'p5', 'mb4']):
                found = False
                for about in tabela.find_all('p', class_ = ['break-words', 'white-space-pre-wrap', 'mb5', 'text-body-small', 't-black--light']):
                    if about:
                        row['Sobre'] = tag_cleanup(about)
                        
                for titulo, conteudo in zip_longest(tabela.find_all('dt', class_ = ['mb1', 'text-heading-small']), tabela.find_all('dd', class_ = ['mb4', 'text-body-small', 't-black--light'])):
                    a = tag_cleanup(titulo)
                    b = tag_cleanup(conteudo)
                    
                    if a == 'Tamanho da empresa':
                        if b.endswith('funcionários'):
                            found = True
                            
                    else:
                        if not found:
                            if not a == 'None':
                                row[a] = b
                            else:
                                row['Fundada em'] = b
                        else:
                            row['Tamanho da empresa'] = b.split()[0]
                            found = False
                            
            df = df.append(row, ignore_index=True)
            
        df.to_excel('resultados.xlsx')
        
    except TimeoutException:
        try:
            browser.quit()
        finally:
            print('Timeout')
            sys.exit()


if __name__ == '__main__':
    main()