import datetime
import json
import asyncio
import logging

import aioschedule
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN_BOT'))
dp = Dispatcher()


class Parser:
    url = "https://api.coingecko.com/api/v3/simple/price"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": os.getenv("TOKEN_API")
    }
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    async def get_coin_price(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        with open('data.json', 'w') as file:
            data = json.loads(response.text)
            data['bitcoin']['time'] = datetime.datetime.now().strftime("%H:%M")
            data['bitcoin']['usd_24h_change'] = round(data['bitcoin']['usd_24h_change'], 2)
            file.write(json.dumps(data))

    def check_coin_price(self):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
            change_price = f"{data['bitcoin']['usd_24h_change']}%"
            if int(data['bitcoin']['usd_24h_change']) > 0:
                change_price += '💹'
            else:
                change_price += "🔻"
            return (f"BTC: {data['bitcoin']['usd']} $\n\n"
                    f"Change price with 24 hours: {change_price}\n\n"
                    f"Last update: {data['bitcoin']['time']}")


parser = Parser()

asyncio.run(parser.get_coin_price())


async def update_price():
    while True:
        await parser.get_coin_price()
        await asyncio.sleep(60 * 15)
        print('update price')


@dp.message(CommandStart())
async def cdm_start(message: Message):
    await message.answer(
        "Hello, I'm a crypto bot. I will help you keep track of the current rates of all the most popular cryptocurrencies")


@dp.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'{parser.check_coin_price()}')


@dp.message(Command('photo'))
async def cmd_photo(message: Message):
    photo1 = open('img_1.png', 'r').read()
    await message.answer_photo(photo1, caption='Photo')


async def main():
    tasks = [
        asyncio.create_task(update_price()),
        asyncio.create_task(dp.start_polling(bot))
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
