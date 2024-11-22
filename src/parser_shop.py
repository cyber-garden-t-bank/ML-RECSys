import asyncio
from aiohttp import ClientSession
from parsel import Selector
from datetime import datetime
import json
import hues

async def fetch_html(session, url):
    """Fetch HTML content asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                hues.success(f"Successfully fetched URL: {url}")
            else:
                hues.warn(f"Failed to fetch URL: {url} (Status: {response.status})")
            return await response.text()
    except Exception as e:
        hues.error(f"Error fetching URL: {url} - {str(e)}")
        return ""

async def perekrestok_parsing(session, request_word):
    data = []
    base_url = "https://www.perekrestok.ru"
    url = f"{base_url}/cat/search?search={request_word}"
    hues.info("Starting Perekrestok parsing...")
    html = await fetch_html(session, url)
    if not html:
        hues.warn("Failed to parse Perekrestok. Skipping...")
        return data

    selector = Selector(html)
    try:
        last_page = int(selector.xpath('//a[@aria-current="page"]/text()').getall()[-2])
    except:
        last_page = 1

    for page in range(1, last_page + 1):
        url = f"{base_url}/cat/search?search={request_word}&page={page}"
        html = await fetch_html(session, url)
        selector = Selector(html)
        product_cards = selector.css('div.catalog-content__list')
        hues.log(product_cards)
        for product in product_cards:
            if not product.css('div.price-old'):
                continue
            market = "Перекресток"
            title = product.css('div.product-card__title::text').get()
            link = product.css('a.sc-fFubgz.fsUTLG.product-card__link::attr(href)').get()
            price = product.css('div.price-new::text').get()
            discount = product.css('div.sc-cTkwdZ.fPgnFu.product-card__badge span::text').get()
            left = "Unknown"

            if title and link and price and discount:
                title = title.strip()
                link = base_url + link.strip()
                price = price.strip()
                discount = discount.strip()
                data.append([market, title, link, price, discount, left])

    hues.success(f"Perekrestok parsing completed. Found {len(data)} products.")
    return data


# async def diksi_parsing(session, request_word):
#     """Parse Diksi data asynchronously."""
#     data = []
#     base_url = "https://dixy.ru"
#     url = f"{base_url}/catalog/search.php?q={request_word}"
#     hues.info("Starting Diksi parsing...")
#     html = await fetch_html(session, url)
#     if not html:
#         hues.warn("Failed to parse Diksi. Skipping...")
#         return data

#     selector = Selector(html)
#     try:
#         last_page = len(selector.css('a.pagination__item::attr(href)').getall())
#     except:
#         last_page = 1

#     for page in range(1, last_page + 1):
#         url = f"{base_url}/catalog/search.php?q={request_word}&PAGEN_1={page}"
#         html = await fetch_html(session, url)
#         selector = Selector(html)
#         product_cards = selector.css('div.product-container')

#         for product in product_cards:
#             if not product.css('div.dixyCatalogItemPrice__new'):
#                 continue
#             market = "Дикси"
#             title = product.css('div.dixyCatalogItem__title::text').get().strip()
#             link = url
#             price = f"{product.css('div.dixyCatalogItemPrice__new::text').get().strip()}," \
#                     f"{product.css('div.dixyCatalogItemPrice__kopeck::text').get().strip()} ₽"
#             discount = product.css('div.dixyCatalogItemPrice__discount::text').get().strip()
#             date_end = datetime.strptime(product.css('div.dixyCatalogItem__term::text').get().split('-')[1].strip(), "%d.%m.%Y").date()
#             left = str(date_end - datetime.now().date()).split(',')[0]
#             data.append([market, title, link, price, discount, left])

#     hues.success(f"Diksi parsing completed. Found {len(data)} products.")
#     return data

async def get_info_for_word(request_word):
    async with ClientSession() as session:
        tasks = [
            perekrestok_parsing(session, request_word),
           # diksi_parsing(session, request_word),
        ]
        results = await asyncio.gather(*tasks)

    all_data = [item for sublist in results for item in sublist]
    json_data = json.dumps(all_data, ensure_ascii=False, indent=4)
    hues.success(f"Parsing completed for '{request_word}'. Total products found: {len(all_data)}")
    return json_data
