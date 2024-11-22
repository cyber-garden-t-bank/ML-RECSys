from fastapi import FastAPI
from src.parser_shop import get_info_for_word
import asyncio

app = FastAPI()

@app.get("/")
async def root(site_type: str, product_type: str):
    """
    Аргументы:
    - site_type (str): Тип сайта для парсинга (не используется пока).
    - product_type (str): Тип товара для парсинга.
    """
    try:
        result = await get_info_for_word(product_type)
        return {
            "message": "Парсинг завершен!",
            "site_type": site_type,
            "product_type": product_type,
            "data": result,
        }
    except Exception as e:
        return {"message": "Ошибка парсинга", "error": str(e)}
