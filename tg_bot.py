import asyncio
import io
import os
import re

import pandas as pd
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from undetected_playwright.async_api import async_playwright

from database import Database
from database.models import *

TG_API_TOKEN = os.getenv("TG_API_TOKEN")

BOT = Bot(token=TG_API_TOKEN)
DP = Dispatcher()
ROUTER = Router()


@DP.startup()
async def on_startup():
    DP.include_router(ROUTER)


@ROUTER.message(Command("start"))
async def start_command_handler(message: Message):
    await message.answer("Отправьте 1 или больше .xlsx файлов")


@ROUTER.message(F.document)
async def handle_single_doc(message: Message):
    await process_document(message)


async def fetch_data_from_item(url: str, xpath: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            await asyncio.sleep(10)
            await page.wait_for_selector(xpath, timeout=30)
            element = await page.query_selector(xpath)
            data = await element.text_content() if element else None
            await browser.close()

            match = re.search(r'(\d[\d\s]*)', data)
            if match:
                return float(re.sub(r'\s+', '', match.group(1)))
            return None

    except Exception:
        print(f"Error getting {url}")
        return None


async def process_document(message: Message):
    file_name = message.document.file_name
    if not file_name.endswith('.xlsx'):
        await message.reply("Пожалуйста, отправьте файл с расширением .xlsx")
        return

    file_info = await BOT.get_file(message.document.file_id)
    file_bytes = await BOT.download_file(file_info.file_path)

    file_stream = io.BytesIO(file_bytes.read())

    try:
        df = pd.read_excel(file_stream)
        items = [f"Содержимое файла *{file_name}*:"]
        products_list = []

        async with await Database().get_session() as session:
            async with session.begin():
                for _, row_pd in df.iterrows():
                    row = row_pd.to_dict()
                    items.append(
                        f"Title: `{row.get('title')}\n`"
                        f"URL: `{row.get('url')}`\n"
                        f"xpath: `{row.get('xpath')}`\n"
                    )
                    product = Products()
                    product.title = row.get('title')
                    product.url = row.get('url')
                    product.xpath = row.get('xpath')
                    products_list.append(product)

                    session.add(product)

        await session.commit()

        semaphore = asyncio.Semaphore(5)

        async def limited_fetch(item):
            async with semaphore:
                return await fetch_data_from_item(item.url, item.xpath)

        for i in range(0, len(items), 20):
            await message.reply("\n".join(items[i:i + 20]), parse_mode="Markdown")

        await message.reply(f"Поиск цен для *{file_name}* ...", parse_mode="Markdown")

        fetch_tasks = []
        for item in products_list:
            task = asyncio.create_task(limited_fetch(item))
            fetch_tasks.append(task)

        results = await asyncio.gather(*fetch_tasks)
        filtered_results = list(filter(lambda x: x is not None, results))


    except Exception as e:
        print(f"Ошибка при обработке файла {file_name}: {e}")
        await message.reply(f"Ошибка при обработке файла {file_name}")
        return

    await message.reply(
        f"Количество товаров: {len(results)}\n"
        f"Количество успешных запросов: {len(filtered_results)}\n"
        f"Максимальная цена: {max(filtered_results)}\n"
        f"Средняя цена: {sum(filtered_results) / len(filtered_results)}\n"
        f"Минимальная цена: {min(filtered_results)}"
    )


async def start_bot():
    await Database().init()

    await DP.start_polling(BOT)


if __name__ == '__main__':
    asyncio.run(start_bot())
