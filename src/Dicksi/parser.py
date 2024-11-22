import time
import pandas as pd
from selenium import webdriver as wb
from bs4 import BeautifulSoup as bs
from datetime import datetime

def Soup(url):
    br.get(url)
    time.sleep(3)
    return bs(br.page_source)

def PerekrestokParsing(requestWord):
    data = []
    url = f"https://www.perekrestok.ru/cat/search?search={requestWord}"
    soup = Soup(url)
    try:
        lastNum = int([num.text for num in soup.find_all('a', {'aria-current': 'page'})][-2])
    except:
        lastNum = 1
    for page in range(1, lastNum + 1):
        url = f"https://www.perekrestok.ru/cat/search?search={requestWord}&page={page}"
        soup = Soup(url)
        productCards = soup.find_all('div', {'class': 'sc-dlfnbm ldVxnE'})
        for productCard in productCards:
            if not productCard.find('div', {'class': 'price-old'}):
                continue
            market = "Перекресток"
            title = productCard.find('div', {'class': 'product-card__title'}).text.strip()
            link = "https://www.perekrestok.ru" + productCard.find('a', {'class': 'sc-fFubgz fsUTLG product-card__link'}).get('href')
            price = productCard.find('div', {'class': 'price-new'}).text.strip()
            discount = productCard.find('div', {'class': 'sc-cTkwdZ fPgnFu product-card__badge'}).find('span').text.strip()
            left = "Unknown"
            productElems = [market, title, link, price, discount, left]
            data.append(productElems)
    return data

def DiksiParser(requestWord):
    data = []
    url = f"https://dixy.ru/catalog/search.php?q={requestWord}"
    br.get(url)
    count = 1
    try:
        while br.find_element_by_css_selector("body > section.list-products > div > a"):
            br.find_element_by_css_selector("body > section.list-products > div > a").click()
            count += 1
    except:
        pass
    for page in range(1, count+1):
        url = f"https://dixy.ru/catalog/search.php?q={requestWord}&PAGEN_1={page}"
        soup = Soup(url)
        productCards = soup.find_all('div', {'class':'product-container'})
        for productCard in productCards:
            if not productCard.find('div', {'class': 'dixyCatalogItemPrice__new'}):
                continue
            title = productCard.find('div', {'class': 'dixyCatalogItem__title'}).text.strip()
            market = "Дикси"
            link = url
            price = productCard.find('div', {'class': 'dixyCatalogItemPrice__new'}).text.strip() + "," + productCard.find('div', {'class': 'dixyCatalogItemPrice__kopeck'}).text.strip() + " ₽"
            discount = productCard.find('div', {'class': 'dixyCatalogItemPrice__discount'}).text.strip()
            dateEnd = datetime.strptime(productCard.find('div', {'class':'dixyCatalogItem__term'}).text.strip().split('-')[1].strip(), "%d.%m.%Y").date()
            dateNow = datetime.now().date()
            left = str(dateEnd - dateNow).split(',')[0]
            productElems = [market, title, link, price, discount, left]
            data.append(productElems)
    return data

def MagnoliaParser(requestWord):
    data = []
    url = f"https://shop.mgnl.ru/search/?query={requestWord}&limit=2048"
    soup = Soup(url)
    productCards = soup.find_all('div', {'class':'inner_wrap TYPE_1'})
    for productCard in productCards:
        if not productCard.find('div', {'class': 'price_group min 1618b9f0-7969-11ea-9fc5-40167e7389e1'}):
            continue
        title = productCard.find('div', {'class': 'item-title'}).text.strip()
        market = "Магнолия"
        link = productCard.find('div', {'class': 'item-title'}).find('a').get('href')
        price = productCard.find('div', {'class': 'price_group min 1618b9f0-7969-11ea-9fc5-40167e7389e1'}).find('div',{'class':'price font-bold font_mxs'}).get("data-value").replace(".",",") + " ₽"
        discount = productCard.find('div', {'class': 'sale_block'}).text.strip()
        left = "Unknown"
        productElems = [market, title, link, price, discount, left]
        data.append(productElems)
    return data

br = wb.Chrome(".\chromedriver.exe")
requestWord = input("Скидки на какой товар вы хотите найти? ")
allData = []
allData += PerekrestokParsing(requestWord)
allData += DiksiParser(requestWord)
allData += MagnoliaParser(requestWord)
data = pd.DataFrame(allData, columns=['Магазин', 'Название', 'Ссылка', 'Цена','Скидка', 'Осталось до конца акции'])
name = f"Скидки на \'{requestWord}\' {datetime.now().date()}.xlsx"
data.to_excel(name)