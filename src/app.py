from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root(site_type: str, product_type: str):
    """
    Аргументы:
    - site_type (str): Тип сайта для парсинга.
    - product_type (str): Тип товара для парсинга.
    """
    return {
        "message": "Ручка работает!",
        "site_type": site_type,
        "product_type": product_type
    }
